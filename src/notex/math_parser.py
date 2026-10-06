"""Parse a small mathematical language with operator precedence and source spans.

No eval(), Python execution, or LaTeX passthrough is involved. The notes parser
hands us its original source and cursor; errors retain the original location.
"""

import re
from dataclasses import dataclass
from typing import NoReturn

from .models import Math, MathExpression, MathKind, ParseError, SourceSpan
from .syntax import MAX_NESTING

NUMBER = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9]*")
NEWLINE_CALL = re.compile(r"newline\s*\(\s*\)")

# Canonical argument order is expression first, then variable/index and bounds.
ARITIES: dict[str, tuple[int, ...]] = {
    "sqrt": (1,),
    "root": (2,),
    "frac": (2,),
    "sum": (4,),
    "product": (4,),
    "integral": (2, 4),
    "derivative": (2, 3),
    "partial": (2, 3),
    "limit": (3,),
    "abs": (1,),
    "binom": (2,),
    "sin": (1,),
    "cos": (1,),
    "tan": (1,),
    "asin": (1,),
    "acos": (1,),
    "atan": (1,),
    "sinh": (1,),
    "cosh": (1,),
    "tanh": (1,),
    "ln": (1,),
    "log": (1, 2),
    "exp": (1,),
}
ALIASES = {
    "summation": "sum",
    "prod": "product",
    "int": "integral",
    "integrals": "integral",
    "diff": "derivative",
    "derivatives": "derivative",
}
UNICODE_SYMBOLS = {
    "α": "alpha",
    "β": "beta",
    "γ": "gamma",
    "δ": "delta",
    "ε": "epsilon",
    "ζ": "zeta",
    "η": "eta",
    "θ": "theta",
    "ι": "iota",
    "κ": "kappa",
    "λ": "lambda",
    "μ": "mu",
    "ν": "nu",
    "ξ": "xi",
    "π": "pi",
    "ρ": "rho",
    "σ": "sigma",
    "τ": "tau",
    "υ": "upsilon",
    "φ": "phi",
    "χ": "chi",
    "ψ": "psi",
    "ω": "omega",
    "Γ": "Gamma",
    "Δ": "Delta",
    "Θ": "Theta",
    "Λ": "Lambda",
    "Ξ": "Xi",
    "Π": "Pi",
    "Σ": "Sigma",
    "Υ": "Upsilon",
    "Φ": "Phi",
    "Ψ": "Psi",
    "Ω": "Omega",
    "∞": "inf",
}
UNICODE_SYMBOLS.update(
    {
        "ο": "o",
        "ς": "varsigma",
        "ϵ": "varepsilon",
        "ϑ": "vartheta",
        "ϕ": "varphi",
        "ϖ": "varpi",
        "ϱ": "varrho",
        "∇": "nabla",
        "ℏ": "hbar",
        "Α": "A",
        "Β": "B",
        "Ε": "E",
        "Ζ": "Z",
        "Η": "H",
        "Ι": "I",
        "Κ": "K",
        "Μ": "M",
        "Ν": "N",
        "Ο": "O",
        "Ρ": "P",
        "Τ": "T",
        "Χ": "X",
    }
)
UNICODE_OPERATORS = {
    "×": "*",
    "·": "*",
    "÷": "/",
    "−": "-",
    "±": "+-",
    "≤": "<=",
    "≥": ">=",
    "≠": "!=",
    "≈": "~=",
    "→": "->",
}
RELATIONS = frozenset({"=", "==", "!=", "<=", ">=", "<", ">", "~=", "->"})
BINDING = {
    **dict.fromkeys(RELATIONS, 10),
    "+": 20,
    "-": 20,
    "+-": 20,
    "*": 30,
    "/": 30,
    "^": 50,
    "_": 50,
}


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    span: SourceSpan


