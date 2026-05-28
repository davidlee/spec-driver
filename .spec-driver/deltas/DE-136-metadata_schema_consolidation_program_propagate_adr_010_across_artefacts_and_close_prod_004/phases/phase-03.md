---
id: IP-136-P03
slug: "136-metadata_schema_consolidation_program_propagate_adr_010_across_artefacts_and_close_prod_004-phase-03"
name: IP-136 Phase 03 — Per-artefact propagation (DE-139 → DE-140 → DE-141 → DE-142)
created: "2026-05-22"
updated: "2026-05-22"
status: in-progress
kind: phase
plan: IP-136
delta: DE-136
---

# Phase 3 — Per-artefact propagation (DE-139 → DE-140 → DE-141 → DE-142)

## 1. Objective

Drive the four remaining per-artefact child deltas to `completed` in DEC-004 sequence, propagating the foundations laid by DE-118 + DE-137 across spec (incl. PROD), requirements-in-spec, audit, and revision artefact kinds. DE-138 (delta-kind) closed at Phase 3 entry and sets the per-artefact precedent that DE-139..DE-142 inherit.

This is umbrella-level orchestration: each child delta is itself a delta with its own DR/IP/phases, owns its own VT/VA, and runs to its own audit gate. P03 at the umbrella level is a sequence shepherd — confirm entrance, drive sibling delta to closure, validate strict-mode flip in `workflow.toml`, and hand off to the next sibling. No new implementation lives in this phase.

## 2. Links & References

- **Delta**: DE-136
- **Design Revision Sections**:
  - DR-136 §7 (spec placement table; F-A PROD sub-table carried by DE-139)
  - DR-136 §8 (requirements-in-spec placement; `supekku:spec.requirements@v1`)
  - DR-136 §9 (audit placement; findings → block, per-finding outcome enum)
  - DR-136 §10 (revision placement; new `REVISION_FRONTMATTER_METADATA`, `supekku:revision.change@v1` action enum + conditional rules)
  - DR-136 §11.3 (per-kind strict-mode flip via `workflow.toml`)
  - DR-136 §13.1 (verification roll-up acceptance for Phase 4)
- **Specs / PRODs**: PROD-004.FR-001..FR-007 + NF-001 (Phase 4 verification gate; Phase 3 lands the per-kind evidence each child rolls up)
- **Support Docs**:
  - DE-138 close (precedent): `.spec-driver/deltas/DE-138-*/` + RE-042
  - DE-138 P03 logs: `p03-risk-recon-log.md`, `p03-sweep-drift-log.md` (template siblings inherit)
  - `notes.md` Phase 1 child-delta map (F-A, F-C, F-D, F-F scope-notes inherited by named children)
  - DE-118 + DE-137 close evidence (foundations baseline; AUD-026)

## 3. Entrance Criteria

- [x] Phase 2 completed (2026-05-19; foundations ready; AUD-026 recorded)
- [x] DE-138 completed (precedent set; pattern documented; RE-042 attached)
- [x] DE-136 still `in-progress` (confirmed 2026-05-22)
- [x] Foundations smoke: `validate workspace --strict` baseline — 9 issues (1 pre-existing error DE-030/DR-030 unresolved, 8 audit-gate warnings on draft/in-progress deltas incl. PROD-004.FR-007 coverage mismatch). No new error class vs P02 wrap.
- [x] DE-139 ready to enter: scope-note F-A inherited; DR-139 skeleton exists (needs authoring); `status: draft`

## 4. Exit Criteria / Done When

