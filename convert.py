"""Convert plain-text box expressions into a complete LaTeX document."""

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


DEFAULT_TEMPLATE = Path(__file__).resolve().with_name("class_notes_boxes.tex")


@dataclass(frozen=True)
class Box:
    name: str
    content: str


class ParseError(ValueError):
    """Invalid note syntax, with a source location."""


def load_box_names(template: Path) -> set[str]:
    """Read environment names from the existing tcolorbox definitions."""
    source = template.read_text(encoding="utf-8")
    names = set(re.findall(r"\\newtcolorbox(?:\[[^\]]*\])?\{([A-Za-z][A-Za-z0-9_]*)\}", source))
    if not names:
        raise ValueError(f"No box definitions found in {template}")
    return names


def parse_notes(source: str, allowed_names: set[str]) -> list[Box]:
    """Parse boxes, preserving balanced parentheses and multiline content.

    Within content, \\( and \\) represent literal unmatched parentheses,
    and \\\\ represents a literal backslash. Other backslashes remain text.
    """
    boxes = []
    pos = 0

    def fail(message: str, at: int) -> None:
        line = source.count("\n", 0, at) + 1
        column = at - source.rfind("\n", 0, at)
        raise ParseError(f"line {line}, column {column}: {message}")

    while pos < len(source):
        if source[pos].isspace():
            pos += 1
            continue
        start = pos
        match = re.match(r"[A-Za-z][A-Za-z0-9_]*", source[pos:])
        if match is None:
            fail("expected a box name", pos)
        name = match.group()
        if name not in allowed_names:
            fail(f"unknown box name '{name}'", start)
        pos += len(name)
        while pos < len(source) and source[pos].isspace():
            pos += 1
        if pos == len(source) or source[pos] != "(":
            fail(f"expected '(' after '{name}'", pos)
        pos += 1
        depth = 1
        content = []
        while pos < len(source):
            char = source[pos]
            if char == "\\" and pos + 1 < len(source) and source[pos + 1] in "()\\":
                content.append(source[pos + 1])
                pos += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    pos += 1
                    break
            content.append(char)
            pos += 1
        if depth:
            fail(f"missing closing ')' for '{name}'", start)
        boxes.append(Box(name, "".join(content).strip()))
    return boxes


def escape_latex(text: str) -> str:
    """Escape plain text once, including characters used for LaTeX commands."""
    replacements = {
        "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}",
        "$": r"\$", "&": r"\&", "#": r"\#", "%": r"\%",
        "_": r"\_", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def render_document(boxes: list[Box], template: Path = DEFAULT_TEMPLATE) -> str:
    template_path = template.resolve().as_posix()
    if any(char in template_path for char in "%{}\n\r"):
        raise ValueError("The template path cannot contain %, braces, or newlines")
    body = "\n\n".join(
        f"\\begin{{{box.name}}}\n{escape_latex(box.content)}\n\\end{{{box.name}}}"
        for box in boxes
    )
    return (
        "\\documentclass[11pt]{article}\n"
        "\\usepackage[margin=1in]{geometry}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage{lmodern}\n\n"
        "\\def\\NotesBoxesOnly{1}\n"
        f"\\input{{\\detokenize{{{template_path}}}}}\n\n"
        f"\\begin{{document}}\n\n{body}\n\n\\end{{document}}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 text file containing box expressions")
    parser.add_argument("-o", "--output", type=Path, help="output .tex file (default: input name with .tex extension)")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="LaTeX box definitions file")
    args = parser.parse_args()
    output = args.output or args.input.with_suffix(".tex")
    try:
        if output.resolve() in {args.input.resolve(), args.template.resolve()}:
            raise ValueError("Output must differ from the input and template files")
        names = load_box_names(args.template)
        boxes = parse_notes(args.input.read_text(encoding="utf-8-sig"), names)
        document = render_document(boxes, args.template)
        output.write_text(document, encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        print(f"{args.input}: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {output} ({len(boxes)} boxes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
