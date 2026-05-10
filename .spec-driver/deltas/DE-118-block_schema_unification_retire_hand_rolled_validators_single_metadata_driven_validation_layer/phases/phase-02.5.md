---
id: IP-118-P02.5
slug: "118-block_schema_unification_retire_hand_rolled_validators_single_metadata_driven_validation_layer-phase-02.5"
name: IP-118 Phase 02.5
created: "2026-05-09"
updated: "2026-05-09"
status: completed
kind: phase
plan: IP-118
delta: DE-118
---

# Phase 02.5 — Declaration Fidelity

## 1. Objective

Bring the six lax `BlockMetadata` declarations into line with the observed contract before P03 swaps land. **Mechanism is unchanged** — no validator code edits, no swap commits, no retirements. Only widen declarations to match what the lax hand-rolled validators silently accept today on real corpus.

The phase exists because P02's snapshot harness surfaced 30 verdict disagreements (`hand-rolled: PASS, metadata: FAIL`) across six validators. DR-118 §2's premise correction explains *why* the work is needed; this phase performs *what* is needed.

Concretely, P02.5 ships:

1. Per-block additions to six `BlockMetadata` declarations (`PLAN_OVERVIEW_METADATA`, `PHASE_OVERVIEW_METADATA`, `PHASE_TRACKING_METADATA`, `VERIFICATION_COVERAGE_METADATA`, `SPEC_RELATIONSHIPS_METADATA`/`SPEC_CAPABILITIES_METADATA`, `DELTA_RELATIONSHIPS_METADATA`).
2. Harness re-run after each batch; closure when zero disagreements remain.
3. Backlog / drift entries for the 18 malformed-YAML files (informational, separate work).

**Out of scope**: validator code, swap commits, future tightening (which fields *should not* be there) — that is DE-137 work per DR-136 §11.3.

## 2. Links & References

- **Delta**: DE-118
- **Design Revision Sections**: DR-118 §2 (premise correction), §7 DEC-001 (premise note), §7 DEC-007 (harness DEC).
- **IP-118 §4**: P02.5 row introduced 2026-05-09.
- **Antecedent**: P02 harness output catalogued in `../notes.md` (P02 closure section).
- **Cross-cutting governance**: DR-136 §11.3 (consumer-repo migration; tightening is DE-137 territory).
- **Backlog**: IMPR-035 (workflow.* deferral; no new IMP needed for P02.5 since fidelity is widening, not tightening).

## 3. Entrance Criteria

- [ ] IP-118-P02 closed; harness operational; `notes.md` contains the disagreement inventory.
- [ ] `interactions[].description` patch from P02 either reverted or formally folded into the P02.5 commit (audit-trail decision — see §6).
- [ ] DR-118 §2 premise correction landed; DEC-001 rationale annotated.
- [ ] No outstanding `/consult` thread on DE-118 design.

## 4. Exit Criteria / Done When

- [ ] All six lax declarations widened to cover fields observed in real corpus (per the inventory below).
- [ ] `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` reports **zero disagreements** (modulo the 18 malformed-YAML files, which surface as a separate informational category).
- [ ] `just check` passes.
- [ ] `uv run spec-driver validate` produces baseline-identical output (8 audit-gate warnings, modulo install-skew noise).
- [ ] 18 malformed-YAML files logged as either drift entries or backlog issues (one per file or grouped as appropriate); list captured in `../notes.md` P02.5 section.
- [ ] `notes.md` carries a P02.5 closure section: per-declaration additions, before/after harness output, drift-entry references for malformed YAML.
- [ ] No code changes outside the six `*_metadata.py` files (and any one-off corpus fixes that arise; flag any such fixes for `/consult` if they go beyond trivial typos).

## 5. Verification

- **Tests** (additive, light):
  - Existing per-block metadata tests continue to pass; widening declarations should not break any test that asserts a specific *field is accepted* — only those that assert *field is rejected* (none expected, since the metadata path was lax pre-DE-118).
  - No new test files. The harness IS the verification surface for P02.5.
- **Tooling**:
  - `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` — primary gate.
  - `just check` — full lint + test gate.
  - `uv run spec-driver validate` — baseline-diff (must equal `validate-baseline.txt`).
- **Evidence to capture**:
  - Pre-P02.5 disagreement count (already in P02 notes).
  - Per-declaration disagreement-delta after each patch.
  - Final harness output (zero disagreements) pasted into `../notes.md`.

## 6. Assumptions & STOP Conditions

### Assumptions

