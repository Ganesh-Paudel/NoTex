"""Discover note syntax from the packaged or user-selected LaTeX templates."""

import re
from pathlib import Path

# Templates ship inside the installed wheel, not beside the caller's notes file.
TEMPLATE_DIRECTORY = Path(__file__).resolve().parent / "templates"
DEFAULT_TEMPLATE = TEMPLATE_DIRECTORY / "class_notes_boxes.tex"
DEFAULT_TEXT_TEMPLATE = TEMPLATE_DIRECTORY / "class_notes_text.tex"


def strip_comments(source: str) -> str:
    """Remove TeX comments while retaining escaped percent signs."""
    lines = []
    for line in source.splitlines():
        backslashes = 0
        for pos, char in enumerate(line):
            if char == "%" and backslashes % 2 == 0:
                line = line[:pos]
                break
            backslashes = backslashes + 1 if char == "\\" else 0
        lines.append(line)
    return "\n".join(lines)


def load_text_commands(template: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Read syntax declarations beside their LaTeX definitions."""
    source = template.read_text(encoding="utf-8")
    definitions = strip_comments(source)
    headings: dict[str, str] = {}
    styles: dict[str, str] = {}
    # Example declaration: % notex-style bold NotesBold
    # Templates define both the input keyword and its corresponding LaTeX macro.
    for kind, name, command in re.findall(
        r"^% notex-(heading|style) ([A-Za-z][A-Za-z0-9_]*) ([A-Za-z]+)$",
        source,
        re.MULTILINE,
    ):
        target = headings if kind == "heading" else styles
        if name in headings or name in styles:
            raise ValueError(f"Duplicate text syntax name '{name}' in {template}")
        # Each declared macro must accept exactly one content argument.
        if not re.search(r"\\newcommand\{\\" + command + r"\}\[1\]", definitions):
            raise ValueError(f"Missing one-argument command '{command}' in {template}")
        target[name] = command
    if not headings or not styles:
        raise ValueError(f"No heading or style declarations found in {template}")
    return headings, styles


def load_box_names(template: Path) -> set[str]:
    """Read environment names from the existing tcolorbox definitions."""
    source = strip_comments(template.read_text(encoding="utf-8"))
    # Allow optional tcolorbox settings before the environment name,
    # including definitions such as \newtcolorbox[auto counter]{question}.
    matches = re.findall(r"\\newtcolorbox(?:\[[^\]]*\])?\{([A-Za-z][A-Za-z0-9_]*)\}", source)
    names = set(matches)
    if len(names) != len(matches):
        raise ValueError(f"Duplicate box definitions found in {template}")
    if not names:
        raise ValueError(f"No box definitions found in {template}")
    return names
