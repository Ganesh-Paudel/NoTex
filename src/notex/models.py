"""Immutable syntax tree nodes and source diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

MathKind: TypeAlias = Literal[
    "number", "symbol", "unary", "binary", "group", "call", "script", "factorial", "continuation"
]


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
class MathExpression:
    """A mathematical expression, not executable Python or raw LaTeX.

    Height bounds the eventual rendering recursion, including long chains of
    left-associative operations that do not deeply recurse during parsing.
    """

    kind: MathKind
    value: str
    children: tuple[MathExpression, ...]
    span: SourceSpan
    height: int


@dataclass(frozen=True)
class Math:
    """One or more equation rows, displayed inline or as a standalone block."""

    rows: tuple[MathExpression, ...]
    span: SourceSpan
    display: bool = False


@dataclass(frozen=True)
class LineBreak:
    """An explicit newline() in paragraph or box content."""

    span: SourceSpan


@dataclass(frozen=True)
class Style:
    """A style such as bold{...}, whose children may include nested styles."""

    name: str
    children: tuple[InlineNode, ...]
    span: SourceSpan


@dataclass(frozen=True)
class Box:
    """A top-level expression: a box, a heading, or an ordinary note paragraph."""

    name: str
    children: tuple[InlineNode, ...]
    span: SourceSpan


InlineNode: TypeAlias = Text | Style | Math | LineBreak


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
