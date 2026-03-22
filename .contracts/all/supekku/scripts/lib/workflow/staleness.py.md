# supekku.scripts.lib.workflow.staleness

Staleness evaluation for review-index cache.

Evaluates bootstrap_status transitions per DR-102 §8:
  warm → stale (staleness triggers)
  stale → invalid (invalidation rules)
  stale → reusable (reusability rules)

Design authority: DR-102 §8.

## Functions

- `_check_invalidation(cached_index) -> list[str]`: Check if stale cache should be marked invalid (DR-102 §8).

Returns list of invalidation reasons (empty if not invalid).
- `_extract_cached_files(cached_index) -> set[str]`: Extract all file paths from the cached domain_map.
- `_is_reusable(triggers, changed_files, cached_index) -> bool`: Check if stale cache is reusable for incremental update (DR-102 §8).

Reusable when:
1. Staleness is only commit_drift or minor scope change
2. domain_map file list is a superset of changed files (surface contracted)
3. No invariants contradicted
- `check_domain_map_files_exist(domain_map, root) -> list[str]`: Check which domain_map files have been deleted.

Returns list of deleted file paths. If non-empty, the cache
should be marked invalid per DR-102 §8.
- `evaluate_staleness(cached_index) -> StalenessResult`: Evaluate staleness of a review-index cache.

Args:
  cached_index: The existing review-index.yaml data.
  current_phase_id: Active phase ID.
  current_head: Current git HEAD (short sha).
  changed_files: Files changed since cache was built (optional).
  delta_updated: DE-*.md frontmatter updated timestamp (optional).

Returns:
  StalenessResult with status and triggered reasons.

## Classes

### StalenessResult

Result of staleness evaluation.
