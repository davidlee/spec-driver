# supekku.scripts.lib.memory.staleness

Batched staleness computation for memory artifacts.

Computes staleness by counting git commits that touched scoped paths
since a memory's last verified SHA. Uses a single git invocation for
all scoped memories (DEC-086-06).

## Functions

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
