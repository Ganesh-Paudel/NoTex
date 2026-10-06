# Contributing

Use Python 3.10 or newer and an isolated environment. Install development tools with:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]' -c requirements-dev.txt
```

Keep parsing, LaTeX rendering, PDF compilation, and user interfaces separate. Add regression tests for observable behavior when changing syntax, diagnostics, output protection, or build handling. Preserve the source spans needed by future editor integration. Do not emit raw user content as LaTeX commands.

Bundled definitions are in `src/notex/templates/`. When adding a heading or style, put its `% notex-heading` or `% notex-style` declaration immediately above the matching one-argument macro. Add an example to `notes.txt`, update the README, and verify real LaTeX compilation. The template catalog also retains direct LaTeX usage that differs from converter behavior for `note`.

Before submitting a change:

```sh
ruff check .
ruff format --check .
mypy
python -m coverage run -m unittest discover -s tests
python -m coverage report
python -m build
python -m twine check --strict dist/*
python tools/verify_wheel.py dist/*.whl
```

Use `ruff format .` to apply formatting. Install TeX Live to run the PDF integration test locally. CI runs a separate LaTeX job so a skipped local test is not the only PDF verification. Keep generated caches, environments, wheel builds, and temporary LaTeX files out of commits. The tracked `notes.tex` and `notes.pdf` are example artifacts; regenerate them after intentional changes to the examples or rendering.

Describe the problem, the resulting behavior, and meaningful validation in pull requests. Update `CHANGELOG.md` for changes users need to know about. Version metadata lives in `pyproject.toml`.

The project does not yet declare a license. Selecting one and confirming ownership of the proposed `notex-notes` distribution name are explicit release decisions; building a wheel does not publish it.
