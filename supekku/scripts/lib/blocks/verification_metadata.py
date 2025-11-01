"""Metadata definition for verification coverage blocks.

This module defines the metadata schema for verification coverage blocks,
enabling metadata-driven validation and JSON Schema generation.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

# Reuse constants from verification.py
from .verification import (
  COVERAGE_SCHEMA,
  COVERAGE_VERSION,
  VALID_KINDS,
  VALID_STATUSES,
)

# Regex patterns for validation
VERIFICATION_ID_PATTERN = r"^V[TAH]-\d{3,}$"
SUBJECT_ID_PATTERN = r"^(SPEC|PROD|IP|AUD)-\d{3,}(?:-[A-Z0-9]+)*$"
REQUIREMENT_ID_PATTERN = r"^(SPEC|PROD)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$"
PHASE_ID_PATTERN = r"^IP-\d{3,}(?:-[A-Z0-9]+)*\.PHASE-\d{2}$"

# Metadata definition for verification coverage blocks
VERIFICATION_COVERAGE_METADATA = BlockMetadata(
  version=COVERAGE_VERSION,
  schema_id=COVERAGE_SCHEMA,
  description=(
    "Tracks verification artifacts (tests, analyses, histories) for requirements"
  ),
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=COVERAGE_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{COVERAGE_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=COVERAGE_VERSION,
      required=True,
      description=f"Schema version (must be {COVERAGE_VERSION})",
    ),
    "subject": FieldMetadata(
      type="string",
      required=True,
      pattern=SUBJECT_ID_PATTERN,
      description="Subject ID being verified (SPEC, PROD, IP, or AUD artifact)",
    ),
    "entries": FieldMetadata(
      type="array",
      required=True,
      min_items=1,
      description="List of verification coverage entries",
      items=FieldMetadata(
        type="object",
        required=True,
        description="A single verification coverage entry",
        properties={
          "artefact": FieldMetadata(
            type="string",
            required=True,
            pattern=VERIFICATION_ID_PATTERN,
            description="Verification artifact ID (VT-###, VA-###, or VH-###)",
          ),
          "kind": FieldMetadata(
            type="enum",
            required=True,
            enum_values=sorted(VALID_KINDS),
            description="Verification artifact kind (VT=test, VA=analysis, VH=history)",
          ),
          "requirement": FieldMetadata(
            type="string",
            required=True,
            pattern=REQUIREMENT_ID_PATTERN,
            description="Requirement ID being verified (e.g., SPEC-100.FR-001)",
          ),
          "phase": FieldMetadata(
            type="string",
            required=False,
            pattern=PHASE_ID_PATTERN,
            description="Optional implementation phase (e.g., IP-001.PHASE-01)",
          ),
          "status": FieldMetadata(
            type="enum",
            required=True,
            enum_values=sorted(VALID_STATUSES),
            description="Verification status",
          ),
          "notes": FieldMetadata(
            type="string",
            required=False,
            description="Optional notes about verification",
          ),
        },
      ),
    ),
  },
  examples=[
    {
      "schema": COVERAGE_SCHEMA,
      "version": COVERAGE_VERSION,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
          "notes": "Unit tests passing",
        },
        {
          "artefact": "VA-002",
          "kind": "VA",
          "requirement": "SPEC-100.NFR-PERF",
          "phase": "IP-001.PHASE-01",
          "status": "in-progress",
        },
      ],
    }
  ],
)

__all__ = [
  "VERIFICATION_COVERAGE_METADATA",
]