- [ ] DE-139 `completed` — spec-kind propagation (tech SPEC + PROD blocks, taxonomy strict, `list specs` enrichment, `v03_spec_blocks.py`); F-A PROD coverage authored in DR-139
- [ ] DE-140 `completed` — requirements-in-spec block-ification (`supekku:spec.requirements@v1`, regex parser retired, interactive `admin migrate-requirements`, `v04_spec_requirements.py`)
- [ ] DE-141 `completed` — audit-kind propagation (findings → block, per-finding strict outcome enum, `list audits` enrichment, `v05_audit_findings.py`); F-C + F-D honoured
- [ ] DE-142 `completed` — revision-kind propagation (NEW `REVISION_FRONTMATTER_METADATA`, `supekku:revision.change@v1` action enum + conditional rules, `applies_to` derivation, `v06_revision_metadata.py`); F-F coordination with DE-118 closed
- [ ] `workflow.toml` per-kind strict-mode entries set for `spec`, `requirement`, `audit`, `revision` (in addition to `delta` from DE-138); each child delta flips its own kind at close
- [ ] Workspace `validate --strict` shows no new error class introduced by Phase 3 closures; remaining warnings either resolved or drift-tracked
- [ ] Revision metadata class exists (`REVISION_FRONTMATTER_METADATA` registered, validated via `MetadataValidator`)
- [ ] Phase 3 evidence captured in §10; IP-136 §9 Phase 3 row marked complete; phase status `completed`

## 5. Verification

- **Per-child-delta**: each sibling defines its own VT/VA in its own IP. Umbrella P03 does NOT re-run sibling verification; it state-checks closure and confirms the workflow.toml flip + workspace baseline holds.
- **Umbrella-level smoke (one pass at phase close)**:
  - `uv run spec-driver show delta DE-139` / `DE-140` / `DE-141` / `DE-142` → all `status: completed`
  - `uv run spec-driver validate workspace --strict` → no new error class vs P02 baseline
  - `uv run spec-driver validate workspace --kind spec` (and `--kind requirement`, `--kind audit`, `--kind revision`) → conformance per kind after its strict-mode flip
  - `grep -nE "^\s*(spec|requirement|audit|revision)\s*=\s*true" workflow.toml` → confirm flips landed
  - `uv run spec-driver schema enums revision` → confirm revision schema registered (covered by DE-142 close)
  - `uv run spec-driver admin migrate --list` → migration steps for each kind registered post-close
- **Evidence to capture** (§10):
  - One-line closure receipt per sibling (`DE-XXX completed YYYY-MM-DD; RE-XXX attached; AUD-XXX recorded`)
  - Workspace baseline diff (pre-P03 vs post-P03)
  - Any drift entries filed during sibling sweeps (link to drift register)
- **Tests**: no new VT/VA created in Phase 3 at the umbrella level. Program-level VA-DE136-CLOSE-001 fires in Phase 4.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - DE-138 precedent (block reshape + applies_to derivation + list enrichment + migration step pattern) is reusable by siblings without re-litigating DR-136 §6 mechanics.
  - F-A (PROD placement) is DE-139's scope; F-C + F-D are DE-141's; F-F is DE-142's. Each child carries its inherited scope-note into its own DR.
  - Per-kind strict-mode flip is the closing act of each sibling delta, not P03 work.
  - Sibling deltas may proceed strictly sequentially per DEC-004 (no parallel execution); umbrella P03 enforces sequence but does not block on calendar dates.
- **STOP when**:
  - A sibling delta's audit gate raises a finding that ripples into the placement-table itself → pause sequence; route to `/draft-design-revision` against DR-136.
  - Per-kind strict-mode flip in `workflow.toml` introduces a workspace error class not anticipated by the sibling's own audit → file ISSUE-*, route to `/consult` before the next sibling enters.
  - Two siblings (back-to-back) require the same DR-136 amendment → escalate; the umbrella may need its own RE-xxx before P04.
  - DE-140 (reqs-in-spec) reveals the regex parser retirement breaks more callers than its DR scoped → STOP and revise; do not absorb into a sibling's IP.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                              | Parallel? | Notes |
