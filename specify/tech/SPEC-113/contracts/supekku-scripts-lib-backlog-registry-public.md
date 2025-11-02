# supekku.scripts.lib.backlog.registry

Backlog management utilities for creating and managing backlog entries.

## Constants

- `BACKLOG_ID_PATTERN`

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
- `next_identifier(entries, prefix) -> str`: Determine next sequential identifier.

Args:
  entries: Existing entry paths.
  prefix: Identifier prefix.

Returns:
  Next available identifier.
- `slugify(value) -> str`: Convert value to URL-friendly slug.

Args:
  value: String to slugify.

Returns:
  Lowercase slug with hyphens.

## Classes

### BacklogTemplate

Template for creating backlog entries with specific metadata.
