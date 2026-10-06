# Class notes boxes: documentation

This collection provides **57 reusable box environments** for a broad range of subjects. There is no finite universal list for every course; these cover common note-taking roles and can be extended. Boxes provide layout and labels, not automatic scientific validation, citations, timeline drawing, or syntax conversion.

## Files

- `class_notes_boxes.tex`: one complete, compilable demonstration with all definitions and examples. It also works as a reusable preamble module.
- `class_notes_boxes_guide.md`: this documentation.

## 1. Compile the demonstration

Install a LaTeX distribution with `tcolorbox`, `amsmath`, `amssymb`, `graphicx`, `booktabs`, `listings`, `geometry`, `fontenc`, `lmodern`, and `hyperref`. These are common TeX Live/MiKTeX packages. Use pdfLaTeX for the supplied examples.

```sh
pdflatex -interaction=nonstopmode -halt-on-error class_notes_boxes.tex
pdflatex -interaction=nonstopmode -halt-on-error class_notes_boxes.tex
```

The second pass fills in the table of contents. Alternatively, upload the `.tex` file to a LaTeX editor and compile it. You do not need Python to use these boxes.

## 2. Use all boxes in a new document

Keep `class_notes_boxes.tex` beside your new `lecture.tex`. Use:

```latex
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}

% Load only the definitions; skip the demonstration document.
\def\NotesBoxesOnly{1}
\input{class_notes_boxes.tex}

\title{Physics I: Newton's Laws}
\author{Your name}
\date{October 6, 2026}

\begin{document}
\maketitle

\begin{question}
What is Newton's second law?
\end{question}

\begin{answer}
For constant mass in an inertial reference frame,
$\vec{F}_{\mathrm{net}}=m\vec{a}$.
\end{answer}

\begin{note}
Use the net force, not just one of the forces.
\end{note}

\end{document}
```

Load the collection once, in the preamble, before `\begin{document}`. Do not paste an entire standalone document inside another document. If your existing template already defines an environment named `question`, `answer`, `note`, `warning`, or `danger`, rename the conflicting environment in this collection before loading it. Most other names end in `box` to reduce collisions.

## 3. General syntax

Every box accepts optional `tcolorbox` settings:

```latex
\begin{definitionbox}[title={Velocity}]
Velocity is the rate of change of position.
\end{definitionbox}
```

Without options, each environment uses its default title. Titles may contain commas if wrapped in braces: `[title={Mass, force, and acceleration}]`.

### Question numbering

```latex
\begin{question}
This is numbered automatically.
\end{question}

\begin{question}[title={Question 25}]
This has a manually chosen display title.
\end{question}
```

Automatic numbers start at 1 and run through the document. A custom title changes only the displayed title; it does not synchronize the counter. To make the next automatic question number 25, place this immediately before it:

```latex
\setcounter{tcb@cnt@question}{24}
\begin{question}
This is Question 25, and the following question will be 26.
\end{question}
```

To reference an automatically numbered question, use `[label={q:motion}]`, then `Question~\ref{q:motion}` elsewhere. Compile twice. Other box types are unnumbered; adding a label to them does not create a meaningful automatic box number.

### Text styles and colors

- `answer`: italic prose; equations retain ordinary math formatting.
- `note`: normal text on a soft green background.
- `warning`: yellow text on a dark background for contrast.
- `danger`: red border and title bar, pale red background, dark body text.
- Blue: definitions, ideas, quantitative rules.
- Gray: examples, evidence, and working steps.
- Green: helpful notes, checks, and summaries.
- Amber: assumptions, uncertainty, and common errors.
- Purple: reflection, connections requiring judgment, and planning.

All boxes are breakable across pages when their content allows it. Large images, tables, and other indivisible objects can still overflow. Avoid deeply nested boxes.

## 4. Complete catalog


### Everyday learning

