# NoteX

NoteX aims to make taking structured notes with LaTeX easy. Write your content in a plain text file using simple expressions such as `question(This is a question)` and `answer(The answer)`, and let NoteX handle the LaTeX document structure and box formatting.

The goal is to spend time writing and studying your notes without having to write LaTeX boilerplate for every box.

## Quick start

Requires Python 3.10 or newer. The converter has no third-party runtime Python dependencies. From a checkout:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
notex notes.txt
```

The `notex` command and `python -m notex` use the installed package. The original `python3 convert.py notes.txt` command also works directly from this checkout without installation.

For PDF output on Ubuntu/Debian:

```sh
sudo apt update
sudo apt install texlive-latex-recommended texlive-latex-extra lmodern
notex notes.txt --pdf
```

This produces `notes.tex` and `notes.pdf`. PDF compilation runs in a temporary directory, disables shell escape, and has a 30-second timeout. A syntax or compilation failure preserves the previous generated files. Each output file is replaced atomically; publication of the pair is not a filesystem transaction.

## Note syntax

For example, a text file could contain:

```text
question(This is a question)
answer(The answer)
note(This is something worth remembering.)
definitionbox(Velocity is the rate of change of position.)
summarybox(The main takeaways from today's lesson.)
```

`note(...)` becomes a regular paragraph without a box or title. Other expressions map to the corresponding box environment defined in [class_notes_boxes.tex](src/notex/templates/class_notes_boxes.tex). For example:

```text
question(This is a question)
```

will become:

```latex
\begin{question}
This is a question
\end{question}
```

The converter generates the surrounding LaTeX document and loads the box definitions. The collection currently includes 57 box types for questions, answers, definitions, examples, formulas, warnings, summaries, and other kinds of notes. See the [box guide](class_notes_boxes_guide.md) for the full catalog.

Content can span multiple lines. Balanced parentheses inside content work normally, for example `answer(A function f(x) takes an input.)`. Use `\(` or `\)` for an unmatched literal parenthesis and `\\` for a literal backslash. Whitespace between boxes is allowed; other text outside boxes produces an error.

LaTeX special characters in ordinary text are escaped automatically. Use `math{...}` for mathematical notation; raw LaTeX commands are not accepted. Ordinary text line breaks are treated as spaces by LaTeX; blank lines separate paragraphs and `newline()` forces a text line break.

## Headings and text formatting

[class_notes_text.tex](src/notex/templates/class_notes_text.tex) defines the headings and text formatting loaded automatically by the converter. Use `--text-template PATH` to select another definitions file.

Headings use the same parentheses syntax as boxes:

```text
title(My Class Notes)
subtitle(Week One)
chapter(Motion)
section(Average Speed)
subsection(Worked Examples)
subsubsection(Units)
paragraph(Reminder)
subparagraph(Details)
note(This is a regular paragraph.)
```

`title` and `subtitle` are centered. `chapter` is an unnumbered section heading because the generated article document has no native chapters. Sections and subsections use standard LaTeX numbering; paragraph and subparagraph headings run into the following text.

Inside headings, paragraphs, and boxes, use `style{content}`:

```text
note(bold{Important}, italic{a term}, underline{a reminder}, and bold{italic{combined styles}}.)
answer(large{The answer is 12 meters per second.})
```

Supported styles: `bold`, `italic`, `underline`, `emphasis`, `monospace`, `smallcaps`, `superscript`, and `subscript`.

Sizes from smallest to largest: `tiny`, `scriptsize`, `footnotesize`, `small`, `normalsize`, `large`, `larger`, `largest`, `huge`, and `hugest`. The last five correspond to LaTeX's `large`, `Large`, `LARGE`, `huge`, and `Huge`. Size changes apply only to their enclosed text. Use blank lines to separate paragraphs; underline is best suited to short phrases because it does not wrap across lines.

Escape literal braces with `\{` and `\}`; for example, `note(bold\{literal\})` prints the formatting syntax literally.

Unescaped parentheses and braces must balance, including inside formatted text. Escapes `\(`, `\)`, `\{`, `\}`, and `\\` are interpreted once. Malformed input reports a line and column in the original notes file. Delimiter and formatting nesting is limited to 64 levels.

The parser creates structured text and style nodes with source offsets before LaTeX rendering. Heading and style names come from declarations next to the commands in the text template, for example `% notex-style bold NotesBold` and `% notex-heading section NotesSection`. A custom template must declare both headings and styles and define each corresponding one-argument command with `\newcommand`.

## Mathematics and line breaks

Write math inside notes, boxes, headings, and text styles:

```text
note(The probability is math{1/10}. A nested root is math{sqrt(1/10)}.)
formulabox(math{v=d/t})
note(bold{Remember math{x_i^2 + 2*x_i + 1 = (x_i+1)^2}.})
```

`math{1/10}` generates `\(\frac{1}{10}\)`. Operators respect algebraic precedence; group a compound numerator or denominator with parentheses, for example `(x+1)/(x-1)`. Use `^` or `**` for powers and `_` for subscripts. `2(x+1)` is implicit multiplication; write `x*(y+1)` when a variable followed by parentheses means multiplication, because `f(x)` is function notation.

For standalone display equations, use `equation(...)` or a top-level `math{...}`:

```text
equation(summation(i^2,i,1,n))
equation(integral(x^2,x,0,1))
equation(derivative(x^3,x,2))
equation(partial(x*y,x))
equation(
  a=(x+1)^2
  =x^2+2*x+1
)
note(First line. newline() Second line.)
```

Within math, actual top-level newlines, `;`, or `newline()` separate equation rows. Rows align at their relation sign; later rows may start with `=` and omit the left side. Newlines inside function arguments or grouped expressions are only whitespace. A standalone `newline()` adds paragraph spacing.

Math supports nested fractions and roots, sums and products, definite/indefinite integrals, ordinary/partial derivatives, limits, binomial coefficients, trig/log functions, Greek symbols, scientific notation, and factorials. See [the math syntax guide](docs/math-syntax.md) for argument order, aliases, operators, and examples. These expressions **typeset mathematics without evaluating, simplifying, differentiating, integrating, or solving it**. Derivative orders must be positive integers. Raw LaTeX/Python commands are rejected, and syntax errors report their location in the original notes file.

`note(math\{1/10\})` prints `math{1/10}` literally. `math`, `equation`, and `newline` are built-in top-level names; `math` and `newline` are reserved inside text and cannot be replaced by template styles. The original `note` environment can still exist in the box template.

## CLI

```sh
notex notes.txt                       # Generate notes.tex
notex notes.txt -o lecture.tex        # Choose the output filename
notex notes.txt --pdf --timeout 60    # Also create notes.pdf
notex notes.txt --json                # Structured result or diagnostics
notex --version
```

Select trusted custom LaTeX definitions with `--template PATH` and `--text-template PATH`. Output files must not alias the input, either template, or one another, including symlinks and hard links. Output directories must already exist.

Exit codes: `0` for success, `1` for conversion/file/build errors, and `2` for invalid command-line arguments. With `--json`, successful results go to stdout; conversion diagnostics go to stderr. Argument errors retain argparse's standard usage output.

A syntax diagnostic includes `kind`, `message`, `offset`, `line`, `column`, and `source`. Offsets count Python Unicode characters from zero; line and column numbers start at one. The renderer escapes ordinary text and validates expression names. Custom templates execute local LaTeX and must be trusted; disabling shell escape does not make TeX an isolation boundary for an internet-facing service.

The generated document imports both templates by absolute path. To move it to another machine or an online editor, copy the template files from `src/notex/templates/` beside the document and change the generated `\input` lines to relative filenames.

The PDF helper currently uses one pdfLaTeX pass, appropriate for the supplied note examples. It does not yet resolve multi-pass features such as tables of contents and cross-references. For a custom document that needs those features, use `latexmk` or run pdfLaTeX again.

## Python API

```python
from notex import ParseError, convert_source
from notex.compiler import compile_pdf

try:
    result = convert_source("section(Motion) note(bold{Remember the units.})")
except ParseError as error:
    print(error.as_dict())
else:
    print(result.latex)
    pdf = compile_pdf(result.latex)
    # pdf.content contains the PDF bytes; no output file has been written.
```

`convert_source()` accepts a complete source snapshot and returns an immutable conversion result with the parsed expressions and generated LaTeX. It reads templates but does not write artifacts. This API is the shared foundation for the CLI and planned live preview.

## Project structure

```text
src/notex/
  models.py       # Syntax tree and structured diagnostics
  templates.py    # Template declarations and validation
  parser.py       # Source text to structured nodes
  renderer.py     # Structured nodes to LaTeX
  math_parser.py  # Mathematical expressions, precedence, and function calls
  math_renderer.py # Math nodes to LaTeX
  syntax.py       # Shared built-in keywords and nesting limit
  service.py      # Conversion API and atomic publication
  compiler.py     # Timeout-bounded PDF builds
  cli.py          # Installed command-line interface
  templates/      # Bundled box and text-formatting definitions
convert.py        # Compatibility wrapper for the original command/API
tests/           # Parser, CLI, file protection, and PDF regression tests
tools/           # Installed-wheel verification
```

The LaTeX templates now live in `src/notex/templates/` and ship in the installed wheel. Edit those canonical files when changing bundled styles. No duplicate root-level templates are maintained. See the [box guide](class_notes_boxes_guide.md) for the full template catalog; `note(...)` is a plain paragraph in the converter even though the LaTeX collection retains a `note` environment for direct use.

## Development

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]' -c requirements-dev.txt
ruff check .
ruff format --check .
mypy
python -m coverage run -m unittest discover -s tests
python -m coverage report
python -m build
python -m twine check --strict dist/*
python tools/verify_wheel.py dist/*.whl
```

The direct development tools are pinned in `requirements-dev.txt`; indirect dependencies resolve for the selected Python version. Runtime dependencies remain empty. Tests use standard-library `unittest`. The real PDF integration test skips when `pdflatex` is unavailable; CI has a dedicated LaTeX job to exercise it. The regular CI matrix covers Python 3.10, 3.12, and 3.13, lint, formatting, strict type checks, an 85% coverage floor, distribution metadata, and installed-wheel resource loading.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the change workflow and [architecture](docs/architecture.md) for design details.

## Try the LaTeX box demonstration

From the project directory, with TeX Live installed:

```sh
pdflatex -interaction=nonstopmode -halt-on-error src/notex/templates/class_notes_boxes.tex
pdflatex -interaction=nonstopmode -halt-on-error src/notex/templates/class_notes_boxes.tex
```

This creates `class_notes_boxes.pdf`; the second pass fills its table of contents. You can also copy the template into another LaTeX project and use it independently of Python.

## Live preview roadmap

The converter and PDF build foundation are implemented. Watching notes, scheduling builds, and displaying updates are the next milestones; there is no preview server or watcher yet. See [the live preview implementation plan](docs/live-preview.md) for architecture, build ordering, API proposals, and acceptance tests.

Before a public package release, choose a project license and confirm the distribution name. No license or public registry ownership has been assumed.


AI was used for most of the building of this tool.