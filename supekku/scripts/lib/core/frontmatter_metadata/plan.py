"""Plan frontmatter metadata for kind: plan, phase, task artifacts.

This module defines the metadata schema for plan/phase/task frontmatter,
extending the base metadata with planning-specific fields. The same schema
is used for all three kinds (plan, phase, task).
"""

from __future__ import annotations

from dataclasses import replace

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA
from .delta import DELTA_STATUS_ENUM_VALUES

# Plan/phase/task statuses share the change-artefact enum (delta is canonical).
PLAN_STATUS_ENUM_VALUES: list[str] = DELTA_STATUS_ENUM_VALUES

# Plan/phase/task status field-VALUE aliases. DR-137 §5.2 matrix omits
# `complete -> completed` here; in practice the legacy kind-agnostic
# `normalize_status` aliased it for all change-artefact kinds, so DE-137
# keeps that compatibility to avoid loader regressions on corpus files
# carrying `status: complete`.
PLAN_STATUS_ALIASES: dict[str, str] = {
  "complete": "completed",
  "active": "in-progress",
  "done": "completed",
  "in_progress": "in-progress",
}

PLAN_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.plan",
  description="Frontmatter fields for plans/phases/tasks (kind: plan|phase|task)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # DE-137 IP-137-P01: status promoted to enum, with legacy aliases (F-30).
    "status": replace(
      BASE_FRONTMATTER_METADATA.fields["status"],
      type="enum",
      pattern=None,
      enum_values=PLAN_STATUS_ENUM_VALUES,
      aliases=PLAN_STATUS_ALIASES,
    ),
    # Plan-specific fields (all optional, shared across plan/phase/task)
    "plan": FieldMetadata(
      type="string",
      required=False,
      description="Owning plan ID (e.g. IP-107). Written by create_phase.",
    ),
    "delta": FieldMetadata(
      type="string",
      required=False,
      description="Owning delta ID (e.g. DE-107). Written by create_phase.",
    ),
    "objective": FieldMetadata(
      type="string",
      required=False,
      description="Qualitative goal for the plan or phase",
    ),
    "entrance_criteria": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Entrance criterion"
      ),
      description="Conditions that must be met before starting",
    ),
    "exit_criteria": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(type="string", pattern=r".+", description="Exit criterion"),
      description="Conditions that must be met to complete",
    ),
  },
  examples=[
    # Minimal plan (base fields only)
    {
      "id": "PLAN-001",
      "name": "Example Plan",
      "slug": "plan-example",
      "kind": "plan",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete plan with all fields
    {
      "id": "PLAN-042",
      "name": "Authentication Implementation Plan",
      "slug": "plan-auth-implementation",
      "kind": "plan",
      "status": "active",
      "lifecycle": "implementation",
      "created": "2024-08-01",
      "updated": "2025-01-15",
      "owners": ["auth-team"],
      "summary": "Plan for implementing OAuth2 authentication across the platform",
      "tags": ["auth", "implementation", "security"],
      "objective": (
        "Implement OAuth2 authentication with token refresh, "
        "meeting all functional and non-functional requirements"
      ),
      "entrance_criteria": [
        "SPEC-101 status == approved",
        "PROD-005 requirements finalized",
        "Test infrastructure available",
      ],
      "exit_criteria": [
        "VT-210 executed and passing",
        "All FR requirements implemented",
        "Security audit completed",
      ],
      "relations": [
        {"type": "implements", "target": "SPEC-101"},
        {"type": "tracked_by", "target": "ISSUE-234"},
      ],
    },
    # Phase example
    {
      "id": "PHASE-001",
      "name": "Authentication Phase 1",
      "slug": "phase-auth-1",
      "kind": "phase",
      "status": "in-progress",
      "created": "2024-08-01",
      "updated": "2025-01-15",
      "plan": "PLAN-042",
      "delta": "DE-042",
      "objective": "Implement core OAuth2 flows",
      "exit_criteria": ["Token generation working", "Refresh flow implemented"],
    },
    # Task example
    {
      "id": "TASK-001",
      "name": "Implement Token Refresh",
      "slug": "task-token-refresh",
      "kind": "task",
      "status": "in-progress",
      "created": "2024-08-15",
      "updated": "2025-01-15",
      "objective": "Implement automatic token refresh on expiration",
      "exit_criteria": ["VT-210 passing"],
    },
  ],
)

__all__ = [
  "PLAN_FRONTMATTER_METADATA",
]
