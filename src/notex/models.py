"""Immutable syntax tree nodes and source diagnostics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpan:
    """Character offsets in the original source: start inclusive, end exclusive."""

    start: int
    end: int


@dataclass(frozen=True)
class Text:
    """Literal text after decoding escapes, with its original source range."""

    value: str
    span: SourceSpan


@dataclass(frozen=True)
class Style:
    """A style such as bold{...}, whose children may include nested styles."""

    name: str
    children: tuple[Text | Style, ...]
    span: SourceSpan


@dataclass(frozen=True)
class Box:
    """A top-level expression: a box, a heading, or an ordinary note paragraph."""

    name: str
    children: tuple[Text | Style, ...]
    span: SourceSpan


class ParseError(ValueError):
    """Invalid syntax with a machine-readable location in the original source."""

    def __init__(self, message: str, *, offset: int, line: int, column: int):
        self.message = message
        self.offset = offset
        self.line = line
        self.column = column
        super().__init__(f"line {line}, column {column}: {message}")

    def as_dict(self) -> dict[str, str | int]:
        """Diagnostic payload suitable for an editor or CLI JSON consumer."""
        return {
            "kind": "syntax",
            "message": self.message,
            "offset": self.offset,
            "line": self.line,
            "column": self.column,
        }
