# supekku.scripts.lib.drift.creation

Drift ledger creation.

Creates new drift ledger files with frontmatter and entry heading.
See DR-065 §10 for the creation template.

## Functions

- `create_drift_ledger(name) -> Path`: Create a new drift ledger file.

Allocates the next DL-NNN ID by scanning existing files. Creates
.spec-driver/drift/ directory if needed.

Args:
name: Ledger name/title.
delta_ref: Optional owning delta (e.g. "DE-065").
repo_root: Repository root (auto-detected if None).

Returns:
Path to the created ledger file.

Raises:
ValueError: If name is empty.
