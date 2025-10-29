"""Requirement lifecycle status constants and definitions."""

from __future__ import annotations

RequirementStatus = str

STATUS_PENDING: RequirementStatus = "pending"
STATUS_IN_PROGRESS: RequirementStatus = "in-progress"
STATUS_LIVE: RequirementStatus = "live"
STATUS_RETIRED: RequirementStatus = "retired"

VALID_STATUSES: set[RequirementStatus] = {
    STATUS_PENDING,
    STATUS_IN_PROGRESS,
    STATUS_LIVE,
    STATUS_RETIRED,
}

__all__ = [
    "RequirementStatus",
    "STATUS_PENDING",
    "STATUS_IN_PROGRESS",
    "STATUS_LIVE",
    "STATUS_RETIRED",
    "VALID_STATUSES",
]
