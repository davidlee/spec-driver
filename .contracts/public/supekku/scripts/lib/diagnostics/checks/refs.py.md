# supekku.scripts.lib.diagnostics.checks.refs

Cross-reference consistency checks.

Delegates to WorkspaceValidator and translates ValidationIssue results
into DiagnosticResult entries.

## Constants

- `CATEGORY`

## Functions

- `check_refs(ws) -> list[DiagnosticResult]`: Check cross-reference consistency by delegating to WorkspaceValidator. - type: ignore[arg-type]
