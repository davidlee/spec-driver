"""Backlog item models and status vocabulary.

Per-kind status sets define accepted lifecycle values (DEC-057-02, DEC-057-08).
Validation is permissive: unknown values are warned, not rejected.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# -- Unified backlog lifecycle statuses (DEC-075-05, supersedes DEC-057-02) --

BACKLOG_BASE_STATUSES: frozenset[str] = frozenset({
  "open",
  "triaged",
  "in-progress",
  "resolved",
})

RISK_EXTRA_STATUSES: frozenset[str] = frozenset({
  "accepted",
  "expired",
})

RISK_STATUSES: frozenset[str] = BACKLOG_BASE_STATUSES | RISK_EXTRA_STATUSES

# Per-kind lookup — all non-risk kinds share the base set.
BACKLOG_STATUSES: dict[str, frozenset[str]] = {
  "issue": BACKLOG_BASE_STATUSES,
  "problem": BACKLOG_BASE_STATUSES,
  "improvement": BACKLOG_BASE_STATUSES,
  "risk": RISK_STATUSES,
}

# Statuses excluded from default list views.
DEFAULT_HIDDEN_STATUSES: frozenset[str] = frozenset({
  "resolved",
})

ALL_VALID_STATUSES: frozenset[str] = BACKLOG_BASE_STATUSES | RISK_EXTRA_STATUSES


def is_valid_status(kind: str, status: str) -> bool:
  """Check whether a status is in the accepted set for the given kind.

  Returns True for known statuses, False for unknown. Logs a warning
  for unknown values (permissive validation per DEC-057-08).
  """
  valid = BACKLOG_STATUSES.get(kind)
  if valid is None:
    logger.warning("Unknown backlog kind %r; cannot validate status %r", kind, status)
    return False
  if status in valid:
    return True
  logger.warning(
    "Status %r is not in accepted values for %s: %s",
    status,
    kind,
    sorted(valid),
  )
  return False


@dataclass
class BacklogItem:
  """Backlog item model representing issues, problems, improvements, and risks."""

  id: str
  kind: str  # issue, problem, improvement, risk
  status: str
  title: str
  path: Path
  frontmatter: dict[str, Any] = field(default_factory=dict)
  tags: list[str] = field(default_factory=list)
  # Kind-specific optional fields
  severity: str = ""
  categories: list[str] = field(default_factory=list)
  impact: str = ""
  likelihood: float = 0.0
  created: str = ""
  updated: str = ""
  ext_id: str = ""
  ext_url: str = ""
