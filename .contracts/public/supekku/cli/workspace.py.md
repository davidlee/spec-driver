# supekku.cli.workspace

Workspace-level commands: install, validate, and doctor.

## Constants

- `app`

## Functions

- @app.command(doctor) `doctor(root, check, json_output, verbose) -> None`: Run workspace health diagnostics.

Checks dependencies, configuration, directory structure, registries,
cross-references, and lifecycle hygiene. Reports pass/warn/fail per check
with actionable suggestions.

Exit codes: 0 = all pass, 1 = warnings, 2 = failures.

- @app.command(install) `install(target_dir, dry_run, auto_yes) -> None`: Initialize spec-driver workspace structure and registry files.

Creates the necessary directory structure and initializes registry files
for a new spec-driver workspace.

- @app.command(validate) `validate(root, sync, strict, verbose) -> None`: Validate workspace metadata and relationships.

Checks workspace integrity, validates cross-references between documents,
and reports any issues found.

By default, only errors and warnings are shown. Use --verbose to see
info-level messages about planned verification artifacts.
