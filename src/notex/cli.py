"""Command-line conversion, optional PDF builds, and structured diagnostics."""

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .compiler import CompileError, compile_pdf
from .models import ParseError
from .service import convert_source, validate_output_paths, write_bytes_atomic
from .templates import DEFAULT_TEMPLATE, DEFAULT_TEXT_TEMPLATE


def package_version() -> str:
    """Read the installed distribution version without duplicating metadata."""
    try:
        return version("notex-notes")
    except PackageNotFoundError:
        return "source checkout (not installed)"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert structured text notes to LaTeX or PDF.")
    parser.add_argument("input", type=Path, help="UTF-8 file containing note expressions")
    parser.add_argument(
        "-o", "--output", type=Path, help="output .tex path (default: input with .tex extension)"
    )
    parser.add_argument(
        "--template", type=Path, default=DEFAULT_TEMPLATE, help="LaTeX box definitions"
    )
    parser.add_argument(
        "--text-template", type=Path, default=DEFAULT_TEXT_TEMPLATE, help="LaTeX text definitions"
    )
    parser.add_argument(
        "--pdf", action="store_true", help="also compile a PDF beside the .tex output"
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="PDF build timeout in seconds (default: 30)"
    )
    parser.add_argument("--json", action="store_true", help="emit JSON results and diagnostics")
    parser.add_argument("--version", action="version", version=f"NoteX {package_version()}")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI; syntax errors preserve any previously generated output."""
    args = build_parser().parse_args(argv)
    output = args.output or args.input.with_suffix(".tex")
    pdf_path = output.with_suffix(".pdf") if args.pdf else None
    try:
        outputs = [output] + ([pdf_path] if pdf_path is not None else [])
        validate_output_paths(outputs, [args.input, args.template, args.text_template])
        # utf-8-sig accepts both ordinary UTF-8 and files with a byte-order mark.
        result = convert_source(
            args.input.read_text(encoding="utf-8-sig"),
            template=args.template,
            text_template=args.text_template,
        )
        # A failed PDF build cannot overwrite the last successful .tex or PDF.
        pdf = compile_pdf(result.latex, timeout=args.timeout) if pdf_path is not None else None
        write_bytes_atomic(output, result.latex.encode("utf-8"))
        if pdf is not None and pdf_path is not None:
            write_bytes_atomic(pdf_path, pdf.content)
    except (OSError, UnicodeError, ValueError) as error:
        diagnostic: dict[str, Any]
        if isinstance(error, ParseError):
            diagnostic = dict(error.as_dict())
        else:
            diagnostic = {
                "kind": "compile" if isinstance(error, CompileError) else "conversion",
                "message": str(error),
            }
        diagnostic["source"] = str(args.input)
        if isinstance(error, CompileError) and error.log:
            diagnostic["log"] = error.log
        if args.json:
            print(json.dumps({"ok": False, "diagnostics": [diagnostic]}), file=sys.stderr)
        else:
            print(f"{args.input}: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(
            json.dumps(
                {
                    "ok": True,
                    "output": str(output),
                    "pdf": str(pdf_path) if pdf_path is not None else None,
                    "expressions": len(result.expressions),
                    "diagnostics": [],
                }
            )
        )
    else:
        print(f"Wrote {output} ({len(result.expressions)} expressions)")
        if pdf_path is not None:
            print(f"Wrote {pdf_path}")
    return 0
