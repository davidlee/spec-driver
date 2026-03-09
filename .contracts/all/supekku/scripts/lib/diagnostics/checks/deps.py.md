# supekku.scripts.lib.diagnostics.checks.deps

Dependency availability checks.

Checks core dependencies and per-language contract generation toolchains.
Python contract generation uses built-in AST and needs no external tool.

## Constants

- `CATEGORY`

## Functions

- `_check_binary(name, label, install_hint) -> DiagnosticResult`: Check if a binary is available in PATH.
- `_check_git() -> DiagnosticResult`
- `_check_python() -> DiagnosticResult`
- `_check_ts_doc_extract(ws) -> DiagnosticResult`
- `check_deps(ws) -> list[DiagnosticResult]`: Check availability of required and optional dependencies.
