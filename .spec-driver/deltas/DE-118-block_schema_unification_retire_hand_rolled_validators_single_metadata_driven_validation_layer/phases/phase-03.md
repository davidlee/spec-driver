---
id: IP-118-P03
slug: "118-block_schema_unification_retire_hand_rolled_validators_single_metadata_driven_validation_layer-phase-03"
name: IP-118 Phase 03
created: "2026-05-10"
updated: "2026-05-10"
status: draft
kind: phase
plan: IP-118
delta: DE-118
---

# Phase 03 — Per-block migration

## 1. Objective

Retire the seven hand-rolled `*Validator` classes in coupling-depth order (DR-118 §4) across **five swap commits**. Each commit dual-validates the affected block type via curated corpus + the snapshot harness, swaps the loader call site to `MetadataValidator(<METADATA>, strict_unknown_keys=True)`, deletes the hand-rolled class, and removes the corresponding entry from `HAND_ROLLED_ADAPTERS` in `snapshot_compare.py`. Two thin wrapper helpers preserve parent-context ID-equality checks (`validate_delta_relationships`, `validate_spec_relationships`); a third wrapper (`validate_spec_capabilities`) lands as ergonomic symmetry, not retirement.

Concretely, P03 ships:

1. **C1** — Retire `VerificationCoverageValidator` (zero external sites; densest unit-test coverage).
2. **C2** — Retire plan trio in one commit: `PlanOverviewValidator`, `PhaseOverviewValidator`, `PhaseTrackingValidator` (shared module; no external sites; no ID kwargs).
3. **C3** — Retire `DeltaRelationshipsValidator`; introduce `validate_delta_relationships(block, *, delta_id)` wrapper; migrate 3 external call sites (`changes/artifacts.py:122`, `requirements/registry.py:243`, `requirements/sync.py:11/132/171`).
4. **C4** — Retire `RelationshipsBlockValidator`; introduce `validate_spec_relationships(block, *, spec_id)` wrapper; introduce `validate_spec_capabilities(block, *, spec_id)` ergonomic helper (no class retired); migrate 1 external call site (`requirements/registry.py:162`).
5. **C5** — Retire `RevisionBlockValidator` and the module-level `_disallow_extra_keys` helper; migrate 2 external call sites (`requirements/sync.py:211`, `changes/updater.py:135`); remove re-export at `changes/blocks/__init__.py:48,57`.

After C5, zero `*Validator` classes from the original seven remain, and `HAND_ROLLED_ADAPTERS` is empty (or the harness module retires — decided at C5).

## 2. Links & References

- **Delta**: DE-118
- **Design Revision Sections**: DR-118 §2 (premise correction note), §4 ("Phase 2 — Per-block migration", "Ordering principle", "ID-kwarg wrappers"), §5 (verification matrix, transitional invariants), §7 DEC-001 / DEC-004 / DEC-007, §8 OQ-HARNESS-LIFECYCLE, §9 R3 / R5 / R7 / R8.
- **Specs / PRODs**: SPEC-114 (blocks/metadata; primary), SPEC-115 (changes/blocks; secondary), SPEC-116 (frontmatter_metadata; pattern reference).
- **Support Docs**:
  - `../notes.md` — P01 inventory (per-validator external-site / ID-kwarg / test-file enumeration); P02.5 closure (declaration-fidelity patches that unblock P03); the "Findings that refine DR-118 §4" section calls out three nuances P03 commit messages must honour.
  - `validate-baseline.txt` — pre-merge gate diff target (8 audit-gate warnings + install-skew noise).
  - `snapshot_compare.py` (`supekku/scripts/lib/blocks/metadata/snapshot_compare.py`) — adapter map at `HAND_ROLLED_ADAPTERS` is the per-commit edit point.

## 3. Entrance Criteria

- [x] IP-118-P02 complete (foundations landed; harness operational; commits `32578038`, `87e03178`, `e81baa72`).
- [x] IP-118-P02.5 complete (declaration fidelity; harness reports zero disagreements; commit `6cba9749`).
- [x] `just check` green at HEAD; `spec-driver validate` baseline-identical at HEAD.
- [x] DR-118 §4 ordering and ID-kwarg wrapper sketches current — premise note (§2) + DEC-001 note already applied during P02.5.
- [x] No outstanding `/consult` thread on DE-118 design.

## 4. Exit Criteria / Done When

