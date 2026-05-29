---
id: mem.pattern.spec-driver.shared-block-id-patterns
name: Shared block ID regex patterns
kind: memory
status: active
memory_type: pattern
created: '2026-05-30'
updated: '2026-05-30'
verified: '2026-05-30'
confidence: medium
tags:
- blocks
- validation
- patterns
summary: REQUIREMENT_ID_PATTERN/SPEC_ID_PATTERN live in blocks/id_patterns.py; (SPEC|PROD|ISSUE)
  + (FR|NF|NFR); reused by revision + verification blocks
---

# Shared block ID regex patterns

## Summary

Spec-driver requirement/spec ID regexes for block-metadata validation are
shared constants in `supekku/scripts/lib/blocks/id_patterns.py`:

- `REQUIREMENT_ID_PATTERN = r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NF|NFR)-[A-Z0-9.-]+$"`
- `SPEC_ID_PATTERN = r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*$"`

Reused by `blocks/revision_metadata.py` and `blocks/verification_metadata.py`.
ADR is deliberately excluded — ADRs are decisions, not specs.

## Context

Placed at the `blocks/` package level per **STD-003** (narrowest shared lib/
subpackage covering all callers — both callers live in `blocks/`, alongside the
`yaml_utils.py` precedent), NOT in the generic `blocks/metadata/` engine package
(which holds domain-agnostic validation machinery).

The universe was deliberately **broadened** (DE-142, DEC-142-08) from the former
SPEC-only/`(FR|NFR)` regexes, which rejected 97 legitimate corpus refs
(`PROD-*`/`ISSUE-*` containers, the `NF` token). Broadening is a pure relaxation
(no previously-valid block becomes invalid) — F-F-safe, rationalised under
ADR-008 (referential integrity is an audit/registry concern, not a block-schema
regex). When adding a new block type with requirement/spec ID fields, import
these rather than hardcoding a regex.

## Provenance

- [[DE-142]] P04 group A; commit `6e657e78`.
- `supekku/scripts/lib/blocks/id_patterns.py` (+ `_test`).
