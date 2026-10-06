"""Syntax names shared by parsing, rendering, and template validation."""

MAX_NESTING = 64
BUILTIN_EXPRESSIONS = frozenset({"note", "math", "equation", "newline"})
INLINE_BUILTINS = frozenset({"math", "newline"})
