---
id: IP-118-P04
slug: "118-block_schema_unification_retire_hand_rolled_validators_single_metadata_driven_validation_layer-phase-04"
name: IP-118 Phase 04
created: "2026-05-16"
updated: "2026-05-16"
status: draft
kind: phase
plan: IP-118
delta: DE-118
---

# Phase 04 — Cleanup

## 1. Objective

Retire the residual workarounds and dead-code surface that DE-118 unblocked but did not yet remove, settle the two long-open OQs (OQ-NAMING-COLLISIONS, OQ-HARNESS-LIFECYCLE), and bring DE-118 to a clean close-change state. P04 is the cleanup tail — no behaviour-equivalence work remains (P03 closed that out at commit `2c5b7073`); P04 is shape-and-naming hygiene plus the close-change gate audit (IMPR-035 → DE-137 reference verified).

Concretely, P04 ships (one task per commit, no swap-style coupling):

1. **4.1** — Delete `REVISION_BLOCK_JSON_SCHEMA` + 4 regex bugs (`revision.py:28` and 4× `\\d` patterns at `:43/:213/:217/:223`); strip `__all__:1055`; optionally move `REVISION_BLOCK_SCHEMA_ID` / `REVISION_BLOCK_VERSION` to `revision_metadata.py` to retire the pre-existing `revision → revision_metadata` cyclic-import warning.
2. **4.2** — Replace `_entry_shape` sentinel with `additional_properties=_SESSION_ENTRY` at `sessions_schema.py:88`; R7 confirmed vacuous in this repo (P01 §2: zero live `workflow.sessions` data), so the migration relies on synthetic corpus added during the commit.
3. **4.3** — Drop `FieldMetadata.required` from `items` definitions across `*_metadata.py` modules; the field is semantically meaningless on array-element shapes (per DR-118 §4 Phase 3 row 4).
4. **4.4** — OQ-NAMING-COLLISIONS resolution: rename `RELATIONSHIPS_MARKER` to `DELTA_RELATIONSHIPS_MARKER` / `SPEC_RELATIONSHIPS_MARKER` in source modules; drop the alias-on-re-export workarounds at `changes/blocks/__init__.py:23,60` and `specs/__init__.py:21,40`.
5. **4.5** — OQ-NAMING-COLLISIONS resolution: rename `VALID_STATUSES` to `CHANGE_STATUSES` / `REQUIREMENT_STATUSES` / `VERIFICATION_STATUSES` in source modules; drop alias-on-import workarounds at `cli/schema_test.py:441-447` and `spec_driver/orchestration/enums.py:20-30`. Larger blast radius than 4.4 — touches every cli/orchestration importer.
6. **4.6** — Residual `__all__` cleanups + OQ-HARNESS-LIFECYCLE settlement. Decide and apply one of: (a) keep `snapshot_compare.py` as runnable infrastructure with empty `HAND_ROLLED_ADAPTERS`; (b) decommission the module + its tests; (c) repurpose as a metadata-only corpus smoke check invoked from `just check`. P03 §3.6 default is (a).
7. **4.7** — Close-change preparation: verify **IMPR-035** exists with content beyond the template stub, names DE-137 as receiver (or DE-136 fallback), and is referenced from DE-118 §8. Tick IP-118 §9. Run `/audit-change` after this lands.

## 2. Links & References

- **Delta**: DE-118
- **Design Revision Sections**: DR-118 §4 ("Phase 3 — Cleanup" table; row-for-row source for tasks 4.1–4.3), §7 DEC-006 (close-change audit gate for IMPR-035), §8 OQ-NAMING-COLLISIONS + OQ-HARNESS-LIFECYCLE (both settle in P04), §9 R6 (DR-136 cross-ref is best-effort; IMPR-035 is the only durable record).
- **Specs / PRODs**: SPEC-114 (blocks/metadata; primary surface for tasks 4.2–4.3), SPEC-115 (changes/blocks; primary surface for task 4.1), SPEC-116 (frontmatter_metadata; pattern reference for additional_properties idiom).
- **Support Docs**:
  - `../notes.md` §5 — OQ-NAMING-COLLISIONS site enumeration for tasks 4.4 / 4.5 (no need to re-enumerate during execution).
  - `../notes.md` "P03 closure summary" + "Key files for P04" — P03 → P04 hand-off catalogue with file/line pointers.
  - `../notes.md` §3.1 — `RevisionBlockValidator` inventory; cross-checks task 4.1's `__all__` impact at `revision.py:1055`.
  - `validate-baseline.txt` — pre-merge gate diff target (8 audit-gate warnings + install-skew noise); **not** updated per DR-118 §5.
  - `IMPR-035-…/IMPR-035.md` (under `.spec-driver/backlog/improvements/`) — load-bearing close-change record; verified in 4.7.

