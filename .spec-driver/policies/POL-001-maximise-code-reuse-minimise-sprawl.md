---
id: POL-001
title: 'POL-001: maximise code reuse, minimise sprawl'
status: required
created: '2025-11-04'
updated: '2026-03-05'
reviewed: '2026-03-05'
owners: []
supersedes: []
superseded_by: []
standards: []
specs: []
requirements: []
deltas: []
related_policies: [POL-002]
related_standards: []
tags: [coding, maintainability, architecture]
summary: Prefer reuse and consolidation over copy/paste; avoid needless duplication and sprawl.
---

# POL-001: maximise code reuse, minimise sprawl

## Statement

When adding or modifying functionality, prefer reuse and consolidation over
copy/paste or parallel implementations. If a capability already exists, extend
or adapt it rather than introducing a competing variant.

This does not require premature abstraction: start specific, but when duplication
appears or reuse is clearly beneficial, extract or align the shared behavior.

## Rationale

Sprawl creates hidden divergence, increases maintenance cost, and makes changes
riskier. Reuse keeps behavior consistent, improves searchability, and reduces
the long-term surface area of the codebase.

## Scope

Applies to all production code in this repository (including CLI, libraries, and
tools). Tests may duplicate small inputs for clarity, but shared fixtures or
domain behaviors should still be centralized.

Excludes prototypes, spikes, and explicitly marked experimental code.

## Verification

Code review should flag new duplication and ask for consolidation or reuse.
Audits can track sprawl hotspots; standards or lint rules should be added if
repeat issues appear.

## References

- (Add related standards or ADRs when created)
