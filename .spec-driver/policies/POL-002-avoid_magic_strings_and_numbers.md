---
id: POL-002
title: 'POL-002: Avoid magic strings and numbers'
status: required
created: '2026-03-05'
updated: '2026-03-05'
reviewed: '2026-03-05'
owners: []
supersedes: []
superseded_by: []
standards: []
specs: []
requirements: []
deltas: []
related_policies: [POL-001]
related_standards: []
tags: [coding, maintainability, readability]
summary: Avoid unexplained literal strings/numbers in production code; use named constants, enums, or config.
---

# POL-002: Avoid magic strings and numbers

## Statement

Production code must not contain unexplained literal strings or numbers that carry
domain meaning. Use named constants, enums, config, or clearly scoped mappings so
intent is explicit and reuse is safe.

Allowed literals are only those that are self-evident and purely local (e.g. `0`
or `1` for indexing, `""` for empty string, `"\n"` for newline, or a single-use
format string), and they must not encode domain semantics.

## Rationale

Magic literals hide intent, invite duplication, and make refactors brittle.
Naming values creates a single source of truth, improves searchability, and
clarifies the domain model for new readers.

## Scope

Applies to all production code in this repository (including CLI, libraries, and
tools). Tests may use literals for simple inputs, but domain-specific values must
still be named if they convey business meaning or are reused.

Excludes prototypes, spikes, and explicitly marked experimental code.

## Verification

Code review should reject new magic literals and request naming or centralization.
We should enforce via lint/static analysis when feasible, and use audits to
catch drift.

## References

- (Add related standards or ADRs when created)
