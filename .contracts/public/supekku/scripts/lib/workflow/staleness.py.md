# supekku.scripts.lib.workflow.staleness

Staleness evaluation for review-index cache.

Evaluates bootstrap_status transitions per DR-102 §8:
warm → stale (staleness triggers)
stale → invalid (invalidation rules)
stale → reusable (reusability rules)

Design authority: DR-102 §8.

## Functions

- `check_domain_map_files_exist(domain_map, root) -> list[str]`: Check which domain_map files have been deleted.

Returns list of deleted file paths. If non-empty, the cache
should be marked invalid per DR-102 §8.

- `evaluate_staleness(cached_index) -> StalenessResult`: Evaluate staleness of a review-index cache.

Args:
cached_index: The existing review-index.yaml data.
current_phase_id: Active phase ID.
current_head: Current git HEAD (short sha).
changed_files: Files changed since cache was built (optional).
delta_updated: DE-\*.md frontmatter updated timestamp (optional).

Returns:
StalenessResult with status and triggered reasons.

## Classes

### BootstrapStatus

Bootstrap status values per DR-102 §8.

### StalenessResult

Result of staleness evaluation.
