"""Backlog item models and status vocabulary.

Per-kind status sets define accepted lifecycle values (DEC-057-02, DEC-057-08).
Validation is permissive: unknown values are warned, not rejected.

OQ-137-02 sunset: ``BACKLOG_BASE_STATUSES`` and ``RISK_STATUSES`` are
transition-window re-exports derived from
``frontmatter_metadata/issue.ISSUE_STATUS_ENUM_VALUES`` and
``frontmatter_metadata/risk.RISK_STATUS_ENUM_VALUES`` respectively.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from supekku.scripts.lib.core.frontmatter_metadata.issue import (
  ISSUE_FRONTMATTER_METADATA,
)
from supekku.scripts.lib.core.frontmatter_metadata.risk import (
  RISK_FRONTMATTER_METADATA,
)

logger = logging.getLogger(__name__)

# -- Unified backlog lifecycle statuses (DEC-075-05, supersedes DEC-057-02) --

# OQ-137-02 sunset: derived re-exports.
BACKLOG_BASE_STATUSES: frozenset[str] = frozenset(
  ISSUE_FRONTMATTER_METADATA.fields["status"].enum_values or []
)
RISK_STATUSES: frozenset[str] = frozenset(
  RISK_FRONTMATTER_METADATA.fields["status"].enum_values or []
)
RISK_EXTRA_STATUSES: frozenset[str] = RISK_STATUSES - BACKLOG_BASE_STATUSES

# Per-kind lookup — all non-risk kinds share the base set.
BACKLOG_STATUSES: dict[str, frozenset[str]] = {
  "issue": BACKLOG_BASE_STATUSES,
  "problem": BACKLOG_BASE_STATUSES,
  "improvement": BACKLOG_BASE_STATUSES,
  "risk": RISK_STATUSES,
}

# Statuses excluded from default list views.
DEFAULT_HIDDEN_STATUSES: frozenset[str] = frozenset(
  {
    "resolved",
  }
)

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


class BacklogItem(BaseModel):
  """Backlog item model representing issues, problems, improvements, and risks."""

  model_config = ConfigDict(extra="ignore")

  id: str = ""
  kind: str = ""  # issue, problem, improvement, risk
  status: str = ""
  title: str = ""
  path: Path = Path()
  frontmatter: dict[str, Any] = {}
  tags: list[str] = []
  # Kind-specific optional fields
  severity: str = ""
  categories: list[str] = []
  impact: str = ""
  likelihood: float = 0.0
  created: str = ""
  updated: str = ""
  ext_id: str = ""
  ext_url: str = ""

  def to_dict(self) -> dict[str, Any]:
    """Serialize to dict with consistent relational fields.

    Always includes ``linked_deltas`` and ``related_requirements`` with ``[]``
    defaults, ensuring JSON parity between ``list`` and ``show`` output.
    """
    data: dict[str, Any] = {
      "id": self.id,
      "kind": self.kind,
      "status": self.status,
      "title": self.title,
      "linked_deltas": self.frontmatter.get("linked_deltas", []) or [],
      "related_requirements": self.frontmatter.get("related_requirements", []) or [],
    }
    if self.tags:
      data["tags"] = self.tags
    if self.severity:
      data["severity"] = self.severity
    if self.categories:
      data["categories"] = self.categories
    if self.impact:
      data["impact"] = self.impact
    if self.likelihood:
      data["likelihood"] = self.likelihood
    if self.created:
      data["created"] = self.created
    if self.updated:
      data["updated"] = self.updated
    if self.ext_id:
      data["ext_id"] = self.ext_id
    if self.ext_url:
      data["ext_url"] = self.ext_url
    return data
