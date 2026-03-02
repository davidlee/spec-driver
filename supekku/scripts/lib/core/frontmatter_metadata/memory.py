"""Memory frontmatter metadata for kind: memory artifacts.

This module defines the metadata schema for memory frontmatter,
extending the base metadata with memory-specific fields for
deterministic retrieval, staleness tracking, and scope matching.

Field mapping from JAMMS v0.1 to spec-driver conventions:
  - JAMMS `type` → `memory_type` (avoids builtin collision)
  - JAMMS `title` → base `name`
  - JAMMS `time.created/updated` → base `created`/`updated`
  - JAMMS `time.verified/review_by` → `verified`/`review_by`
  - JAMMS `owner.contact` → base `owners`
  - JAMMS `policy.audience/visibility` → `audience`/`visibility`
  - JAMMS `relations.requires_reading` → `requires_reading`
  - JAMMS `relations.supersedes/superseded_by` → base `relations` array
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

MEMORY_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.memory",
  description="Frontmatter fields for memory records (kind: memory)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Memory-specific fields
    "memory_type": FieldMetadata(
      type="enum",
      required=True,
      enum_values=[
        "concept",
        "fact",
        "pattern",
        "signpost",
        "system",
        "thread",
      ],
      description="Memory record type for filtering and default cadences",
    ),
    "confidence": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["low", "medium", "high"],
      description="Confidence level in the record's accuracy",
    ),
    "verified": FieldMetadata(
      type="string",
      required=False,
      pattern=r"^\d{4}-\d{2}-\d{2}$",
      description=("ISO-8601 date of last verification against reality (YYYY-MM-DD)"),
    ),
    "review_by": FieldMetadata(
      type="string",
      required=False,
      pattern=r"^\d{4}-\d{2}-\d{2}$",
      description="ISO-8601 date for next required review (YYYY-MM-DD)",
    ),
    "requires_reading": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r".+",
        description="Path or artifact ID that must be read",
      ),
      description="Pre-reading artifacts required for scope/task/change",
    ),
    "scope": FieldMetadata(
      type="object",
      required=False,
      description="Context matching criteria for deterministic surfacing",
      properties={
        "globs": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="string",
            pattern=r".+",
            description="Glob pattern",
          ),
          description="Filesystem glob patterns for path matching",
        ),
        "paths": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="string",
            pattern=r".+",
            description="Exact path",
          ),
          description="Exact path matches (stronger than globs)",
        ),
        "commands": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="string",
            pattern=r".+",
            description="Command string",
          ),
          description="Command-oriented matching entries",
        ),
        "languages": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="string",
            pattern=r".+",
            description="Language tag",
          ),
          description="Programming language tags (e.g., py, ts, go)",
        ),
        "platforms": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="string",
            pattern=r".+",
            description="Platform tag",
          ),
          description="Platform tags (e.g., linux, mac)",
        ),
      },
    ),
    "priority": FieldMetadata(
      type="object",
      required=False,
      description="Ordering hints for hook surfacing",
      properties={
        "severity": FieldMetadata(
          type="enum",
          required=False,
          enum_values=["none", "low", "medium", "high", "critical"],
          description="Severity for hook ordering and filtering",
        ),
        "weight": FieldMetadata(
          type="int",
          required=False,
          description="Integer tie-breaker (higher = more prominent)",
        ),
      },
    ),
    "provenance": FieldMetadata(
      type="object",
      required=False,
      description="Source attribution for anti-drift tracking",
      properties={
        "sources": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="object",
            description="Source entry",
            properties={
              "kind": FieldMetadata(
                type="enum",
                required=False,
                enum_values=[
                  "adr",
                  "code",
                  "commit",
                  "design",
                  "doc",
                  "external",
                  "issue",
                  "pr",
                  "spec",
                ],
                description="Source kind",
              ),
              "ref": FieldMetadata(
                type="string",
                required=False,
                pattern=r".+",
                description="Relative path or URL",
              ),
              "note": FieldMetadata(
                type="string",
                required=False,
                description="Optional human note",
              ),
            },
          ),
          description="Provenance source entries",
        ),
      },
    ),
    "audience": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="enum",
        enum_values=["human", "agent"],
        description="Audience type",
      ),
      description="Intended audience (default: both)",
    ),
    "visibility": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="enum",
        enum_values=["pre", "on_demand"],
        description="Visibility mode",
      ),
      description="Surfacing mode: hook-driven (pre) or manual (on_demand)",
    ),
  },
  examples=[
    # Minimal memory (base fields + required memory_type)
    {
      "id": "MEM-001",
      "name": "Example Memory Record",
      "slug": "mem-example",
      "kind": "memory",
      "status": "active",
      "created": "2026-03-01",
      "updated": "2026-03-01",
      "memory_type": "fact",
    },
    # Complete memory with all fields
    {
      "id": "MEM-042",
      "name": "ADR-11 Required Pre-Reading for Auth Changes",
      "slug": "mem-adr11-required-for-auth",
      "kind": "memory",
      "status": "active",
      "lifecycle": "maintenance",
      "created": "2026-02-01",
      "updated": "2026-03-01",
      "memory_type": "signpost",
      "confidence": "high",
      "verified": "2026-03-01",
      "review_by": "2026-05-01",
      "owners": ["platform-team"],
      "summary": "Pre-read: ADR-11 before modifying auth flow",
      "tags": ["auth", "pre-read"],
      "requires_reading": [
        "specify/decisions/ADR-011-auth-flow.md",
        "memory/system/auth.md",
      ],
      "scope": {
        "globs": ["src/auth/**", "packages/auth/**"],
        "commands": ["test auth:integration"],
      },
      "priority": {
        "severity": "high",
        "weight": 10,
      },
      "provenance": {
        "sources": [
          {"kind": "adr", "ref": "specify/decisions/ADR-011-auth-flow.md"},
        ],
      },
      "audience": ["human", "agent"],
      "visibility": ["pre"],
      "relations": [
        {"type": "relates_to", "target": "ADR-011"},
      ],
    },
  ],
)

__all__ = [
  "MEMORY_FRONTMATTER_METADATA",
]
