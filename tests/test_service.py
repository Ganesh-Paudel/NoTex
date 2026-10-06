"""Conversion boundaries, template validation, and failure-safe file writes."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import convert
from notex.models import Box, SourceSpan
from notex.service import convert_source, write_bytes_atomic
from notex.templates import load_box_names, load_text_commands, strip_comments


class ServiceTests(unittest.TestCase):
    def test_conversion_has_no_output_side_effects(self):
        result = convert_source("title(Example) note(bold{Hello})")
        self.assertEqual(len(result.expressions), 2)
        self.assertIn(r"\NotesTitle{Example}", result.latex)
        self.assertIn(r"\NotesBold{Hello}", result.latex)

    def test_empty_document_is_valid(self):
        result = convert_source(" \n\t")
        self.assertEqual(result.expressions, ())
        self.assertIn(r"\begin{document}", result.latex)

    def test_source_comment_definitions_are_ignored(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "boxes.tex"
            path.write_text("% \\newtcolorbox{fake}{}\n\\newtcolorbox{real}{}\n")
            self.assertEqual(load_box_names(path), {"real"})
            path.write_text("% \\newtcolorbox{fake}{}\n")
            with self.assertRaisesRegex(ValueError, "No box definitions"):
                load_box_names(path)
            path.write_text("\\newtcolorbox{same}{}\n\\newtcolorbox{same}{}\n")
            with self.assertRaisesRegex(ValueError, "Duplicate box definitions"):
                load_box_names(path)

    def test_comments_preserve_escaped_percent(self):
        self.assertEqual(strip_comments("keep \\% value % comment"), "keep \\% value ")
        self.assertEqual(strip_comments("stop \\\\% comment"), "stop \\\\")

    def test_duplicate_or_commented_macro_declarations_are_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "text.tex"
            content = convert.DEFAULT_TEXT_TEMPLATE.read_text()
            path.write_text(content + "\n% notex-style bold NotesBold\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                load_text_commands(path)
            path.write_text(
                content.replace(r"\newcommand{\NotesBold}", r"% \newcommand{\NotesBold}")
            )
            with self.assertRaisesRegex(ValueError, "Missing one-argument"):
                load_text_commands(path)
            path.write_text("% no declarations\n")
            with self.assertRaisesRegex(ValueError, "No heading or style"):
                load_text_commands(path)

    def test_heading_box_collisions_are_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "text.tex"
            path.write_text(
                convert.DEFAULT_TEXT_TEMPLATE.read_text().replace(
                    "% notex-heading title NotesTitle", "% notex-heading question NotesTitle"
                )
            )
            with self.assertRaisesRegex(ValueError, "overlap"):
                convert_source("question(hello)", text_template=path)

    def test_templates_cannot_replace_builtin_math_syntax(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "text.tex"
            for declaration, replacement in (
                ("% notex-style bold NotesBold", "% notex-style math NotesBold"),
                ("% notex-style bold NotesBold", "% notex-style newline NotesBold"),
                ("% notex-heading title NotesTitle", "% notex-heading equation NotesTitle"),
            ):
                with self.subTest(replacement=replacement):
                    path.write_text(
                        convert.DEFAULT_TEXT_TEMPLATE.read_text().replace(declaration, replacement)
                    )
                    with self.assertRaisesRegex(ValueError, "overlap"):
                        convert_source("note(hello)", text_template=path)
            path.write_text(r"\newtcolorbox{math}{}")
            with self.assertRaisesRegex(ValueError, "overlap"):
                convert_source("note(hello)", template=path)

    def test_untrusted_expression_names_cannot_inject_latex(self):
        node = Box("bad}\\input{file", (), SourceSpan(0, 0))
        with self.assertRaisesRegex(ValueError, "Unknown expression"):
            convert.render_document([node])

    def test_unsafe_template_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "template path"):
            convert.render_document([], template=Path("bad%name.tex"))

    def test_failed_atomic_replace_preserves_old_file_and_cleans_temp(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "result.tex"
            path.write_bytes(b"old")
            with patch("notex.service.os.replace", side_effect=OSError("rename failed")):
                with self.assertRaisesRegex(OSError, "rename failed"):
                    write_bytes_atomic(path, b"new")
            self.assertEqual(path.read_bytes(), b"old")
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_atomic_replace_preserves_permissions_and_symlink(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "result.tex"
            path.write_bytes(b"old")
            path.chmod(0o640)
            alias = Path(directory) / "alias.tex"
            alias.symlink_to(path)
            write_bytes_atomic(alias, b"new")
            self.assertEqual(path.read_bytes(), b"new")
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            self.assertTrue(alias.is_symlink())
