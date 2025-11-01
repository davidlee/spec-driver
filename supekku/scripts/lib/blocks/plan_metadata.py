"""Metadata definitions for plan and phase overview blocks.

This module defines the metadata schemas for plan and phase overview blocks,
enabling metadata-driven validation and JSON Schema generation.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

# Reuse constants from plan.py
from .plan import (
  PHASE_SCHEMA,
  PHASE_VERSION,
  PLAN_SCHEMA,
  PLAN_VERSION,
)

# Metadata definition for plan overview blocks
PLAN_OVERVIEW_METADATA = BlockMetadata(
  version=PLAN_VERSION,
  schema_id=PLAN_SCHEMA,
  description="Defines implementation plan with phases, specs, and requirements",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=PLAN_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{PLAN_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=PLAN_VERSION,
      required=True,
      description=f"Schema version (must be {PLAN_VERSION})",
    ),
    "plan": FieldMetadata(
      type="string",
      required=True,
      description="Plan ID (e.g., PLN-001)",
    ),
    "delta": FieldMetadata(
      type="string",
      required=True,
      description="Delta ID this plan implements (e.g., DE-001)",
    ),
    "revision_links": FieldMetadata(
      type="object",
      required=False,
      description="Links to related revisions",
      properties={
        "aligns_with": FieldMetadata(
          type="array",
          required=False,
          description="Revision IDs this plan aligns with",
          items=FieldMetadata(type="string", description="Revision ID"),
        ),
      },
    ),
    "specs": FieldMetadata(
      type="object",
      required=False,
      description="Specifications related to this plan",
      properties={
        "primary": FieldMetadata(
          type="array",
          required=False,
          description="Primary specification IDs",
          items=FieldMetadata(type="string", description="Spec ID"),
        ),
        "collaborators": FieldMetadata(
          type="array",
          required=False,
          description="Collaborator specification IDs",
          items=FieldMetadata(type="string", description="Spec ID"),
        ),
      },
    ),
    "requirements": FieldMetadata(
      type="object",
      required=False,
      description="Requirements related to this plan",
      properties={
        "targets": FieldMetadata(
          type="array",
          required=False,
          description="Requirement IDs targeted by this plan",
          items=FieldMetadata(type="string", description="Requirement ID"),
        ),
        "dependencies": FieldMetadata(
          type="array",
          required=False,
          description="Requirement IDs this plan depends on",
          items=FieldMetadata(type="string", description="Requirement ID"),
        ),
      },
    ),
    "phases": FieldMetadata(
      type="array",
      required=True,
      min_items=1,
      description="Implementation phases for this plan",
      items=FieldMetadata(
        type="object",
        description="A single phase entry",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Phase ID (e.g., PLN-001-P01)",
          ),
          "name": FieldMetadata(
            type="string",
            required=False,
            description="Phase name",
          ),
          "objective": FieldMetadata(
            type="string",
            required=False,
            description="Phase objective statement",
          ),
          "entrance_criteria": FieldMetadata(
            type="array",
            required=False,
            description="Criteria that must be met before starting phase",
            items=FieldMetadata(type="string", description="Criterion"),
          ),
          "exit_criteria": FieldMetadata(
            type="array",
            required=False,
            description="Criteria that must be met to complete phase",
            items=FieldMetadata(type="string", description="Criterion"),
          ),
        },
      ),
    ),
  },
  examples=[
    {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "revision_links": {
        "aligns_with": ["RE-001"],
      },
      "specs": {
        "primary": ["SPEC-100"],
        "collaborators": ["SPEC-200"],
      },
      "requirements": {
        "targets": ["SPEC-100.FR-001", "SPEC-100.FR-002"],
        "dependencies": ["SPEC-200.FR-005"],
      },
      "phases": [
        {
          "id": "PLN-001-P01",
          "name": "Phase 01 - Initial delivery",
          "objective": "Deliver the foundational work for this delta.",
          "entrance_criteria": [],
          "exit_criteria": [],
        }
      ],
    }
  ],
)

# Metadata definition for phase overview blocks
PHASE_OVERVIEW_METADATA = BlockMetadata(
  version=PHASE_VERSION,
  schema_id=PHASE_SCHEMA,
  description="Defines a phase within a plan with objectives, criteria, and tasks",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=PHASE_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{PHASE_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=PHASE_VERSION,
      required=True,
      description=f"Schema version (must be {PHASE_VERSION})",
    ),
    "phase": FieldMetadata(
      type="string",
      required=True,
      description="Phase ID (e.g., PLN-001-P01)",
    ),
    "plan": FieldMetadata(
      type="string",
      required=True,
      description="Plan ID this phase belongs to (e.g., PLN-001)",
    ),
    "delta": FieldMetadata(
      type="string",
      required=True,
      description="Delta ID this phase implements (e.g., DE-001)",
    ),
    "objective": FieldMetadata(
      type="string",
      required=False,
      description="Phase objective statement",
    ),
    "entrance_criteria": FieldMetadata(
      type="array",
      required=False,
      description="Criteria that must be met before starting phase",
      items=FieldMetadata(type="string", description="Criterion"),
    ),
    "exit_criteria": FieldMetadata(
      type="array",
      required=False,
      description="Criteria that must be met to complete phase",
      items=FieldMetadata(type="string", description="Criterion"),
    ),
    "verification": FieldMetadata(
      type="object",
      required=False,
      description="Verification artifacts for this phase",
      properties={
        "tests": FieldMetadata(
          type="array",
          required=False,
          description="Test IDs for verification",
          items=FieldMetadata(type="string", description="Test ID"),
        ),
        "evidence": FieldMetadata(
          type="array",
          required=False,
          description="Evidence items for verification",
          items=FieldMetadata(type="string", description="Evidence item"),
        ),
      },
    ),
    "tasks": FieldMetadata(
      type="array",
      required=False,
      description="Task descriptions for this phase",
      items=FieldMetadata(type="string", description="Task"),
    ),
    "risks": FieldMetadata(
      type="array",
      required=False,
      description="Risk descriptions for this phase",
      items=FieldMetadata(type="string", description="Risk"),
    ),
  },
  examples=[
    {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "objective": "Describe the outcome for this phase.",
      "entrance_criteria": [],
      "exit_criteria": [],
      "verification": {
        "tests": ["VT-001"],
        "evidence": ["Documentation updated"],
      },
      "tasks": [],
      "risks": [],
    }
  ],
)

__all__ = [
  "PHASE_OVERVIEW_METADATA",
  "PLAN_OVERVIEW_METADATA",
]
