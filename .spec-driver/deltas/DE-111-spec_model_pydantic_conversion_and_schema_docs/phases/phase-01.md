---
id: IP-111-P01
slug: "111-spec_model_pydantic_conversion_and_schema_docs-phase-01"
name: Phase 01 — Add plan/delta metadata fields
created: "2026-03-22"
updated: "2026-03-22"
status: in-progress
kind: phase
plan: IP-111
delta: DE-111
objective: Add plan and delta string fields to plan.py frontmatter metadata. Update phase example. Verify schema output.
entrance_criteria: [DR-111 approved]
exit_criteria:
  - plan.py has plan and delta fields
  - Phase example includes plan and delta
  - Schema command shows new fields
  - Tests pass
  - Lint clean
---

# Phase 01 — Add plan/delta metadata fields

## Tasks

| Status | ID  | Description |
| ------ | --- | ----------- |
| [ ]    | 1.1 | Add plan and delta FieldMetadata entries to plan.py |
| [ ]    | 1.2 | Update phase example to include plan and delta |
| [ ]    | 1.3 | Verify schema output |
| [ ]    | 1.4 | Run tests and lint |
