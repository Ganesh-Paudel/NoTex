"""Conversion API and atomic output publication shared by CLI and future preview."""

import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .models import Box
from .parser import parse_notes
from .renderer import render_document
from .syntax import BUILTIN_EXPRESSIONS, INLINE_BUILTINS
from .templates import (
    DEFAULT_TEMPLATE,
    DEFAULT_TEXT_TEMPLATE,
    load_box_names,
    load_text_commands,
)


@dataclass(frozen=True)
class ConversionResult:
    """One completed conversion, independent of any editor or output file."""

    expressions: tuple[Box, ...]
    latex: str


def convert_source(
    source: str,
    *,
    template: Path = DEFAULT_TEMPLATE,
    text_template: Path = DEFAULT_TEXT_TEMPLATE,
) -> ConversionResult:
    """Convert an in-memory source snapshot without writing output files."""
    names = load_box_names(template)
    headings, styles = load_text_commands(text_template)
    collisions = names.intersection(headings)
    if (
        collisions
        or headings.keys() & BUILTIN_EXPRESSIONS
        or styles.keys() & INLINE_BUILTINS
        or names & (BUILTIN_EXPRESSIONS - {"note"})
    ):
        raise ValueError("Template names must not overlap built-in syntax or heading/box names")
    expressions = tuple(parse_notes(source, names, headings=headings, styles=styles))
    return ConversionResult(expressions, render_document(expressions, template, text_template))


def write_bytes_atomic(path: Path, content: bytes) -> None:
    """Replace a file only after all bytes are written to a sibling temporary file.

    A sibling keeps the rename on the same filesystem. Existing file permissions
    are preserved; new files use tempfile's private permissions. Resolve symlinks
    so this function updates their target instead of replacing the symlink itself.
    """
    path = path.resolve()
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        # Clean up only the temporary file owned by this operation.
        temporary.unlink(missing_ok=True)


def validate_output_paths(outputs: list[Path], protected: list[Path]) -> None:
    """Reject input/template aliases and outputs that alias one another."""
    for index, output in enumerate(outputs):
        for other in protected + outputs[:index]:
            same_path = output.resolve() == other.resolve()
            same_file = output.exists() and other.exists() and output.samefile(other)
            if same_path or same_file:
                raise ValueError("Outputs must differ from the input, templates, and each other")