- [ ] All five P03 swap commits landed on `main` within R8's ≤4-week window (counted from C1 merge).
- [ ] Zero of the seven hand-rolled `*Validator` classes remain in `supekku/scripts/lib/blocks/`.
- [ ] `HAND_ROLLED_ADAPTERS` in `snapshot_compare.py` is empty (or the harness module is decommissioned per P04 cleanup — see §10 hand-off).
- [ ] Three wrapper helpers exist alongside their metadata declarations:
  - `validate_delta_relationships(block, *, delta_id)` — `delta_metadata.py` (or sibling); ID-equality check retained.
  - `validate_spec_relationships(block, *, spec_id)` — `spec_metadata.py` (or sibling); ID-equality check retained.
  - `validate_spec_capabilities(block, *, spec_id)` — `spec_metadata.py` (or sibling); ergonomic alias only (no ID-equality check; `spec.capabilities` block has no `spec` field).
- [ ] All 5 external call-site migrations landed (DR-118 §4 enumeration plus the `requirements/sync.py:132` annotation surfaced in P01).
- [ ] `re-exports`/`__all__` cleaned up:
  - `revision.py:1059` no longer lists `RevisionBlockValidator`.
  - `revision.py:1055` retains `REVISION_BLOCK_JSON_SCHEMA` for now (delete is P04 task).
  - `changes/blocks/__init__.py:48,57` no longer re-exports `RevisionBlockValidator`.
  - `delta.py:171`, `relationships.py:273`, `verification.py:281`, `plan.py:667-671` no longer list their respective hand-rolled classes.
- [ ] `just check` passes after every commit.
- [ ] `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` returns 0 (zero disagreements) after every commit. After C5, the run is metadata-only across all block types — no dual-validation remains, but the report.ok contract holds.
- [ ] `uv run spec-driver validate` produces baseline-identical output after every commit (8 audit-gate warnings, modulo install-skew noise).
- [ ] Commit messages enumerate retired classes + migrated call sites (per DR-118 §4 §5 transitional-invariant text).
- [ ] `notes.md` records per-commit harness output (one short block per commit) and any drift surfaced.

## 5. Verification

- **Curated parallel-test corpora** (per DEC-007; one corpus per metadata declaration, eight total):
  - `verification_metadata_test.py` — already present; extend with positive paths + every negative branch in `verification.py:43+` source.
  - `plan_metadata_test.py` — already covers `PlanOverview` (line 36) and `PhaseOverview` (line 354); **extend to cover `PhaseTracking`** (currently absent — gap surfaced in `notes.md` §4 finding 3). Either inline in `plan_metadata_test.py` or new `tracking_metadata_test.py`; phase implementer decides at C2.
  - `delta_metadata_test.py` — already present; extend with corpus exercising `delta_id` ID-equality wrapper path.
  - `spec_metadata_test.py` (or new `relationships_metadata_test.py`) — **must be created** at C4. Cover both `SPEC_RELATIONSHIPS_METADATA` and `SPEC_CAPABILITIES_METADATA` corpora plus the `spec_id` wrapper ID-equality check.
  - `revision_metadata_test.py` — already present; extend with the four `REVISION_BLOCK_JSON_SCHEMA` regex-bug cases (DR-118 §5 explicit requirement).
- **Per-commit gates** (apply identically to C1–C5):
  - Add/extend the relevant corpus (positive paths + every hand-rolled negative branch + applicable regex-bug cases).
  - Tests green dual-asserting (parallel test imports both validators) before swap.
  - Swap the loader call site; delete the hand-rolled class; trim parallel-test file to MetadataValidator-only assertions; update the corresponding `__all__`; remove the entry + import from `snapshot_compare.HAND_ROLLED_ADAPTERS`.
  - `just check` green.
  - `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` → 0 disagreements.
  - `uv run spec-driver validate` baseline-diff clean.
  - `just pylint-files <changed-files>` — no new pylint regressions on touched files.
- **Evidence to capture**:
  - Per-commit harness output appended to `notes.md` under a "P03 progress" section.
  - Final P03 closure entry summarising 5/5 commit hashes + line-count delta + any drift handled.
  - `validate-baseline.txt` is **not** updated — it is the unchanged regression target per DR-118 §5.
- **Test transitions** (DEC-007 limitation acknowledged): each post-swap corpus file carries the header comment `# Captures hand-rolled <Validator> behaviour as of DE-118; tightening or relaxing rules is an *intended* drift event handled in the delta that introduces it.`

