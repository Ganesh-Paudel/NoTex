"""Run with: python3 -m unittest -v"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from convert import (
    DEFAULT_TEMPLATE,
    HEADINGS,
    MAX_NESTING,
    TEXT_STYLES,
    ParseError,
    Style,
    Text,
    escape_latex,
    format_text,
    load_box_names,
    load_text_commands,
    parse_notes,
    render_document,
    render_inline,
)


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.names = load_box_names(DEFAULT_TEMPLATE)

    def test_multiline_parentheses_and_multiple_boxes(self):
        boxes = parse_notes(
            "question(What is f(x)?)\nanswer(\nFirst line.\n\nSecond line.\n)", self.names
        )
        self.assertEqual(
            [(box.name, render_inline(box.children, TEXT_STYLES)) for box in boxes],
            [("question", "What is f(x)?"), ("answer", "First line.\n\nSecond line.")],
        )

    def test_literal_unmatched_parentheses_and_backslash(self):
        boxes = parse_notes(r"note(Open \( and close \); path C:\\notes.)", self.names)
        self.assertEqual(
            render_inline(boxes[0].children, TEXT_STYLES),
            r"Open ( and close ); path C:\textbackslash{}notes.",
        )

    def test_invalid_input_reports_location(self):
        cases = [
            ("note(ok)\nunknown(text)", "line 2, column 1: unknown box name"),
            ("note(ok)\nanswer(missing", "line 2, column 1: missing closing"),
            ("question text", "line 1, column 10: expected '('"),
            ("note(ok))", "line 1, column 9: expected a box name"),
        ]
        for source, message in cases:
            with self.subTest(source=source), self.assertRaises(ParseError) as raised:
                parse_notes(source, self.names)
            self.assertIn(message, str(raised.exception))

    def test_special_characters_are_escaped_once(self):
        self.assertEqual(
            escape_latex("\\{}$&#%_~^"),
            r"\textbackslash{}\{\}\$\&\#\%\_\textasciitilde{}\textasciicircum{}",
        )

    def test_every_defined_box_can_be_rendered(self):
        for name in self.names:
            if name == "note":
                continue
            with self.subTest(name=name):
                document = render_document(parse_notes(f"{name}(50% & more)", self.names))
                self.assertIn(f"\\begin{{{name}}}\n50\\% \\& more\n\\end{{{name}}}", document)
                self.assertIn("\\def\\NotesBoxesOnly{1}", document)

    def test_notes_render_as_plain_paragraphs_between_boxes(self):
        document = render_document(
            parse_notes(
                "question(Ready?) note(50% & more) note(Next paragraph.) answer(Yes.)",
                self.names,
            )
        )
        self.assertIn(
            "\\end{question}\n\n50\\% \\& more\n\nNext paragraph.\n\n\\begin{answer}",
            document,
        )
        self.assertNotIn("\\begin{note}", document)
        self.assertNotIn("\\end{note}", document)

    def test_headings_and_all_styles(self):
        for name, command in HEADINGS.items():
            document = render_document(parse_notes(f"{name}(50% & more)", self.names))
            self.assertIn(f"\\{command}{{50\\% \\& more}}", document)
        for name, command in TEXT_STYLES.items():
            self.assertEqual(format_text(f"{name}{{50% & more}}"), f"\\{command}{{50\\% \\& more}}")

    def test_nested_formatting_and_literal_syntax(self):
        self.assertEqual(format_text("bold{italic{50%}}"), r"\NotesBold{\NotesItalic{50\%}}")
        self.assertEqual(format_text(r"bold\{literal\}"), r"bold\{literal\}")
        self.assertEqual(format_text("f(x) {value}"), r"f(x) \{value\}")
        with self.assertRaises(ParseError):
            format_text("bold{unfinished")

    def test_ast_retains_original_source_spans(self):
        source = "\n  note(  hello bold{italic{world}}  )"
        box = parse_notes(source, self.names)[0]
        self.assertEqual(
            source[box.span.start : box.span.end], "note(  hello bold{italic{world}}  )"
        )
        self.assertIsInstance(box.children[0], Text)
        self.assertEqual(box.children[0].value, "hello ")
        self.assertEqual(source[box.children[0].span.start : box.children[0].span.end], "hello ")
        style = box.children[1]
        self.assertIsInstance(style, Style)
        self.assertEqual(source[style.span.start : style.span.end], "bold{italic{world}}")
        self.assertEqual(style.children[0].name, "italic")

    def test_escapes_are_consumed_once(self):
        cases = [
            (r"note(bold\{literal\})", r"bold\{literal\}"),
            (r"note(bold{open \( and close \)})", r"\NotesBold{open ( and close )}"),
            (r"note(\\\{literal\})", r"\textbackslash{}\{literal\}"),
            (r"note(\alpha & 50%)", r"\textbackslash{}alpha \& 50\%"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                box = parse_notes(source, self.names)[0]
                self.assertEqual(render_inline(box.children, TEXT_STYLES), expected)

    def test_formatting_errors_report_original_locations(self):
        cases = [
            ("note(ok)\nnote(\n  bold{unfinished", "line 3, column 3: missing closing '}'"),
            ("note(ok)\nnote(extra})", "line 2, column 11: unexpected '}'"),
            ("note(bold{text)", "line 1, column 15: unexpected ')'"),
            ("note({text)", "line 1, column 11: unexpected ')'"),
        ]
        for source, message in cases:
            with self.subTest(source=source), self.assertRaises(ParseError) as raised:
                parse_notes(source, self.names)
            self.assertIn(message, str(raised.exception))

    def test_literal_groups_and_identifier_boundaries(self):
        self.assertEqual(format_text("bold{f(x) {value}}"), r"\NotesBold{f(x) \{value\}}")
        self.assertEqual(
            format_text("notbold{text} _bold{text}"), r"notbold\{text\} \_bold\{text\}"
        )

    def test_long_identifier_after_underscore_is_literal(self):
        text = "_" + "a" * 100_000
        self.assertEqual(format_text(text), r"\_" + "a" * 100_000)

    def test_nesting_limit_is_a_parse_error(self):
        for opening, closing in [("bold{", "}"), ("(", ")"), ("{", "}")]:
            source = (
                "note(" + opening * (MAX_NESTING + 1) + "text" + closing * (MAX_NESTING + 1) + ")"
            )
            with (
                self.subTest(opening=opening),
                self.assertRaisesRegex(ParseError, "line 1, column .*maximum nesting"),
            ):
                parse_notes(source, self.names)

    def test_custom_text_template_controls_parsing_and_rendering(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "text.tex"
            path.write_text(
                "% notex-heading heading CustomHeading\n"
                "% notex-style highlight CustomHighlight\n"
                "\\newcommand{\\CustomHeading}[1]{\\section{#1}}\n"
                "\\newcommand{\\CustomHighlight}[1]{\\textbf{#1}}\n"
            )
            headings, styles = load_text_commands(path)
            nodes = parse_notes(
                "heading(highlight{Hello})", self.names, headings=headings, styles=styles
            )
            self.assertIn(
                r"\CustomHeading{\CustomHighlight{Hello}}",
                render_document(nodes, text_template=path),
            )
            path.write_text("% notex-heading heading Missing\n% notex-style highlight Missing\n")
            with self.assertRaisesRegex(ValueError, "Missing one-argument command"):
                load_text_commands(path)


if __name__ == "__main__":
    unittest.main()