## 3. Entrance Criteria

- [x] IP-118-P03 complete (5/5 swap commits landed; `HAND_ROLLED_ADAPTERS` empty; harness final state recorded). Closure commit `237cd99d`.
- [x] `just check` green at HEAD; `spec-driver validate` baseline-identical.
- [x] Harness reports 0 disagreements at HEAD (HEAD `5d555985`: scanned 1656 files, 0 dual-validated, 877 metadata-only).
- [x] No outstanding `/consult` thread on DE-118 design.
- [x] DR-118 §4 Phase 3 table and §8 OQ entries unchanged since P02.5 close; no design rework triggered by P03 outcomes.

## 4. Exit Criteria / Done When

- [x] `REVISION_BLOCK_JSON_SCHEMA` deleted from `revision.py`; the 4 regex-bug patterns gone; `__all__` entry removed; `revision_metadata_test.py::test_metadata_generates_json_schema` continues to pass against the metadata-derived JSON schema (already shape-asserts; no rebase required).
- [x] `_entry_shape` sentinel removed from `sessions_schema.py`; replaced with `additional_properties=_SESSION_ENTRY`; synthetic-corpus tests cover positive + every negative branch + nested-strictness + empty-map silent-pass.
- [x] `FieldMetadata.required` arg dropped at every `items=FieldMetadata(required=...)` direct-kwarg site (one site: `verification_metadata.py:58`); no semantic change (harness 0-disagreement; 4843/4843 tests pass).
- [x] `RELATIONSHIPS_MARKER` no longer exists as a colliding name: source modules export `DELTA_RELATIONSHIPS_MARKER` / `SPEC_RELATIONSHIPS_MARKER` directly; alias-on-re-export workarounds collapsed to direct imports; final grep `rg "\bRELATIONSHIPS_MARKER\b" supekku/` returns zero hits.
- [x] `VALID_STATUSES` no longer exists as a colliding name: source modules export `CHANGE_STATUSES`, `REQUIREMENT_STATUSES`, `VERIFICATION_STATUSES` directly; alias-on-import workarounds in `cli/schema_test.py` and `spec_driver/orchestration/enums.py` collapsed to direct imports; `VALID_COVERAGE_STATUSES` workaround alias retired (consumer `coverage.py` migrated to `VERIFICATION_STATUSES` directly); final grep `rg "\bVALID_STATUSES\b" supekku/ spec_driver/` returns zero hits.
- [ ] OQ-HARNESS-LIFECYCLE settled and documented in this phase sheet §9 with rationale; one of {keep, decommission, repurpose} applied.
- [ ] IMPR-035 verified: file exists at `.spec-driver/backlog/improvements/IMPR-035-…/IMPR-035.md`; content beyond template stub; names DE-137 (or DE-136 fallback) as receiver; referenced from DE-118.md §8 "Follow-ups & Tracking".
- [ ] `just check` passes after every commit.
- [ ] `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` returns 0 disagreements after every commit (or, if 4.6 decommissions, the equivalent metadata-only validator path is exercised by the test suite).
- [ ] `uv run spec-driver validate` produces baseline-identical output after every commit (8 audit-gate warnings + install-skew noise).
- [ ] Commit messages enumerate retired symbols + migrated call sites (P03 lineage: `feat(DE-118): <subject> (P04 <N>)`).
- [ ] `notes.md` records per-task harness output + final P04 closure summary (5+ commit hashes; harness final state if shape changed).
- [ ] IP-118.md §9 ticks "IP-118-P04 complete" and "All verification gates passed; ready for `/audit-change` → `/close-change`".

