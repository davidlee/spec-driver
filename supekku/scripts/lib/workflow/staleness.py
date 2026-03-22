"""Staleness evaluation for review-index cache.

Evaluates bootstrap_status transitions per DR-102 §8:
  warm → stale (staleness triggers)
  stale → invalid (invalidation rules)
  stale → reusable (reusability rules)

Design authority: DR-102 §8.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class BootstrapStatus:
  """Bootstrap status values per DR-102 §8."""

  COLD = "cold"
  WARMING = "warming"
  WARM = "warm"
  STALE = "stale"
  INVALID = "invalid"
  REUSABLE = "reusable"


@dataclass
class StalenessResult:
  """Result of staleness evaluation."""

  status: str
  triggers: list[str] = field(default_factory=list)
  can_incremental_update: bool = False


def evaluate_staleness(
  cached_index: dict[str, Any],
  *,
  current_phase_id: str,
  current_head: str,
  changed_files: list[str] | None = None,
  delta_updated: str | None = None,
) -> StalenessResult:
  """Evaluate staleness of a review-index cache.

  Args:
    cached_index: The existing review-index.yaml data.
    current_phase_id: Active phase ID.
    current_head: Current git HEAD (short sha).
    changed_files: Files changed since cache was built (optional).
    delta_updated: DE-*.md frontmatter updated timestamp (optional).

  Returns:
    StalenessResult with status and triggered reasons.
  """
  cache_key = cached_index.get("staleness", {}).get("cache_key", {})
  cached_phase = cache_key.get("phase_id", "")
  cached_head = cache_key.get("head", "")

  triggers: list[str] = []

  # 1. Commit drift
  if cached_head != current_head:
    triggers.append("commit_drift")

  # 2. Phase boundary crossing
  if cached_phase != current_phase_id:
    triggers.append("phase_boundary_crossing")

  # 3. Major scope change (delta updated timestamp newer than cache)
  if delta_updated:
    cache_bootstrapped = cached_index.get("review", {}).get(
      "last_bootstrapped_at",
      "",
    )
    if delta_updated > cache_bootstrapped:
      triggers.append("major_scope_change")

  # 4. Dependency surface expansion
  if changed_files:
    cached_files = _extract_cached_files(cached_index)
    new_files = set(changed_files) - cached_files
    if new_files:
      triggers.append("dependency_surface_expansion")

  if not triggers:
    return StalenessResult(status=BootstrapStatus.WARM)

  # Check invalidation rules (stale → invalid)
  invalidation_reasons = _check_invalidation(
    cached_index,
    changed_files=changed_files,
  )
  if invalidation_reasons:
    return StalenessResult(
      status=BootstrapStatus.INVALID,
      triggers=triggers + invalidation_reasons,
    )

  # Check reusability rules (stale → reusable)
  if _is_reusable(triggers, changed_files, cached_index):
    return StalenessResult(
      status=BootstrapStatus.REUSABLE,
      triggers=triggers,
      can_incremental_update=True,
    )

  return StalenessResult(status=BootstrapStatus.STALE, triggers=triggers)


def _extract_cached_files(cached_index: dict[str, Any]) -> set[str]:
  """Extract all file paths from the cached domain_map."""
  files: set[str] = set()
  for entry in cached_index.get("domain_map", []):
    files.update(entry.get("files", []))
  return files


def _check_invalidation(
  cached_index: dict[str, Any],
  *,
  changed_files: list[str] | None = None,
) -> list[str]:
  """Check if stale cache should be marked invalid (DR-102 §8).

  Returns list of invalidation reasons (empty if not invalid).
  """
  reasons: list[str] = []

  # Schema version mismatch
  if cached_index.get("version") != 1:
    reasons.append("schema_version_mismatch")

  # Schema ID mismatch
  if cached_index.get("schema") != "supekku.workflow.review-index":
    reasons.append("schema_id_mismatch")

  # File deletion invalidation is deferred to command-level code
  # that can check Path.exists() via check_domain_map_files_exist().

  return reasons


def _is_reusable(
  triggers: list[str],
  changed_files: list[str] | None,
  cached_index: dict[str, Any],
) -> bool:
  """Check if stale cache is reusable for incremental update (DR-102 §8).

  Reusable when:
  1. Staleness is only commit_drift or minor scope change
  2. domain_map file list is a superset of changed files (surface contracted)
  3. No invariants contradicted
  """
  # Only reusable for minor staleness
  severe_triggers = {"phase_boundary_crossing", "dependency_surface_expansion"}
  if severe_triggers & set(triggers):
    return False

  # If we have changed files, check surface contraction
  if changed_files:
    cached_files = _extract_cached_files(cached_index)
    if not set(changed_files).issubset(cached_files):
      return False

  return True


def check_domain_map_files_exist(
  domain_map: list[dict[str, Any]],
  root: Path,
) -> list[str]:
  """Check which domain_map files have been deleted.

  Returns list of deleted file paths. If non-empty, the cache
  should be marked invalid per DR-102 §8.
  """
  deleted: list[str] = []
  for entry in domain_map:
    for f in entry.get("files", []):
      if not (root / f).exists():
        deleted.append(f)
  return deleted
