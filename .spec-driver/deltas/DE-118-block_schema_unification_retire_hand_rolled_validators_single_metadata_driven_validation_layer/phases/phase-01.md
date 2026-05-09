---
id: IP-118-P01
slug: "118-block_schema_unification_retire_hand_rolled_validators_single_metadata_driven_validation_layer-phase-01"
name: IP-118 Phase 01
created: "2026-05-09"
updated: "2026-05-09"
status: completed
kind: phase
plan: IP-118
delta: DE-118
---

# Phase 01 — Inventory & Baseline

## 1. Objective

Pure discovery and pre-flight. No code changes. Produce the inventory artefacts and baselines that downstream phases depend on:

1. Per-validator external call site inventory (all 7 retiring classes).
2. Per-validator cross-block / ID-kwarg / external-state check inventory.
3. Per-validator test-fixture and `__all__` / re-export site inventory.
4. `spec-driver validate` baseline against this repo (regression reference for every subsequent commit).
5. Live-corpus pre-check for the `_entry_shape` → `additional_properties` migration (R7 mitigation): validate existing `workflow.sessions` data against `_SESSION_ENTRY` shape; resolve divergences or document as a curated test case.

## 2. Links & References

- **Delta**: DE-118
- **Design Revision Sections**: DR-118 §3 (target outcomes), §4 ("Phase 2 — Ordering principle" + "Pre-Phase-2 inventory tasks" + "ID-kwarg wrappers"), §5 (verification matrix + "Validation baseline mechanism"), §9 (R3, R7, R8).
- **Specs / PRODs**: SPEC-114, SPEC-115, SPEC-116.
- **Support Docs**: IMPR-035 (workflow.* deferral); DR-136 §11.1, §11.3 (boundaries).

## 3. Entrance Criteria

- [x] DR-118 approved (two adversarial review passes integrated 2026-05-09).
- [x] DE-118.md reconciled with DR-118.
- [x] IMPR-035 created and populated.
- [x] No outstanding `/consult` thread on DE-118 design.

## 4. Exit Criteria / Done When

- [x] **Inventory artefact committed** at `.spec-driver/deltas/DE-118-.../notes.md`. Per-validator sections cover external call sites, ID-kwarg / external-state checks, test-fixture sites, `__all__` / re-export sites for all 7 retiring classes.
- [x] **`validate-baseline.txt`** committed at `.spec-driver/deltas/DE-118-.../validate-baseline.txt`. Captures exact `spec-driver validate` output verbatim (8 audit-gate warnings + install-skew noise).
- [x] **R7 pre-check resolved**: vacuous — no live `workflow.sessions` block instances exist anywhere in this repo. Synthetic-corpus requirement noted for P03 sessions swap. See notes.md §2.
- [x] **OQ-NAMING-COLLISIONS sites enumerated** for `RELATIONSHIPS_MARKER` (2 origin sites + 2 disambiguating re-export shims) and `VALID_STATUSES` (4 origin sites + 2 disambiguation patterns). See notes.md §5.
- [x] No code changes in this phase. `git diff` touches only `.spec-driver/`.

## 5. Verification

- **Tests**: none (no code).
- **Tooling**:
  - `uv run spec-driver validate > .spec-driver/deltas/DE-118-.../validate-baseline.txt 2>&1` to capture baseline.
  - Greps via `rg` (or `grep -rn`) for: each `*Validator` class name across `supekku/` and `.spec-driver/`; each `BlockMetadata` declaration's marker; `__all__` entries.
  - For R7: a one-shot Python REPL session (or scratch script) running `MetadataValidator(WORKFLOW_SESSIONS_METADATA, strict_unknown_keys=True)` against parsed `workflow.sessions` data; output captured into the inventory artefact.
