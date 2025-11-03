# supekku.scripts.lib.backlog.registry

Backlog management utilities for creating and managing backlog entries.

## Constants

- `BACKLOG_ID_PATTERN`
- `__all__`

## Functions

- `append_backlog_summary() -> list[str]`: Append new entries to backlog summary file.

Args:
  repo_root: Optional repository root. Auto-detected if not provided.

Returns:
  List of newly added summary lines.
- `backlog_root(repo_root) -> Path`: Get backlog directory path.

Args:
  repo_root: Repository root path.

Returns:
  Backlog directory path.
- `create_backlog_entry(kind, name) -> Path`: Create a new backlog entry.

Args:
  kind: Entry kind (issue, problem, improvement, risk).
  name: Entry name/title.
  repo_root: Optional repository root. Auto-detected if not provided.

Returns:
  Path to created entry file.

Raises:
  ValueError: If kind is not supported.
- `discover_backlog_items() -> list[BacklogItem]`: Discover all backlog items in workspace.

Args:
  root: Repository root (auto-detected if None)
  kind: Filter by kind (issue|problem|improvement|risk|all)

Returns:
  List of BacklogItem objects
- `extract_title(path) -> str`: Extract title from backlog entry file.

Args:
  path: Path to backlog entry.

Returns:
  Entry title from frontmatter or first heading.
- `load_backlog_registry(root) -> list[str]`: Load backlog priority ordering from registry.

Args:
  root: Repository root path (auto-detected if None)

Returns:
  Ordered list of backlog item IDs. Empty list if registry doesn't exist
  or ordering field is missing.

Raises:
  yaml.YAMLError: If registry file exists but contains invalid YAML
- `next_identifier(entries, prefix) -> str`: Determine next sequential identifier.

Args:
  entries: Existing entry paths.
  prefix: Identifier prefix.

Returns:
  Next available identifier.
- `save_backlog_registry(ordering, root) -> None`: Save backlog priority ordering to registry.

Args:
  ordering: Ordered list of backlog item IDs
  root: Repository root path (auto-detected if None)

Note:
  Creates parent directories if needed. Uses atomic write via temporary file.
- `slugify(value) -> str`: Convert value to URL-friendly slug.

Args:
  value: String to slugify.

Returns:
  Lowercase slug with hyphens.
- `sync_backlog_registry(root) -> dict[Tuple[str, int]]`: Sync backlog registry with filesystem.

Discovers all backlog items, merges with existing registry ordering,
and writes updated registry. Preserves order of existing items,
appends new items, and prunes orphaned IDs.

Args:
  root: Repository root path (auto-detected if None)

Returns:
  Dictionary with sync statistics:
    - total: total items in registry after sync
    - added: number of new items added
    - removed: number of orphaned items removed
    - unchanged: number of items already in registry

## Classes

### BacklogTemplate

Template for creating backlog entries with specific metadata.
