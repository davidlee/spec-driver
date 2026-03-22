"""Review findings schema definition — supekku:workflow.review-findings@v2."""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
from supekku.scripts.lib.blocks.workflow_metadata import (
  ARTIFACT_KIND_VALUES,
  DISPOSITION_AUTHORITY_VALUES,
  FINDING_DISPOSITION_ACTION_VALUES,
  FINDING_STATUS_VALUES,
  REVIEW_FINDINGS_SCHEMA,
  REVIEW_FINDINGS_VERSION,
  REVIEW_STATUS_VALUES,
  ROLE_VALUES,
)


def _finding_disposition() -> FieldMetadata:
  """Disposition sub-schema for a review finding (DR-109 §3.4)."""
  return FieldMetadata(
    type="object",
    required=False,
    description="Finding disposition record",
    properties={
      "action": FieldMetadata(
        type="enum",
        required=True,
        enum_values=FINDING_DISPOSITION_ACTION_VALUES,
        description="Disposition action",
      ),
      "authority": FieldMetadata(
        type="enum",
        required=True,
        enum_values=DISPOSITION_AUTHORITY_VALUES,
        description="Who made the disposition decision",
      ),
      "actor_id": FieldMetadata(
        type="string",
        required=False,
        description="Specific identity when needed",
      ),
      "rationale": FieldMetadata(
        type="string",
        required=False,
        description="Required for waive, defer",
      ),
      "backlog_ref": FieldMetadata(
        type="string",
        required=False,
        description="Backlog item ref (e.g. ISSUE-045), when action=defer",
      ),
      "resolved_at": FieldMetadata(
        type="string",
        required=False,
        description="Git sha, when action=fix",
      ),
      "superseded_by": FieldMetadata(
        type="string",
        required=False,
        description="Finding ID, when action=supersede",
      ),
      "timestamp": FieldMetadata(
        type="string",
        required=False,
        description="ISO 8601 timestamp",
      ),
    },
  )


def _finding_item() -> FieldMetadata:
  """Single review finding record (DR-109 §3.4)."""
  return FieldMetadata(
    type="object",
    description="Review finding",
    properties={
      "id": FieldMetadata(
        type="string",
        required=True,
        description="Finding ID (e.g., R3-001), unique across all lists",
      ),
      "title": FieldMetadata(
        type="string",
        required=True,
        description="Short title",
      ),
      "summary": FieldMetadata(
        type="string",
        required=False,
        description=(
          "Finding summary (required for open/superseded, optional for resolved/waived)"
        ),
      ),
      "status": FieldMetadata(
        type="enum",
        required=True,
        enum_values=FINDING_STATUS_VALUES,
        description="Finding status (derived from disposition)",
      ),
      "disposition": _finding_disposition(),
      "files": FieldMetadata(
        type="array",
        required=False,
        description="Related file paths",
        items=FieldMetadata(type="string", description="File path"),
      ),
      "related_invariants": FieldMetadata(
        type="array",
        required=False,
        description="Related invariant IDs",
        items=FieldMetadata(type="string", description="Invariant ID"),
      ),
      "resolution_summary": FieldMetadata(
        type="string",
        required=False,
        description="How finding was resolved",
      ),
    },
  )


def _findings_list(*, required: bool = False) -> FieldMetadata:
  """List of finding records."""
  return FieldMetadata(
    type="array",
    required=required,
    description="List of review findings",
    items=_finding_item(),
  )


def _round_entry() -> FieldMetadata:
  """Single round entry in the accumulative rounds array (DR-109 §3.5)."""
  return FieldMetadata(
    type="object",
    description="Review round entry",
    properties={
      "round": FieldMetadata(
        type="int",
        required=True,
        description="Round number (monotonically increasing)",
      ),
      "status": FieldMetadata(
        type="enum",
        required=True,
        enum_values=REVIEW_STATUS_VALUES,
        description="Round outcome status",
      ),
      "reviewer_role": FieldMetadata(
        type="enum",
        required=False,
        enum_values=ROLE_VALUES,
        description="Role performing the review",
      ),
      "completed_at": FieldMetadata(
        type="string",
        required=False,
        description="Round completion timestamp (ISO 8601)",
      ),
      "summary": FieldMetadata(
        type="string",
        required=False,
        description="Round summary (free-text)",
      ),
      # session: opaque dict, autobahn-owned (DR-109 §3.6).
      # Not validated by schema — passes through unvalidated.
      "blocking": _findings_list(),
      "non_blocking": _findings_list(),
    },
  )


REVIEW_FINDINGS_METADATA = BlockMetadata(
  version=REVIEW_FINDINGS_VERSION,
  schema_id=REVIEW_FINDINGS_SCHEMA,
  description="Accumulative issue ledger across review rounds (v2)",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=REVIEW_FINDINGS_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{REVIEW_FINDINGS_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=REVIEW_FINDINGS_VERSION,
      required=True,
      description=f"Schema version (must be {REVIEW_FINDINGS_VERSION})",
    ),
    "artifact": FieldMetadata(
      type="object",
      required=True,
      description="Artifact identification",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Entity ID",
        ),
        "kind": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ARTIFACT_KIND_VALUES,
          description="Artifact kind",
        ),
      },
    ),
    "review": FieldMetadata(
      type="object",
      required=True,
      description="Review state",
      properties={
        "current_round": FieldMetadata(
          type="int",
          required=True,
          description="Latest round number",
        ),
      },
    ),
    "rounds": FieldMetadata(
      type="array",
      required=True,
      min_items=1,
      description="Accumulative round entries (DR-109 §3.5)",
      items=_round_entry(),
    ),
  },
  examples=[
    {
      "schema": REVIEW_FINDINGS_SCHEMA,
      "version": REVIEW_FINDINGS_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "review": {"current_round": 1},
      "rounds": [
        {
          "round": 1,
          "status": "changes_requested",
          "reviewer_role": "reviewer",
          "completed_at": "2026-03-20T16:00:00+00:00",
          "blocking": [
            {
              "id": "R1-001",
              "title": "Missing error handling in schema lookup",
              "summary": "Fallback path does not log the block type that failed.",
              "status": "open",
              "files": ["supekku/cli/schema.py"],
            },
          ],
          "non_blocking": [
            {
              "id": "R1-002",
              "title": "Typo in description field",
              "summary": "Minor typo.",
              "status": "resolved",
              "disposition": {
                "action": "fix",
                "authority": "author",
                "resolved_at": "def5678",
                "timestamp": "2026-03-20T17:00:00+00:00",
              },
            },
          ],
        },
      ],
    }
  ],
)