## 5. Verification

- **Per-task gates** (apply identically to 4.1–4.7 except where noted):
  - `just check` green.
  - `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` → 0 disagreements (or post-4.6 the equivalent successor check).
  - `uv run spec-driver validate` baseline-diff clean.
  - `just pylint-files <changed-files>` — no new pylint regressions on touched files; opportunistic reductions (e.g. cyclic-import retirement in 4.1) tracked in commit message.
- **Task-specific evidence**:
  - **4.1**: `revision_metadata_test.py::test_metadata_generates_json_schema` passes (metadata-derived JSON schema replaces the deleted literal); the 4 `test_regex_bug_*` regression tests (added in P03 C5) continue to pass — these are the canonical guard against re-introducing the `\\d` bug if a future agent restores the literal.
  - **4.2**: synthetic-corpus tests in `sessions_schema_test.py` (or `sessions_metadata_test.py` — placement decided at execution per the `<source>_metadata_test.py` mirror rule) cover positive paths + every required-field negative for `_SESSION_ENTRY`. Harness re-run against any `.spec-driver/run/sessions/` data (creates the dir + a synthetic block if absent — R7 still vacuous at execution time).
  - **4.3**: harness re-run after each `*_metadata.py` patch to prove no verdict drift.
  - **4.4 / 4.5**: existing test suites continue to pass after rename; grep across `supekku/` confirms no straggler `from … import RELATIONSHIPS_MARKER` / `VALID_STATUSES` lines remain.
  - **4.6**: if option (a) keep — harness invocation documented in CONTRIBUTING / STD-004 note; if (b) decommission — harness module + tests deleted and `notes.md` records the decision; if (c) repurpose — `just check` integration tested.
  - **4.7**: IMPR-035 inspection commit message quotes the receiver-artefact line; `spec-driver show backlog IMPR-035` exit-0 (or equivalent CLI surface).
- **Evidence to capture**:
  - Per-commit harness output appended to `notes.md` under a "P04 progress" section (mirrors P03 structure).
  - Final P04 closure entry summarising commit hashes + line-count delta + OQ resolutions.
  - `validate-baseline.txt` is **not** updated — it remains the unchanged regression target per DR-118 §5 until close-change retires it.

## 6. Assumptions & STOP Conditions

### Assumptions

