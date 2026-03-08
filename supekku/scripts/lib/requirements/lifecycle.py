"""Requirement lifecycle status constants and definitions."""

from __future__ import annotations

RequirementStatus = str

STATUS_PENDING: RequirementStatus = "pending"
STATUS_IN_PROGRESS: RequirementStatus = "in-progress"
STATUS_ACTIVE: RequirementStatus = "active"
STATUS_RETIRED: RequirementStatus = "retired"
STATUS_DEPRECATED: RequirementStatus = "deprecated"
STATUS_SUPERSEDED: RequirementStatus = "superseded"

VALID_STATUSES: set[RequirementStatus] = {
  STATUS_PENDING,
  STATUS_IN_PROGRESS,
  STATUS_ACTIVE,
  STATUS_RETIRED,
  STATUS_DEPRECATED,
  STATUS_SUPERSEDED,
}

TERMINAL_STATUSES: set[RequirementStatus] = {
  STATUS_RETIRED,
  STATUS_DEPRECATED,
  STATUS_SUPERSEDED,
}

__all__ = [
  "STATUS_ACTIVE",
  "STATUS_DEPRECATED",
  "STATUS_IN_PROGRESS",
  "STATUS_PENDING",
  "STATUS_RETIRED",
  "STATUS_SUPERSEDED",
  "TERMINAL_STATUSES",
  "VALID_STATUSES",
  "RequirementStatus",
]
