---
id: mem.concept.spec-driver.ceremony.settler
name: Settler Ceremony Mode
kind: memory
status: active
memory_type: concept
updated: "2026-03-06"
verified: "2026-03-06"
confidence: high
tags: [spec-driver, ceremony, settler]
summary: "Medium ceremony: delta-first delivery with selective specs, backlog intake, and flexible evidence capture. The default mode for most projects."
priority:
  severity: medium
  weight: 7
scope:
  commands: [uv run spec-driver create delta]
  paths: [specify/decisions/ADR-004-canonical_workflow_loop.md]
provenance:
  sources:
    - kind: adr
      ref: ADR-004
    - kind: code
      note: Delta completion coverage and lifecycle behavior
      ref: supekku/scripts/complete_delta.py
    - kind: code
      note: Coverage gate specifics and enforcement defaults
      ref: supekku/scripts/lib/changes/coverage_check.py
---

# Settler Ceremony Mode

## Intent

Delta-first delivery with selective evergreen specs and flexible evidence
capture. Traceability without governance overhead.

## Activated Primitives

- **[[mem.concept.spec-driver.backlog]]** — issues, improvements, problems, risks for intake
- **[[mem.concept.spec-driver.delta]]** — primary delivery mechanism
- **[[mem.concept.spec-driver.spec]]** — assembly specs are the typical first target; unit specs optional
- **[[mem.concept.spec-driver.design-revision]]** — advisable when change significance warrants explicit design
- **[[mem.concept.spec-driver.plan]]** — advisable when execution needs breakdown
- **[[mem.concept.spec-driver.audit]]** — for discovery/backfill or conformance

## Typical Flows

**Prospective** (planned work):

```text
[optional backlog item] -> delta -> [recommended DR for significant change] -> [IP/phases when execution scope warrants] -> implement -> audit/reconcile -> close
```

**Retrospective** (existing code):

```
audit (discovery/backfill) -> spec/requirement updates -> follow-up delta(s)
```

## How Specs Behave Here

Specs are **converging toward truth**. Some may still be aspirational; others
now accurately reflect the system. As audits and deltas close the gap, specs
mature into the source of truth described in
[[mem.concept.spec-driver.philosophy]].

## Agent Guidance

- Deltas are the standard work unit — use `uv run spec-driver create delta` for intentional changes
- Cards may coexist with deltas but are not interchangeable — cards do not link to the delta->IP flow
- When closing work, follow [[mem.pattern.spec-driver.delta-completion]]
- `complete delta` normally requires verified parent-spec coverage blocks for
  all delta requirements; see [[mem.fact.spec-driver.coverage-gate]]
- Audits are legitimate for discovery (applying spec-driver to existing code), not just conformance
