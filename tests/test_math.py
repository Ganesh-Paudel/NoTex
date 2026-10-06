"""Math notation, nesting, precedence, diagnostics, and integration regression tests."""

import unittest
from dataclasses import replace

import convert
from notex import Math, ParseError, convert_source, parse_math, render_math
from notex.math_renderer import render_expression
from notex.syntax import MAX_NESTING


class MathTests(unittest.TestCase):
    def latex(self, source):
        return render_math(parse_math(source))

    def test_simple_and_nested_fractions(self):
        cases = [
            ("1/10", r"\(\frac{1}{10}\)"),
            ("(a+b)/(c-d)", r"\(\frac{a + b}{c - d}\)"),
            ("1/(1+1/x)", r"\(\frac{1}{1 + \frac{1}{x}}\)"),
            ("a/b/c", r"\(\frac{\frac{a}{b}}{c}\)"),
            ("a/(b/c)", r"\(\frac{a}{\frac{b}{c}}\)"),
            ("frac(1,10)", r"\(\frac{1}{10}\)"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(self.latex(source), expected)

    def test_precedence_and_associativity(self):
        cases = [
            ("1+2/3", r"1 + \frac{2}{3}"),
            ("a-b-c", "a - b - c"),
            ("x^2^3", "x^{2^{3}}"),
            ("x**2", "x^{2}"),
            ("-x^2", "-x^{2}"),
            ("(-x)^2", r"\left(-x\right)^{2}"),
            ("2^-3", "2^{-3}"),
            ("2(x+1)", r"2 \, \left(x + 1\right)"),
            ("(x+1)y", r"\left(x + 1\right) \, y"),
            ("a*b/c", r"\frac{a \cdot b}{c}"),
            ("x_i^2", "x_{i}^{2}"),
            ("x^2_i", "x_{i}^{2}"),
            ("x_{i+1}^{n-1}", "x_{i + 1}^{n - 1}"),
            ("n!", "n!"),
            ("x_i!", "x_{i}!"),
            ("x^2!", "x^{2!}"),
            ("+x", "+x"),
            ("[x+1]", r"\left[x + 1\right]"),
            ("{x+1}", "{x + 1}"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(self.latex(source), r"\(" + expected + r"\)")

    def test_roots_sums_products_and_integrals(self):
        cases = [
            ("sqrt(1/10)", r"\sqrt{\frac{1}{10}}"),
            ("root(x,3)", r"\sqrt[3]{x}"),
            ("summation(i^2,i,1,n)", r"\sum_{i=1}^{n} {i^{2}}"),
            ("sum(i+1,i,0,n)", r"\sum_{i=0}^{n} {\left(i + 1\right)}"),
            ("product(i,i,1,n)", r"\prod_{i=1}^{n} {i}"),
            ("prod(i,i,1,n)", r"\prod_{i=1}^{n} {i}"),
            ("integral(x^2,x)", r"\int {x^{2}}\,\mathrm{d}x"),
            ("integral(x+1,x,0,1)", r"\int_{0}^{1} {\left(x + 1\right)}\,\mathrm{d}x"),
            ("int(x,x,0,inf)", r"\int_{0}^{\infty} {x}\,\mathrm{d}x"),
            ("Integral(x,x)", r"\int {x}\,\mathrm{d}x"),
            ("integrals(x,x)", r"\int {x}\,\mathrm{d}x"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(self.latex(source), r"\(" + expected + r"\)")

    def test_derivatives_partial_derivatives_and_limits(self):
        cases = [
            ("derivative(x^2,x)", r"\frac{\mathrm{d}}{\mathrm{d}x}\left(x^{2}\right)"),
            ("diff(x^3,x,2)", r"\frac{\mathrm{d}^{2}}{\mathrm{d}{x}^{2}}\left(x^{3}\right)"),
            ("derivatives(x,x,01)", r"\frac{\mathrm{d}}{\mathrm{d}x}\left(x\right)"),
            ("partial(x*y,x)", r"\frac{\partial}{\partial x}\left(x \cdot y\right)"),
            (
                "partial(x^2*y,x,2)",
                r"\frac{\partial^{2}}{\partial{x}^{2}}\left(x^{2} \cdot y\right)",
            ),
            ("derivative(x_i^2,x_i)", r"\frac{\mathrm{d}}{\mathrm{d}x_{i}}\left(x_{i}^{2}\right)"),
            ("limit(sin(x)/x,x,0)", r"\lim_{x\to 0} \left(\frac{\sin\left(x\right)}{x}\right)"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(self.latex(source), r"\(" + expected + r"\)")

    def test_other_functions_and_symbols(self):
        cases = [
            ("abs(x)", r"\left|x\right|"),
            ("binom(n,k)", r"\binom{n}{k}"),
            ("log(x,2)", r"\log_{2}\left(x\right)"),
            ("asin(x)", r"\arcsin\left(x\right)"),
            ("f(x,y)", r"f\left(x, y\right)"),
            ("density(x)", r"\operatorname{density}\left(x\right)"),
            ("f()", r"f\left(\right)"),
            ("alpha(x)", r"\alpha\left(x\right)"),
            ("alpha+pi+inf", r"\alpha + \pi + \infty"),
            ("α+π+∞", r"\alpha + \pi + \infty"),
            ("ο+Α+∇+ℏ", r"o + A + \nabla + \hbar"),
            ("1.5e-3", r"1.5 \times 10^{-3}"),
            ("1e3^2", r"\left(1 \times 10^{3}\right)^{2}"),
            (".5+2.", ".5 + 2."),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(self.latex(source), r"\(" + expected + r"\)")

    def test_relations_and_unicode_operators(self):
        cases = [
            ("x==1", "x = 1"),
            ("x!=1", r"x \ne 1"),
            ("x<=1", r"x \le 1"),
            ("x>=1", r"x \ge 1"),
            ("x<1", "x < 1"),
            ("x>1", "x > 1"),
            ("x~=1", r"x \approx 1"),
            ("x->0", r"x \to 0"),
            ("x+-1", r"x \pm 1"),
            ("x+/-1", r"x \pm 1"),
            ("±sqrt(x)", r"\pm \sqrt{x}"),
            ("x±1", r"x \pm 1"),
            ("2×3", r"2 \cdot 3"),
            ("2÷3", r"\frac{2}{3}"),
            ("x−1", "x - 1"),
            ("x≤1", r"x \le 1"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(self.latex(source), r"\(" + expected + r"\)")

    def test_equation_rows_and_continuations(self):
        for separator in ("\n", ";", " newline() "):
            with self.subTest(separator=separator):
                result = self.latex("x=1+1" + separator + "=2")
                self.assertIn(r"\begin{aligned}", result)
                self.assertIn("x &= 1 + 1 \\\\\n&= 2", result)
        result = self.latex("\n  x+1 \n\n y+2\n")
        self.assertIn("&x + 1 \\\\\n&y + 2", result)

    def test_wrapping_inside_groups_does_not_add_rows(self):
        self.assertEqual(self.latex("sqrt(\n 1/10\n)"), r"\(\sqrt{\frac{1}{10}}\)")

    def test_notes_math_nested_in_styles_and_boxes(self):
        source = "note(Chance: bold{math{1/10}}, 10% & more.) formulabox(math{sqrt(1/10)})"
        result = convert_source(source)
        self.assertIn(r"\NotesBold{\(\frac{1}{10}\)}", result.latex)
        self.assertIn(r"10\% \& more.", result.latex)
        self.assertIn("\\begin{formulabox}\n\\(\\sqrt{\\frac{1}{10}}\\)", result.latex)

    def test_top_level_math_and_equation_are_displayed(self):
        for source in ("math{1/10}", "equation(1/10)"):
            with self.subTest(source=source):
                result = convert_source(source)
                self.assertIn("\\[\n\\frac{1}{10}\n\\]", result.latex)
                self.assertNotIn(r"\begin{equation}", result.latex)
                self.assertIsInstance(result.expressions[0].children[0], Math)

    def test_newlines_in_text_and_between_paragraphs(self):
        result = convert_source("note(First newline() second.) newline() note(Third.)")
        self.assertIn(r"First \leavevmode\newline{} second.", result.latex)
        self.assertIn(r"\par\medskip", result.latex)
        self.assertIn(r"\leavevmode\newline{}", convert.format_text("newline() start"))
        with self.assertRaisesRegex(ParseError, "takes no arguments"):
            convert_source("note(newline(1))")
        with self.assertRaisesRegex(ParseError, "takes no arguments"):
            convert_source("newline(1)")

    def test_escaped_math_syntax_is_literal(self):
        self.assertEqual(convert.format_text(r"math\{1/10\}"), r"math\{1/10\}")
        self.assertEqual(convert.format_text(r"newline\(\)"), "newline()")
        self.assertEqual(convert.format_text("_math{1/10}"), r"\_math\{1/10\}")

    def test_math_and_children_retain_original_spans(self):
        source = "note(\n  math{sqrt(1/10)}\n)"
        result = convert_source(source)
        node = result.expressions[0].children[0]
        self.assertIsInstance(node, Math)
        self.assertEqual(source[node.span.start : node.span.end], "math{sqrt(1/10)}")
        expression = node.rows[0]
        self.assertEqual(source[expression.span.start : expression.span.end], "sqrt(1/10)")
        fraction = expression.children[0]
        self.assertEqual(source[fraction.span.start : fraction.span.end], "1/10")

    def test_nested_calculus_and_probability_functions(self):
        result = self.latex("integral(integral(x*y,x,0,1),y,0,2)")
        self.assertIn(r"\int_{0}^{2} {\int_{0}^{1}", result)
        self.assertIn(r"\mathrm{d}x}\,\mathrm{d}y", result)
        result = self.latex("partial(partial(f(x,y),x),y)")
        self.assertEqual(result.count(r"\frac{\partial}"), 2)
        result = self.latex("P(X=k)=binom(n,k)*p^k*(1-p)^{n-k}")
        self.assertIn(r"P\left(X = k\right) = \binom{n}{k}", result)
        self.assertIn(r"p^{k} \cdot \left(1 - p\right)^{n - k}", result)

    def test_math_errors_report_original_locations(self):
        source = "note(ok)\nnote(math{sqrt(1,)})"
        with self.assertRaises(ParseError) as raised:
            convert_source(source)
        error = raised.exception
        self.assertEqual(error.line, 2)
        self.assertEqual(error.column, 18)
        self.assertEqual(source[error.offset], ")")

    def test_malformed_math_rejects_invalid_input(self):
        cases = [
            ("", "cannot be empty"),
            ("1/", "expected a math expression"),
            ("sqrt()", "expects 1 arguments"),
            ("sqrt(1,2)", "expects 1 arguments"),
            ("sum(i,i,1)", "expects 4 arguments"),
            ("integral(x,x,0)", "expects 2 or 4 arguments"),
            ("derivative(x,1)", "requires a variable"),
            ("derivative(x,x,0)", "positive integer"),
            ("derivative(x,x,1.5)", "positive integer"),
            ("derivative(x,x,-1)", "positive integer"),
            ("derivative(x,x,n)", "positive integer"),
            ("sqrt(1", "missing closing"),
            ("[x)", "unexpected ')'"),
            ("(x,y)", "expected ')'"),
            ("1,2", "unexpected token"),
            ("sqrt(1 2,)", "expected a math expression"),
            ("f(x,y;z)", "line breaks must be between"),
            ("newline(1)", "takes no arguments"),
            ("x_i_j", "duplicate '_'"),
            ("x_i^2_3", "duplicate '_'"),
            ("x^2_i^3", "duplicate '^'"),
            (r"\input{file}", "unsupported character"),
            ("x$", "unsupported character"),
            ("f('text')", "unsupported character"),
        ]
        for source, message in cases:
            with self.subTest(source=source):
                with self.assertRaises(ParseError) as raised:
                    parse_math(source)
                self.assertIn(message, str(raised.exception))

    def test_missing_math_delimiter_and_wrong_top_level_syntax(self):
        for source in ("note(math{1/10)", "math{1/10", "equation(1/10", "math(1/10)"):
            with self.subTest(source=source), self.assertRaises(ParseError):
                convert_source(source)

    def test_math_nesting_and_long_expression_limits(self):
        for source in (
            "sqrt(" * MAX_NESTING + "x" + ")" * MAX_NESTING,
            "(" * (MAX_NESTING + 1) + "x" + ")" * (MAX_NESTING + 1),
            "-" * (MAX_NESTING + 1) + "x",
            "+".join(["x"] * (MAX_NESTING + 1)),
        ):
            with self.subTest(source=source), self.assertRaisesRegex(ParseError, "maximum nesting"):
                parse_math(source)
        source = "note(" + "bold{" * 60 + "math{sqrt(sqrt(sqrt(sqrt(x))))}" + "}" * 60 + ")"
        with self.assertRaisesRegex(ParseError, "maximum nesting"):
            convert_source(source)

    def test_renderer_rejects_injected_atom_values(self):
        node = parse_math("x").rows[0]
        for kind, value in (
            ("symbol", r"\input{file}"),
            ("number", "1$"),
            ("unary", r"\input"),
            ("script", r"\input"),
            ("call", r"\input"),
            ("unexpected", "x"),
        ):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                render_expression(replace(node, kind=kind, value=value))