- **Evidence to capture**:
  - Inventory tables in `notes.md` (one section per validator).
  - Verbatim `validate-baseline.txt`.
  - R7 pre-check output (paste into inventory under a clearly-marked subsection).

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - Live `workflow.sessions` data exists somewhere reachable (this repo's `.spec-driver/run/sessions/` or external corpus). If absent, R7 pre-check trivially passes; record this explicitly.
  - The 5 external call sites already enumerated in DR-118 §4 (`requirements/sync.py:211`, `changes/updater.py:135`, `changes/blocks/__init__.py:48,57`, `requirements/registry.py:162,243`, `changes/artifacts.py:122`) are the canonical list; this phase verifies completeness, not discovery from scratch.
- **STOP when**:
  - Inventory uncovers a *7th* class with non-trivial external-state coupling not anticipated by DR-118 §4 (escalate to `/consult`; may require DR-118 revision).
  - R7 pre-check surfaces ≥10 divergences (suggests the migration is *not* behaviour-preserving for sessions; escalate to `/consult` and possibly defer the sessions-related work to IP-118-P04 cleanup or to DE-137).
  - Baseline capture itself fails (e.g. validator crash on current state — would block everything; escalate immediately).

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Capture `validate-baseline.txt` | no (precedes all other inventory work — it's the regression reference) | 8 audit-gate warnings + 2 lines install-skew noise |
| [x] | 1.2 | Inventory: `RevisionBlockValidator` (sites, kwargs, tests, exports) | yes | direct-swap candidate; parallel-test exists |
| [x] | 1.3 | Inventory: `DeltaRelationshipsValidator` (incl. ID-kwarg semantics) | yes | wrapper required; sync.py annotation site found (DR-118 §4 omitted) |
| [x] | 1.4 | Inventory: `RelationshipsBlockValidator` (incl. `spec_id` semantics) | yes | wrapper required; **no parallel-test exists** (P03 must add) |
| [x] | 1.5 | Inventory: `VerificationCoverageValidator` | yes | confirmed: zero external sites; densest unit-test coverage |
| [x] | 1.6 | Inventory: plan trio | yes | all three pure structural; **no `tracking_metadata_test.py`** (P03 must add) |
| [x] | 1.7 | R7 pre-check: validate live `workflow.sessions` data against `_SESSION_ENTRY` | yes (after 1.1) | vacuous — no live consumer data exists in this repo |
| [x] | 1.8 | Opportunistic: enumerate `RELATIONSHIPS_MARKER` and `VALID_STATUSES` collision sites | yes | feeds OQ-NAMING-COLLISIONS for P04; sites recorded in notes.md §5 |
| [x] | 1.9 | Consolidate inventory into `notes.md`; commit | no | this commit |

### Task Details

- **1.1 Capture `validate-baseline.txt`**
  - **Design / Approach**: `uv run spec-driver validate > validate-baseline.txt 2>&1` from the repo root, then `mv validate-baseline.txt .spec-driver/deltas/DE-118-.../`.
  - **Files / Components**: new file in delta dir.
  - **Testing**: visual review only — confirm output matches the 8 known audit-gate warnings + nothing else.
  - **Observations & AI Notes**: this is the regression reference for every subsequent commit; if the baseline ever changes during P02–P04 due to *unrelated* drift, capture a new baseline as part of that drift's resolution, not silently.
  - **Commits / References**: single commit "chore(DE-118): capture validate baseline for IP-118-P01".

- **1.2–1.6 Per-validator inventories**
  - **Design / Approach**: for each class, populate a sub-section in `notes.md` with: `External call sites`, `ID-kwarg / external-state checks`, `Test fixture sites`, `__all__ / re-export sites`. Use `rg` greps. Cross-check against DR-118 §4 for completeness.
  - **Files / Components**: write to `notes.md` only; touch no Python.
  - **Testing**: each inventory ends with a "completeness assertion": "no other instantiation site found across `supekku/`, `.spec-driver/`, and project root."
  - **Observations & AI Notes**: 1.5 (VerificationCoverageValidator) is the foundational confirmation — if it has hidden external-state coupling, the Phase 2 ordering needs revisiting.
  - **Commits / References**: one commit covering 1.2–1.6 + 1.8 if convenient: "chore(DE-118): inventory retiring validators for IP-118-P01".

- **1.7 R7 pre-check**
  - **Design / Approach**: load every `workflow.sessions` block reachable in this repo (look under `.spec-driver/run/sessions/` and any active session files) into Python; instantiate `MetadataValidator(WORKFLOW_SESSIONS_METADATA, strict_unknown_keys=True)` (note: this requires the IP-118-P02 code changes; for P01 the simpler approach is to *manually* check each block against `_SESSION_ENTRY`'s declared shape). If no live data exists, record "no live sessions data found; R7 vacuous" and proceed.
  - **Files / Components**: scratch script (not committed) or REPL session; output transcribed into `notes.md`.
  - **Testing**: divergences become curated corpus test cases for P03's `workflow.sessions` corpus (if any).
  - **Observations & AI Notes**: this is the load-bearing pre-check for the `_entry_shape` migration. If divergences are non-trivial, the design may need to add `min_entries` / per-entry `required` semantics earlier than OQ-NON-EMPTY-INVARIANT contemplates.
  - **Commits / References**: same commit as 1.2–1.6.

- **1.8 Opportunistic naming-collision enumeration**
  - **Design / Approach**: `rg "^RELATIONSHIPS_MARKER\s*=" supekku/`, `rg "^VALID_STATUSES\s*=" supekku/`. Record collision sites in inventory under "Phase 4 OQ-NAMING-COLLISIONS handover".
  - **Files / Components**: `notes.md`.
  - **Testing**: n/a.
  - **Commits / References**: same commit.

- **1.9 Consolidate + commit**
  - **Design / Approach**: ensure `notes.md` is internally coherent (TOC, per-validator sections, R7 subsection, P04 handover); single commit.
  - **Files / Components**: `notes.md` final form.
  - **Testing**: re-read end-to-end for completeness.
  - **Commits / References**: "chore(DE-118): close IP-118-P01 — inventory and baseline captured".

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Inventory misses an external site that surfaces only at P03 swap time | P03 swap commits delete the class — broken imports fail loudly at `just check`; treat as discovery, escalate to amend P03 commit | open |
| R7 pre-check requires P02 code (`additional_properties`) to run programmatically | manual shape-comparison against `_SESSION_ENTRY` text is sufficient for P01; programmatic re-check during P02 if divergences flagged | open |
| Live `workflow.sessions` data absent from this repo | record explicitly; phase still completes; acknowledge in inventory that DE-118 cannot pre-check sessions divergence | open |

## 9. Decisions & Outcomes

- `2026-05-09` — Phase scope confirmed as inventory + baseline only; no code. Rationale: DR-118 §4 pre-Phase-2 inventory tasks must produce documents *before* P02/P03 swap commits; folding into P02 would mix discovery with implementation and risk inventory items being overlooked under coding pressure.

## 10. Findings / Research Notes

Detailed findings live in `../notes.md`. Highlights worth surfacing here:

- **VerificationCoverageValidator** has zero external sites → safest first swap (DR-118 §4 ordering principle confirmed).
- **DeltaRelationshipsValidator** has 5 external touchpoints (DR-118 §3 listed 2). Full set: `changes/artifacts.py:122`, `requirements/registry.py:240/243`, `requirements/sync.py:11/132/171`. Wrapper helper `validate_delta_relationships` required.
- **RelationshipsBlockValidator** has only 1 external instantiation (`requirements/registry.py:162`); validate-call reaches `sync.py:273` via second-hand `Any`-typed parameter. Wrapper helper `validate_spec_relationships` required.
- **`spec.capabilities` is already metadata-only** — no hand-rolled validator class exists. DR-118 §3's `validate_spec_capabilities` mention is convenience-wrapper only, not a retirement.
- **Parallel-test gaps**: `relationships_metadata_test.py` and `tracking_metadata_test.py` do not exist. P03 swap commits for those validators must add (or extend an existing file with) the metadata-validator parallel coverage **before** the swap.
- **R7 pre-check vacuous**: no live `workflow.sessions` data in this repo. Synthetic corpus required for P03 sessions swap.
- **DR-118 changes recommended**: none. Refinements documented in `notes.md` §4 inform P03 commit-message authoring without invalidating any DR decision.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied (all items in §4).
- [x] `validate-baseline.txt` committed.
- [x] `notes.md` carries the 7 per-validator inventory sections + R7 pre-check subsection + P04 handover (naming collisions).
- [x] Spec/Delta/Plan updated if any P01 finding shifts scope — none did. Refinements logged in notes.md §4 only.
- [x] Hand-off note to IP-118-P02 in `notes.md` §6: "Inventory complete. P02 may begin."
