---
id: IMPR-027
name: Squelch audit-gate warnings for historical deltas that will never get conformance audits
created: "2026-03-22"
updated: "2026-03-22"
status: idea
kind: improvement
categories: [validation, noise]
---

# Squelch audit-gate warnings for historical deltas

## Problem

`spec-driver validate` emits 29 "Audit gate is required but no completed conformance audit found" warnings for old completed deltas (DE-002 through DE-090). These will never get retroactive audits. The noise obscures real issues — after DE-112 cleanup, these are 29 of 43 remaining warnings.

## Options

1. **Cutoff date** — skip audit-gate check for deltas completed before a configurable date
2. **`no_audit_required` marker** — add frontmatter field to opt out per-delta
3. **Severity downgrade** — emit as `info` instead of `warning` for completed deltas older than N days
4. **Accept** — the warnings are true statements, just noisy

## Context

- Surfaced during DE-112 Phase 3 noise reduction
- AUD-001 (5 undispositioned findings) is separate genuine debt
