"""PDF tool discovery, build failure, timeouts, and real LaTeX integration."""

import shutil
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import convert
from notex.compiler import CompileError, compile_pdf
from notex.service import convert_source


class CompilerTests(unittest.TestCase):
    def test_missing_compiler_has_actionable_message(self):
        with patch("notex.compiler.shutil.which", return_value=None):
            with self.assertRaisesRegex(CompileError, "install TeX Live"):
                compile_pdf("unused")

    def test_timeout_is_reported(self):
        with (
            patch("notex.compiler.shutil.which", return_value="pdflatex"),
            patch(
                "notex.compiler.subprocess.run",
                side_effect=subprocess.TimeoutExpired("pdflatex", 1),
            ),
        ):
            with self.assertRaisesRegex(CompileError, "exceeded 1 seconds"):
                compile_pdf("unused", timeout=1)

    def test_nonpositive_or_nonfinite_timeout_is_rejected(self):
        for timeout in (0, -1, float("nan"), float("inf")):
            with (
                self.subTest(timeout=timeout),
                self.assertRaisesRegex(ValueError, "finite positive"),
            ):
                compile_pdf("unused", timeout=timeout)

    def test_failed_build_retains_log(self):
        process = subprocess.CompletedProcess(["pdflatex"], 1, "! Example error\n")
        with (
            patch("notex.compiler.shutil.which", return_value="pdflatex"),
            patch("notex.compiler.subprocess.run", return_value=process),
        ):
            with self.assertRaises(CompileError) as raised:
                compile_pdf("unused")
        self.assertIn("Example error", str(raised.exception))
        self.assertEqual(raised.exception.log, process.stdout)

    def test_success_without_pdf_is_still_failure(self):
        process = subprocess.CompletedProcess(["pdflatex"], 0, "no artifact")
        with (
            patch("notex.compiler.shutil.which", return_value="pdflatex"),
            patch("notex.compiler.subprocess.run", return_value=process),
        ):
            with self.assertRaisesRegex(CompileError, "See the build log"):
                compile_pdf("unused")

    def test_compiler_uses_isolated_directory_and_disables_shell_escape(self):
        directories = []

        def run(arguments, **kwargs):
            build = Path(kwargs["cwd"])
            directories.append(build)
            self.assertIn("-no-shell-escape", arguments)
            self.assertNotIn("shell", kwargs)
            self.assertEqual((build / "document.tex").read_text(), "latex snapshot")
            (build / "document.pdf").write_bytes(b"%PDF-test")
            return subprocess.CompletedProcess(arguments, 0, "done")

        with (
            patch("notex.compiler.shutil.which", return_value="pdflatex"),
            patch("notex.compiler.subprocess.run", side_effect=run),
        ):
            result = compile_pdf("latex snapshot")
        self.assertEqual(result.content, b"%PDF-test")
        self.assertFalse(directories[0].exists())

    @unittest.skipUnless(shutil.which("pdflatex"), "TeX Live is not installed")
    def test_all_example_notes_compile_with_real_latex(self):
        root = Path(convert.__file__).resolve().parent
        result = convert_source((root / "notes.txt").read_text())
        pdf = compile_pdf(result.latex)
        self.assertTrue(pdf.content.startswith(b"%PDF-"))

    @unittest.skipUnless(shutil.which("pdflatex"), "TeX Live is not installed")
    def test_math_layout_and_edge_cases_compile_with_real_latex(self):
        source = """
            newline()
            title(Math notation math{alpha+pi})
            section(Equations math{x_i^2})
            note(newline() newline() Start. math{sqrt(1/10)} newline() End.)
            equation(1e3^2 + x_1! + root(x,3) + abs(x))
            equation(sin(x)+cos(x)+tan(x)+asin(x)+acos(x)+atan(x))
            equation(sinh(x)+cosh(x)+tanh(x)+ln(x)+log(x)+log(x,2)+exp(x))
            equation(partial(partial(f(x,y),x),y))
            equation(integral(integral(x*y,x,0,1),y,0,2))
            equation(x=(-b+/-sqrt(b^2-4*a*c))/(2*a))
            equation(alpha+beta+Gamma+θ+inf+hbar+nabla)
            equation(x=1+1 newline() =2 newline() y=3)
        """
        result = compile_pdf(convert_source(source).latex)
        self.assertTrue(result.content.startswith(b"%PDF-"))
