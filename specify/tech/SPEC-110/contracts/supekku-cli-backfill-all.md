# supekku.cli.backfill

Backfill commands for replacing stub specs with fresh templates.

## Constants

- `app`

## Functions

- `_write_spec_with_frontmatter(spec_path, frontmatter, body) -> None`: Write spec file with frontmatter and body.

Args:
  spec_path: Path to spec file
  frontmatter: Frontmatter dict to serialize as YAML
  body: Body content (markdown)
- @app.command(spec) `backfill_spec(spec_id, force, root) -> None`: Replace stub spec body with template (preserving frontmatter).

This command resets a stub spec to a clean template state, filling in
basic variables (spec_id, name, kind) from frontmatter. The agent or
user can then complete the sections intelligently.

By default, only specs detected as stubs (status='stub' or ≤30 lines)
will be backfilled. Use --force to override this safety check.
