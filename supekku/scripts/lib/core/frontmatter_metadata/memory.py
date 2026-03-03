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

from dataclasses import replace

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

MEMORY_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.memory",
  description="Frontmatter fields for memory records (kind: memory)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Base field persistence overrides for memory compaction
    "lifecycle": replace(
      BASE_FRONTMATTER_METADATA.fields["lifecycle"],
      persistence="optional",
    ),
    "owners": replace(
      BASE_FRONTMATTER_METADATA.fields["owners"],
      persistence="optional",
      default_value=[],
    ),
    "auditers": replace(
      BASE_FRONTMATTER_METADATA.fields["auditers"],
      persistence="optional",
      default_value=[],
    ),
    "source": replace(
      BASE_FRONTMATTER_METADATA.fields["source"],
      persistence="optional",
    ),
    "summary": replace(
      BASE_FRONTMATTER_METADATA.fields["summary"],
      persistence="optional",
    ),
    "tags": replace(
      BASE_FRONTMATTER_METADATA.fields["tags"],
      persistence="optional",
      default_value=[],
    ),
    "relations": replace(
      BASE_FRONTMATTER_METADATA.fields["relations"],
      persistence="optional",
      default_value=[],
    ),
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
      persistence="optional",
    ),
    "verified": FieldMetadata(
      type="string",
      required=False,
      pattern=r"^\d{4}-\d{2}-\d{2}$",
      description=("ISO-8601 date of last verification against reality (YYYY-MM-DD)"),
      persistence="optional",
    ),
    "review_by": FieldMetadata(
      type="string",
      required=False,
      pattern=r"^\d{4}-\d{2}-\d{2}$",
      description="ISO-8601 date for next required review (YYYY-MM-DD)",
      persistence="optional",
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
      persistence="optional",
      default_value=[],
    ),
    "scope": FieldMetadata(
      type="object",
      required=False,
      description="Context matching criteria for deterministic surfacing",
      persistence="optional",
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
      persistence="optional",
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
      persistence="optional",
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
      persistence="optional",
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
      persistence="optional",
    ),
    "links": FieldMetadata(
      type="object",
      required=False,
      description=("Resolved cross-artifact links parsed from body [[...]] tokens"),
      persistence="optional",
      properties={
        "out": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="object",
            description="Resolved outgoing link",
            properties={
              "id": FieldMetadata(
                type="string",
                required=True,
                pattern=r".+",
                description="Target artifact ID",
              ),
              "path": FieldMetadata(
                type="string",
                required=True,
                pattern=r".+",
                description="Relative path to target",
              ),
              "kind": FieldMetadata(
                type="string",
                required=True,
                description=("Artifact kind (adr, spec, memory, etc.)"),
              ),
              "label": FieldMetadata(
                type="string",
                required=False,
                description=("Optional display label from [[id|label]]"),
              ),
            },
          ),
          description="Resolved outgoing links",
          persistence="derived",
          default_value=[],
        ),
        "missing": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="object",
            description="Unresolved link target",
            properties={
              "raw": FieldMetadata(
                type="string",
                required=True,
                pattern=r".+",
                description="Original link target text",
              ),
            },
          ),
          description="Unresolved link targets",
        ),
      },
    ),
  },
  examples=[
    # Representative memory with scope, priority, provenance (default example)
    {
      "id": "mem.signpost.auth.prereading",
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
    # Minimal memory (base fields + required memory_type only)
    {
      "id": "mem.fact.example",
      "name": "Example Memory Record",
      "slug": "mem-example",
      "kind": "memory",
      "status": "active",
      "created": "2026-03-01",
      "updated": "2026-03-01",
      "memory_type": "fact",
    },
  ],
)

__all__ = [
  "MEMORY_FRONTMATTER_METADATA",
]
