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

# -- Per-kind accepted lifecycle statuses (DEC-057-02) --

ISSUE_STATUSES: frozenset[str] = frozenset(
  {
    "open",
    "triaged",
    "in-progress",
    "resolved",
    "done",
    "implemented",
    "verified",
  }
)

PROBLEM_STATUSES: frozenset[str] = frozenset(
  {
    "captured",
    "investigating",
    "mitigated",
    "resolved",
  }
)

IMPROVEMENT_STATUSES: frozenset[str] = frozenset(
  {
    "idea",
    "planned",
    "in-progress",
    "implemented",
  }
)

RISK_STATUSES: frozenset[str] = frozenset(
  {
    "suspected",
    "confirmed",
    "mitigated",
    "accepted",
    "expired",
  }
)

BACKLOG_STATUSES: dict[str, frozenset[str]] = {
  "issue": ISSUE_STATUSES,
  "problem": PROBLEM_STATUSES,
  "improvement": IMPROVEMENT_STATUSES,
  "risk": RISK_STATUSES,
}

# Statuses excluded from default list views.
# Matches current list_backlog() hardcoded exclusion — no behaviour change.
DEFAULT_HIDDEN_STATUSES: frozenset[str] = frozenset(
  {
    "resolved",
    "implemented",
  }
)

ALL_VALID_STATUSES: frozenset[str] = frozenset().union(*BACKLOG_STATUSES.values())


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
