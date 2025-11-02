"""Plan frontmatter metadata for kind: plan, phase, task artifacts.

This module defines the metadata schema for plan/phase/task frontmatter,
extending the base metadata with planning-specific fields. The same schema
is used for all three kinds (plan, phase, task).
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

PLAN_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.plan",
  description="Frontmatter fields for plans/phases/tasks (kind: plan|phase|task)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Plan-specific fields (all optional, shared across plan/phase/task)
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
      items=FieldMetadata(
        type="string", pattern=r".+", description="Exit criterion"
      ),
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
      "status": "active",
      "created": "2024-08-01",
      "updated": "2025-01-15",
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
