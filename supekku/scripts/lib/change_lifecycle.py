"""Change artifact lifecycle status constants and definitions.

For deltas, revisions, and audits - distinct from requirement lifecycle statuses.
"""

from __future__ import annotations

ChangeStatus = str

# Change artifact statuses
STATUS_DRAFT: ChangeStatus = "draft"
STATUS_PENDING: ChangeStatus = "pending"
STATUS_IN_PROGRESS: ChangeStatus = "in-progress"
STATUS_COMPLETED: ChangeStatus = "completed"
STATUS_DEFERRED: ChangeStatus = "deferred"

# Legacy alias for backwards compatibility
STATUS_COMPLETE: ChangeStatus = "complete"  # Maps to completed

VALID_STATUSES: set[ChangeStatus] = {
  STATUS_DRAFT,
  STATUS_PENDING,
  STATUS_IN_PROGRESS,
  STATUS_COMPLETED,
  STATUS_DEFERRED,
  STATUS_COMPLETE,  # Allow for backwards compatibility
}

# Canonical mapping for normalization
CANONICAL_STATUS_MAP: dict[str, str] = {
  "complete": STATUS_COMPLETED,  # Normalize legacy status
  "completed": STATUS_COMPLETED,
  "draft": STATUS_DRAFT,
  "pending": STATUS_PENDING,
  "in-progress": STATUS_IN_PROGRESS,
  "deferred": STATUS_DEFERRED,
}


def normalize_status(status: str) -> str:
  """Normalize a status string to its canonical form."""
  normalized = status.lower().strip()
  return CANONICAL_STATUS_MAP.get(normalized, normalized)


__all__ = [
  "CANONICAL_STATUS_MAP",
  "STATUS_COMPLETE",
  "STATUS_COMPLETED",
  "STATUS_DEFERRED",
  "STATUS_DRAFT",
  "STATUS_IN_PROGRESS",
  "STATUS_PENDING",
  "VALID_STATUSES",
  "ChangeStatus",
  "normalize_status",
]
