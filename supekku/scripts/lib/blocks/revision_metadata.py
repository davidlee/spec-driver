"""Metadata definition for revision change blocks.

This module defines the metadata schema for revision change blocks,
enabling metadata-driven validation and JSON Schema generation.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

# Import lifecycle statuses for requirement validation
from supekku.scripts.lib.requirements.lifecycle import (
  VALID_STATUSES as REQUIREMENT_VALID_STATUSES,
)

# Reuse constants from revision.py
from .revision import (
  REVISION_BLOCK_SCHEMA_ID,
  REVISION_BLOCK_VERSION,
)

# Metadata definition for revision change blocks
REVISION_CHANGE_METADATA = BlockMetadata(
  version=REVISION_BLOCK_VERSION,
  schema_id=REVISION_BLOCK_SCHEMA_ID,
  description="Documents changes to specs and requirements in a revision",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=REVISION_BLOCK_SCHEMA_ID,
      required=True,
      description=f"Schema identifier (must be '{REVISION_BLOCK_SCHEMA_ID}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=REVISION_BLOCK_VERSION,
      required=True,
      description=f"Schema version (must be {REVISION_BLOCK_VERSION})",
    ),
    "metadata": FieldMetadata(
      type="object",
      required=True,
      description="Revision metadata including ID and generation details",
      properties={
        "revision": FieldMetadata(
          type="string",
          required=True,
          pattern=r"^RE-\d{3,}$",
          description="Revision ID (e.g., RE-001)",
        ),
        "prepared_by": FieldMetadata(
          type="string",
          required=False,
          description="Who or what prepared this revision",
        ),
        "generated_at": FieldMetadata(
          type="string",
          required=False,
          description="When this revision was generated",
        ),
      },
    ),
    "specs": FieldMetadata(
      type="array",
      required=True,
      description="Specification changes in this revision",
      items=FieldMetadata(
        type="object",
        description="A single spec change entry",
        properties={
          "spec_id": FieldMetadata(
            type="string",
            required=True,
            pattern=r"^SPEC-\d{3}(?:-[A-Z0-9]+)*$",
            description="Specification ID (e.g., SPEC-100)",
          ),
          "action": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["created", "retired", "updated"],
            description="Action performed on the spec",
          ),
          "summary": FieldMetadata(
            type="string",
            required=False,
            description="Summary of changes to this spec",
          ),
          "requirement_flow": FieldMetadata(
            type="object",
            required=False,
            description="Requirement flow changes for this spec",
            properties={
              "added": FieldMetadata(
                type="array",
                required=False,
                description="Requirements added to this spec",
                items=FieldMetadata(
                  type="string",
                  pattern=r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$",
                  description="Requirement ID",
                ),
              ),
              "removed": FieldMetadata(
                type="array",
                required=False,
                description="Requirements removed from this spec",
                items=FieldMetadata(
                  type="string",
                  pattern=r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$",
                  description="Requirement ID",
                ),
              ),
              "moved_in": FieldMetadata(
                type="array",
                required=False,
                description="Requirements moved into this spec",
                items=FieldMetadata(
                  type="string",
                  pattern=r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$",
                  description="Requirement ID",
                ),
              ),
              "moved_out": FieldMetadata(
                type="array",
                required=False,
                description="Requirements moved out of this spec",
                items=FieldMetadata(
                  type="string",
                  pattern=r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$",
                  description="Requirement ID",
                ),
              ),
            },
          ),
          "section_changes": FieldMetadata(
            type="array",
            required=False,
            description="Section-level changes in this spec",
            items=FieldMetadata(
              type="object",
              description="A single section change",
              properties={
                "section": FieldMetadata(
                  type="string",
                  required=True,
                  description="Section name or identifier",
                ),
                "change": FieldMetadata(
                  type="enum",
                  required=True,
                  enum_values=["added", "modified", "removed", "renamed"],
                  description="Type of change to the section",
                ),
                "before_path": FieldMetadata(
                  type="string",
                  required=False,
                  description="Path before the change",
                ),
                "after_path": FieldMetadata(
                  type="string",
                  required=False,
                  description="Path after the change",
                ),
                "notes": FieldMetadata(
                  type="string",
                  required=False,
                  description="Additional notes about the change",
                ),
              },
            ),
          ),
        },
      ),
    ),
    "requirements": FieldMetadata(
      type="array",
      required=True,
      description="Requirement changes in this revision",
      items=FieldMetadata(
        type="object",
        description="A single requirement change entry",
        properties={
          "requirement_id": FieldMetadata(
            type="string",
            required=True,
            pattern=r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$",
            description="Requirement ID (e.g., SPEC-100.FR-001)",
          ),
          "kind": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["functional", "non-functional"],
            description="Type of requirement",
          ),
          "action": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["introduce", "modify", "move", "retire"],
            description="Action performed on the requirement",
          ),
          "summary": FieldMetadata(
            type="string",
            required=False,
            description="Summary of changes to this requirement",
          ),
          "origin": FieldMetadata(
            type="array",
            required=False,
            description=(
              "Origin sources for this requirement "
              "(conditionally required when action is 'move')"
            ),
            items=FieldMetadata(
              type="object",
              description="A single origin source",
              properties={
                "kind": FieldMetadata(
                  type="enum",
                  required=True,
                  enum_values=["backlog", "external", "requirement", "spec"],
                  description="Type of origin source",
                ),
                "ref": FieldMetadata(
                  type="string",
                  required=True,
                  description=(
                    "Reference ID "
                    "(pattern depends on kind, see validator for details)"
                  ),
                ),
                "notes": FieldMetadata(
                  type="string",
                  required=False,
                  description="Additional notes about this origin",
                ),
              },
            ),
          ),
          "destination": FieldMetadata(
            type="object",
            required=False,
            description=(
              "Destination spec for this requirement "
              "(conditionally required when action is introduce/modify/move)"
            ),
            properties={
              "spec": FieldMetadata(
                type="string",
                required=True,
                pattern=r"^SPEC-\d{3}(?:-[A-Z0-9]+)*$",
                description="Target specification ID",
              ),
              "requirement_id": FieldMetadata(
                type="string",
                required=False,
                pattern=r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$",
                description="Target requirement ID",
              ),
              "path": FieldMetadata(
                type="string",
                required=False,
                description="Path within the specification",
              ),
              "additional_specs": FieldMetadata(
                type="array",
                required=False,
                description="Additional specifications affected",
                items=FieldMetadata(
                  type="string",
                  pattern=r"^SPEC-\d{3}(?:-[A-Z0-9]+)*$",
                  description="Specification ID",
                ),
              ),
            },
          ),
          "lifecycle": FieldMetadata(
            type="object",
            required=False,
            description="Lifecycle tracking for this requirement",
            properties={
              "status": FieldMetadata(
                type="enum",
                required=False,
                enum_values=sorted(REQUIREMENT_VALID_STATUSES),
                description="Current lifecycle status",
              ),
              "introduced_by": FieldMetadata(
                type="string",
                required=False,
                pattern=r"^RE-\d{3,}$",
                description="Revision ID that introduced this requirement",
              ),
              "implemented_by": FieldMetadata(
                type="array",
                required=False,
                description="Delta IDs that implement this requirement",
                items=FieldMetadata(
                  type="string",
                  pattern=r"^DE-\d{3,}$",
                  description="Delta ID",
                ),
              ),
              "verified_by": FieldMetadata(
                type="array",
                required=False,
                description="Audit IDs that verify this requirement",
                items=FieldMetadata(
                  type="string",
                  pattern=r"^AUD-\d{3,}$",
                  description="Audit ID",
                ),
              ),
            },
          ),
          "text_changes": FieldMetadata(
            type="object",
            required=False,
            description="Text-level changes for this requirement",
            properties={
              "before_excerpt": FieldMetadata(
                type="string",
                required=False,
                description="Text before the change",
              ),
              "after_excerpt": FieldMetadata(
                type="string",
                required=False,
                description="Text after the change",
              ),
              "diff_ref": FieldMetadata(
                type="string",
                required=False,
                description="Reference to a diff artifact",
              ),
            },
          ),
        },
      ),
    ),
  },
  examples=[
    {
      "schema": REVISION_BLOCK_SCHEMA_ID,
      "version": REVISION_BLOCK_VERSION,
      "metadata": {
        "revision": "RE-001",
        "prepared_by": "alice@example.com",
        "generated_at": "2025-01-15T10:00:00Z",
      },
      "specs": [
        {
          "spec_id": "SPEC-100",
          "action": "created",
          "summary": "Initial authentication specification",
          "requirement_flow": {
            "added": ["SPEC-100.FR-AUTH", "SPEC-100.NFR-SECURITY"],
          },
          "section_changes": [
            {
              "section": "Security Requirements",
              "change": "added",
              "notes": "Added comprehensive security section",
            }
          ],
        },
        {
          "spec_id": "SPEC-200",
          "action": "updated",
          "summary": "Enhanced user management spec",
          "requirement_flow": {
            "moved_in": ["SPEC-100.FR-USER-001"],
            "removed": ["SPEC-200.FR-DEPRECATED"],
          },
        },
      ],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-AUTH",
          "kind": "functional",
          "action": "introduce",
          "summary": "Implement OAuth2 authentication flow",
          "destination": {
            "spec": "SPEC-100",
            "path": "/security/authentication",
            "additional_specs": ["SPEC-200"],
          },
          "lifecycle": {
            "status": "pending",
            "introduced_by": "RE-001",
          },
        },
        {
          "requirement_id": "SPEC-100.FR-USER-001",
          "kind": "functional",
          "action": "move",
          "summary": "Move user profile requirement to auth spec",
          "origin": [
            {
              "kind": "spec",
              "ref": "SPEC-200",
              "notes": "Originally in user management spec",
            }
          ],
          "destination": {
            "spec": "SPEC-100",
            "requirement_id": "SPEC-100.FR-USER-001",
          },
          "lifecycle": {
            "status": "in-progress",
            "introduced_by": "RE-001",
            "implemented_by": ["DE-001"],
          },
          "text_changes": {
            "before_excerpt": "User shall have profile data",
            "after_excerpt": "Authenticated user shall have profile data",
            "diff_ref": "commit-abc123",
          },
        },
        {
          "requirement_id": "SPEC-100.NFR-SECURITY",
          "kind": "non-functional",
          "action": "introduce",
          "summary": "Security compliance requirement",
          "destination": {
            "spec": "SPEC-100",
          },
          "lifecycle": {
            "status": "live",
            "introduced_by": "RE-001",
            "implemented_by": ["DE-001", "DE-002"],
            "verified_by": ["AUD-001"],
          },
        },
      ],
    }
  ],
)

__all__ = [
  "REVISION_CHANGE_METADATA",
]