- The harness baseline at HEAD remains 0 disagreements throughout P04. Tasks 4.1–4.3 may shift block counts (e.g. 4.2 introduces per-entry validation that didn't run before) but must not introduce a disagreement.
- `REVISION_BLOCK_JSON_SCHEMA` has no production consumers beyond the now-deleted `RevisionBlockValidator` (retired in P03 C5). The 4.1 P01 inventory confirmed this; re-verify with a pre-deletion grep across `supekku/` and `.spec-driver/`.
- `metadata_to_json_schema` (the metadata-driven JSON schema generator) produces a schema equivalent to the literal that `test_metadata_generates_json_schema` previously asserted against. Confirmed in P03 by the test itself — the test generates from metadata and previously compared against the (buggy) literal; 4.1 simplifies the test to assert the generated schema's shape directly.
- `_SESSION_ENTRY` shape is correctly declared at `sessions_schema.py:13-39`. P01 §2 documented the four fields; 4.2 reuses the declaration as-is via `additional_properties=_SESSION_ENTRY` — no schema authoring.
- The `RELATIONSHIPS_MARKER` and `VALID_STATUSES` rename surface is bounded by the notes.md §5 enumeration. Re-grep at 4.4 / 4.5 entry; if new sites appear, scope expands (still within P04 — these are colocated cleanups).
- IMPR-035 already exists (created during DR-DE reconciliation 2026-05-09 per DEC-006). 4.7 is verification, not authoring.

### STOP when

- The snapshot harness reports a non-zero disagreement count at any P04 commit boundary. Implies a P03-equivalent semantic divergence that the cleanup work introduced. Escalate via `/consult`; do not proceed.
- `spec-driver validate` produces a NEW warning/error (beyond the 8 audit-gate baseline + install-skew noise). Implies unintended semantic change. Investigate and resolve before commit lands.
- 4.2's synthetic-corpus negative cases reveal an `_SESSION_ENTRY` shape mismatch (e.g. a required field that real workflow.sessions data wouldn't provide). The shape is theoretical until consumer repos emit `workflow.sessions` blocks; if the declaration is wrong, **decide whether to fix the declaration or accept first-contact strictness** — escalate via `/consult` before either path. Per P01 §2, R7 noted this as a drift implication for IMPR-035.
- 4.5 surfaces a circular dependency or migration chain that wasn't visible at planning time (e.g. `cli/schema_test.py` referencing `orchestration/enums.py` which references the colliding constant). The blast radius assumption may be wrong; document and escalate.
- IMPR-035 verification (4.7) finds the receiving artefact is **not** DE-137 (e.g. DE-137 has been retired or descoped). Per DEC-006, the fallback is DE-136. If neither receiver exists, **do not close DE-118**; surface to user and create a follow-up authoring task.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x]    | 4.1 | Delete `REVISION_BLOCK_JSON_SCHEMA` + 4 regex bugs; optional: retire `revision → revision_metadata` cyclic-import | no (independent) | Touches `revision.py` + `revision_metadata.py`. Cyclic-import retirement APPLIED (no external consumers; net <10 LOC churn). Test `test_metadata_generates_json_schema` already shape-asserts on generated schema — no rebase needed. |
| [x]    | 4.2 | Replace `_entry_shape` sentinel with `additional_properties=_SESSION_ENTRY` | yes (after 4.1) | Touches `sessions_schema.py` + `workflow_metadata_test.py::WorkflowSessionsTest` (existing co-location; no `sessions_metadata.py` so mirror-rule primary form doesn't apply). 6 synthetic-corpus tests added. |
| [x]    | 4.3 | Drop `FieldMetadata.required` from `items` definitions | yes (after 4.1) | Single production site: `verification_metadata.py:58` (`items=FieldMetadata(type="object", required=True, ...)`). 17 other `items=FieldMetadata` sites with `required=` matches were inner-property declarations (legitimate), not direct kwargs on `items`. |
| [x]    | 4.4 | OQ-NAMING-COLLISIONS: rename `RELATIONSHIPS_MARKER` | yes (after 4.1) | `blocks/delta.py` → `DELTA_RELATIONSHIPS_MARKER`; `blocks/relationships.py` → `SPEC_RELATIONSHIPS_MARKER`. Alias-on-re-export workarounds at `changes/blocks/__init__.py` and `specs/__init__.py` collapsed to direct imports. |
| [x]    | 4.5 | OQ-NAMING-COLLISIONS: rename `VALID_STATUSES` | no (after 4.4) | `changes/lifecycle.py` → `CHANGE_STATUSES`; `requirements/lifecycle.py` → `REQUIREMENT_STATUSES`; `blocks/verification.py` → `VERIFICATION_STATUSES`. 7 consumer-import sites updated; 6 alias-on-import workaround lines collapsed (3 each in `cli/schema_test.py` + `spec_driver/orchestration/enums.py`). Also retired `VALID_COVERAGE_STATUSES` workaround alias from `verification.py` + migrated `coverage.py` consumer; dropped local `REQUIREMENT_VALID_STATUSES` alias from `revision_metadata.py`. |
| [ ]    | 4.6 | Residual `__all__` cleanups + OQ-HARNESS-LIFECYCLE settlement | no (after 4.1–4.5) | Decision options (a) keep / (b) decommission / (c) repurpose. P03 §3.6 default is (a); decide here. |
| [ ]    | 4.7 | Close-change preparation: IMPR-035 audit + IP-118 §9 tick | no (after 4.6) | Verify IMPR-035 references DE-137; hand off to `/audit-change`. |

### Task Details

- **4.1 Delete `REVISION_BLOCK_JSON_SCHEMA` + 4 regex bugs**
  - **Design / Approach**: Pre-deletion grep across `supekku/` and `.spec-driver/` for `REVISION_BLOCK_JSON_SCHEMA` — expect only `revision.py:28` (definition) and `revision.py:1055` (`__all__` entry). Delete both. The 4 regex bugs are inline in the literal (`r"^RE-\\d{3,}$"` etc.) so they go with the parent. Update `revision_metadata_test.py::test_metadata_generates_json_schema` to assert against the metadata-derived schema directly (the test already generates from metadata; only the comparison target changes). **Optional cyclic-import retirement**: `revision.py` imports `revision_metadata` for schema registration (one direction) and `revision_metadata.py` imports `REVISION_BLOCK_SCHEMA_ID` / `REVISION_BLOCK_VERSION` from `revision.py` (the other direction, pre-existing cyclic-import warning). Move the two constants to `revision_metadata.py` as their canonical declaration site; `revision.py` becomes a one-way importer. If the optional retirement adds >50 LOC of churn or surfaces consumer imports, defer to a follow-up.
  - **Files / Components**: `supekku/scripts/lib/blocks/revision.py`, `revision_metadata.py` (optional), `revision_metadata_test.py`, downstream `__all__` consumers.
  - **Testing**: `revision_metadata_test.py::test_metadata_generates_json_schema` passes; the 4 `test_regex_bug_*` tests (P03 C5) continue to pass; harness 0-disagreement; `just check` green.
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `feat(DE-118): delete REVISION_BLOCK_JSON_SCHEMA + 4 regex bugs (P04 4.1)`; reference DR-118 §4 Phase 3 row 1.

- **4.2 Replace `_entry_shape` with `additional_properties=_SESSION_ENTRY`**
  - **Design / Approach**: At `sessions_schema.py:88`, replace `properties={"_entry_shape": _SESSION_ENTRY, ...}` (or however the sentinel is currently keyed) with `properties=None, additional_properties=_SESSION_ENTRY`. The validator's object-type branch (DEC-004) handles dynamic-key validation against `additional_properties` at every depth via the recursive `_validate_field` algorithm. R7 vacuous: P01 §2 confirmed zero `.spec-driver/run/sessions/` data, so the migration introduces *new enforcement* but cannot break real corpus. Document the first-contact strictness implication in IMPR-035 (consumer repos emitting `workflow.sessions` blocks will hit it at first contact); no separate drift entry needed.
  - **Files / Components**: `supekku/scripts/lib/blocks/sessions_schema.py`, sibling test (placement per `<source>_metadata_test.py` mirror rule: `sessions_metadata_test.py` if separate metadata file exists, else `sessions_schema_test.py`).
  - **Testing**: synthetic corpus: positive (well-formed session entry), negative for each of the 4 fields (`session_name` missing, `status` not in enum, `last_seen` missing, `sandbox` wrong type), nested-strictness (unknown key at entry level rejected under `strict_unknown_keys=True`), empty-map silent-pass (DEC-004 documented behaviour). Add IMPR-035 note covering first-contact strictness.
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `feat(DE-118): replace _entry_shape with additional_properties=_SESSION_ENTRY (P04 4.2)`; reference DR-118 DEC-004 + §4 Phase 3 row 2.

- **4.3 Drop `FieldMetadata.required` from `items` definitions**
  - **Design / Approach**: Grep `FieldMetadata(.*items=FieldMetadata(` across `supekku/scripts/lib/blocks/` to find array-of-object shapes. At each `items=FieldMetadata(...)` site, drop the `required` kwarg if present — it has no semantic effect on array elements (items are positional, not key-addressed). The validator's `_validate_field` array branch ignores `items.required` per DR-118 §4 Phase 3 row 4. Cross-reference DR-118 §4 to confirm the rationale; if any site uses `items.required` to convey a different intent (e.g. min-length proxy), escalate before deleting.
  - **Files / Components**: `*_metadata.py` modules across `supekku/scripts/lib/blocks/`.
  - **Testing**: harness 0-disagreement re-run after each batch; existing `*_metadata_test.py` files continue to pass (no test asserts on `items.required` since the validator never honoured it).
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `feat(DE-118): drop FieldMetadata.required from items definitions (P04 4.3)`; reference DR-118 §4 Phase 3 row 4.

- **4.4 OQ-NAMING-COLLISIONS: rename `RELATIONSHIPS_MARKER`**
  - **Design / Approach**: Per `notes.md §5`. Rename `RELATIONSHIPS_MARKER` in `blocks/delta.py:15` → `DELTA_RELATIONSHIPS_MARKER`; in `blocks/relationships.py:15` → `SPEC_RELATIONSHIPS_MARKER`. Update originating `__all__` lines. Drop the alias-on-re-export workarounds at `changes/blocks/__init__.py:23,60` (currently `RELATIONSHIPS_MARKER as DELTA_RELATIONSHIPS_MARKER`) and `specs/__init__.py:21,40` (currently `RELATIONSHIPS_MARKER as SPEC_RELATIONSHIPS_MARKER`) — re-export the renamed constants directly. Grep `RELATIONSHIPS_MARKER` across the whole repo (`supekku/`, `.spec-driver/`, project root) to catch any stragglers; the disambiguated re-exports were the only consumers per the P01 inventory but verify.
  - **Files / Components**: `blocks/delta.py`, `blocks/relationships.py`, `changes/blocks/__init__.py`, `specs/__init__.py`, downstream callers.
  - **Testing**: existing test suites continue to pass; final grep `rg "RELATIONSHIPS_MARKER"` returns only the two renamed constants (no bare `RELATIONSHIPS_MARKER` survives).
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `refactor(DE-118): rename RELATIONSHIPS_MARKER to disambiguate (P04 4.4)`; reference DR-118 §4 Phase 3 row 3 + DR-118 §8 OQ-NAMING-COLLISIONS.

- **4.5 OQ-NAMING-COLLISIONS: rename `VALID_STATUSES`**
  - **Design / Approach**: Per `notes.md §5`. Rename source-module constants: `changes/lifecycle.py:20` `VALID_STATUSES` → `CHANGE_STATUSES`; `requirements/lifecycle.py:14` `VALID_STATUSES` → `REQUIREMENT_STATUSES`; `blocks/verification.py:24` inline-literal `VALID_STATUSES` → `VERIFICATION_STATUSES`. `blocks/verification_metadata.py:16` import follows. Drop alias-on-import workarounds at `cli/schema_test.py:441-447` and `spec_driver/orchestration/enums.py:20-30`. Each rename has a larger blast radius than 4.4 — every cli/orchestration consumer that imports `VALID_STATUSES` from one of the three sources needs updating. Grep before deleting any alias to enumerate consumers.
  - **Files / Components**: `changes/lifecycle.py`, `requirements/lifecycle.py`, `blocks/verification.py`, `blocks/verification_metadata.py`, `cli/schema_test.py`, `spec_driver/orchestration/enums.py`, plus every consumer surfaced by the grep.
  - **Testing**: existing test suites continue to pass; final grep `rg "\\bVALID_STATUSES\\b"` returns only the three renamed constants and the aliased-import sites (then those drop too).
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `refactor(DE-118): rename VALID_STATUSES to disambiguate (P04 4.5)`; reference DR-118 §4 Phase 3 row 3 + DR-118 §8 OQ-NAMING-COLLISIONS.

- **4.6 Residual `__all__` cleanups + OQ-HARNESS-LIFECYCLE settlement**
  - **Design / Approach**: Two parts. **Part A — `__all__` audit**: after 4.1–4.5, sweep the `__all__` lines across `blocks/`, `changes/blocks/`, `requirements/`, `specs/` for stale entries (renamed-but-still-listed names, deleted symbols, etc.). Apply a single tidy-up commit. **Part B — OQ-HARNESS-LIFECYCLE**: the dual-validate harness has been a metadata-only smoke pass since C5 (`HAND_ROLLED_ADAPTERS={}`). Three options per DR-118 §8: (a) keep the module as runnable infrastructure; the empty adapter map is harmless and the harness still reports `Report.ok` against the corpus; (b) decommission the module + its tests entirely — the dual-validate use case is gone; (c) repurpose as a metadata-only corpus smoke check, wired into `just check` so it runs on every CI cycle. P03 §3.6 default is (a) — settle here. Recommendation under STD-004 (orphan prevention): if option (a), add a README/comment line documenting the on-demand run trigger (e.g. "run after extending `*_metadata.py` declarations to catch corpus drift"); if option (b), delete `snapshot_compare.py` + `snapshot_compare_test.py` and the dev-tool entry from any docs. Discuss in §9 decisions block before committing.
  - **Files / Components**: `__all__` lines across affected modules; `supekku/scripts/lib/blocks/metadata/snapshot_compare.py` (+ test) per the lifecycle decision.
  - **Testing**: `just check` green; if (b) decommission, confirm no test imports `snapshot_compare`; if (c) repurpose, the new invocation surface runs in CI.
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `chore(DE-118): __all__ cleanups + settle OQ-HARNESS-LIFECYCLE (P04 4.6)`; reference DR-118 §8 OQ-HARNESS-LIFECYCLE + STD-004.

- **4.7 Close-change preparation: IMPR-035 audit + IP-118 §9 tick**
  - **Design / Approach**: Per DEC-006 close-change audit step. Open `.spec-driver/backlog/improvements/IMPR-035-…/IMPR-035.md` and verify: (1) content exists beyond the template stub (i.e. the IMP describes the 7 affected workflow blocks, the deferred mechanism, and acceptance criteria); (2) the IMP names DE-137 as receiving artefact (or DE-136 as fallback per DEC-006); (3) DE-118.md §8 "Follow-ups & Tracking" references IMPR-035 by ID. If any check fails, **do not proceed to close-change**: surface to user; create a follow-up authoring task; resolve before audit. After audit pass, tick IP-118 §9 ("IP-118-P04 complete" + "All verification gates passed; ready for `/audit-change` → `/close-change`"). Append P04 closure summary to `notes.md` (mirrors P03 closure entry shape). Hand off to `/audit-change`.
  - **Files / Components**: `.spec-driver/backlog/improvements/IMPR-035-…/IMPR-035.md` (read-only audit), `DE-118.md` §8 (read-only audit), `IP-118.md` §9 (tick), `notes.md` (P04 closure entry).
  - **Testing**: human-readable audit only; no automated check.
  - **Observations & AI Notes**: …
  - **Commits / References**: commit message format `chore(DE-118): close IP-118-P04 — cleanup + IMPR-035 close-change gate (P04 4.7)`; reference DR-118 DEC-006 + IP-118 §9.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| **R12 (new)** `metadata_to_json_schema` produces a schema that differs in shape from the deleted `REVISION_BLOCK_JSON_SCHEMA` literal | `test_metadata_generates_json_schema` already generates from metadata; 4.1 simplifies the test to assert the generated schema's shape, not equivalence to the literal. The 4 `test_regex_bug_*` regression tests (P03 C5) pin the correct regex semantics. | open |
| **R7 (carryover)** `_entry_shape` migration is *new* enforcement, not equivalence | P01 §2 confirmed R7 vacuous in this repo (zero live `workflow.sessions` data). First-contact strictness will apply when consumer repos emit `workflow.sessions` blocks; documented in IMPR-035 during 4.2. | open (vacuous in-repo) |
| **R13 (new)** OQ-NAMING-COLLISIONS rename surfaces consumer-import sites not in `notes.md §5` | Grep pre-rename in 4.4 / 4.5 task entry. The notes enumeration is "focused on the two names DR-118 §3 called out, not exhaustive"; widening is expected within P04 scope. | open |
| **R14 (new)** OQ-HARNESS-LIFECYCLE decision is irreversible if option (b) decommission is chosen | Decommissioning deletes the module and its tests. Recovery would require recreating the harness from git history. **Mitigation**: prefer option (a) keep as the default; option (b) only if a strong reason emerges (e.g. STD-004 ownership concerns that the on-demand run trigger doesn't address). Capture the decision rationale in §9 before committing. | open |
| **R15 (new)** IMPR-035 receiving artefact is not DE-137 (e.g. DE-137 retired or DE-136 fallback active) | 4.7 audit explicitly checks for receiver-name. STOP condition above triggers a follow-up authoring task before close-change. Per DEC-006, both DE-137 and DE-136 fallback are durable receivers; failure mode is neither existing. | open |
| **R16 (new)** Pre-existing `revision → revision_metadata` cyclic-import retirement (optional in 4.1) introduces a deeper import chain than expected | The optional retirement is gated: if moving `REVISION_BLOCK_SCHEMA_ID` / `REVISION_BLOCK_VERSION` adds >50 LOC of churn or surfaces consumer imports, defer to a follow-up. The core 4.1 deliverable (regex-bug deletion) is independent. | open |

## 9. Decisions & Outcomes

- `2026-05-16` — **Test-file placement (4.2) — extend `workflow_metadata_test.py::WorkflowSessionsTest`.** The `<source>_metadata_test.py` mirror rule's primary form (`sessions_metadata_test.py`) is inapplicable — there is no `sessions_metadata.py`; the canonical declaration site is `sessions_schema.py`. The fallback (`sessions_schema_test.py`) would require migrating 4 existing `WorkflowSessionsTest` tests for no clear benefit. Extending the existing test class colocates with prior sessions tests and keeps the diff focused on the swap itself.
- `2026-05-16` — **Cyclic-import retirement (4.1) — APPLIED.** External consumer-import surface for `REVISION_BLOCK_SCHEMA_ID` / `REVISION_BLOCK_VERSION` is zero (only `revision.py` and `revision_metadata.py` reference them). Moved both constants to `revision_metadata.py` as their canonical declaration site; `revision.py` imports them back via a one-way top-level import. The pre-existing deferred-bottom imports (`REVISION_CHANGE_METADATA`, `BlockSchema`, `register_block_schema`) were promoted to module-top alongside the constants — no more `noqa: E402` needed. Net LOC delta: ~5 lines added in `revision_metadata.py`, ~3 net removed in `revision.py` after factoring out the now-deleted `REQUIREMENT_VALID_STATUSES` import (it lived only inside the deleted literal). Well under the 50-LOC gate. Pylint on the two touched files improved from 3 messages to 1 (the lone remaining `too-many-locals` is in `render_revision_change_block`, pre-existing, unrelated).
- `YYYY-MM-DD` — _(remaining pre-planned slots:)_
  - **OQ-HARNESS-LIFECYCLE settlement** at 4.6 — one of (a) keep / (b) decommission / (c) repurpose. Rationale captured here before committing.

## 10. Findings / Research Notes

- **`notes.md §5` is the authoritative enumeration** for tasks 4.4 / 4.5 site lists. Do not re-enumerate during execution unless a grep widens the surface.
- **Phase-03 §10 "Findings"** establishes two carryover patterns: (1) `<source>_metadata_test.py` mirror rule for test-file placement; (2) production-caller verification before assuming a swap site. 4.2's `sessions_metadata_test.py` decision applies (1); none of the P04 tasks are swaps so (2) is moot.
- **DR-118 §9 R7** carries the migration framing for 4.2: "new enforcement, not equivalence". Frame the 4.2 commit message and IMPR-035 note accordingly.
- **STD-004 (script lifecycle, orphan prevention)** is the governing standard for OQ-HARNESS-LIFECYCLE (4.6). The lifecycle decision must produce a documented owner + re-run trigger, regardless of which option is chosen.

## 11. Wrap-up Checklist

- [ ] All P04 commits landed; OQ-NAMING-COLLISIONS resolved (both names disambiguated).
- [ ] `REVISION_BLOCK_JSON_SCHEMA` + 4 regex bugs deleted; `_entry_shape` retired; `FieldMetadata.required` dropped from items.
- [ ] OQ-HARNESS-LIFECYCLE settled and documented in §9.
- [ ] IMPR-035 audit passed (content + DE-137 receiver + DE-118 §8 cross-ref); recorded in §9.
- [ ] `notes.md` records P04 closure with per-task harness output and final commit hash list.
- [ ] `IP-118.md` §9 progress tracking ticks "IP-118-P04 complete" and "All verification gates passed; ready for `/audit-change` → `/close-change`".
- [ ] `just check` green at HEAD.
- [ ] `spec-driver validate` baseline-identical at HEAD.
- [ ] Hand-off to `/audit-change` recorded (no further phases follow P04).
