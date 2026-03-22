# supekku.scripts.lib.backlog.registry

Backlog management utilities for creating and managing backlog entries.

Provides BacklogRegistry (ADR-009 conformant class) and module-level
wrapper functions for backwards compatibility (DEC-057-04).

## Constants

- `BACKLOG_ID_PATTERN`
- `logger`

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

Thin wrapper around BacklogRegistry for backwards compatibility (DEC-057-04).

Args:
root: Repository root (auto-detected if None)
kind: Filter by kind (issue|problem|improvement|risk|all)

Returns:
List of BacklogItem objects, sorted by ID.

- `extract_title(path) -> str`: Extract title from backlog entry file.

Args:
path: Path to backlog entry.

Returns:
Entry title from frontmatter or first heading.

- `find_backlog_items_by_id(item_id, root, kind) -> list[BacklogItem]`: Find backlog items by ID.

Thin wrapper around BacklogRegistry for backwards compatibility (DEC-057-04).
Returns a list because duplicate IDs may exist (data quality issue).

Args:
item_id: Backlog item ID (e.g. 'ISSUE-001', 'IMPR-003').
root: Repository root path.
kind: Optional kind filter ('issue', 'problem', 'improvement', 'risk').

Returns:
List of matching BacklogItem objects, sorted by path.

- `find_item(item_id, root, kind) -> <BinOp>`: Find a single backlog item by ID.

Thin wrapper around BacklogRegistry for backwards compatibility (DEC-057-04).

Args:
item_id: Backlog item ID (e.g. 'ISSUE-001').
root: Repository root path (auto-detected if None).
kind: Optional kind filter.

Returns:
BacklogItem or None if not found.

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

- `sync_backlog_registry(root) -> dict[Tuple[str, int]]`: Sync backlog registry with filesystem.

Discovers all backlog items, merges with existing registry ordering,
and writes updated registry. Preserves order of existing items,
appends new items, and prunes orphaned IDs.

Args:
root: Repository root path (auto-detected if None)
dry_run: If True, compute stats but skip writing registry.

Returns:
Dictionary with sync statistics: - total: total items in registry after sync - added: number of new items added - removed: number of orphaned items removed - unchanged: number of items already in registry

## Classes

### BacklogRegistry

Registry for backlog items (ADR-009 conformant).

Provides find/collect/iter/filter over all backlog item types.
Eagerly loads and caches items on construction (DEC-057-05).

#### Methods

- `collect(self) -> dict[Tuple[str, BacklogItem]]`: Return all backlog items as a dict keyed by ID (ADR-009 contract).
- `filter(self) -> list[BacklogItem]`: Filter items by domain-specific criteria.

Returns a list (ADR-009 contract). Empty list when no matches.

- `find(self, item_id) -> <BinOp>`: Find a backlog item by ID.

Returns the matching item or None (ADR-009 contract).

- `iter(self) -> Iterator[BacklogItem]`: Iterate over items, optionally filtered by status and/or kind.

### BacklogTemplate

Template for creating backlog entries with specific metadata.