## 6. Assumptions & STOP Conditions

### Assumptions

- The harness baseline at HEAD remains 0 disagreements throughout P03. Each swap commit removes its block type from `HAND_ROLLED_ADAPTERS` so the harness no longer dual-validates that type — it transitions to metadata-only counting (`Report.blocks_metadata_only`). The contract holds because `Disagreement` records require both adapters; once the hand-rolled side is gone, no disagreement can be produced for that type.
- Each retiring class's `validate(...)` returns `list[str]` or `list[ValidationMessage]` whose truthiness maps cleanly to "rejection" (verdict semantics in DEC-007). Confirmed for all seven by P01 inventory.
- `MetadataValidator` produces equivalent verdicts on every block instance touched by `.spec-driver/` corpus, given the P02.5 declaration widenings. Confirmed empirically at HEAD via the harness — but each swap is a fresh proof point at the unit level via curated corpus.
- The two wrapper helpers (`validate_delta_relationships`, `validate_spec_relationships`) keep the ID-equality check exactly as the hand-rolled class enforced it — including `if delta_id is None: skip` semantics (only check when caller provides it). Reproduce the conditional, not just the equality, to preserve partial-context callers.
- `validate_spec_capabilities` is ergonomic only: `spec.capabilities` block has **no `spec` field at the data layer** (per `notes.md` §3.3); the wrapper's `spec_id` parameter is unused except for caller-API symmetry. Document the asymmetry explicitly at the wrapper docstring; do not introduce a fake ID-equality check.
- Commit boundaries match DR-118 §4 ordering. Reordering for tactical convenience is allowed only if the harness report stays at 0 disagreements after each commit (it must — coupling-depth order minimises blast radius regardless of ordering).

### STOP when

- The snapshot harness reports a non-zero disagreement count at any commit boundary. Implies either declaration drift between P02.5 close and the swap, or a real semantic divergence the corpus did not catch. Escalate via `/consult`; do not proceed.
- `spec-driver validate` produces a NEW warning/error (beyond the 8 audit-gate baseline + install-skew noise). Implies an unintended semantic change. Investigate and resolve before commit lands.
- A retiring class turns out to have an external-state check not surfaced in P01 inventory (e.g. a registry lookup, file-system access, or implicit cross-block reference). Wrap it with a thin helper; do not attempt to express it inside `MetadataValidator`. If the wrapper grows beyond ~10 lines, escalate via `/consult`.
- A wrapper helper is needed for an unexpected fourth case (i.e. the C1, C2, or C5 commits surface ID-kwarg semantics not previously catalogued). Escalate.
- Phase 2 (this phase) accumulates partial-stall risk — fewer than 5 commits landed and the wall-clock has reached 4 weeks since C1. Per R8: complete the remaining commits or revert the landed swaps to restore single-system state. Surface to user before either path.
- A test-file split decision (C2's `tracking_metadata_test.py` vs extending `plan_metadata_test.py`; C4's new `relationships_metadata_test.py`) reveals a deeper layering issue. Document the choice in §9; no escalation needed.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ]    | 3.1 | **C1** — Retire `VerificationCoverageValidator` | no (sequencing) | Smallest blast radius; densest unit-test coverage. |
| [ ]    | 3.2 | **C2** — Retire plan trio (`PlanOverviewValidator`, `PhaseOverviewValidator`, `PhaseTrackingValidator`) in one commit | no (after C1) | Includes `tracking_metadata_test.py` decision (extend `plan_metadata_test.py` vs new file). |
| [ ]    | 3.3 | **C3** — Retire `DeltaRelationshipsValidator`; introduce `validate_delta_relationships` wrapper | no (after C2) | 3 external call sites; `sync.py:132` annotation must be migrated alongside `:171` callsite. |
| [ ]    | 3.4 | **C4** — Retire `RelationshipsBlockValidator`; introduce `validate_spec_relationships` + `validate_spec_capabilities` (ergonomic) wrappers | no (after C3) | Create `relationships_metadata_test.py` (or sibling) — currently absent. |
| [ ]    | 3.5 | **C5** — Retire `RevisionBlockValidator` and `_disallow_extra_keys` helper | no (after C4) | Largest blast radius: 2 external sites + `__all__` re-export removal. |
| [ ]    | 3.6 | Wrap-up — `notes.md` P03 closure section; IP-118 progress tick; harness final state recorded | yes (after 3.5) | Hand-off to P04. |

