---
id: mem.fact.spec-driver.status-enums
name: Canonical Status Enums
kind: memory
status: active
memory_type: fact
updated: "2026-05-18"
verified: "2026-05-18"
confidence: high
tags: [spec-driver, lifecycle, status, sharp-edge]
summary: "Authoritative status enums for requirements, change artifacts, and verification coverage. After DE-137 IP-137-P01, the per-kind FieldMetadata is the source of truth; lifecycle constants are derived re-exports."
priority:
  severity: high
  weight: 10
scope:
  commands:
    - uv run spec-driver complete delta
    - complete delta
    - uv run spec-driver sync
    - uv run spec-driver validate workspace
  paths:
    - supekku/scripts/complete_delta.py
    - supekku/scripts/lib/changes/coverage_check.py
    - supekku/scripts/lib/requirements/lifecycle.py
    - supekku/scripts/lib/requirements/registry.py
    - supekku/scripts/lib/changes/lifecycle.py
    - supekku/scripts/lib/blocks/verification.py
    - supekku/scripts/lib/blocks/metadata/aliases.py
    - supekku/scripts/lib/core/frontmatter_metadata/
    - supekku/cli/workflow.py
    - spec_driver/orchestration/enums.py
    - .spec-driver/deltas/*/phases/phase-*.md
provenance:
  sources:
    - kind: code
      note: Per-kind status enum source of truth (FRONTMATTER_METADATA_REGISTRY)
      ref: supekku/scripts/lib/core/frontmatter_metadata/__init__.py
    - kind: code
      note: Read-time alias canonicalisation (normalize_field)
      ref: supekku/scripts/lib/blocks/metadata/aliases.py
    - kind: code
      note: Change artefact status constants (derived re-export)
      ref: supekku/scripts/lib/changes/lifecycle.py
    - kind: code
      note: Derived ENUM_REGISTRY (Category A walks FRONTMATTER_METADATA_REGISTRY)
      ref: spec_driver/orchestration/enums.py
    - kind: delta
      note: DE-137 IP-137-P01 — DEC-137-14, DEC-137-23 (status enum unification)
      ref: .spec-driver/deltas/DE-137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child/DR-137.md
---

# Canonical Status Enums

## Source of truth (post DE-137 IP-137-P01)

Every artefact kind's `status` enum lives on its
`FRONTMATTER_METADATA_REGISTRY[kind].fields["status"]` `FieldMetadata`.
Legacy lifecycle constants (`CHANGE_STATUSES`, `REQUIREMENT_STATUSES`,
`SPEC_STATUSES`, ...) are **derived re-exports** carrying the
`OQ-137-02 sunset` comment; do not edit them directly. The named
`STATUS_*` constants (e.g. `STATUS_COMPLETED = "completed"`) remain
as convenience handles for callers that need individual references.

## Requirement Lifecycle (canonical)

- `pending`
- `in-progress`
- `active`
- `retired`
- `deprecated`
- `superseded`

## Change Artifact Lifecycle (canonical)

- `draft`
- `pending`
- `in-progress`
- `completed`
- `deferred`

Applies to: deltas, revisions, audits, plans, phases, tasks (DE-104).

Permanent aliases on every change-artefact kind's `FieldMetadata.aliases`
(applied at read time via `normalize_field`; under strict mode the
validator emits warnings with `fix_kind="rewrite_value"`):

- `complete` → `completed`
- `done` → `completed`
- `active` → `in-progress`
- `in_progress` → `in-progress`

## Verification Coverage Statuses

- `planned`
- `in-progress`
- `verified`
- `failed`
- `blocked`

## How to canonicalise a value at read time

```python
from supekku.scripts.lib.blocks.metadata.aliases import normalize_field
canonical = normalize_field("delta", "status", raw_value)  # lower + strip + alias lookup
```

`normalize_field` returns the lower-cased + whitespace-stripped input
when the kind/field/value has no alias declared.

## Important caveats

- The `MetadataValidator` is **report-only**; it never mutates the
  supplied data. Loaders that need canonical values at read time must
  call `normalize_field` explicitly. `validate workspace --fix`
  consumes `ValidationError.fix_hint` to rewrite source files.
- Revision lifecycle ingestion in the requirements registry tolerates
  non-canonical status strings from payloads; the strict-mode CLI
  catches these via the `MetadataValidator(strict=True)` path.

## Non-Canonical Terms to Avoid

- `implemented`
- `verified` (as requirement lifecycle status)
- `live`
- `archive`
