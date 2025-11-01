# supekku.cli.workspace

Workspace-level commands: install and validate.

## Constants

- `app`

## Functions

- @app.command(install) `install(target_dir, dry_run, auto_yes) -> None`: Initialize spec-driver workspace structure and registry files.

Creates the necessary directory structure and initializes registry files
for a new spec-driver workspace.
- @app.command(validate) `validate(root, sync, strict) -> None`: Validate workspace metadata and relationships.

Checks workspace integrity, validates cross-references between documents,
and reports any issues found.