- The disagreement inventory captured in P02 (and in this user's `/consult` summary) is complete and accurate. **Re-run the harness as the first task of P02.5** to confirm the count and field set before patching anything.
- Widening a `BlockMetadata` declaration with a field already silently accepted by the lax hand-rolled validator cannot regress any existing test. (If it does, the test was asserting *more* than the lax validator enforced — a separate finding worth `/consult`.)
- The 18 malformed-YAML files are pre-existing data bugs unrelated to validator drift. **Confirm via spot-check** during P02.5 setup; if any file's malformed-ness is actually a metadata-vs-data mismatch dressed up as YAML noise, escalate.
- The `interactions[].description` patch already in `supekku/scripts/lib/blocks/spec_metadata.py` (uncommitted at P02.5 entry) is the kind of widening P02.5 should ship. The phase commits it as part of the fidelity batch — but only after the audit-trail decision in §6 below resolves.

### Audit-trail decision (must resolve at P02.5 entry)

The `interactions[].description` patch was made during P02 mid-investigation, before the P02.5 phase was authored. Two options for keeping the audit trail honest:

- **(a) Revert + re-land**: revert the patch (cleanest), re-run the harness to capture the *true* P02-baseline disagreement count, then re-land the patch as part of the P02.5 batch. Audit trail: P02 = mechanism + harness; P02.5 = all fidelity widening including this one.
- **(b) Leave + document**: keep the patch in P02; note in `../notes.md` that one fidelity patch jumped the gun; harness output reflects post-patch state with all other disagreements unaffected.

**Default recommendation: (a) revert + re-land**. Cost is a few minutes; clarity is durable.

### STOP when

- A widening adds a field to a declaration that *should not* be there per any existing spec or schema authority. That is tightening territory (DE-137); escalate via `/consult` rather than narrowing the declaration unilaterally.
- The harness reports more than zero disagreements after all six declarations are patched — implies a missed field, a one-off artefact deviation, or a parser issue. Investigate before closing.
- A malformed-YAML file turns out to be a real schema violation rather than a YAML-syntax issue. Reclassify and route to drift / backlog appropriately.
- Any test fails after a widening patch. The widening is supposed to be subtractive on the validator's reject-set; a failing test indicates a deeper assumption mismatch.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.5.0 | Resolve audit-trail decision (§6); revert (or keep) `interactions[].description` patch | no (gate) | Reverted; re-landed in 2.5.8/2.5.9 |
| [x] | 2.5.1 | Re-run harness to capture true P02-baseline disagreement set; commit inventory to `../notes.md` | no (depends on 2.5.0) | True baseline = 39 (not 30; patch had been masking 9 cases) |
| [x] | 2.5.2 | Widen `PHASE_OVERVIEW_METADATA` — add top-level `name`, `status` | yes (after 2.5.1) | True observed gap was just `name` + `status`; the larger field list in original draft was tracking territory |
| [x] | 2.5.3 | Widen `PHASE_TRACKING_METADATA` — top-level `status/started/completed/last_updated/tasks_completed/tasks_total/tasks_done/tasks_blocked/notes/progress`; `tasks[].notes`; `entrance_criteria[].notes`/`exit_criteria[].notes`; `progress[]` shape with `notes` plural-form alias | yes | Largest patch; covered all 12 disagreements |
| [x] | 2.5.4 | Widen `PLAN_OVERVIEW_METADATA` — `phases[].status`, `phases[].completion_date`, `phases[].notes` | yes | 8 disagreements covered |
| [~] | 2.5.5 | `SPEC_CAPABILITIES_METADATA` (originally listed 5 disagreements) | n/a | **No real disagreements.** Original count was malformed-YAML files counted under same artefact. Skipped. |
| [~] | 2.5.6 | `VERIFICATION_COVERAGE_METADATA` (originally listed 4 disagreements) | n/a | **No real disagreements.** Same as 2.5.5; all 4 were malformed-YAML. Skipped. |
| [x] | 2.5.7 | Widen `DELTA_RELATIONSHIPS_METADATA` — top-level `backlog_items` (DE-015); `phases[].goal`, `phases[].status` (DE-007 legacy authoring) | yes | 2 disagreements covered |
| [x] | 2.5.8 | `SPEC_RELATIONSHIPS_METADATA` `interactions[].summary` (PROD-009) — patched the artefact (`summary` → `description`) | yes | One-off; declaration not widened |
| [x] | 2.5.9 | Re-land `interactions[].description` (covers 8 specs) | no | Bundled with the SPEC_RELATIONSHIPS_METADATA widening |
| [x] | 2.5.10 | Log 18 malformed-YAML files | yes | Captured in `../notes.md` P02.5 section; recommend single backlog issue |
| [x] | 2.5.11 | Final gate: harness 0 disagreements; lint clean; tests passing; baseline-diff identical | no (closure) | Pending commit by owner |

### Task notes

- **2.5.5 / 2.5.6** carry "uninvestigated" tags from the original `/consult` summary — first action is to enumerate the observed extras from the harness diff, then patch. Do **not** speculate; the harness output is the authoritative inventory.
- **2.5.8** is the exception to the widening pattern. `interactions[].summary` appears in PROD-009 only; the field name suggests it was a one-off authoring choice, not a contract field. Patch the artefact (rename `summary` → `description` or remove) rather than widening the declaration. Confirm during the task.
- **2.5.10** does not block 2.5.11. If a malformed-YAML file proves to be a real schema violation rather than a YAML bug, reclassify it; otherwise it ships as a drift entry or backlog issue and the harness's separate "malformed YAML" count surfaces non-gating.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| **R-P025-1** Widening misses a field — harness still reports disagreements after the batch lands. | Re-run harness after each declaration patch; closure gate is zero. | open |
| **R-P025-2** Widening adds a field that shouldn't be there per spec authority — silently encodes a contract drift as canonical. | Cross-check each new field against existing schema docs, ADRs, and the blocks' inferred semantics. When in doubt, escalate via `/consult` rather than widening unilaterally. | open |
| **R-P025-3** Test failure after widening — indicates a test was asserting more than the lax validator enforced. | Investigate per failure; do not soften the test without `/consult`. | open |
| **R-P025-4** Malformed-YAML file is actually a schema violation, not a YAML syntax bug. | Spot-check during 2.5.10; reclassify if so. | open |
| **R-P025-5** Patching `interactions[].summary` artefact (PROD-009) introduces a cascading rename across other documents. | Verify with `rg "summary:" PROD-009.md` and check no other artefact depends on the field name; if it does, defer the rename and widen the declaration after all. | open |

## 9. Decisions & Outcomes

- `2026-05-09` — **P02.5 phase inserted** between P02 and P03 (this phase). Rationale: DR-118 §2 premise correction; harness's job is to surface drift; fixing drift is separable work from mechanism (P02) and retirement (P03). Detailed reasoning in the `/consult` thread that authored this phase.
- `2026-05-09` — **Future tightening explicitly deferred to DE-137** per DR-136 §11.3. P02.5 widens only; never narrows. Any tightening would be premature for DE-118's behaviour-preservation contract.
- `2026-05-09` — **Audit-trail decision resolved**: reverted the in-flight `interactions[].description` patch, captured the true 39-disagreement baseline (not 30 — patch had been masking 9 cases), then re-landed the field as part of the SPEC_RELATIONSHIPS_METADATA widening in this phase. Clean ledger.
- `2026-05-09` — **`spec.capabilities` and `verification.coverage` have no fidelity gap.** The original `/consult` summary's "5 + 4 disagreements" was a misread of harness output: those counts reflect MALFORMED entries (YAML parse errors), not DISAGREEMENT entries (verdict mismatches). The metadata declarations for these two block types match observed reality already. No widening required.
- `2026-05-09` — **PROD-009 `interactions[].summary` patched in artefact, not declaration.** Field appeared in PROD-009 only (one-off authoring drift). Renaming to `description` aligns with the contract field used everywhere else.

## 10. Findings / Research Notes

P02 closure provides the disagreement inventory. P02.5 commences by re-running the harness to confirm the inventory is current, then patches per the task list. Findings during P02.5 land here:

- Per-declaration before/after disagreement counts.
- Field-by-field rationale for widening (especially for any field that *almost* shouldn't be there).
- Malformed-YAML triage outcomes.
- Any one-off artefact patches (analogous to 2.5.8) and their rationale.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied (all items in §4).
- [x] Verification evidence stored: harness 0-disagreement output appended to `../notes.md`; per-declaration deltas captured.
- [x] Spec/Delta/Plan updated: phase-02.5 sheet status `draft` → `completed`; IP-118 progress flag pending commit.
- [x] Hand-off note to IP-118-P03 in `../notes.md` final paragraph: P02.5 fidelity landed; harness green; P03 may begin per DR-118 §4 ordering (VerificationCoverageValidator first).
