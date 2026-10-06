"""Render validated mathematical nodes with an explicit LaTeX command vocabulary."""

import re

from .math_parser import IDENTIFIER, NUMBER, RELATIONS
from .models import Math, MathExpression

SYMBOLS = {
    name: "\\" + name
    for name in (
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "varepsilon",
        "zeta",
        "eta",
        "theta",
        "vartheta",
        "iota",
        "kappa",
        "lambda",
        "mu",
        "nu",
        "xi",
        "pi",
        "varpi",
        "rho",
        "varrho",
        "sigma",
        "varsigma",
        "tau",
        "upsilon",
        "phi",
        "varphi",
        "chi",
        "psi",
        "omega",
        "Gamma",
        "Delta",
        "Theta",
        "Lambda",
        "Xi",
        "Pi",
        "Sigma",
        "Upsilon",
        "Phi",
        "Psi",
        "Omega",
        "hbar",
        "nabla",
    )
}
SYMBOLS.update({"inf": r"\infty", "infinity": r"\infty", "oo": r"\infty"})
OPERATORS = {
    "+": "+",
    "-": "-",
    "+-": r"\pm",
    "*": r"\cdot",
    "implicit": r"\,",
    "=": "=",
    "==": "=",
    "!=": r"\ne",
    "<=": r"\le",
    ">=": r"\ge",
    "<": "<",
    ">": ">",
    "~=": r"\approx",
    "->": r"\to",
}
NAMED_FUNCTIONS = {
    name: "\\" + name for name in ("sin", "cos", "tan", "sinh", "cosh", "tanh", "ln", "log", "exp")
}
NAMED_FUNCTIONS.update({"asin": r"\arcsin", "acos": r"\arccos", "atan": r"\arctan"})


def ungroup(node: MathExpression) -> MathExpression:
    """Fractions, roots, and scripts supply their own grouping braces."""
    while node.kind == "group":
        node = node.children[0]
    return node


def parentheses(content: str) -> str:
    return rf"\left({content}\right)"


def render_expression(node: MathExpression) -> str:
    """Typeset the expression; no arithmetic evaluation or simplification occurs."""
    if node.kind == "number":
        if NUMBER.fullmatch(node.value) is None:
            raise ValueError("Invalid math number")
        if "e" in node.value.lower():
            mantissa, exponent = re.split("[eE]", node.value)
            return rf"{mantissa} \times 10^{{{exponent}}}"
        return node.value
    if node.kind == "symbol":
        if IDENTIFIER.fullmatch(node.value) is None:
            raise ValueError("Invalid math symbol")
        return SYMBOLS.get(node.value, node.value)
    if node.kind == "group":
        value = render_expression(node.children[0])
        if node.value == "(":
            return parentheses(value)
        if node.value == "[":
            return rf"\left[{value}\right]"
        return "{" + value + "}"
    if node.kind == "unary":
        if node.value not in {"+", "-", "+-"}:
            raise ValueError("Invalid unary math operator")
        return (
            OPERATORS[node.value] + " " + render_expression(node.children[0])
            if node.value == "+-"
            else node.value + render_expression(node.children[0])
        )
    if node.kind == "continuation":
        return OPERATORS[node.value] + " " + render_expression(node.children[0])
    if node.kind == "factorial":
        return render_expression(node.children[0]) + "!"
    if node.kind == "binary":
        left, right = node.children
        if node.value == "/":
            return rf"\frac{{{render_expression(ungroup(left))}}}{{{render_expression(ungroup(right))}}}"
        return f"{render_expression(left)} {OPERATORS[node.value]} {render_expression(right)}"
    if node.kind == "script":
        if node.value not in {"_", "^", "_^"}:
            raise ValueError("Invalid math script")
        base = render_expression(node.children[0])
        if node.children[0].kind == "number" and "e" in node.children[0].value.lower():
            base = parentheses(base)
        values = [render_expression(ungroup(child)) for child in node.children[1:]]
        if node.value == "_^":
            return rf"{base}_{{{values[0]}}}^{{{values[1]}}}"
        return f"{base}{node.value}{{{values[0]}}}"
    if node.kind == "call":
        return render_call(node)
    raise ValueError("Unknown math expression kind")


def render_call(node: MathExpression) -> str:
    name = node.value
    if IDENTIFIER.fullmatch(name) is None:
        raise ValueError("Invalid math function name")
    arguments = [render_expression(ungroup(child)) for child in node.children]
    if name == "sqrt":
        return rf"\sqrt{{{arguments[0]}}}"
    if name == "root":
        return rf"\sqrt[{arguments[1]}]{{{arguments[0]}}}"
    if name in ("frac", "binom"):
        return f"\\{name}{{{arguments[0]}}}{{{arguments[1]}}}"
    if name == "abs":
        return rf"\left|{arguments[0]}\right|"
    if name in ("sum", "product", "integral"):
        body = arguments[0]
        expression = ungroup(node.children[0])
        if expression.kind == "binary" and expression.value in {"+", "-", "+-"} | RELATIONS:
            body = parentheses(body)
        if name in ("sum", "product"):
            operator = r"\sum" if name == "sum" else r"\prod"
            return rf"{operator}_{{{arguments[1]}={arguments[2]}}}^{{{arguments[3]}}} {{{body}}}"
        bounds = rf"_{{{arguments[2]}}}^{{{arguments[3]}}}" if len(arguments) == 4 else ""
        return rf"\int{bounds} {{{body}}}\,\mathrm{{d}}{arguments[1]}"
    if name in ("derivative", "partial"):
        operator = r"\mathrm{d}" if name == "derivative" else r"\partial"
        order = arguments[2].lstrip("0") if len(arguments) == 3 else "1"
        numerator = operator if order.lstrip("0") == "1" else rf"{operator}^{{{order}}}"
        variable = arguments[1]
        denominator = (
            (rf"{operator}{variable}" if name == "derivative" else rf"{operator} {variable}")
            if order.lstrip("0") == "1"
            else rf"{operator}{{{variable}}}^{{{order}}}"
        )
        return rf"\frac{{{numerator}}}{{{denominator}}}" + parentheses(arguments[0])
    if name == "limit":
        return rf"\lim_{{{arguments[1]}\to {arguments[2]}}} " + parentheses(arguments[0])
    if name == "log" and len(arguments) == 2:
        return rf"\log_{{{arguments[1]}}}" + parentheses(arguments[0])
    command = NAMED_FUNCTIONS.get(name)
    if command is None:
        command = (
            SYMBOLS.get(name, name)
            if len(name) == 1 or name in SYMBOLS
            else rf"\operatorname{{{name}}}"
        )
    return command + parentheses(", ".join(arguments))


def render_math(node: Math) -> str:
    if len(node.rows) == 1:
        content = render_expression(node.rows[0])
    else:
        rows = []
        for row in node.rows:
            if row.kind == "continuation":
                rows.append("&" + render_expression(row))
            elif row.kind == "binary" and row.value in RELATIONS:
                left, right = row.children
                rows.append(
                    f"{render_expression(left)} &{OPERATORS[row.value]} {render_expression(right)}"
                )
            else:
                rows.append("&" + render_expression(row))
        content = "\\begin{aligned}\n" + " \\\\\n".join(rows) + "\n\\end{aligned}"
    return ("\\[\n" + content + "\n\\]") if node.display else "\\(" + content + "\\)"
