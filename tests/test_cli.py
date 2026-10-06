"""Exercise user-visible CLI results and protection of existing artifacts."""

import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

# Importing convert also permits tests from a checkout without installation.
import convert
from notex.cli import main
from notex.compiler import CompileError, PdfResult


class CliTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "notes.txt"
        self.output = self.root / "notes.tex"
        self.pdf = self.root / "notes.pdf"
        self.source.write_text("note(bold{Hello} & goodbye.)", encoding="utf-8-sig")

    def invoke(self, *arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main([str(self.source), *arguments])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_json_success_and_bom_input(self):
        code, stdout, stderr = self.invoke("--json")
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertTrue(json.loads(stdout)["ok"])
        self.assertIn(r"\NotesBold{Hello} \& goodbye.", self.output.read_text())

    def test_explicit_output_and_human_readable_result(self):
        target = self.root / "custom.tex"
        code, stdout, stderr = self.invoke("-o", str(target))
        self.assertEqual(code, 0)
        self.assertIn(str(target), stdout)
        self.assertEqual(stderr, "")
        self.assertTrue(target.is_file())

    def test_invalid_source_preserves_existing_outputs(self):
        self.output.write_text("last successful tex")
        self.pdf.write_bytes(b"last successful pdf")
        self.source.write_text("note(ok)\nnote(bold{unfinished)")
        code, stdout, stderr = self.invoke("--json", "--pdf")
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        diagnostic = json.loads(stderr)["diagnostics"][0]
        self.assertEqual(diagnostic["kind"], "syntax")
        self.assertEqual(diagnostic["line"], 2)
        self.assertEqual(self.output.read_text(), "last successful tex")
        self.assertEqual(self.pdf.read_bytes(), b"last successful pdf")

    def test_failed_compilation_preserves_existing_outputs(self):
        self.output.write_text("last successful tex")
        self.pdf.write_bytes(b"last successful pdf")
        with patch("notex.cli.compile_pdf", side_effect=CompileError("bad build", log="error log")):
            code, _, stderr = self.invoke("--pdf", "--json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stderr)["diagnostics"][0]["log"], "error log")
        self.assertEqual(self.output.read_text(), "last successful tex")
        self.assertEqual(self.pdf.read_bytes(), b"last successful pdf")

    def test_completed_pdf_is_published(self):
        with patch("notex.cli.compile_pdf", return_value=PdfResult(b"%PDF-test", "")):
            code, stdout, _ = self.invoke("--pdf")
        self.assertEqual(code, 0)
        self.assertIn(str(self.pdf), stdout)
        self.assertEqual(self.pdf.read_bytes(), b"%PDF-test")

    def test_source_alias_and_hard_link_are_rejected(self):
        original = self.source.read_bytes()
        link = self.root / "alias.tex"
        link.hardlink_to(self.source)
        for target in (self.source, link):
            with self.subTest(target=target):
                code, _, stderr = self.invoke("-o", str(target))
                self.assertEqual(code, 1)
                self.assertIn("Outputs must differ", stderr)
                self.assertEqual(self.source.read_bytes(), original)

    def test_pdf_and_tex_must_not_alias(self):
        code, _, stderr = self.invoke("-o", str(self.pdf), "--pdf")
        self.assertEqual(code, 1)
        self.assertIn("Outputs must differ", stderr)

    def test_missing_input_is_reported_without_traceback(self):
        self.source.unlink()
        code, _, stderr = self.invoke("--json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stderr)["diagnostics"][0]["kind"], "conversion")
        self.assertNotIn("Traceback", stderr)

    def test_compatibility_script_runs_from_another_directory(self):
        process = subprocess.run(
            [sys.executable, str(Path(convert.__file__).resolve()), str(self.source)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertTrue(self.output.is_file())