### Task Details

- **3.1 C1 — Retire `VerificationCoverageValidator`**
  - **Design / Approach**: Direct swap. No external call sites; no ID kwargs (P01 confirmed). `verification.py:43+` class deleted; `verification.py:281` `__all__` entry removed. Loader at `verification.py:43` (or wherever wired) replaced with `MetadataValidator(VERIFICATION_COVERAGE_METADATA, strict_unknown_keys=True)`. Adapter `_adapt_verification_coverage` + import removed from `snapshot_compare.py`.
  - **Files / Components**: `supekku/scripts/lib/blocks/verification.py`, `verification_test.py` (trim hand-rolled assertions; keep MetadataValidator-only paths), `verification_metadata_test.py` (extend corpus per DEC-007), `snapshot_compare.py:51-54,78-81,100-108`.
  - **Testing**: `verification_metadata_test.py` corpus covers every negative branch in current `VerificationCoverageValidator.validate(...)`. Existing 25-instantiation `verification_test.py` is the source of negative cases — port them, then delete the hand-rolled-only test file (or trim it down).
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `feat(DE-118): retire VerificationCoverageValidator (P03 C1)`; reference DR-118 §4.

- **3.2 C2 — Retire plan trio**
  - **Design / Approach**: All three classes share `plan.py`. Single commit. No external call sites; no ID kwargs (P01 confirmed). Three loader sites in `plan.py` swapped to `MetadataValidator(<META>, strict_unknown_keys=True)`. Three `__all__` entries removed at `plan.py:667-671`. Three adapters + their imports removed from `snapshot_compare.py`.
  - **Files / Components**: `supekku/scripts/lib/blocks/plan.py`, `plan_metadata_test.py` (extend with `PhaseTracking` corpus OR add new `tracking_metadata_test.py`), `tracking_test.py` (port negative cases then trim), `snapshot_compare.py:37-44,83-95,100-108`.
  - **Testing**: phase implementer decides where the `PhaseTracking` corpus lives. Recommendation: extend `plan_metadata_test.py` (single file matches the single-`plan.py` source). If ≥10 corpus cases, factor into `tracking_metadata_test.py` to keep the overview file readable.
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `feat(DE-118): retire plan trio validators (P03 C2)`.

- **3.3 C3 — Retire `DeltaRelationshipsValidator` + wrapper**
  - **Design / Approach**: Author `validate_delta_relationships(block, *, delta_id)` per DR-118 §4 sketch. Place alongside `DELTA_RELATIONSHIPS_METADATA` in `delta_metadata.py` (or sibling per local convention). Wrapper calls `MetadataValidator(...).validate(block.data)` then layers the `data["delta"] == delta_id` check (preserving the `if delta_id is None: skip` conditional from `delta.py:48-53`). Class `DeltaRelationshipsValidator` deleted; `delta.py:171` `__all__` updated. Three external call sites migrated (per `notes.md` §4 finding 1: `artifacts.py:122`, `registry.py:243`, **`sync.py:11/132/171`**). Harness adapter `_adapt_delta_relationships` + import removed from `snapshot_compare.py`.
  - **Files / Components**: `supekku/scripts/lib/blocks/delta.py`, `delta_metadata.py`, `changes/artifacts.py`, `requirements/registry.py`, `requirements/sync.py`, `delta_metadata_test.py`, `snapshot_compare.py:33-36,68-70,100-108`.
  - **Testing**: extend `delta_metadata_test.py` to cover wrapper paths: `delta_id` matches, `delta_id` mismatches, `delta_id is None` (skip ID check), wrapper returns combined errors in stable order.
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `feat(DE-118): retire DeltaRelationshipsValidator + introduce validate_delta_relationships (P03 C3)`.

