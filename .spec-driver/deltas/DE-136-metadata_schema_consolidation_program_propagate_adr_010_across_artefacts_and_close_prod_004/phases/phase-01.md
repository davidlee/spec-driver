---
id: IP-136-P01
slug: "136-metadata_schema_consolidation_program_propagate_adr_010_across_artefacts_and_close_prod_004-phase-01"
name: IP-136 Phase 01 — Program kickoff and child-delta scoping
created: "2026-05-05"
updated: "2026-05-05"
status: draft
kind: phase
plan: IP-136
delta: DE-136
---

# Phase 1 — Program kickoff and child-delta scoping

## 1. Objective

Lock the per-artefact placement tables already drafted in DR-136 §§6–10 by reviewing them against current artefact reality, scope and open the cross-cutting and per-artefact child deltas that will execute the program, and produce a coordination map (`notes.md`) that each child delta inherits — so child-delta authors do not re-derive placement decisions or re-litigate sequencing.

DE-118 already exists and is the first dependency for Phase 2. This phase does not modify DE-118; it ensures it is positioned correctly in the program sequence.

## 2. Links & References

- **Delta**: DE-136
- **Design Revision Sections**: DR-136 §3 (architecture intent), §4 (universal cuts), §§6–10 (per-artefact placement tables), §5 (cross-cutting deliverables), §11 (migration mechanics), §13 (verification roll-up), DEC-016/DEC-017 (review integrations)
- **Specs / PRODs**: PROD-004.FR-001..FR-007, PROD-004.NF-001 (program-level targets, verified at Phase 4); SPEC-114, SPEC-116 (reconciled at Phase 4)
- **Support Docs**: DE-118 (existing draft — first child); DE-106/DR-106 §3a (precedent placement-analysis pattern); ADR-010 (placement heuristic); POL-001/POL-003 (reuse + module boundaries); STD-003 (utility placement)

## 3. Entrance Criteria

- [x] DE-136 in `draft` with §§3–8 reviewed against external review feedback
- [x] DR-136 in `draft`, external adversarial review integrated (DEC-017)
- [x] IP-136 phase overview locked (this plan)
- [ ] DE-136 transitioned to `in-progress` (per `/execute-phase` entrance)

## 4. Exit Criteria / Done When

