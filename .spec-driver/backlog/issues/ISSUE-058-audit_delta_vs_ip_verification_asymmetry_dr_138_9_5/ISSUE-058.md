---
id: ISSUE-058
name: audit delta-vs-IP verification asymmetry (DR-138 §9.5)
created: "2026-05-20"
updated: "2026-05-20"
status: open
kind: issue
categories: [governance, verification, audit]
severity: p3
impact: process
---

# audit delta-vs-IP verification asymmetry (DR-138 §9.5)

## Origin

- **Source**: DR-138 §9.5 (DEC-138-08) + §15.1 + F-138-24.
- **Tracking-artefact requirement**: DE-138 IP-138-P04 acceptance gate (§10.5) — without this filing, the "follow-up audit scoped" gate item is non-falsifiable.
- **Replaces placeholder**: F-138-24 (DR-138 §16.2).

## Problem

DEC-138-08 deferred the structural asymmetry between delta `## 6. Verification Strategy` prose and IP `supekku:verification.coverage@v1` block. The decision is *conditional* (F-138-I): defensible **only if** delta §6 prose is narrative-only across the corpus.

If the audit finds structured commitments (VT-IDs, requirement → VT mappings) embedded in §6 prose, DEC-138-08 is wrong and the asymmetry is an ADR-010 rule-4 violation. Audit outcome shapes whether corrective action is governance-only (skill/validation/memory tuning) or also requires a follow-up content-migration delta.

## Audit shape (per DR-138 §9.5)

1. **Sample-audit** delta §6 prose across the corpus. Aim for coverage spanning early (DE-001..050), middle (DE-051..100), and recent (DE-100+) deltas to detect drift over time.
2. **Characterise drift patterns and root cause** — why practitioners may write structured commitments in delta §6 instead of IP coverage block:
   - skill prompt ambiguity (`execute-phase`, `plan-phases`, `draft-design-revision`)?
   - missing validation hook (no lint rule flags prose VT-* refs in delta §6)?
   - unclear memory guidance (no `mem.pattern.*` clarifying delta-vs-IP verification split)?
3. **Output corrective surface scopes** across:
   - **Skills**: likely `execute-phase`, `plan-phases`, `draft-design-revision`.
   - **Validation**: e.g. lint hook flagging prose VT-* references in delta §6.
   - **Memories**: e.g. `mem.pattern.*` clarifying the delta-vs-IP verification split.

Goal: audit *shapes* improvement, not just enumerates violations — prevent asymmetry re-emergence.

## Consumption point

- **Umbrella**: DE-136 metadata schema consolidation program.
- **Phase**: DE-136 Phase 04 — umbrella audit consumes this work as a tracked deliverable.
- **Reference at DE-138 close**: DR-138 §10.5 acceptance row + §15.1 follow-up entry should cross-reference `ISSUE-058`.

## Ownership

- **Owner**: DE-136 P04 umbrella audit (no individual owner; absorbed by umbrella audit cycle).
- **Due**: next umbrella audit (DE-136 P04 execution window).

## Related

- DR-138 §9.5, §10.5, §15.1, §16.2 (F-138-I, F-138-24).
- DEC-138-08.
- ADR-010 (rule-4: structured truth lives in canonical location).
- DE-136 (umbrella).
