# supekku.cli.resolve

Resolve commands for cross-artifact link resolution.

## Constants

- `ArtifactIndex`
- `app`
- `log`

## Functions

- `_collect_backlog_items(root, index) -> None`: Add backlog items to the artifact index.
- `_collect_changes(root, index) -> None`: Add change artifacts (deltas, revisions, audits) to the artifact index.
- `_collect_decisions(root, index) -> None`: Add ADR decisions to the artifact index.
- `_collect_drift_ledgers(root, index) -> None`: Add drift ledgers to the artifact index.
- `_collect_memory_artifacts(root, index) -> None`: Add memory records to the artifact index.
- `_collect_specs(root, index) -> None`: Add specs to the artifact index.
- `_resolve_memory_links(root, dry_run, link_mode, scope_path) -> dict`: Resolve inline links in memory records.

For each mem.*.md file (or a single scoped file): parse body for
``[[...]]`` tokens, resolve against artifact index, update frontmatter.

Args:
  root: Repository root path.
  dry_run: If True, skip writing changes.
  link_mode: Link persistence mode.
  scope_path: If given, resolve only this file.

Returns:
  Stats dict with processed, resolved, missing, missing_detail,
  and warnings.
- `_resolve_memory_path(root, mem_id) -> Path`: Resolve a memory ID to its file path.

Raises typer.Exit on failure.
- `_resolve_single_memory(mem_file, root, index, stats) -> None`: Resolve links in a single memory file and update stats.
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