- [ ] Placement tables in DR-136 §§4, 6, 7, 8, 9, 10 reviewed against current artefact reality; any new structural inconsistencies surfaced as DR amendments rather than carried forward into child deltas
- [ ] Child delta IDs assigned for the six remaining child deltas and drafted (frontmatter only — full DR/IP/phase work is the child delta's own concern):
  - Cross-cutting infrastructure (Y/Z/X + `validate file` + `validate --kind` + skill tuning + `admin migrate` orchestrator)
  - Delta per-artefact propagation
  - Spec per-artefact propagation
  - Requirements-in-spec block-ification
  - Audit per-artefact propagation
  - Revision per-artefact propagation + `REVISION_FRONTMATTER_METADATA`
- [ ] Each opened child delta's frontmatter includes a `relates_to: DE-136` relation citing this umbrella; `applies_to` scoped to the kind it owns; `audit_gate` set per DR-136 §13
- [ ] `notes.md` in this delta directory contains the child-delta map: child ID → DR-136 § anchor → owner section → entry phase
- [ ] Sequence verified against DR-136 DEC-004 (DE-118 → cross-cutting → delta → spec → requirements-in-spec → audit → revision → close); any sequencing change recorded in DR-136 DEC log
- [ ] No new design questions opened that block Phase 2 entry; substantive new design problems route to `/draft-design-revision` per skill guidance, not absorbed silently

## 5. Verification

- **Tooling/commands**:
  - `uv run spec-driver validate --strict` after each child delta is drafted — expected baseline: only DE-135/DE-136/new-child audit-gate warnings (no new errors).
  - `uv run spec-driver list deltas -s draft` to confirm child deltas are visible with correct IDs.
  - `uv run spec-driver show delta <child-id>` per child delta to confirm `relates_to: DE-136` is set.
- **Evidence to capture**: `notes.md` child-delta map with IDs, DR-136 anchors, and the resolved sequence; brief decision log entry per child delta if any DR-136 placement table changed during review.
- **Tests**: no code changes in this phase. No VTs land in Phase 1.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - DR-136's external-review integration (DEC-017) is sufficient — no further DR rework expected before scoping child deltas.
  - DE-118 stays in scope as drafted; if DE-118's design needs amendment to align with DR-136 §11 boundary, that becomes a Phase 2 entrance task, not a Phase 1 task.
  - Child deltas can be drafted (`draft` status, frontmatter + summary only) without their own DR/IP. The full draft → DR → IP → phase → execute loop is each child's work, not the umbrella's.
  - Six child deltas (one cross-cutting + five per-artefact) is the correct decomposition. Splitting further only if one's blast radius forces it.
- **STOP when**:
  - Reviewing a placement table surfaces a structural conflict the DR-136 doesn't already address (e.g. a kind has frontmatter↔block conflict the table didn't anticipate). Route to `/draft-design-revision` for that section before drafting that kind's child delta.
  - DE-118's existing scope cannot be reconciled with DR-136 §11 boundary on inspection — pause and `/consult` rather than absorbing rework into Phase 1.
  - Sequence comes under pressure (e.g. cross-cutting work would benefit from an earlier per-artefact pilot). Surface as a DR amendment via `/draft-design-revision`.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID | Description | Parallel? | Notes |
|---|---|---|---|---|
| [ ] | 1.1 | Review placement tables in DR-136 §§4, 6, 7, 8, 9, 10 against current `.spec-driver/**` reality | [ ] | Sample 2–3 real artefacts per kind; surface drift as DR amendments via `/draft-design-revision` |
| [ ] | 1.2 | Confirm DE-118 scope and frontmatter aligns with DR-136 §11 migration boundary | [ ] | Read-only check; any rework is a Phase 2 entrance task |
| [ ] | 1.3 | Scope and open cross-cutting child delta | [P] | Per `/scope-delta`; cite DE-136; entry phase: Phase 2 |
| [ ] | 1.4 | Scope and open delta per-artefact child delta | [P] | Per `/scope-delta`; cite DE-136; DR-136 §6 anchor |
| [ ] | 1.5 | Scope and open spec per-artefact child delta | [P] | Per `/scope-delta`; cite DE-136; DR-136 §7 anchor |
| [ ] | 1.6 | Scope and open requirements-in-spec child delta | [P] | Per `/scope-delta`; cite DE-136; DR-136 §8 anchor |
| [ ] | 1.7 | Scope and open audit per-artefact child delta | [P] | Per `/scope-delta`; cite DE-136; DR-136 §9 anchor |
| [ ] | 1.8 | Scope and open revision per-artefact child delta | [P] | Per `/scope-delta`; cite DE-136; DR-136 §10 anchor |
| [ ] | 1.9 | Write `notes.md` child-delta map | [ ] | Child IDs → DR anchors → owner sections → entry phase; updates IP-136 §4 phase rows with assigned IDs |
| [ ] | 1.10 | Reconfirm sequence (DEC-004) and exit criteria; transition Phase 1 to `completed` | [ ] | After 1.1–1.9; `validate --strict` baseline check |

### Task Details

- **1.1 Review placement tables against artefact reality**
  - **Design / Approach**: Per kind, pick 2–3 real artefacts from `.spec-driver/**`; check each row in the relevant DR-136 placement table is consistent with the artefact's current shape and DR-136 §11 migration plan. Look specifically for fields the table doesn't account for (drift entries from external review F2/F3).
  - **Files / Components**: `.spec-driver/specs/`, `.spec-driver/deltas/`, `.spec-driver/audits/`, `.spec-driver/revisions/`.
  - **Testing**: none.
  - **Observations & AI Notes**: TBD — record any DR amendment triggers here.

