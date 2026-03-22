---
id: IMPR-026
name: Permissive Pydantic models produce shallow validation — BacklogItem and MemoryRecord accept almost any input
created: "2026-03-22"
updated: "2026-03-22"
status: idea
kind: improvement
categories: [validation, models]
---

# Permissive Pydantic models produce shallow validation

## Problem

`BacklogItem` and `MemoryRecord` use `extra="ignore"` and default all fields, so `Model(**fm)` passes for almost any dict. The kind-aware validation (DE-112) catches only type errors (e.g. `likelihood: "not-a-number"`, `tags: "not-a-list"`). Missing `id`, wrong `kind` values, empty required fields — all pass silently.

## Options

1. Add `@field_validator` checks for required-in-practice fields (id, kind, status)
2. Create separate strict validation schemas (construction stays permissive, validation is tighter)
3. Accept shallow validation as intentional — the models serve construction, not enforcement

## Context

- Surfaced during DE-112 Phase 2 testing
- `DriftLedger` is stricter (`id` and `name` required, no defaults) — inconsistent
