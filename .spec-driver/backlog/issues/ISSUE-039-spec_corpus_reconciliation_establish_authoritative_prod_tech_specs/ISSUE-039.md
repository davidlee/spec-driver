---
id: ISSUE-039
name: 'Spec corpus reconciliation: establish authoritative PROD & TECH specs'
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: issue
categories: [specs, governance, quality]
severity: p2
impact: system
---

# Spec corpus reconciliation: establish authoritative PROD & TECH specs

## Problem

The spec corpus has accumulated drift: design intent has evolved but specs
haven't kept pace. PROD specs are all draft (except PROD-005), TECH specs are
mostly empty stubs, and there are contradictions across documents that undermine
trust in the specs as a source of truth.

Until specs are authoritative, they create confusion rather than clarity —
agents and humans encounter conflicting guidance and can't confidently rely on
any single document.

## Current state

- **16 PROD specs**: 15 draft, 1 active. Most describe real capabilities but
  haven't been validated against current implementation/intent.
- **24 TECH specs**: 14 empty stubs (auto-generated), 8 drafts with partial
  content, 0 active. Stubs will be deleted; deliberate specs created for real
  subsystems.
- **3 accepted ADRs**: ADR-001 (self-hosting), ADR-002 (no backlinks in
  frontmatter), ADR-003 (unit vs assembly specs).
- **Contradictions**: Design intent has evolved; some docs reflect earlier
  thinking that conflicts with current direction.

## Goal

Every PROD spec is either `active` (authoritative, reflects reality) or
explicitly `deferred`/`retired`. TECH specs cover important subsystems with
real content. Contradictions are resolved and codified as ADRs.

## Strategy

### Phase A — Contradiction discovery & resolution

Agent-assisted survey of all PROD specs, ADRs, policies, CLAUDE.md, and
glossary to systematically flag:

- Statements that contradict other documents
- Ambiguous or undefined concepts used inconsistently
- Outdated assumptions that no longer hold
- Overlapping responsibilities between specs

**Output**: Contradiction register — a list of conflicts requiring human
resolution. Each entry: the conflicting statements, which docs, and a
suggested resolution path (ADR, spec revision, or editorial fix).

**Human work**: Review each contradiction, make the design call. Results
codified as ADRs (if architectural) or spec revisions (if local).

### Phase B — PROD spec reconciliation

For each PROD spec, in priority order:

1. Apply resolved contradictions / new ADRs
2. Compare stated intent against implemented reality
3. Revise content (via spec revision RE-xxx)
4. Promote to `active` or mark `deferred`/`retired`

### Phase C — TECH spec reset

1. Delete all 14 stub TECH specs
2. Decide which subsystems deserve deliberate specs (~8-12)
3. Renumber from SPEC-001
4. Create new specs with real content informed by contracts + PROD specs

### Phase D — TECH spec backfill

Fill out new TECH specs in priority order, driven by which PROD specs they
support and which subsystems are actively changing.

## Deltas

| Phase | Delta | Description                                 |
| ----- | ----- | ------------------------------------------- |
| A     | TBD   | Contradiction discovery & ADR resolution    |
| B     | TBD   | PROD spec reconciliation & promotion        |
| C     | TBD   | TECH spec reset & renumbering               |
| D     | TBD   | TECH spec backfill (may be multiple deltas) |

## Risks

- **Human bottleneck**: Contradiction resolution requires design decisions only
  the maintainer can make. Mitigate by batching related contradictions.
- **Scope creep**: Temptation to perfect every spec. Mitigate by defining
  "active-ready" as a clear bar, not perfection.
- **Renumbering churn**: TECH spec renumbering touches many cross-references.
  Mitigate by doing it in one clean pass after stubs are deleted.
