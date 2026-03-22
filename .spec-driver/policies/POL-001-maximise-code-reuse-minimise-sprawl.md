---
id: POL-001
title: "POL-001: maximise code reuse, minimise sprawl"
status: required
created: "2025-11-04"
updated: "2026-03-22"
reviewed: "2026-03-05"
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

**Extraction threshold**: If a function body is needed in ≥2 non-test modules,
it must be extracted to a shared utility before the second caller merges.
"Near-identical" means same algorithm with trivial parameter-name differences.
Code review must reject the second copy; it may not approve it with a "clean
this up later" comment. Audits that find ≥3 copies of equivalent logic treat
each copy beyond the first as a P1 finding.

**Competing systems**: This policy applies to competing implementations, not
only verbatim copies. If two modules or classes answer the same question (e.g.
"is this block valid?"), one must be designated canonical and the other
deprecated with a migration delta. A system may not grow a second implementation
path for a concern that already has one without first opening a delta to retire
the existing one.

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

- Code review must reject a second copy of equivalent logic. "Will clean up
  later" is not an acceptable justification.
- Audits finding ≥3 copies of equivalent logic treat each copy beyond the first
  as a P1 finding requiring a remediation delta.
- New modules or classes that duplicate the responsibility of an existing one
  must include a deprecation plan for the incumbent in the same delta.

## References

- (Add related standards or ADRs when created)
