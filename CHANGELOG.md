# Changelog

## Unreleased

- Add inline/display mathematics with precedence-aware fractions, powers, subscripts, nested roots, sums, integrals, derivatives, and algebraic expressions.
- Add equation rows, continuation rows, explicit text line breaks, source diagnostics, and math examples.
- Split the converter into an installable typed library and command-line interface.
- Bundle LaTeX templates in `src/notex/templates/`; root-level template paths have moved.
- Retain the `python3 convert.py` command and compatibility imports.
- Add PDF compilation with timeouts and isolated build artifacts.
- Add JSON conversion diagnostics and an in-memory conversion API.
- Preserve previous artifacts on parse/build failure and publish files atomically.
- Reject aliases of inputs/templates and duplicate/conflicting template declarations.
- Add lint, formatting, strict type checking, coverage, packaging verification, and CI.
- Document the live preview architecture and implementation milestones.

## 0.1.0 foundation

- Parse box, heading, paragraph, and nested text-formatting expressions.
- Preserve source spans and report syntax locations.
- Escape plain text during LaTeX rendering and bound parser nesting.
- Provide filled examples for the bundled box and text styles.
