"""Compatibility entry point; implementation lives in src/notex.

Run directly from a checkout with python3 convert.py notes.txt. Installed users
can use the notex command or python -m notex. Re-exports retain the original
converter's import API, except that parsed boxes now contain structured nodes.
"""

import sys
from pathlib import Path

# The source checkout works before an editable install. Installed entry points
# import the package normally and do not change the Python search path.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from notex.cli import main  # noqa: E402
from notex.models import Box, ParseError, SourceSpan, Style, Text  # noqa: E402
from notex.parser import MAX_NESTING, NotesParser, parse_notes  # noqa: E402
from notex.renderer import (  # noqa: E402
    escape_latex,
    format_text,
    render_document,
    render_inline,
)
from notex.templates import (  # noqa: E402
    DEFAULT_TEMPLATE,
    DEFAULT_TEXT_TEMPLATE,
    load_box_names,
    load_text_commands,
)

# Legacy constants are loaded only in this compatibility module. Importing the
# installed library no longer performs template file I/O.
HEADINGS, TEXT_STYLES = load_text_commands(DEFAULT_TEXT_TEMPLATE)

__all__ = [
    "Box",
    "DEFAULT_TEMPLATE",
    "DEFAULT_TEXT_TEMPLATE",
    "HEADINGS",
    "MAX_NESTING",
    "NotesParser",
    "ParseError",
    "SourceSpan",
    "Style",
    "TEXT_STYLES",
    "Text",
    "escape_latex",
    "format_text",
    "load_box_names",
    "load_text_commands",
    "main",
    "parse_notes",
    "render_document",
    "render_inline",
]

if __name__ == "__main__":
    raise SystemExit(main())
