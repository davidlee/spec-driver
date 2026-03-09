# supekku.cli.resolve

Resolve commands for cross-artifact link resolution.

## Constants

- `ArtifactIndex`
- `app`
- `log`

## Functions

- `build_artifact_index(root) -> ArtifactIndex`: Build artifact ID → (relative_path, kind) index.

Collects IDs from all known registries: decisions, specs,
deltas, revisions, audits, memory records, and backlog items.

Args:
  root: Repository root path.

Returns:
  Dict mapping artifact ID to (relative_path, kind).
- @app.command(links) `resolve_links(dry_run, link_mode, verbose, scope_path, scope_id) -> None`: Resolve [[...]] links in memory record bodies.

Parses wikilink tokens from memory body text, resolves them
against known artifacts, and writes results to frontmatter.