| Environment | Default title | What to put inside |
|---|---|---|
| `note` | Note | Supplementary explanation or a helpful reminder. |
| `definitionbox` | Definition | A term with its precise meaning. |
| `conceptbox` | Key Concept | An important idea in your own words. |
| `notationbox` | Notation | Explain symbols, abbreviations, and conventions. |
| `objectivebox` | Learning Objectives | State what you should be able to explain or do. |
| `contextbox` | Background / Context | Give background needed to understand a topic. |
| `connectionbox` | Connection | Connect a topic to earlier lessons or another subject. |
| `summarybox` | Summary | Record the main takeaways of a lesson. |

### Questions and study

| Environment | Default title | What to put inside |
|---|---|---|
| `question` | Question | A numbered question; numbering increases automatically. |
| `answer` | Answer | An answer with automatically italicized prose. |
| `examplebox` | Example | A concrete illustration of an idea. |
| `solutionbox` | Worked Solution | Show the reasoning and steps of a calculation. |
| `practicebox` | Practice | An exercise to complete independently. |
| `recallbox` | Active Recall | A prompt to answer without consulting the notes. |
| `hintbox` | Hint | A small clue that does not reveal the entire solution. |
| `misconceptionbox` | Common Mistake | Identify an error, explain why it fails, and give a correction. |
| `askbox` | Ask / Clarify | An unanswered question for an instructor or later research. |
| `actionbox` | Action Item | A task, its next step, and an optional due date. |
| `reflectionbox` | Reflection | Evaluate your understanding, approach, or learning progress. |

### Math and quantitative reasoning

| Environment | Default title | What to put inside |
|---|---|---|
| `formulabox` | Formula / Rule | An equation or rule, with variables, units, and conditions of use. |
| `theorembox` | Theorem / Principle | A formal result together with its hypotheses. |
| `proofbox` | Proof | A logical argument establishing a claim. |
| `derivationbox` | Derivation | Develop an equation from definitions or established relationships. |
| `assumptionbox` | Assumptions | Make the conditions of a model or calculation explicit. |
| `givenbox` | Given / Find | Separate known quantities from the target quantity. |
| `unitsbox` | Units / Dimensions | Define units, convert them, or check dimensions. |
| `checkbox` | Result Check | Check sign, magnitude, units, limiting behavior, or plausibility. |
| `specialcasebox` | Special Case / Exception | Identify boundaries, exceptions, or cases requiring different treatment. |

### Science, labs, and research

| Environment | Default title | What to put inside |
|---|---|---|
| `hypothesisbox` | Hypothesis | A testable prediction with a rationale. |
| `variablesbox` | Variables / Controls | List independent, dependent, and controlled variables. |
| `equipmentbox` | Equipment / Materials | List apparatus, quantities, and relevant specifications. |
| `procedurebox` | Procedure / Method | Numbered steps for carrying out a repeatable task. |
| `observationbox` | Observation | Describe what was observed without mixing in interpretation. |
| `databox` | Data | Measurements or a small table with units and labels. |
| `uncertaintybox` | Uncertainty / Error | Discuss measurement uncertainty and systematic or random errors. |
| `analysisbox` | Analysis | Explain how data or evidence supports your interpretation. |
| `conclusionbox` | Conclusion | State the result, evidence, and limits of the conclusion. |

### Humanities, languages, and social sciences

| Environment | Default title | What to put inside |
|---|---|---|
| `claimbox` | Claim / Thesis | A position that needs support from evidence. |
| `evidencebox` | Evidence / Source | Evidence with enough source information to find it again. |
| `quotationbox` | Quotation | An exact quotation with its source and page or location. |
| `interpretationbox` | Interpretation | Explain what a passage, event, or piece of evidence means. |
| `counterargumentbox` | Counterargument | Present an objection fairly and evaluate a response. |
| `comparisonbox` | Comparison | Compare related ideas using the same criteria. |
| `timelinebox` | Timeline | Events in chronological order with their significance. |
| `casebox` | Case Study | Apply a model to a specific person, organization, event, or scenario. |
| `vocabularybox` | Vocabulary | A word, meaning, pronunciation, and an example sentence. |
| `grammarbox` | Grammar / Language Pattern | A language pattern with examples and exceptions. |

