"""Metadata definition for phase tracking blocks.

This module defines the metadata schema for phase.tracking@v1 blocks,
enabling metadata-driven validation and JSON Schema generation.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

# Reuse constants from plan.py
from .plan import (
  TRACKING_SCHEMA,
  TRACKING_VERSION,
)

# Metadata definition for phase tracking blocks
PHASE_TRACKING_METADATA = BlockMetadata(
  version=TRACKING_VERSION,
  schema_id=TRACKING_SCHEMA,
  description=(
    "Structured progress tracking for phases with tasks, criteria, and file paths"
  ),
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=TRACKING_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{TRACKING_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=TRACKING_VERSION,
      required=True,
      description=f"Schema version (must be {TRACKING_VERSION})",
    ),
    "phase": FieldMetadata(
      type="string",
      required=True,
      description="Phase ID (e.g., IP-001.PHASE-01)",
    ),
    "status": FieldMetadata(
      type="string",
      required=False,
      description="Phase lifecycle status (planned, in_progress, completed, blocked)",
    ),
    "started": FieldMetadata(
      type="string",
      required=False,
      description="ISO date when work on this phase started",
    ),
    "completed": FieldMetadata(
      type="string",
      required=False,
      description="ISO date when phase work completed",
    ),
    "last_updated": FieldMetadata(
      type="string",
      required=False,
      description="ISO date of most recent update",
    ),
    "tasks_completed": FieldMetadata(
      type="int",
      required=False,
      description="Number of tasks completed",
    ),
    "tasks_total": FieldMetadata(
      type="int",
      required=False,
      description="Total number of tasks",
    ),
    "tasks_done": FieldMetadata(
      type="int",
      required=False,
      description="Number of tasks marked done (legacy alias for tasks_completed)",
    ),
    "tasks_blocked": FieldMetadata(
      type="int",
      required=False,
      description="Number of tasks currently blocked",
    ),
    "notes": FieldMetadata(
      type="string",
      required=False,
      description="Free-text notes for the phase as a whole",
    ),
    "progress": FieldMetadata(
      type="array",
      required=False,
      description="Timestamped progress log entries",
      items=FieldMetadata(
        type="object",
        description="Progress entry",
        properties={
          "timestamp": FieldMetadata(
            type="string",
            required=False,
            description="ISO timestamp for the entry",
          ),
          "task": FieldMetadata(
            type="string",
            required=False,
            description="Task ID this entry refers to",
          ),
          "status": FieldMetadata(
            type="string",
            required=False,
            description="Status at this point in time",
          ),
          "note": FieldMetadata(
            type="string",
            required=False,
            description="Free-text note for this progress entry (singular form)",
          ),
          "notes": FieldMetadata(
            type="string",
            required=False,
            description="Free-text note for this progress entry (plural-form alias)",
          ),
        },
      ),
    ),
    "files": FieldMetadata(
      type="object",
      required=False,
      description="Phase-level file paths",
      properties={
        "references": FieldMetadata(
          type="array",
          required=False,
          description="Files referenced but not modified",
          items=FieldMetadata(type="string", description="File path or glob"),
        ),
        "context": FieldMetadata(
          type="array",
          required=False,
          description="Files providing context (can use globs)",
          items=FieldMetadata(type="string", description="File path or glob"),
        ),
      },
    ),
    "entrance_criteria": FieldMetadata(
      type="array",
      required=False,
      description="Entrance criteria with completion status",
      items=FieldMetadata(
        type="object",
        description="Criterion item",
        properties={
          "item": FieldMetadata(
            type="string",
            required=True,
            description="Criterion description",
          ),
          "completed": FieldMetadata(
            type="bool",
            required=True,
            description="Whether criterion is satisfied",
          ),
          "notes": FieldMetadata(
            type="string",
            required=False,
            description="Free-text notes for this criterion",
          ),
        },
      ),
    ),
    "exit_criteria": FieldMetadata(
      type="array",
      required=False,
      description="Exit criteria with completion status",
      items=FieldMetadata(
        type="object",
        description="Criterion item",
        properties={
          "item": FieldMetadata(
            type="string",
            required=True,
            description="Criterion description",
          ),
          "completed": FieldMetadata(
            type="bool",
            required=True,
            description="Whether criterion is satisfied",
          ),
          "notes": FieldMetadata(
            type="string",
            required=False,
            description="Free-text notes for this criterion",
          ),
        },
      ),
    ),
    "tasks": FieldMetadata(
      type="array",
      required=False,
      description="Task list with status and file tracking",
      items=FieldMetadata(
        type="object",
        description="Task item",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Task ID (e.g., '6.1', 'setup')",
          ),
          "description": FieldMetadata(
            type="string",
            required=True,
            description="Task description",
          ),
          "status": FieldMetadata(
            type="enum",
            enum_values=["pending", "in_progress", "completed", "blocked"],
            required=True,
            description="Task status",
          ),
          "notes": FieldMetadata(
            type="string",
            required=False,
            description="Free-text notes for this task",
          ),
          "files": FieldMetadata(
            type="object",
            required=False,
            description="Files affected by this task",
            properties={
              "added": FieldMetadata(
                type="array",
                required=False,
                description="Files added by this task",
                items=FieldMetadata(type="string", description="File path"),
              ),
              "modified": FieldMetadata(
                type="array",
                required=False,
                description="Files modified by this task",
                items=FieldMetadata(type="string", description="File path"),
              ),
              "removed": FieldMetadata(
                type="array",
                required=False,
                description="Files removed by this task",
                items=FieldMetadata(type="string", description="File path"),
              ),
              "tests": FieldMetadata(
                type="array",
                required=False,
                description="Test files for this task",
                items=FieldMetadata(type="string", description="File path"),
              ),
              "references": FieldMetadata(
                type="array",
                required=False,
                description="Files referenced for context",
                items=FieldMetadata(type="string", description="File path"),
              ),
            },
          ),
        },
      ),
    ),
  },
  examples=[
    {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-06",
      "files": {
        "references": [
          "supekku/scripts/lib/blocks/schema_registry.py",
          "supekku/scripts/lib/blocks/plan.py",
        ],
        "context": [
          "change/deltas/DE-004-*/phases/phase-05.md",
        ],
      },
      "entrance_criteria": [
        {"item": "Phases 01, 04, 05 complete", "completed": True},
        {"item": "All VT-PHASE tests passing", "completed": True},
        {"item": "phase.overview schema registered", "completed": True},
      ],
      "exit_criteria": [
        {"item": "phase.tracking JSON schema created", "completed": False},
        {"item": "schema show phase.tracking works", "completed": False},
        {"item": "VA-PHASE-001 executed", "completed": False},
        {"item": "VA-PHASE-002 executed", "completed": False},
      ],
      "tasks": [
        {
          "id": "6.7",
          "description": "Add JSON schema for phase.tracking@v1",
          "status": "in_progress",
          "files": {
            "added": [
              "supekku/scripts/lib/blocks/tracking_metadata.py",
            ],
            "modified": [
              "supekku/scripts/lib/blocks/__init__.py",
            ],
            "tests": [
              "supekku/scripts/lib/blocks/tracking_metadata_test.py",
            ],
          },
        },
        {
          "id": "6.8",
          "description": "Execute VA-PHASE-001 and VA-PHASE-002",
          "status": "pending",
        },
      ],
    }
  ],
)

__all__ = [
  "PHASE_TRACKING_METADATA",
]
