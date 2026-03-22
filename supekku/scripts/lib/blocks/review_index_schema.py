"""Review index schema definition — supekku:workflow.review-index@v1."""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
from supekku.scripts.lib.blocks.workflow_metadata import (
  ARTIFACT_KIND_VALUES,
  BOOTSTRAP_STATUS_VALUES,
  REVIEW_INDEX_SCHEMA,
  REVIEW_INDEX_VERSION,
  REVIEW_SESSION_SCOPE_VALUES,
  REVIEW_STATUS_VALUES,
)

REVIEW_INDEX_METADATA = BlockMetadata(
  version=REVIEW_INDEX_VERSION,
  schema_id=REVIEW_INDEX_SCHEMA,
  description="Reviewer bootstrap cache for amortizing review setup cost",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=REVIEW_INDEX_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{REVIEW_INDEX_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=REVIEW_INDEX_VERSION,
      required=True,
      description=f"Schema version (must be {REVIEW_INDEX_VERSION})",
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
      description="Review session state",
      properties={
        "session_scope": FieldMetadata(
          type="enum",
          required=False,
          enum_values=REVIEW_SESSION_SCOPE_VALUES,
          description="Review session scope",
        ),
        "bootstrap_status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=BOOTSTRAP_STATUS_VALUES,
          description="Bootstrap cache status",
        ),
        "last_bootstrapped_at": FieldMetadata(
          type="string",
          required=True,
          description="Last bootstrap timestamp (ISO 8601)",
        ),
        "judgment_status": FieldMetadata(
          type="enum",
          required=False,
          enum_values=REVIEW_STATUS_VALUES,
          description="Review judgment status (DR-109 §3.3)",
        ),
        "source_handoff": FieldMetadata(
          type="string",
          required=False,
          description="Path to source handoff file",
        ),
      },
    ),
    "domain_map": FieldMetadata(
      type="array",
      required=True,
      min_items=1,
      description="Domain areas the reviewer has learned",
      items=FieldMetadata(
        type="object",
        description="Domain area entry",
        properties={
          "area": FieldMetadata(
            type="string",
            required=True,
            description="Area name (unique within domain_map)",
          ),
          "purpose": FieldMetadata(
            type="string",
            required=True,
            description="Area purpose",
          ),
          "files": FieldMetadata(
            type="array",
            required=True,
            min_items=1,
            description="Files in this area",
            items=FieldMetadata(type="string", description="File path"),
          ),
        },
      ),
    ),
    "invariants": FieldMetadata(
      type="array",
      required=False,
      description="Known invariants to protect during review",
      items=FieldMetadata(
        type="object",
        description="Invariant",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Invariant ID (unique within invariants)",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            description="Invariant summary",
          ),
        },
      ),
    ),
    "risk_areas": FieldMetadata(
      type="array",
      required=False,
      description="Identified risk areas",
      items=FieldMetadata(
        type="object",
        description="Risk area",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Risk area ID (unique within risk_areas)",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            description="Risk description",
          ),
          "files": FieldMetadata(
            type="array",
            required=False,
            description="Related files",
            items=FieldMetadata(type="string", description="File path"),
          ),
        },
      ),
    ),
    "review_focus": FieldMetadata(
      type="array",
      required=False,
      description="Areas to focus review effort",
      items=FieldMetadata(type="string", description="Focus area"),
    ),
    "known_decisions": FieldMetadata(
      type="array",
      required=False,
      description="Decisions the reviewer should be aware of",
      items=FieldMetadata(
        type="object",
        description="Known decision",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Decision ID (unique within known_decisions)",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            description="Decision summary",
          ),
        },
      ),
    ),
    "staleness": FieldMetadata(
      type="object",
      required=True,
      description="Cache staleness tracking",
      properties={
        "cache_key": FieldMetadata(
          type="object",
          required=True,
          description="Cache key for staleness detection",
          properties={
            "phase_id": FieldMetadata(
              type="string",
              required=True,
              description="Phase ID at cache time",
            ),
            "head": FieldMetadata(
              type="string",
              required=True,
              description="Git HEAD at cache time",
            ),
          },
        ),
        "invalidation_triggers": FieldMetadata(
          type="array",
          required=False,
          description="Events that would invalidate the cache",
          items=FieldMetadata(type="string", description="Trigger description"),
        ),
      },
    ),
  },
  examples=[
    {
      "schema": REVIEW_INDEX_SCHEMA,
      "version": REVIEW_INDEX_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "review": {
        "bootstrap_status": "warm",
        "last_bootstrapped_at": "2026-03-20T14:00:00+00:00",
        "judgment_status": "pending",
        "source_handoff": "workflow/handoff.current.yaml",
      },
      "domain_map": [
        {
          "area": "CLI show commands",
          "purpose": "Render artifact details to terminal",
          "files": ["supekku/cli/show.py", "supekku/cli/schema.py"],
        },
      ],
      "invariants": [
        {
          "id": "INV-001",
          "summary": "show schema output must be valid JSON Schema Draft 2020-12",
        },
      ],
      "risk_areas": [
        {
          "id": "RA-001",
          "summary": "Hardcoded metadata lookup may miss new block types",
          "files": ["supekku/cli/schema.py"],
        },
      ],
      "review_focus": ["Schema completeness", "Example validity"],
      "known_decisions": [
        {"id": "DEC-110-001", "summary": "Attach metadata to BlockSchema"},
      ],
      "staleness": {
        "cache_key": {"phase_id": "IP-090.PHASE-01", "head": "abc1234"},
        "invalidation_triggers": ["New phase started", "DR revised"],
      },
    }
  ],
)
