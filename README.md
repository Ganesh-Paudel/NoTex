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

Content is treated as plain text: LaTeX special characters are escaped automatically. Raw LaTeX commands and math syntax are not supported yet. Ordinary line breaks are treated as spaces by LaTeX; blank lines separate paragraphs.

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

The generated document references the absolute location of `class_notes_boxes.tex`, so you can compile it locally from another directory. To move it to another machine or an online editor, include the definitions file and change the generated `\input` line to `\input{class_notes_boxes.tex}`.

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
