# supekku.scripts.lib.memory.selection

Memory selection — scope matching, specificity scoring, and path normalization.

Pure functions for deterministic filtering and ordering of memory records.
Implements MEM-FR-003 per JAMMS §5 and design-phase-04-selection.md.

## Functions

- `is_surfaceable(record, context) -> bool`: Check whether a record should be surfaced.

Excludes (unless skip_status_filter):

- status in {deprecated, superseded, obsolete}
- draft unless include_draft
  Always checks:
- thread: requires scope-matched to context AND recently verified

Args:
record: Memory record to check.
context: Optional match context for thread evaluation.
include_draft: Whether to include draft records.
skip_status_filter: Skip status-based exclusions (when caller
has already pre-filtered by explicit --status).
thread_recency_days: Max days since verified for thread inclusion.
today: Reference date; defaults to date.today().

Returns:
True if the record should be surfaced.

- `matches_scope(record, context) -> bool`: Check if a record's scope matches the given context.

OR logic across dimensions. A dimension only participates if the
context provides input for it.

Args:
record: Memory record to check.
context: Caller's current context.

Returns:
True if any active dimension matches.

- `normalize_path(path) -> str`: Normalize a path to repo-relative POSIX form.

Rules:

- Strip leading './'
- Resolve '..' segments
- Preserve trailing '/' (directory marker)
- Make absolute paths relative to repo_root if provided
- Collapse double slashes

Args:
path: Raw path string.
repo_root: If provided, absolute paths are relative to this root.

Returns:
Normalized repo-relative POSIX path string.

- `scope_specificity(record, context) -> int`: Score how specific the scope match is.

Returns the MAX specificity across matched dimensions:
3 = matched via scope.paths (exact or prefix)
2 = matched via scope.globs
1 = matched via scope.commands
0 = matched via tags only / no match / no context

Args:
record: Memory record to score.
context: Caller's current context.

Returns:
Integer specificity score (0-3).

- `select(records, context) -> list[MemoryRecord]`: Filter, match, and order memory records deterministically.

Pipeline:

1. Filter by is_surfaceable (status, draft, thread rules)
2. If context provided, filter non-threads by matches_scope
3. Sort by sort_key
4. Apply limit

Args:
records: Input memory records.
context: Optional match context for scope filtering.
include_draft: Whether to include draft records.
skip_status_filter: Skip status-based exclusions (when caller
has already pre-filtered by explicit --status).
thread_recency_days: Max days since verified for thread inclusion.
limit: Maximum number of results (None = unlimited).
today: Reference date; defaults to date.today().

Returns:
Sorted list of matching memory records.

- `sort_key(record, context) -> tuple[Tuple[int, int, int, int, str]]`: Build a deterministic sort key for a memory record.

5-level key per JAMMS §5.4:

1. severity rank (critical=0 → none=4)
2. -weight (higher weight sorts first)
3. -specificity (more specific scope sorts first)
4. verified recency (fewer days since = better; null = last)
5. id (lexicographic)

Args:
record: Memory record to build key for.
context: Optional match context for specificity scoring.
today: Reference date for recency; defaults to date.today().

Returns:
5-tuple usable as a sort key.

## Classes

### MatchContext

Caller's current context for scope matching.

Attributes:
paths: Changed/target files (repo-relative, POSIX-normalized).
command: Command being run (e.g. "test auth --verbose").
tags: Explicit tags for scope matching.