- **1.2 DE-118 scope alignment with §11 boundary**
  - **Design / Approach**: Read DE-118's existing draft. Verify its scope (block validator unification) does not assume migration steps invoke validation/, and that the block-validator unification it lands serves both strict-on-validate and tolerant-on-read modes per DEC-005.
  - **Files / Components**: `.spec-driver/deltas/DE-118-*/`.
  - **Testing**: none.
  - **Observations & AI Notes**: TBD.

- **1.3–1.8 Scope child deltas**
  - **Design / Approach**: For each, run `/scope-delta`. Each child delta's frontmatter must:
    - cite DE-136 in `relations` as `relates_to`;
    - scope `applies_to` to the kind it owns (cross-cutting delta scoped per §5 deliverables);
    - reference the relevant DR-136 § for placement and DR-136 §11 for migration mechanics;
    - set `audit_gate` per DR-136 §13.1 expectations (most child deltas medium tier; cross-cutting may justify higher given blast radius).
  - **Files / Components**: new `.spec-driver/deltas/DE-XXX-*/` per child.
  - **Testing**: `uv run spec-driver list deltas -s draft` after each.
  - **Observations & AI Notes**: TBD — record assigned IDs here as they're allocated.

- **1.9 Child-delta map in `notes.md`**
  - **Design / Approach**: Markdown table: child ID | scope summary (one line) | DR-136 § anchor | sequence position | entry phase. This is the canonical map child-delta authors use to find their inherited decisions.
  - **Files / Components**: `notes.md` in this delta dir; update IP-136 §4 phase row labels with assigned IDs.
  - **Testing**: none.
  - **Observations & AI Notes**: TBD.

- **1.10 Phase wrap**
  - **Design / Approach**: Run `validate --strict` baseline; confirm exit criteria; transition phase status to `completed`; update IP-136 progress.
  - **Files / Components**: `phases/phase-01.md`, `IP-136.md`.
  - **Testing**: `uv run spec-driver validate --strict`.
  - **Observations & AI Notes**: TBD.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|---|---|---|
| Reviewing placement tables surfaces a fundamental gap requiring substantial DR rework, mid-phase | STOP condition routes to `/draft-design-revision`; do not absorb silently | open |
| Child deltas drift from program intent during scoping | Each child delta cites DE-136 and the relevant DR-136 §; `notes.md` map is the inheritance contract | open |
| ID collisions or off-by-one allocation when six new deltas are opened in parallel | Allocate sequentially via `/scope-delta`, not in parallel `Bash` calls; record IDs in `notes.md` immediately | open |
| External review F1 boundary tightening conflicts with DE-118's existing design | Task 1.2 is a read-only check; rework, if needed, is escalated to a Phase 2 entrance task or `/consult` | open |

## 9. Decisions & Outcomes

- `2026-05-05` — Phase 1 is coordination-only; no code changes. Sequencing follows DR-136 DEC-004 (DE-118 → cross-cutting → delta → spec → requirements-in-spec → audit → revision → close).
- `2026-05-05` — Six child deltas (one cross-cutting + five per-artefact). DE-118 is the seventh, already drafted. Further decomposition only on demonstrated blast-radius pressure.

## 10. Findings / Research Notes

- TBD during execution.

## 11. Wrap-up Checklist

- [ ] All exit criteria satisfied
- [ ] `notes.md` child-delta map written and IP-136 §4 phase rows updated with child IDs
- [ ] `uv run spec-driver validate --strict` baseline matches expectation (only audit-gate warnings on draft deltas)
- [ ] Phase status transitioned to `completed`
- [ ] Hand-off note for Phase 2: DE-118 ready to land first; cross-cutting delta drafted and ready to enter its own phase work