| ------ | --- | ------------------------------------------------------------------------ | --------- | ----- |
| [x]    | 3.1 | Confirm P03 entrance: foundations baseline + DE-138 closure receipt      | [ ]       | Confirmed 2026-05-22; baseline 9 issues (1 pre-existing, 8 audit-gate); DE-138 completed; DE-139 ready |
| [x]    | 3.2 | Drive DE-139 to `completed` (spec-kind; tech SPEC + PROD)                | [ ]       | Completed; 4 phases; audit deferred to DE-136 umbrella |
| [x]    | 3.3 | Confirm `workflow.toml` `[validation.strict].spec = true` flipped       | [ ]       | Confirmed — `spec = true` + `schema_version spec = "0.10.0+003"` |
| [x]    | 3.4 | Drive DE-140 to `completed` (requirements-in-spec block-ification)       | [ ]       | Completed; 5 phases; AUD-027 conformance audit completed |
| [x]    | 3.5 | Confirm `workflow.toml` `[validation.strict].requirement = true` flipped | [ ]       | `[validation.strict_requirements]` flipped via DE-143 (bulk migration of 68 specs; separate config section per DEC-140-13 — requirements is feature-level, not kind-level) |
| [ ]    | 3.6 | Drive DE-141 to `completed` (audit-kind; findings → block)               | [ ]       | F-C (`audit_window` optional) + F-D (per-finding outcome) honoured |
| [ ]    | 3.7 | Confirm `workflow.toml` `[validation.strict].audit = true` flipped       | [ ]       | DE-141 close gate |
| [ ]    | 3.8 | Drive DE-142 to `completed` (revision-kind; new metadata class)          | [ ]       | F-F coordination with DE-118 closed in DE-142 |
| [ ]    | 3.9 | Confirm `workflow.toml` `[validation.strict].revision = true` flipped    | [ ]       | DE-142 close gate |
| [ ]    | 3.10 | Workspace baseline check: `validate --strict` no new error class        | [ ]       | Compare against P02 wrap baseline |
| [ ]    | 3.11 | Phase wrap: capture evidence in §10, update IP-136 §9, transition phase to `completed` | [ ] | Hand-off note for Phase 4 (umbrella close) |

### Task Details

- **3.1 Entrance confirmation**
  - **Design / Approach**: read DE-138 close evidence + AUD-026 receipt; re-run `validate workspace --strict` to confirm baseline (DE-135 + DE-136 + DE-139..DE-142 warnings only).
  - **Files / Components**: state read-out + one command.
  - **Testing**: command output; no code changes.

- **3.2 / 3.4 / 3.6 / 3.8 Sibling delta closure shepherding**
  - **Design / Approach**: each sibling is its own delta; this task is the orchestration cue to route into `/execute-phase` for that delta's active phase. Umbrella P03 does NOT execute sibling internals — it confirms entrance, monitors progress, and records closure receipt. Each sibling delta inherits the named scope-notes from `notes.md` (Phase 1 child-delta map).
  - **Files / Components**: `.spec-driver/deltas/DE-13{9,40,41,42}-*/` (sibling delta bundles).
  - **Testing**: per-sibling VT/VA at sibling close; umbrella records receipt only.
  - **STOP**: sibling audit ripples into DR-136 placement-table → pause + `/draft-design-revision`.

- **3.3 / 3.5 / 3.7 / 3.9 Per-kind strict-mode flip confirmation**
  - **Design / Approach**: after each sibling close, grep `workflow.toml` for the new strict-mode entry. Each sibling delta is responsible for flipping its own kind at close (DR-136 §11.3 boundary). Umbrella P03 confirms the flip landed, does not perform it.
  - **Files / Components**: project `workflow.toml`.
  - **Testing**: `grep` + `validate workspace --kind <kind>` smoke-check after flip.

- **3.10 Workspace baseline check**
  - **Design / Approach**: run `validate workspace --strict` at end of P03; diff error/warning set vs the P02 wrap baseline (§10 of phase-02.md). No new error class is acceptable; new warnings on resolved siblings should not exist (audit gates close them).
  - **Files / Components**: workspace.
  - **Testing**: command output saved as evidence.

