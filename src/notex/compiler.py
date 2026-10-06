"""Bounded PDF compilation in a temporary build directory."""

import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class CompileError(ValueError):
    """Compilation failed without publishing a replacement PDF."""

    def __init__(self, message: str, *, log: str = ""):
        self.log = log
        super().__init__(message)


@dataclass(frozen=True)
class PdfResult:
    """The completed PDF and build output, ready for atomic publication."""

    content: bytes
    log: str


def compile_pdf(latex: str, *, timeout: float = 30.0) -> PdfResult:
    """Run pdflatex once, without a shell, and retain no auxiliary build files.

    The generated template imports already use absolute paths. One pass is
    sufficient for current notes; cross-references and TOCs would require a
    multi-pass build. Custom templates are trusted local code.
    """
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("PDF compilation timeout must be a finite positive number")
    executable = shutil.which("pdflatex")
    if executable is None:
        raise CompileError("pdflatex is not installed; install TeX Live to use --pdf")
    with tempfile.TemporaryDirectory(prefix="notex-build-") as directory:
        build = Path(directory)
        (build / "document.tex").write_text(latex, encoding="utf-8")
        try:
            process = subprocess.run(
                [
                    executable,
                    "-no-shell-escape",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "document.tex",
                ],
                cwd=build,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise CompileError(f"PDF compilation exceeded {timeout:g} seconds") from error
        pdf = build / "document.pdf"
        if process.returncode != 0 or not pdf.is_file():
            detail = next(
                (line for line in process.stdout.splitlines() if line.startswith("!")),
                "See the build log for details",
            )
            raise CompileError(f"PDF compilation failed: {detail}", log=process.stdout)
        return PdfResult(pdf.read_bytes(), process.stdout)
