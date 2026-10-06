"""Run with: python3 -m unittest -v"""

import unittest

from convert import Box, DEFAULT_TEMPLATE, ParseError, escape_latex, load_box_names, parse_notes, render_document


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.names = load_box_names(DEFAULT_TEMPLATE)

    def test_multiline_parentheses_and_multiple_boxes(self):
        self.assertEqual(
            parse_notes("question(What is f(x)?)\nanswer(\nFirst line.\n\nSecond line.\n)", self.names),
            [Box("question", "What is f(x)?"), Box("answer", "First line.\n\nSecond line.")],
        )

    def test_literal_unmatched_parentheses_and_backslash(self):
        self.assertEqual(
            parse_notes(r"note(Open \( and close \); path C:\\notes.)", self.names),
            [Box("note", "Open ( and close ); path C:\\notes.")],
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
        document = render_document(parse_notes(
            "question(Ready?) note(50% & more) note(Next paragraph.) answer(Yes.)",
            self.names,
        ))
        self.assertIn(
            "\\end{question}\n\n50\\% \\& more\n\nNext paragraph.\n\n\\begin{answer}",
            document,
        )
        self.assertNotIn("\\begin{note}", document)
        self.assertNotIn("\\end{note}", document)


if __name__ == "__main__":
    unittest.main()
