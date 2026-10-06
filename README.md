# NoteX

NoteX aims to make taking structured notes with LaTeX easy. Write your content in a plain text file using simple expressions such as `question(This is a question)` and `answer(The answer)`, and let NoteX handle the LaTeX document structure and box formatting.

The goal is to spend time writing and studying your notes without having to write LaTeX boilerplate for every box.

## Note syntax

For example, a text file could contain:

```text
question(This is a question)
answer(The answer)
note(This is something worth remembering.)
definitionbox(Velocity is the rate of change of position.)
summarybox(The main takeaways from today's lesson.)
```

`note(...)` becomes a regular paragraph without a box or title. Other expressions map to the corresponding box environment defined in [class_notes_boxes.tex](class_notes_boxes.tex). For example:

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

LaTeX special characters are escaped automatically. Raw LaTeX commands and math syntax are not supported yet. Ordinary line breaks are treated as spaces by LaTeX; blank lines separate paragraphs.

## Headings and text formatting

[class_notes_text.tex](class_notes_text.tex) defines the headings and text formatting loaded automatically by the converter. Use `--text-template PATH` to select another definitions file.

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

## Convert your notes

Use Python 3.10 or newer. No third-party Python packages are required. Save your notes as a UTF-8 text file, then run:

```sh
python3 convert.py notes.txt -o notes.tex
```

If you omit `-o`, the output uses the input filename with a `.tex` extension. Unknown box names and malformed expressions produce an error with a line and column number.

To create a PDF, install the LaTeX packages described below and run:

```sh
pdflatex -interaction=nonstopmode -halt-on-error notes.tex
```

The generated document references the absolute locations of `class_notes_boxes.tex` and `class_notes_text.tex`, so you can compile it locally from another directory. To move it to another machine or an online editor, include both definitions files and change the generated `\input` lines to relative filenames.

## Current state

The project currently contains a text-to-LaTeX converter and the LaTeX foundation:

- [convert.py](convert.py): parser, plain-text escaping, and command-line document generation.
- [class_notes_boxes.tex](class_notes_boxes.tex): reusable box definitions and a complete demonstration document.
- [class_notes_boxes_guide.md](class_notes_boxes_guide.md): the box catalog, usage instructions, and examples.

You can compile the demonstration or use the boxes directly in a LaTeX document today.

## Try the existing boxes

Install a LaTeX distribution such as TeX Live or MiKTeX with the packages listed in the [guide](class_notes_boxes_guide.md#1-compile-the-demonstration). From the project directory, run:

```sh
pdflatex -interaction=nonstopmode -halt-on-error class_notes_boxes.tex
pdflatex -interaction=nonstopmode -halt-on-error class_notes_boxes.tex
```

This creates `class_notes_boxes.pdf`. The second pass fills in the table of contents. You can also upload the `.tex` file to a LaTeX editor and compile it there.

## Roadmap

1. **Plain text to LaTeX (implemented):** convert box expressions in a text file into a `.tex` document using the existing box definitions.
2. **Incremental builds:** avoid rebuilding everything on every edit and reuse unchanged work where possible.
3. **Live preview:** show the rendered notes as the source text changes.
4. **Richer notes:** extend the syntax and workflow as more complex note-taking needs arise.

Incremental builds and live preview are planned improvements.
