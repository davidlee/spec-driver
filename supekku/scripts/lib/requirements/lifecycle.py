"""Requirement lifecycle status constants and definitions."""

from __future__ import annotations

RequirementStatus = str

STATUS_PENDING: RequirementStatus = "pending"
STATUS_IN_PROGRESS: RequirementStatus = "in-progress"
STATUS_ACTIVE: RequirementStatus = "active"
STATUS_RETIRED: RequirementStatus = "retired"

VALID_STATUSES: set[RequirementStatus] = {
  STATUS_PENDING,
  STATUS_IN_PROGRESS,
  STATUS_ACTIVE,
  STATUS_RETIRED,
}

__all__ = [
  "STATUS_IN_PROGRESS",
  "STATUS_ACTIVE",
  "STATUS_PENDING",
  "STATUS_RETIRED",
  "VALID_STATUSES",
  "RequirementStatus",
]
