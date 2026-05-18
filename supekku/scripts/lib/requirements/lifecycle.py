"""Requirement lifecycle status constants and definitions.

OQ-137-02 sunset: ``REQUIREMENT_STATUSES`` is a transition-window
re-export derived from
``frontmatter_metadata/requirement.REQUIREMENT_STATUS_ENUM_VALUES``.
The named ``STATUS_*`` constants remain canonical for callers that need
individual references.
"""

from __future__ import annotations

from supekku.scripts.lib.core.frontmatter_metadata.requirement import (
  REQUIREMENT_FRONTMATTER_METADATA,
)

RequirementStatus = str

STATUS_PENDING: RequirementStatus = "pending"
STATUS_IN_PROGRESS: RequirementStatus = "in-progress"
STATUS_ACTIVE: RequirementStatus = "active"
STATUS_RETIRED: RequirementStatus = "retired"
STATUS_DEPRECATED: RequirementStatus = "deprecated"
STATUS_SUPERSEDED: RequirementStatus = "superseded"

# OQ-137-02 sunset: derived re-export.
REQUIREMENT_STATUSES: frozenset[RequirementStatus] = frozenset(
  REQUIREMENT_FRONTMATTER_METADATA.fields["status"].enum_values or []
)

TERMINAL_STATUSES: frozenset[RequirementStatus] = frozenset(
  {
    STATUS_RETIRED,
    STATUS_DEPRECATED,
    STATUS_SUPERSEDED,
  }
)

__all__ = [
  "STATUS_ACTIVE",
  "STATUS_DEPRECATED",
  "STATUS_IN_PROGRESS",
  "STATUS_PENDING",
  "STATUS_RETIRED",
  "STATUS_SUPERSEDED",
  "TERMINAL_STATUSES",
  "REQUIREMENT_STATUSES",
  "RequirementStatus",
]
