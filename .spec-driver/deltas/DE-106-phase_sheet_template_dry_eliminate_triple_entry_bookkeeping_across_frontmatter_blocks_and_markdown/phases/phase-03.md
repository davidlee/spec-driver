---
id: IP-106-P03
slug: "106-phase_sheet_template_dry_eliminate_triple_entry_bookkeeping_across_frontmatter_blocks_and_markdown-phase-03"
name: "Phase 03 — Validation + ADR + skills + spec reconciliation"
created: "2026-03-22"
updated: "2026-03-22"
status: in-progress
kind: phase
plan: IP-106
delta: DE-106
objective: >-
  Wire phase frontmatter validation. Land placement-rule ADR. Audit and update
  skills. Reconcile PROD-006. Emit memories. Create follow-up backlog items.
entrance_criteria:
  - Phase 2 complete
  - All creation/display/compatibility tests passing
exit_criteria:
  - Phase frontmatter validated via Pydantic model or inline fallback
  - ADR landed (scoped to DE-106-derived placement heuristic)
  - "Skills updated in supekku/skills/ (execute-phase, plan-phases, update-delta-docs, notes)"
  - PROD-006 requirements reconciled with new representation and accepted fidelity reductions
  - "Memories created (contract-vs-progress, canonical fields, frontmatter-block-precedence)"
  - "Follow-up backlog items captured (bulk migration, broader kind-aware validation)"
  - "Lint clean, all tests passing"
---

# Phase 03 — Validation + ADR + skills + spec reconciliation

## 1. Objective

Complete governance, documentation, and validation work to close DE-106. Wire phase frontmatter validation via PhaseSheet, land the placement heuristic ADR, update skills that reference blocks, reconcile PROD-006, create memories, and capture follow-up backlog items.

## 2. Links & References

- **Delta**: DE-106
- **Design Revision**: DR-106 §3a (field analysis), §7 (DEC-004 ADR), §8 (OQ-003 spec reconciliation)
- **Specs**: PROD-006 (reconciliation target)
- **Phase 1/2**: phase-01.md, phase-02.md (completed)

## 3. Entrance Criteria

- [x] Phase 2 complete
- [x] All creation/display/compatibility tests passing (635 relevant tests)

## 4. Exit Criteria / Done When

- [ ] Phase frontmatter validated via Pydantic model
- [ ] ADR landed (placement heuristic)
- [ ] Skills updated (execute-phase, plan-phases, update-delta-docs, notes)
- [ ] PROD-006 reconciled
- [ ] Memories created (3)
- [ ] Follow-up backlog items captured (2)
- [ ] Lint clean, all tests passing

## 5. Verification

- `uv run pytest supekku -q` — all tests passing
- `uv run ruff check supekku` — lint clean on changed files
- `uv run spec-driver validate` — no new warnings for new-format phases

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [ ]    | 3.1 | Wire phase frontmatter validation | `frontmatter_schema.py` or validator |
| [ ]    | 3.2 | Land placement heuristic ADR | DEC-004 from DR-106 |
| [ ]    | 3.3 | Audit and update skills | 4 skills: execute-phase, plan-phases, update-delta-docs, notes |
| [ ]    | 3.4 | Reconcile PROD-006 | Update requirements, capabilities, verification coverage |
| [ ]    | 3.5 | Create memories | contract-vs-progress, canonical fields, frontmatter-block-precedence |
| [ ]    | 3.6 | Create follow-up backlog items | bulk migration, broader kind-aware validation |

## 9. Decisions & Outcomes

_(populated during execution)_

## 10. Findings / Research Notes

_(populated during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated for audit/closure
