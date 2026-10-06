"""Smoke-test an installed wheel outside the checkout without downloading packages."""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="notex-wheel-") as directory:
        root = Path(directory)
        installed = root / "installed"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-deps",
                "--target",
                str(installed),
                str(args.wheel.resolve()),
            ],
            check=True,
        )
        environment = dict(os.environ, PYTHONPATH=str(installed))
        # Check that wheel imports and template paths do not resolve to src/.
        check = (
            "from pathlib import Path; import notex; "
            "from notex.templates import DEFAULT_TEMPLATE, DEFAULT_TEXT_TEMPLATE, load_box_names; "
            f"root = Path({str(installed)!r}); "
            "assert Path(notex.__file__).is_relative_to(root); "
            "assert DEFAULT_TEMPLATE.is_relative_to(root); "
            "assert DEFAULT_TEXT_TEMPLATE.is_file(); "
            "assert len(load_box_names(DEFAULT_TEMPLATE)) == 57"
        )
        subprocess.run([sys.executable, "-c", check], cwd=root, env=environment, check=True)
        notes = root / "example.txt"
        notes.write_text("title(Installed wheel) note(bold{Hello} & goodbye.)", encoding="utf-8")
        subprocess.run(
            [sys.executable, "-m", "notex", str(notes), "--json"],
            cwd=root,
            env=environment,
            check=True,
        )
        if r"\NotesBold{Hello} \& goodbye." not in notes.with_suffix(".tex").read_text():
            raise RuntimeError("Installed wheel produced unexpected LaTeX")
    print("Installed-wheel smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
