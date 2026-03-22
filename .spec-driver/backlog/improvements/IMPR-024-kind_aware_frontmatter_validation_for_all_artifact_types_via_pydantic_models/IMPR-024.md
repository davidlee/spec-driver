---
id: IMPR-024
name: Kind-aware frontmatter validation for all artifact types via Pydantic models
created: "2026-03-22"
updated: "2026-03-22"
status: idea
kind: improvement
relations:
  - type: follows_from
    target: DE-106
  - type: follows_from
    target: DE-107
---

# Kind-aware frontmatter validation for all artifact types via Pydantic models

## Problem

Frontmatter validation in `frontmatter_schema.py` checks only generic
required fields (`id`, `name`, `slug`, `status`, etc.). Kind-specific
validation is ad-hoc: phases have `PhaseSheet` (DE-106), but other artifact
kinds (delta, revision, audit, memory, spec) lack model-based validation.

## Proposed Solution

Following DE-107's Pydantic go decision (via DE-106 phase model spike):
1. Define Pydantic models for each artifact kind's frontmatter
2. Wire kind-aware validation in `validate_frontmatter()` or the workspace validator
3. Use `extra="ignore"` to maintain forward compatibility

## Priority

Medium. The phase model proves the pattern works (37ms import, clean
parsing). Extension to other kinds is straightforward but requires per-kind
field analysis similar to DR-106 §3a.

## Context

- PhaseSheet model: `supekku/scripts/lib/changes/phase_model.py`
- DE-107 Pydantic spike: go decision made via DE-106 Phase 1
- ADR-010: placement heuristic guides which fields go in frontmatter
