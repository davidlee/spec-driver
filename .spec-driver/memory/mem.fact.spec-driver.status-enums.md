---
id: mem.fact.spec-driver.status-enums
name: Canonical Status Enums
kind: memory
status: active
memory_type: fact
updated: "2026-03-03"
verified: "2026-03-03"
confidence: high
tags: [spec-driver, lifecycle, status, sharp-edge]
summary: "Authoritative status enums for requirements, change artifacts, and verification coverage, including tolerated legacy/non-canonical cases."
priority:
  severity: high
  weight: 10
scope:
  commands:
    - uv run spec-driver complete delta
    - complete delta
    - uv run spec-driver sync
    - uv run spec-driver validate
  paths:
    - supekku/scripts/complete_delta.py
    - supekku/scripts/lib/changes/coverage_check.py
    - supekku/scripts/lib/requirements/lifecycle.py
    - supekku/scripts/lib/requirements/registry.py
    - supekku/scripts/lib/changes/lifecycle.py
    - supekku/scripts/lib/blocks/verification.py
provenance:
  sources:
    - kind: code
      note: Canonical requirement lifecycle constants
      ref: supekku/scripts/lib/requirements/lifecycle.py
    - kind: code
      note: Revision lifecycle ingestion currently accepts raw status strings
      ref: supekku/scripts/lib/requirements/registry.py
    - kind: code
      note: Change artifact status constants and canonical mapping
      ref: supekku/scripts/lib/changes/lifecycle.py
    - kind: code
      note: Verification coverage status constants
      ref: supekku/scripts/lib/blocks/verification.py
---

# Canonical Status Enums

## Requirement Lifecycle (canonical)

- `pending`
- `in-progress`
- `active`
- `retired`

## Change Artifact Lifecycle (canonical)

- `draft`
- `pending`
- `in-progress`
- `completed`
- `deferred`

Legacy alias:

- `complete` is normalized to `completed`

## Verification Coverage Statuses

- `planned`
- `in-progress`
- `verified`
- `failed`
- `blocked`

## Important Caveat

Revision lifecycle ingestion in requirements registry currently tolerates
non-canonical status strings from payloads (it does not hard-validate against
the canonical requirement enum on read).

Follow-up strict-mode work should apply one shared status-policy validator to
both write-time and read-time paths.

## Non-Canonical Terms to Avoid

- `implemented`
- `verified` (as requirement lifecycle status)
- `live`
- `archive`
