# NoteX

NoteX aims to make taking structured notes with LaTeX easy. Write your content in a plain text file using simple expressions such as `question(This is a question)` and `answer(The answer)`, and let NoteX handle the LaTeX document structure and box formatting.

The goal is to spend time writing and studying your notes without having to write LaTeX boilerplate for every box.

## Planned note syntax

For example, a text file could contain:

```text
question(This is a question)
answer(The answer)
note(This is something worth remembering.)
definitionbox(Velocity is the rate of change of position.)
summarybox(The main takeaways from today's lesson.)
```

Each expression will map to the corresponding box environment defined in [class_notes_boxes.tex](class_notes_boxes.tex). For example:

```text
question(This is a question)
```

will become:

```latex
\begin{question}
This is a question
\end{question}
```

The converter will generate the surrounding LaTeX document and load the box definitions. The collection currently includes 57 box types for questions, answers, definitions, examples, formulas, warnings, summaries, and other kinds of notes. See the [box guide](class_notes_boxes_guide.md) for the full catalog.

This text syntax is the intended interface; the converter has not been implemented yet. Details such as multiline content, literal parentheses, and LaTeX special characters still need to be defined.

## Current state

The project currently contains the LaTeX foundation:

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

1. **Plain text to LaTeX:** build a converter that reads a normal text file, recognizes box expressions, and produces a compilable `.tex` document using the existing box definitions.
2. **Incremental builds:** avoid rebuilding everything on every edit and reuse unchanged work where possible.
3. **Live preview:** show the rendered notes as the source text changes.
4. **Richer notes:** extend the syntax and workflow as more complex note-taking needs arise.

The first milestone is a straightforward text-to-LaTeX conversion workflow. Incremental builds and live preview are planned improvements.