- **3.4 C4 — Retire `RelationshipsBlockValidator` + two wrappers**
  - **Design / Approach**: Author `validate_spec_relationships(block, *, spec_id)` (preserves `data["spec"] == spec_id` check) and `validate_spec_capabilities(block, *, spec_id)` (ergonomic only — `spec.capabilities` block has no `spec` field; wrapper accepts `spec_id` for API symmetry but ignores it; document explicitly in docstring). Place both alongside their metadata declarations in `spec_metadata.py` (or sibling). Class `RelationshipsBlockValidator` deleted; `relationships.py:273` `__all__` updated. One external call site migrated (`requirements/registry.py:162`). Harness adapter `_adapt_spec_relationships` + import removed from `snapshot_compare.py`.
  - **Files / Components**: `supekku/scripts/lib/blocks/relationships.py`, `spec_metadata.py`, `requirements/registry.py`, **new** `supekku/scripts/lib/blocks/relationships_metadata_test.py` (or extend `spec_metadata_test.py` if present), `snapshot_compare.py:45-48,73-75,100-108`.
  - **Testing**: file is new — bring it up with both `SPEC_RELATIONSHIPS_METADATA` and `SPEC_CAPABILITIES_METADATA` corpora. Cover positive + negative branches from `relationships.py:32+` source. Cover wrapper paths: `spec_id` match/mismatch/None for `validate_spec_relationships`; `spec_id` ignored for `validate_spec_capabilities`. Existing coverage of this validator is thin (P01 found no standalone `relationships_test.py`); harness + new corpus are the safety net.
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `feat(DE-118): retire RelationshipsBlockValidator + introduce spec wrappers (P03 C4)`.

- **3.5 C5 — Retire `RevisionBlockValidator`**
  - **Design / Approach**: Loader sites in `revision.py` swapped to `MetadataValidator(REVISION_CHANGE_METADATA, strict_unknown_keys=True)`. Class `RevisionBlockValidator` deleted (`revision.py:362+`); module-level `_disallow_extra_keys` helper deleted (`revision.py:350`); `revision.py:1059` `__all__` entry removed. Two external call sites migrated (`requirements/sync.py:211`, `changes/updater.py:135`). Re-export at `changes/blocks/__init__.py:48,57` removed. Harness adapter `_adapt_revision` + import removed from `snapshot_compare.py`. Note: `REVISION_BLOCK_JSON_SCHEMA` (revision.py:28) **stays** at this commit — its deletion is P04 work (bundled with the four regex-bug case removal).
  - **Files / Components**: `supekku/scripts/lib/blocks/revision.py`, `changes/blocks/__init__.py`, `requirements/sync.py`, `changes/updater.py`, `revision_test.py` (trim hand-rolled assertions; keep MetadataValidator-only paths), `revision_metadata_test.py` (extend with the four regex-bug cases — DR-118 §5 explicit requirement), `snapshot_compare.py:49,64-66,100-108`.
  - **Testing**: revision test surface is the largest of the seven; carefully port negative cases. The four `REVISION_BLOCK_JSON_SCHEMA` regex-bug cases (e.g. `r"^RE-\\d{3,}$"`) are landmark cases — confirm `MetadataValidator` accepts the previously-blocked-by-regex inputs (regex bug means the hand-rolled validator was over-rejecting; metadata-driven path now correctly accepts).
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `feat(DE-118): retire RevisionBlockValidator + remove changes/blocks re-export (P03 C5)`.

- **3.6 Wrap-up**
  - **Design / Approach**: After C5, decide on `snapshot_compare.py` lifecycle. Three options: (a) keep with empty `HAND_ROLLED_ADAPTERS` as no-op-but-runnable infrastructure (defers OQ-HARNESS-LIFECYCLE to P04); (b) decommission the harness module + its tests (closes OQ-HARNESS-LIFECYCLE early); (c) repurpose the harness as a metadata-only smoke test against `.spec-driver/`. Default: (a) — keep, defer the lifecycle decision to P04 alongside OQ-NAMING-COLLISIONS work.
  - **Files / Components**: `notes.md` (closure section), `IP-118.md` (§9 progress tracking).
  - **Testing**: `just check` green at HEAD; harness still runs (zero disagreements; possibly zero dual-validations).
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `chore(DE-118): close IP-118-P03 — 7 hand-rolled validators retired across 5 commits`.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| **R1** Hand-rolled subtle semantics not in BlockMetadata | Per-validator inventory done in P01; ID-kwarg wrappers handle the two confirmed cases; STOP-condition triggers if a third surfaces | open |
| **R3** External call site missed at swap | P01 enumeration; commit messages enumerate sites; `notes.md §4 finding 1` corrects the `sync.py:132` annotation gap | open |
| **R5** Helper-shape mismatch on swap | Per-commit corpus + harness re-run catches shape drift before commit lands | open |
| **R7** `_entry_shape` migration is new enforcement | Vacuous in this repo (P01 §2: zero `workflow.sessions` instances); P03 sessions swap is **not** part of P03 — `_entry_shape` replacement is a P04 cleanup task | resolved (vacuous) |
| **R8** Phase 2 partial-stall (≤4 weeks then revert) | Wall-clock tracking begins at C1 merge; STOP-condition surfaces at week-3 if <3/5 commits landed | open |
| **R9** Metadata declarations narrower than observed contract | Resolved at P02.5 close; harness baseline 0 at P03 entry. Re-checked at every commit boundary | resolved |
| **NEW R10** Wrapper-helper API drift | Three wrappers (`validate_delta_relationships`, `validate_spec_relationships`, `validate_spec_capabilities`) introduce new public surface. **Mitigation**: place alongside metadata declarations (not in a new module); name conventions match metadata declaration names; no re-exports added through `changes/blocks/__init__.py`; document the `validate_spec_capabilities` ergonomic-only nature explicitly. | open |
| **NEW R11** Test-file split asymmetry | C2 plan trio and C4 relationships have different test-file states (extend vs create new). Risk of the "where do these tests live" question recurring per call site. **Mitigation**: phase implementer documents the choice in §9 once made; `notes.md` records the convention for future block-validator migrations (DE-137, DE-142). | open |

