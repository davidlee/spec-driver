# supekku.scripts.lib.backlog

Backlog management utilities for creating and managing backlog entries.

## Constants

- `BACKLOG_ID_PATTERN`
- `__all__`

## Functions

- `append_backlog_summary() -> list[str]`
- `backlog_root(repo_root) -> Path`
- `create_backlog_entry(kind, name) -> Path`
- `extract_title(path) -> str`
- `find_repo_root(start) -> Path`
- `next_identifier(entries, prefix) -> str`
- `slugify(value) -> str`

## Classes

### BacklogTemplate

Template for creating backlog entries with specific metadata.
