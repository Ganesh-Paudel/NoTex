"""One-pass parser for headings, paragraphs, boxes, and nested inline styles."""

import re
from collections.abc import Mapping
from typing import NoReturn

from .models import Box, ParseError, SourceSpan, Style, Text
from .templates import DEFAULT_TEXT_TEMPLATE, load_text_commands

# Limit recursive groups before Python's recursion limit can be reached.
MAX_NESTING = 64
NAME_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


class NotesParser:
    """Parse expressions and inline styles directly from the original source."""

    def __init__(
        self,
        source: str,
        allowed_names: set[str],
        headings: Mapping[str, str],
        styles: Mapping[str, str],
    ):
        self.source = source
        # Plain paragraphs are built in even if a custom box template omits note.
        self.allowed_names = allowed_names | {"note"} | headings.keys()
        self.styles = styles
        self.pos = 0

    def fail(self, message: str, at: int) -> NoReturn:
        # Convert a character offset into a one-based line and column.
        # rfind returns -1 before the first newline, giving column at + 1.
        line = self.source.count("\n", 0, at) + 1
        column = at - self.source.rfind("\n", 0, at)
        raise ParseError(message, offset=at, line=line, column=column)

    def skip_space(self) -> None:
        while self.pos < len(self.source) and self.source[self.pos].isspace():
            self.pos += 1

    def content(
        self, closing: str | None, opening: int, depth: int = 0, context: str = "text"
    ) -> tuple[Text | Style, ...]:
        """Read children until the expected delimiter, or EOF if closing is None.

        Recursive calls share the cursor into the unchanged source. The opening
        offset and context identify the construct to report if it never closes.
        """
        if depth > MAX_NESTING:
            self.fail(f"maximum nesting depth of {MAX_NESTING} exceeded", opening)
        nodes: list[Text | Style] = []
        buffer: list[str] = []
        start = self.pos

        def flush() -> None:
            # Coalesce adjacent literal characters into one node. Its source
            # span can be longer than its value because an escape uses two
            # source characters to represent one literal character.
            if buffer:
                nodes.append(Text("".join(buffer), SourceSpan(start, self.pos)))
                buffer.clear()

        while self.pos < len(self.source):
            char = self.source[self.pos]
            # Consume escapes before checking delimiters or style keywords.
            # Unknown backslash sequences remain ordinary text.
            if (
                char == "\\"
                and self.pos + 1 < len(self.source)
                and self.source[self.pos + 1] in "(){}\\"
            ):
                buffer.append(self.source[self.pos + 1])
                self.pos += 2
                continue
            if char == closing:
                flush()
                self.pos += 1
                return tuple(nodes)
            # Reject a closing delimiter that does not match the current group.
            if char in "})":
                self.fail(f"unexpected '{char}'", self.pos)
            match = NAME_PATTERN.match(self.source, self.pos)
            # Avoid treating the end of an identifier such as _bold as a style.
            boundary = self.pos == 0 or not (
                self.source[self.pos - 1].isascii()
                and (self.source[self.pos - 1].isalnum() or self.source[self.pos - 1] == "_")
            )
            if match:
                name = match.group()
                if (
                    boundary
                    and name in self.styles
                    and self.source[match.end() : match.end() + 1] == "{"
                ):
                    # Store a style node rather than emitting LaTeX during parsing.
                    flush()
                    style_start = self.pos
                    self.pos = match.end() + 1
                    children = self.content("}", style_start, depth + 1, f"style '{name}'")
                    nodes.append(Style(name, children, SourceSpan(style_start, self.pos)))
                    start = self.pos
                    continue
                # Advance over the whole ordinary identifier without copying
                # the remaining source into a temporary substring.
                buffer.append(name)
                self.pos = match.end()
                continue
            if char in "({":
                # Balanced ordinary delimiters remain literal text.
                flush()
                literal_start = self.pos
                self.pos += 1
                end = ")" if char == "(" else "}"
                children = self.content(end, literal_start, depth + 1, "literal group")
                nodes.append(Text(char, SourceSpan(literal_start, literal_start + 1)))
                nodes.extend(children)
                nodes.append(Text(end, SourceSpan(self.pos - 1, self.pos)))
                start = self.pos
                continue
            buffer.append(char)
            self.pos += 1
        flush()
        if closing is not None:
            self.fail(f"missing closing '{closing}' for {context}", opening)
        return tuple(nodes)

    def parse(self) -> list[Box]:
        """Read name(content) expressions separated by optional whitespace."""
        expressions: list[Box] = []
        self.skip_space()
        while self.pos < len(self.source):
            start = self.pos
            match = NAME_PATTERN.match(self.source, self.pos)
            if match is None:
                self.fail("expected a box name", self.pos)
            name = match.group()
            if name not in self.allowed_names:
                self.fail(f"unknown box name '{name}'", start)
            self.pos = match.end()
            self.skip_space()
            if self.pos == len(self.source) or self.source[self.pos] != "(":
                self.fail(f"expected '(' after '{name}'", self.pos)
            self.pos += 1
            children = list(self.content(")", start, context=f"'{name}'"))
            # Trim only outer whitespace, retaining original source offsets.
            if children and isinstance(children[0], Text):
                node = children[0]
                value = node.value.lstrip()
                children[0] = Text(
                    value, SourceSpan(node.span.start + len(node.value) - len(value), node.span.end)
                )
            if children and isinstance(children[-1], Text):
                node = children[-1]
                value = node.value.rstrip()
                children[-1] = Text(
                    value, SourceSpan(node.span.start, node.span.end - len(node.value) + len(value))
                )
            expressions.append(
                Box(
                    name,
                    tuple(n for n in children if not isinstance(n, Text) or n.value),
                    SourceSpan(start, self.pos),
                )
            )
            self.skip_space()
        return expressions


def parse_notes(
    source: str,
    allowed_names: set[str],
    *,
    headings: Mapping[str, str] | None = None,
    styles: Mapping[str, str] | None = None,
) -> list[Box]:
    """Build the note tree using either default or caller-supplied text syntax."""
    if headings is None or styles is None:
        default_headings, default_styles = load_text_commands(DEFAULT_TEXT_TEMPLATE)
        headings = default_headings if headings is None else headings
        styles = default_styles if styles is None else styles
    return NotesParser(source, allowed_names, headings, styles).parse()