## 9. Decisions & Outcomes

- `2026-05-10` — **Per-commit structure** decided as: parallel-test corpus + swap + delete + adapter-map prune in **one commit per validator** (5 commits total, with C2 grouping the plan trio per DR-118 §4). Rationale: a precursor "add corpus only" commit gives reviewer leverage but doubles ceremony; the swap commit itself is small enough that reviewing corpus + swap together is tractable and the harness's continuous 0-disagreement gate provides external proof.
- `2026-05-10` — **`validate_spec_capabilities` scope** decided as ergonomic helper, not retirement. `spec.capabilities` is already metadata-only (no hand-rolled validator class exists per P01 §3.3); the wrapper exists for API symmetry with `validate_spec_relationships`. Wrapper docstring explicitly notes the asymmetry (no ID-equality check; `spec_id` parameter accepted but unused).
- `2026-05-10` — **Harness lifecycle deferred** to P04. After C5, `HAND_ROLLED_ADAPTERS` is empty but the module remains runnable; OQ-HARNESS-LIFECYCLE settles in P04 alongside OQ-NAMING-COLLISIONS and `REVISION_BLOCK_JSON_SCHEMA` deletion.
- `2026-05-10` — **`notes.md §4 finding 1`** flagged: P03 C3 commit must enumerate `requirements/sync.py:11/132/171` (annotation + call site) in addition to the DR-118 §3 sites.

## 10. Findings / Research Notes

- Wrapper helpers are placed alongside metadata declarations (e.g. `delta_metadata.py`, `spec_metadata.py`) — keeps `MetadataValidator` pure (block-only) and avoids a new module. POL-003 boundary respected.
- After C5, `snapshot_compare.py` becomes a metadata-only health check (the `HAND_ROLLED_ADAPTERS` map is empty; the harness still scans the corpus and reports `blocks_metadata_only` count). This is intentional — leaves the diagnostic infrastructure intact for future schema work without forcing a P04 deletion choice now.
- Per `notes.md §3.3`, no standalone `blocks/relationships_test.py` exists. The hand-rolled `RelationshipsBlockValidator` was historically tested only via integration through `requirements/registry.py` callers. C4's new `relationships_metadata_test.py` therefore *adds* test coverage rather than replacing it. Net P03 effect: tightened unit-test surface for the relationships block.

## 11. Wrap-up Checklist

- [ ] All five swap commits landed; zero hand-rolled validator classes remain.
- [ ] Three wrapper helpers in place (`validate_delta_relationships`, `validate_spec_relationships`, `validate_spec_capabilities`).
- [ ] `HAND_ROLLED_ADAPTERS` empty in `snapshot_compare.py`.
- [ ] `notes.md` records P03 closure with per-commit harness output and final commit hash list.
- [ ] `IP-118.md` §9 progress tracking ticks "IP-118-P03 complete".
- [ ] `just check` green at HEAD.
- [ ] `spec-driver validate` baseline-identical at HEAD.
- [ ] Harness final state at HEAD recorded (expected: 0 disagreements, ~0 dual-validations, all blocks counted as `blocks_metadata_only`).
- [ ] Hand-off to IP-118-P04 noted: `REVISION_BLOCK_JSON_SCHEMA` deletion + `_entry_shape` replacement + OQ-NAMING-COLLISIONS rename + OQ-HARNESS-LIFECYCLE settlement.
