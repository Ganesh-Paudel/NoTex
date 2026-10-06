"""NoteX: structured plain-text notes to LaTeX."""

from .models import Box, ParseError, SourceSpan, Style, Text
from .parser import parse_notes
from .renderer import format_text, render_document
from .service import ConversionResult, convert_source

__all__ = [
    "Box",
    "ConversionResult",
    "ParseError",
    "SourceSpan",
    "Style",
    "Text",
    "convert_source",
    "format_text",
    "parse_notes",
    "render_document",
]
