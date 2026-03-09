# supekku.scripts.lib.diagnostics.checks.deps

Dependency availability checks.

Checks core dependencies and per-language contract generation toolchains.
Python contract generation uses built-in AST and needs no external tool.

## Constants

- `CATEGORY`

## Functions

- `check_deps(ws) -> list[DiagnosticResult]`: Check availability of required and optional dependencies.
