"""Render syntax trees into escaped LaTeX without reparsing literal text."""

from collections.abc import Mapping, Sequence
from pathlib import Path

from .math_renderer import render_math
from .models import Box, InlineNode, LineBreak, Math, Text
from .parser import NotesParser
from .syntax import BUILTIN_EXPRESSIONS
from .templates import (
    DEFAULT_TEMPLATE,
    DEFAULT_TEXT_TEMPLATE,
    load_box_names,
    load_text_commands,
)


def escape_latex(text: str) -> str:
    """Escape plain text once, including characters used for LaTeX commands."""
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "#": r"\#",
        "%": r"\%",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    # Map original characters once so generated escape commands are not escaped.
    return "".join(replacements.get(char, char) for char in text)


def render_inline(nodes: tuple[InlineNode, ...], styles: Mapping[str, str]) -> str:
    """Render already-parsed nodes; never reinterpret escaped text as syntax."""
    parts = []
    for node in nodes:
        if isinstance(node, Text):
            parts.append(escape_latex(node.value))
        elif isinstance(node, Math):
            parts.append(render_math(node))
        elif isinstance(node, LineBreak):
            # leavevmode also makes a leading newline() valid at paragraph start.
            parts.append(r"\leavevmode\newline{}")
        else:
            parts.append(f"\\{styles[node.name]}{{{render_inline(node.children, styles)}}}")
    return "".join(parts)


def format_text(text: str) -> str:
    """Convenience API for standalone inline text using the same parser."""
    headings, styles = load_text_commands(DEFAULT_TEXT_TEMPLATE)
    parser = NotesParser(text, set(), headings, styles)
    return render_inline(parser.content(None, 0), styles)


def render_document(
    boxes: Sequence[Box],
    template: Path = DEFAULT_TEMPLATE,
    text_template: Path = DEFAULT_TEXT_TEMPLATE,
) -> str:
    """Wrap rendered expressions in an article that imports both templates."""
    paths = [path.resolve().as_posix() for path in (template, text_template)]
    # detokenize handles ordinary filename characters, but these characters
    # would still break the surrounding LaTeX input argument or source line.
    for path in paths:
        if any(char in path for char in "%{}\n\r"):
            raise ValueError("The template path cannot contain %, braces, or newlines")
    headings, styles = load_text_commands(text_template)
    allowed_names = load_box_names(template) | headings.keys() | BUILTIN_EXPRESSIONS
    for box in boxes:
        if box.name not in allowed_names:
            raise ValueError(f"Unknown expression name '{box.name}'")
    # Blank lines separate expressions into paragraphs. Headings become macros,
    # notes become unboxed text, and other names become box environments.
    body = "\n\n".join(
        r"\par\medskip"
        if box.name == "newline"
        else f"\\{headings[box.name]}{{{render_inline(box.children, styles)}}}"
        if box.name in headings
        else render_inline(box.children, styles)
        if box.name in {"note", "math", "equation"}
        else f"\\begin{{{box.name}}}\n{render_inline(box.children, styles)}\n\\end{{{box.name}}}"
        for box in boxes
    )
    # NotesBoxesOnly skips the box template's standalone demonstration document.
    return (
        "\\documentclass[11pt]{article}\n"
        "\\usepackage[margin=1in]{geometry}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage{lmodern}\n\n"
        "\\usepackage{amsmath,amssymb}\n\n"
        "\\def\\NotesBoxesOnly{1}\n"
        + "".join(f"\\input{{\\detokenize{{{path}}}}}\n" for path in paths)
        + "\n"
        + f"\\begin{{document}}\n\n{body}\n\n\\end{{document}}\n"
    )