### Programming, engineering, and practical work

| Environment | Default title | What to put inside |
|---|---|---|
| `codebox` | Code | A short code listing with its language and purpose. |
| `outputbox` | Expected / Actual Output | Record a program result, calculation output, or observed behavior. |
| `debugbox` | Error / Fix | Record the symptom, root cause, correction, and verification. |
| `designbox` | Design Decision | Record a decision, alternatives, reasons, and trade-offs. |
| `testbox` | Test Case | Specify input, expected result, and pass or fail evidence. |
| `figurebox` | Figure / Diagram | A labeled diagram or image with a descriptive caption. |
| `techniquebox` | Technique / Skill | Describe a practical technique and its success criteria. |
| `feedbackbox` | Feedback / Critique | Record feedback and a concrete improvement to make. |

### Safety and cautions

| Environment | Default title | What to put inside |
|---|---|---|
| `warning` | Warning | A caution requiring attention; yellow text on a dark background. |
| `danger` | Danger | A serious hazard; red frame and title bar with a pale red body. |

## 5. Rich contents

### Equations and labeled fields

```latex
\begin{formulabox}[title={Newton's Second Law}]
\[
  \sum \vec{F}=m\vec{a}
\]
\NotesField{Symbols}{$m$ is mass; $\vec{a}$ is acceleration.}
\NotesField{Units}{Newtons, kilograms, and $\mathrm{m/s^2}$.}
\NotesField{When it applies}{Constant mass in an inertial frame.}
\end{formulabox}
```

`\NotesField{Label}{Content}` works inside any box. Labels are your choice. Useful fields include Purpose, Given, Find, Assumptions, Source, Page, Evidence, Interpretation, Deadline, Expected, and Actual.

### Numbered steps and bullet points

```latex
\begin{procedurebox}
\begin{enumerate}
  \item Draw the forces.
  \item Choose coordinate axes.
  \item Apply Newton's second law.
\end{enumerate}
\end{procedurebox}

\begin{summarybox}
\begin{itemize}
  \item Net force determines acceleration.
  \item Mass measures resistance to acceleration.
\end{itemize}
\end{summarybox}
```

### A table

```latex
\begin{comparisonbox}[title={Speed versus velocity}]
\centering
\begin{tabular}{lll}
\toprule
Property & Speed & Velocity \\
\midrule
Type & Scalar & Vector \\
Direction & No & Yes \\
\bottomrule
\end{tabular}
\end{comparisonbox}
```

Use ordinary tables for small comparisons. Long tables need special care inside breakable boxes; put large multipage tables outside boxes. The collection does not resize wide tables automatically.

### Code and output

```latex
\begin{codebox}[title={Python example}]
\begin{lstlisting}[style=notescode,language=Python]
def square(number):
    return number * number

print(square(5))
\end{lstlisting}
\end{codebox}

\begin{outputbox}
\begin{lstlisting}[style=notescode]
25
\end{lstlisting}
\end{outputbox}
```

Use `lstlisting` for literal code. Do not escape underscores, braces, percent signs, or backslashes inside it. For Java, change `language=Python` to `language=Java`. The environment formats code; it does not execute it. The provided listing style is designed for ordinary ASCII source; international scripts may need a different code-rendering setup.

### Images

```latex
\begin{figurebox}[title={Free-body diagram}]
\centering
\includegraphics[width=0.7\linewidth]{force_diagram.png}
\par\small Figure: Forces acting on the block. Source: your source here.
\end{figurebox}
```

Supply your own image file. Do not put a floating `figure` environment inside a box. `figurebox` is a container; it does not draw diagrams or maintain a separate figure counter.

### Sources and quotations

```latex
\begin{evidencebox}
\NotesField{Source}{Author, title, year, page 42.}
\NotesField{Evidence}{A concise paraphrase of the relevant finding.}
\NotesField{Relevance}{Explain how it supports your claim.}
\end{evidencebox}
```