class MathParser:
    """Tokenize one math region and construct its immutable expression tree."""

    def __init__(self, source: str, start: int, closing: str | None, opening: int, depth: int = 0):
        self.source = source
        self.start = start
        self.closing = closing
        self.opening = opening
        self.budget = MAX_NESTING - depth
        self.tokens: list[Token] = []
        self.index = 0
        self.end = start

    def fail(self, message: str, at: int) -> NoReturn:
        raise ParseError(
            message,
            offset=at,
            line=self.source.count("\n", 0, at) + 1,
            column=at - self.source.rfind("\n", 0, at),
        )

    def tokenize(self) -> None:
        pos = self.start
        groups: list[str] = []
        while pos < len(self.source):
            char = self.source[pos]
            if char == self.closing and not groups:
                self.end = pos + 1
                self.tokens.append(Token("end", "", SourceSpan(pos, pos)))
                return
            if char.isspace():
                if char == "\n" and not groups:
                    self.tokens.append(Token("row", "newline", SourceSpan(pos, pos + 1)))
                pos += 1
                continue
            newline = NEWLINE_CALL.match(self.source, pos)
            if char == ";" or newline:
                if groups:
                    self.fail("math line breaks must be between complete equations", pos)
                end = newline.end() if newline else pos + 1
                self.tokens.append(Token("row", "newline", SourceSpan(pos, end)))
                pos = end
                continue
            number = NUMBER.match(self.source, pos)
            name = IDENTIFIER.match(self.source, pos)
            if number or name:
                match = number or name
                assert match is not None
                self.tokens.append(
                    Token(
                        "number" if number else "name", match.group(), SourceSpan(pos, match.end())
                    )
                )
                pos = match.end()
                continue
            if char in UNICODE_SYMBOLS:
                self.tokens.append(Token("name", UNICODE_SYMBOLS[char], SourceSpan(pos, pos + 1)))
            elif char in UNICODE_OPERATORS:
                self.tokens.append(
                    Token("operator", UNICODE_OPERATORS[char], SourceSpan(pos, pos + 1))
                )
            elif char in "([{":
                groups.append({"(": ")", "[": "]", "{": "}"}[char])
                if len(groups) > self.budget:
                    self.fail(f"maximum nesting depth of {MAX_NESTING} exceeded", pos)
                self.tokens.append(Token("open", char, SourceSpan(pos, pos + 1)))
            elif char in ")]}":
                if not groups or groups[-1] != char:
                    self.fail(f"unexpected '{char}' in math", pos)
                groups.pop()
                self.tokens.append(Token("close", char, SourceSpan(pos, pos + 1)))
            elif char == ",":
                self.tokens.append(Token("comma", char, SourceSpan(pos, pos + 1)))
            elif char in "+-*/^_=!<>":
                if self.source[pos : pos + 3] == "+/-":
                    self.tokens.append(Token("operator", "+-", SourceSpan(pos, pos + 3)))
                    pos += 3
                    continue
                pair = self.source[pos : pos + 2]
                if pair in ("**", "==", "!=", "<=", ">=", "->", "+-"):
                    self.tokens.append(
                        Token("operator", "^" if pair == "**" else pair, SourceSpan(pos, pos + 2))
                    )
                    pos += 2
                    continue
                self.tokens.append(Token("operator", char, SourceSpan(pos, pos + 1)))
            elif self.source[pos : pos + 2] == "~=":
                self.tokens.append(Token("operator", "~=", SourceSpan(pos, pos + 2)))
                pos += 2
                continue
            else:
                self.fail(f"unsupported character '{char}' in math", pos)
            pos += 1
        if groups or self.closing is not None:
            expected = groups[-1] if groups else self.closing
            self.fail(f"missing closing '{expected}' in math", self.opening)
        self.end = pos
        self.tokens.append(Token("end", "", SourceSpan(pos, pos)))

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def consume(self) -> Token:
        token = self.current
        self.index += 1
        return token

    def node(
        self,
        kind: MathKind,
        value: str,
        children: tuple[MathExpression, ...],
        span: SourceSpan,
    ) -> MathExpression:
        height = 1 + max((child.height for child in children), default=0)
        if height > self.budget:
            self.fail(f"maximum nesting depth of {MAX_NESTING} exceeded", span.start)
        return MathExpression(kind, value, children, span, height)

    def expect(self, value: str) -> Token:
        if self.current.value != value:
            self.fail(f"expected '{value}' in math", self.current.span.start)
        return self.consume()

    def expression(
        self, minimum: int = 0, depth: int = 0, exponent: bool = False
    ) -> MathExpression:
        if depth >= self.budget:
            self.fail(f"maximum nesting depth of {MAX_NESTING} exceeded", self.current.span.start)
        left = self.atom(depth)
        while True:
            token = self.current
            if token.value == "!":
                if minimum > 60:
                    break
                self.consume()
                left = self.node(
                    "factorial", "!", (left,), SourceSpan(left.span.start, token.span.end)
                )
                continue
            implicit = token.kind in ("number", "name", "open")
            operator = "implicit" if implicit else token.value
            binding = 30 if implicit else BINDING.get(operator, -1)
            if binding < minimum or (exponent and operator == "_"):
                break
            if not implicit:
                self.consume()
            if operator in ("^", "_"):
                right = self.expression(50 if operator == "^" else 61, depth + 1, operator == "^")
                if left.kind == "script" and operator not in left.value:
                    base, existing = left.children
                    children = (
                        (base, existing, right) if operator == "^" else (base, right, existing)
                    )
                    left = self.node(
                        "script", "_^", children, SourceSpan(base.span.start, right.span.end)
                    )
                elif left.kind == "script" and operator in left.value:
                    self.fail(
                        f"duplicate '{operator}' script; use parentheses to group it",
                        token.span.start,
                    )
                else:
                    left = self.node(
                        "script",
                        operator,
                        (left, right),
                        SourceSpan(left.span.start, right.span.end),
                    )
            else:
                right = self.expression(binding + 1, depth + 1)
                left = self.node(
                    "binary", operator, (left, right), SourceSpan(left.span.start, right.span.end)
                )
        return left

    def atom(self, depth: int) -> MathExpression:
        token = self.consume()
        if token.kind in ("number", "name"):
            if token.kind == "name" and self.current.value == "(":
                self.consume()
                arguments: list[MathExpression] = []
                if self.current.value != ")":
                    arguments.append(self.expression(depth=depth + 1))
                    while self.current.value == ",":
                        self.consume()
                        arguments.append(self.expression(depth=depth + 1))
                end = self.expect(")")
                name = ALIASES.get(token.value.lower(), token.value.lower())
                if name not in ARITIES:
                    name = token.value
                children = tuple(arguments)
                self.validate_call(name, children, token.span.start)
                return self.node("call", name, children, SourceSpan(token.span.start, end.span.end))
            return self.node(
                "number" if token.kind == "number" else "symbol", token.value, (), token.span
            )
        if token.value in ("+", "-", "+-"):
            child = self.expression(40, depth + 1)
            return self.node(
                "unary", token.value, (child,), SourceSpan(token.span.start, child.span.end)
            )
        if token.kind == "open":
            child = self.expression(depth=depth + 1)
            end = self.expect({"(": ")", "[": "]", "{": "}"}[token.value])
            return self.node(
                "group", token.value, (child,), SourceSpan(token.span.start, end.span.end)
            )
        self.fail("expected a math expression", token.span.start)

    def validate_call(self, name: str, children: tuple[MathExpression, ...], at: int) -> None:
        if name == "newline":
            self.fail("newline() takes no arguments and separates equation rows", at)
        if name in ARITIES and len(children) not in ARITIES[name]:
            expected = " or ".join(str(count) for count in ARITIES[name])
            self.fail(f"{name}() expects {expected} arguments; got {len(children)}", at)
        if name in ("sum", "product", "integral", "derivative", "partial", "limit"):
            variable = children[1]
            if variable.kind != "symbol" and not (
                variable.kind == "script"
                and variable.value == "_"
                and variable.children[0].kind == "symbol"
            ):
                self.fail(
                    f"{name}() requires a variable or index as its second argument",
                    variable.span.start,
                )
        if name in ("derivative", "partial") and len(children) == 3:
            order = children[2]
            if order.kind != "number" or not order.value.isdigit() or not order.value.lstrip("0"):
                self.fail("derivative order must be a positive integer", order.span.start)

    def parse(self, *, display: bool = False) -> Math:
        self.tokenize()
        rows: list[MathExpression] = []
        while self.current.kind == "row":
            self.consume()
        if self.current.kind == "end":
            self.fail("math expression cannot be empty", self.opening)
        while self.current.kind != "end":
            # A later row can omit its left-hand side: x=1+1 newline() =2.
            if rows and self.current.value in RELATIONS:
                token = self.consume()
                child = self.expression()
                rows.append(
                    self.node(
                        "continuation",
                        token.value,
                        (child,),
                        SourceSpan(token.span.start, child.span.end),
                    )
                )
            else:
                rows.append(self.expression())
            if self.current.kind not in ("row", "end"):
                self.fail("unexpected token in math", self.current.span.start)
            while self.current.kind == "row":
                self.consume()
        return Math(tuple(rows), SourceSpan(self.opening, self.end), display)


def parse_math(source: str) -> Math:
    """Parse standalone math text using the same grammar as math{...}."""
    return MathParser(source, 0, None, 0).parse()
