# supekku.cli.compact

Compact commands for stripping default/derived frontmatter fields.

## Constants

- `app`

## Functions

- @app.command(delta) `compact_deltas(delta_id, dry_run, root) -> None`: Compact delta frontmatter by stripping default/derived fields.

Uses FieldMetadata persistence annotations to remove fields that carry
no information (empty defaults, derived values). Safe: read-side tolerance
means existing parsers handle compacted files unchanged.
