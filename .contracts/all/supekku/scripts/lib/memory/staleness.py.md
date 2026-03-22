# supekku.scripts.lib.memory.staleness

Batched staleness computation for memory artifacts.

Computes staleness by counting git commits that touched scoped paths
since a memory's last verified SHA. Uses a single git invocation for
all scoped memories (DEC-086-06).

## Constants

- `__all__`

## Functions

- `_assign_commit_counts(results, attested, commit_data) -> None`: Count commits affecting each attested memory's scope paths.
- `_collect_all_pathspecs(attested) -> list[str]`: Collect deduplicated pathspecs from all attested records.
- `_collect_scope_paths(record) -> list[str]`: Collect all scope paths and converted globs for a record.
- `_days_since(record, today) -> <BinOp>`: Compute days since the most relevant date on a record.
- `_find_oldest_sha(attested) -> str`: Find the verified_sha from the record with the oldest verified date.
- `_parse_git_log_output(output) -> list[_CommitEntry]`: Parse ``git log --oneline --name-only`` output into commit entries.
- `_path_matches_scope(file_path, scope_paths) -> bool`: Check whether a file path matches any scope path (prefix match).
- `_query_git_log(attested, root) -> <BinOp>`: Run a single git log and parse commits with affected paths.

Returns None if git is unavailable or the command fails, so callers
can distinguish "no commits found" from "unable to query."
- `compute_batch_staleness(records, root) -> list[StalenessInfo]`: Compute staleness for multiple memories using a single git invocation.

For scoped+attested memories, runs one ``git log`` from the oldest
verified SHA and counts commits per memory's scope paths.

Unscoped and unattested memories fall back to ``days_since`` from
their verified or updated date.

Args:
  records: Memory records to evaluate.
  root: Repository root for git commands.

Returns:
  StalenessInfo for each input record, in the same order.
- `glob_to_pathspec(glob) -> str`: Convert a scope glob pattern to a git pathspec.

Strips trailing ``/**`` (directory wildcard) to produce a directory
prefix that git understands. Other patterns pass through as-is.
Leading ``./`` is also stripped.

Args:
  glob: Scope glob pattern (e.g. ``supekku/cli/**``).

Returns:
  Git-compatible pathspec string.

## Classes

### StalenessInfo

Staleness data for a single memory.

### _CommitEntry

A parsed commit from git log output.