Quotation and evidence boxes do not generate bibliography entries. For automatic citations, add a bibliography system separately and use its citation commands within the boxes.

## 6. Customize or extend

### Change one box

```latex
\begin{note}[title={Exam reminder},colback=green!10!white]
Review unit conversions.
\end{note}
```

### Change all boxes

After loading the collection, add:

```latex
\tcbset{notesbase/.append style={arc=1mm,boxrule=1pt}}
```

To change a shared color family:

```latex
\tcbset{notesgreen/.append style={colback=green!4!white}}
```

### Add a new box type

Add this in your preamble, after loading the collection, or in the BOX DEFINITIONS section of the collection:

```latex
\newtcolorbox{discussionbox}[1][]{
  notesbase,
  notespurple,
  title={Discussion},
  #1
}
```

Then use it normally:

```latex
\begin{discussionbox}[title={Class discussion}]
What evidence would change your interpretation?
\end{discussionbox}
```

`[1][]` means one optional argument with an empty default. `#1` passes those optional settings to the box. Keeping `#1` last lets per-box settings override the defaults. Choose an environment name that is not already defined. Add your new environment to this guide's catalog so its meaning stays clear.

## 7. Suggested combinations by subject

| Subject | A useful starting set |
|---|---|
| Mathematics | definitionbox, theorembox, proofbox, formulabox, solutionbox, specialcasebox |
| Physics / chemistry | givenbox, assumptionbox, formulabox, unitsbox, figurebox, checkbox |
| Biology | definitionbox, figurebox, comparisonbox, procedurebox, connectionbox |
| Laboratory / research | hypothesisbox, variablesbox, equipmentbox, procedurebox, databox, uncertaintybox, conclusionbox |
| History / literature / philosophy | contextbox, claimbox, evidencebox, quotationbox, interpretationbox, counterargumentbox, timelinebox |
| Languages | vocabularybox, grammarbox, examplebox, practicebox, recallbox |
| Business / social sciences | conceptbox, casebox, comparisonbox, analysisbox, designbox, conclusionbox |
| Programming / engineering | codebox, outputbox, debugbox, designbox, testbox, procedurebox |
| Art / studio / practical skills | figurebox, techniquebox, feedbackbox, reflectionbox, actionbox |
| Any lecture | objectivebox, note, question, answer, summarybox, askbox |

Use only the types you need. Avoid putting every paragraph in a box. Choose a box by the purpose of its content, not only by its color.

## 8. Future Python converter

The `.tex` file contains formatting; Python can supply the content. A `.txt` or `.md` extension is fine if your parser knows the syntax. For example, your future mapping could include:

```python
BOX_ENVIRONMENTS = {
    "question": "question",
    "answer": "answer",
    "note": "note",
    "definition": "definitionbox",
    "formula": "formulabox",
    "warning": "warning",
    "danger": "danger",
}
```

Render a recognized block as `\begin{environment}` plus its converted body and `\end{environment}`. Validate the environment name against a fixed registry. Preserve math and code as separate content types; ordinary LaTeX text needs escaping for characters such as `%`, `&`, `_`, and `#`. Do not indiscriminately escape complete equations or code listings. This delivery contains the LaTeX collection and its documentation, not the Python converter.

## 9. Scope and compatibility

- Demonstrated with the `article` class and pdfLaTeX. Other document classes may need adjustments.
- General non-Latin language support is not configured. Select appropriate fonts and language packages for those classes; using XeLaTeX alone does not supply all required fonts.
- A theorem or proof box is a visual wrapper, not a formal theorem-management system. Proofs have no automatic end-of-proof symbol.
- `question` is the only automatically numbered box. Answers are not automatically linked to questions or hidden.
- The collection does not include automatic flashcard export, answer hiding, grading, bibliography generation, or Python parsing.
- In ordinary LaTeX text, write `50\%`, `A\&B`, and `file\_name`. Use `$...$` for inline mathematics and `\[...\]` for displayed mathematics.
- Useful package reference: https://ctan.org/pkg/tcolorbox
