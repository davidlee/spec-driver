# supekku.scripts.lib.diagnostics.checks.structure

Workspace directory structure checks.

## Constants

- `CATEGORY`

## Functions

- `_check_orphaned_bundles(parent_dir, artifact_type) -> list[DiagnosticResult]`: Find bundle directories that lack a primary markdown file.
- `check_structure(ws) -> list[DiagnosticResult]`: Check workspace directory structure for expected directories and orphans.
