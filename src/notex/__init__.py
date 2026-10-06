"""NoteX: structured plain-text notes to LaTeX."""

from .math_parser import parse_math
from .math_renderer import render_math
from .models import Box, LineBreak, Math, MathExpression, ParseError, SourceSpan, Style, Text
from .parser import parse_notes
from .renderer import format_text, render_document
from .service import ConversionResult, convert_source

__all__ = [
    "Box",
    "ConversionResult",
    "LineBreak",
    "Math",
    "MathExpression",
    "ParseError",
    "SourceSpan",
    "Style",
    "Text",
    "convert_source",
    "format_text",
    "parse_notes",
    "parse_math",
    "render_document",
    "render_math",
]