- **3.11 Phase wrap**
  - **Design / Approach**: write §10 evidence (4 closure receipts + baseline diff + drift links), update IP-136 §9 row for Phase 3, transition phase status to `completed`, write hand-off note for Phase 4 (umbrella close + VA-DE136-CLOSE-001 audit).
  - **Files / Components**: this file, `IP-136.md`, `notes.md` (Phase 3 receipts addendum).
  - **Testing**: `uv run spec-driver validate file phases/phase-03.md` per `/execute-phase` skill gate.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Sibling delta drifts from DR-136 placement-table (e.g. DE-139 invents PROD coverage not in DR §7 + F-A scope-note) | Each sibling DR must cite DR-136 § and inherited scope-note from `notes.md`; umbrella reviewer confirms at sibling close | open |
| Per-kind strict-mode flip introduces error class on legacy artefacts not addressed by sibling's migrate step | Sibling delta scope includes `admin migrate <kind>` step + drift-track residuals; umbrella `validate --strict` baseline check (task 3.10) catches regressions | open |
| DE-140 regex parser retirement breaks unanticipated callers | DE-140 DR must inventory callers; sibling audit gate covers; STOP condition routes to `/consult` if scope balloons | open |
| F-F (REVISION_CHANGE_METADATA shared additively with DE-118) drifts during DE-142 authoring | DE-142 DR cites DE-118 §11.1 boundary explicitly; additive only, no redefinition | open |
| Sequential sequencing slows program (4 siblings, no parallelism) | Acceptable cost per DEC-004 (delta first establishes pattern; revision last benefits from precedents). No mitigation — sequence is intentional | accepted |
| DE-138's `p03-*.md` log pattern not adopted by siblings → patchy P03 evidence | Hand-off note in 3.1 references DE-138 log shape as template; sibling owners encouraged but not mandated | open |

## 9. Decisions & Outcomes

- `2026-05-22` — Phase 3 is orchestration-only: umbrella does not execute sibling internals. Each sibling owns own DR/IP/VT/VA/audit/close per its own delta bundle. Umbrella records entry + closure receipts + strict-mode flip evidence + workspace baseline.
- `2026-05-22` — Sequential per DEC-004; no parallel sibling execution. DE-139 enters first; DE-140 enters when DE-139 closes; etc.

## 10. Findings / Research Notes

### P03 entrance baseline (2026-05-22)

- **DE-138**: `completed` (RE-042 attached; 4 phases closed; precedent pattern set)
- **DE-136**: `in-progress` (no regression)
- **Workspace `validate --strict`**: 9 issues — 1 error (DE-030/DR-030 unresolved, pre-existing), 8 warnings (audit-gate on DE-135/136/138/139/140/141/142 + PROD-004.FR-007 coverage mismatch). No new error class vs P02 wrap.
- **DE-139**: `draft`, DR-139 skeleton present, scope-note F-A inherited. Next: author DR-139, then IP/phases.

### Sibling closure receipts

- **DE-139** completed 2026-05-25; 4 phases; `[validation.strict].spec = true` flipped; audit deferred to DE-136 umbrella close
- **DE-140** completed 2026-05-28; 5 phases; AUD-027 conformance audit (5 findings, all dispositioned); strict requirements flip deferred → DE-143
- **DE-143** completed 2026-05-28; bulk migration of 68 specs to `spec.requirements@v1` blocks; `[validation.strict_requirements]` flipped; 25 drift ledgers (DL-050..DL-074)

## 11. Wrap-up Checklist

- [ ] Exit criteria (§4) satisfied
- [ ] Verification evidence (§10) stored (4 closure receipts + baseline diff)
- [ ] IP-136 §9 Phase 3 row marked complete
- [ ] `workflow.toml` strict-mode flips confirmed for `spec`, `requirement`, `audit`, `revision`
- [ ] Hand-off note for Phase 4: umbrella close. Inputs ready for Phase 4: per-kind strict-mode operational, all five per-artefact deltas closed (DE-138..DE-142), revision metadata class exists, sibling drift entries triaged. Phase 4 work = spec reconciliation (PROD-004 wording OQ-PROD-004-WORDING-RE resolution), PROD-004 FR-001..FR-007 + NF-001 status `verified`, VA-DE136-CLOSE-001 conformance audit (≥5 artefacts per kind sample), `complete delta DE-136` without `--force`.
- [ ] `uv run spec-driver validate file phases/phase-03.md` clean
