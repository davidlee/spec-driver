# Notes for DE-118

## IP-118-P01 — Inventory & Baseline (2026-05-09)

Pure discovery. No code changes. Outputs feed P02 mechanism work and P03 swap commits.

Cross-references:
- DR-118 §4 (Phase 2 ordering, ID-kwarg wrappers, pre-Phase-2 inventory tasks).
- IP-118 §4 phase table.
- `validate-baseline.txt` (sibling file).

### TOC

1. Validate baseline summary
2. R7 pre-check: live `workflow.sessions` data
3. Per-validator inventories
   - 3.1 `RevisionBlockValidator`
   - 3.2 `DeltaRelationshipsValidator`
   - 3.3 `RelationshipsBlockValidator`
   - 3.4 `VerificationCoverageValidator`
   - 3.5 Plan trio: `PlanOverviewValidator`, `PhaseOverviewValidator`, `PhaseTrackingValidator`
4. Findings that refine DR-118 §4
5. P04 handover — OQ-NAMING-COLLISIONS sites
6. Hand-off to IP-118-P02

---

## 1. Validate baseline summary

Captured at `validate-baseline.txt` via `uv run spec-driver validate > … 2>&1`. Exit code 1.

Content (8 audit-gate warnings + 2 lines of environment noise):

- Lines 1–2: `Warning: spec-driver may need re-install (workflow.toml has 0.9.2, running 0.9.3).` — environment-version skew, not workflow-relevant. **Future commits may see these lines drift if `workflow.toml` is bumped or local install is refreshed; treat the install-skew lines as noise during diff.**
- Lines 3–10: 8× `ValidationIssue(level='warning', message='Audit gate is required but no completed conformance audit found', artifact=DE-XXX)` for DE-135, DE-138, DE-140, DE-141, DE-139, DE-142, DE-137, DE-136. These match the audit-gate pattern documented in `mem.pattern.validation.warning-triage` (cause: `applies_to.requirements` populated, no conformance audit yet). Pre-existing state — DE-118 introduces none of them.

Regression rule for P02–P04: every commit should produce an identical 8-warning baseline (modulo install-skew noise). Any new warning is a P02/P03 regression and must be diagnosed before the commit lands.

## 2. R7 pre-check — `workflow.sessions` vs `_SESSION_ENTRY`

**Outcome: vacuous.** No live `workflow.sessions` block instances exist anywhere in this repo.

Method:

```
rg -l "supekku:workflow\.sessions"
```

Result: only `supekku/scripts/lib/blocks/sessions_schema.py` (the module that *defines* the schema/marker) and `supekku/scripts/lib/blocks/workflow_metadata.py` (re-export). **Zero consumer documents.**

Also checked: `.spec-driver/run/sessions/` — directory does not exist. `.spec-driver/run/` contains only `events.jsonl` and `pylint`.

Implication for P02/P03:

- R7 risk (`_entry_shape` migration introducing new enforcement that breaks live data) is **not realisable in this repo** today. The migration cannot break what does not exist.
- Acceptance criterion for P03 sessions swap: regression-test corpus must include synthetic blocks (positive + negative cases against `_SESSION_ENTRY`) since there is no live data to drive empirical coverage.
- Drift implication: if/when consumer repos start emitting `workflow.sessions` blocks, the strict `additional_properties=_SESSION_ENTRY` semantics will apply at first contact. Worth noting in IMPR-035 (already covers `workflow.*` deferral generally) — no separate drift entry needed.

`_SESSION_ENTRY` shape (`sessions_schema.py:13-39`):

| Key            | Type   | Required | Notes                                            |
| -------------- | ------ | -------- | ------------------------------------------------ |
| `session_name` | string | yes      | "(string or null)" per docstring                 |
| `sandbox`      | string | no       |                                                  |
| `status`       | enum   | yes      | values from `SESSION_STATUS_VALUES`              |
| `last_seen`    | string | yes      | ISO 8601 or null per docstring                   |

Currently wired via the `_entry_shape` sentinel at `sessions_schema.py:88`. Phase 4 cleanup replaces the sentinel with `additional_properties=_SESSION_ENTRY` — a P04 task, not P02/P03.

## 3. Per-validator inventories

Methodology: ripgrep across `supekku/`, `.spec-driver/`, project root for class name, `__all__`, instantiation calls, type annotations, test fixtures. Cross-checked against DR-118 §4. Each completeness assertion: "no other instantiation site found across `supekku/` and project root."

### 3.1 `RevisionBlockValidator`

- **Class**: `supekku/scripts/lib/blocks/revision.py:362`. Constructor: implicit (no `__init__`). `validate(self, data: dict[str, Any]) -> list[ValidationMessage]` — note: takes a raw dict, not a parsed Block; no ID-equality kwarg.
- **`__all__` / re-exports**:
  - `blocks/revision.py:1059` (origin module).
  - `changes/blocks/__init__.py:48` (import) and `:57` (re-export). Confirmed by DR-118 §3.
- **External call sites** (instantiations only, excluding tests):
  - `requirements/sync.py:15` (import) → `:211` (`validator = RevisionBlockValidator()` inside `_apply_revision_blocks`).
  - `changes/updater.py:8` (import) → `:135` (`validator = RevisionBlockValidator()` inline).
  - **Both invoke `validator.validate(data)` with a single positional arg.** No ID kwargs, no cross-block external state.
- **Test-fixture sites**:
  - `blocks/revision_test.py` — 3 instantiations (lines 56, 66, 88). Existing test suite for the hand-rolled validator.
  - `blocks/revision_metadata_test.py` — 1 instantiation (line 40). **Parallel-test file already exists** — confirms the established pattern. P03 swap can keep the metadata-test file and delete `revision_test.py` after equivalence is proved.
- **External-state coupling**: none. No parent-context ID checks. **Direct swap candidate.**
- **Completeness assertion**: rg of `RevisionBlockValidator` across `supekku/` + project root matches the 5 production references above + 4 test references. No others.

### 3.2 `DeltaRelationshipsValidator`

- **Class**: `supekku/scripts/lib/blocks/delta.py:28`. Constructor: implicit. `validate(self, block: DeltaRelationshipsBlock, *, delta_id: str | None = None) -> list[str]`. ID-equality check at `delta.py:48-53`: errors when `data["delta"]` ≠ `delta_id`.
- **`__all__` / re-exports**:
  - `blocks/delta.py:171` (origin module).
  - **No re-export** in `changes/blocks/__init__.py` for this name — Phase 3 cleanup of `__init__.py` does not need to remove a `DeltaRelationshipsValidator` line. (DR-118 §3 only listed `RevisionBlockValidator` for the re-export removal.)
- **External call sites**:
  - `changes/artifacts.py:11` (import) → `:122` — direct: `DeltaRelationshipsValidator().validate(block, delta_id=artifact_id)`. **Uses `delta_id` kwarg.**
  - `requirements/registry.py:240` (lazy import inside method) → `:243` — `delta_validator = DeltaRelationshipsValidator()` then passed into `_apply_delta_relations(..., validator=delta_validator)` (`registry.py:248-251`).
  - `requirements/sync.py:11` (import) → `:132` — **type annotation** in `_apply_delta_relations(..., *, validator: DeltaRelationshipsValidator)`. The actual `validate(...)` call is at `sync.py:171`: `validator.validate(block, delta_id=delta_id)`. **Uses `delta_id` kwarg.**
  - DR-118 §3 missed the `requirements/sync.py:132` annotation. Negligible — annotation follows the instantiation site automatically — but the P03 swap commit message must enumerate the full set: `artifacts.py:122`, `registry.py:243`, `sync.py:11/132/171`.
- **Test-fixture sites**:
  - `blocks/delta_metadata_test.py:29` — 1 instantiation. **Parallel-test file already exists.**
  - No `blocks/delta_test.py` for the hand-rolled class; the metadata-parallel test is the only test artifact. (`delta_render_test.py` is a renderer test, separate concern.)
- **External-state coupling**: `delta_id` kwarg drives an ID-equality check that `MetadataValidator` cannot express. **Wrapper helper required** per DR-118 §4. Proposed signature: `validate_delta_relationships(block, *, delta_id: str | None = None) -> list[str]` — internally calls `MetadataValidator(DELTA_RELATIONSHIPS_METADATA, strict_unknown_keys=True).validate(block.data)` then layers the `delta_id` equality check (extracted from `delta.py:48-53`).
- **Completeness assertion**: rg matches the 4 production sites above + 3 test references. No others.

### 3.3 `RelationshipsBlockValidator`

- **Class**: `supekku/scripts/lib/blocks/relationships.py:32`. Constructor: implicit. `validate(self, block: RelationshipsBlock, *, spec_id: str | None = None) -> list[str]`. ID-equality check at `relationships.py:54-58`: errors when `data["spec"]` ≠ `spec_id`.
- **`__all__` / re-exports**:
  - `blocks/relationships.py:273` (origin module).
  - No re-export for the validator under `changes/blocks/__init__.py`. The module also exports unrelated `render_spec_capabilities_block` etc.
  - `specs/__init__.py:21,40` re-exports `RELATIONSHIPS_MARKER as SPEC_RELATIONSHIPS_MARKER` (separate concern; see §5).
- **External call sites**:
  - `requirements/registry.py:12` (import) → `:162` — `relationships_validator = RelationshipsBlockValidator()` then passed into `_apply_spec_relationships(..., validator=relationships_validator)` (`registry.py:236`).
  - `requirements/sync.py` — `_apply_spec_relationships` body at `:253` accepts `validator: Any` (note: typed as `Any`, **not** `RelationshipsBlockValidator`; this is asymmetric with the `DeltaRelationshipsValidator` annotation in the same file). Calls `validator.validate(block, spec_id=spec_id)` at `:273`. **Uses `spec_id` kwarg.**
  - DR-118 §3 listed `requirements/registry.py:162` as the only external site, which is technically true — `sync.py` only consumes the validator second-hand via an `Any`-typed parameter.
- **Test-fixture sites**:
  - **No parallel `relationships_metadata_test.py` exists yet.** Gap from the established pattern. P03 commit for this validator must add the parallel-test corpus first (≥1 commit before swap, ideally same commit but separable for review hygiene).
  - No standalone `blocks/relationships_test.py` either. Coverage of this validator in this repo is thin — likely mostly via integration through `requirements/registry.py` callers. **Risk**: P03 swap for this validator has the weakest unit-test safety net of the seven; lean harder on the snapshot-compare harness.
- **External-state coupling**:
  - `spec_id` kwarg → ID-equality check, same wrapper-helper pattern as DeltaRelationships (`validate_spec_relationships`).
  - **DR-118 §3 also calls for a `validate_spec_capabilities` wrapper.** That phrasing is misleading: `spec.capabilities` (`relationships.py:303-312` `register_block_schema("spec.capabilities", …)`) is **already metadata-only** — there is no hand-rolled validator class for it. The "wrapper" for capabilities is just a convenience surface for callers who want a single import — `MetadataValidator(SPEC_CAPABILITIES_METADATA, strict_unknown_keys=True).validate(...)` is functionally complete on its own. Recommendation: P03 should ship `validate_spec_capabilities` as a thin alias for caller ergonomics, but it carries no ID-equality logic and has no hand-rolled validator to retire.
- **Completeness assertion**: rg matches the 2 production sites above + 0 unit-test references. No others.

### 3.4 `VerificationCoverageValidator`

- **Class**: `supekku/scripts/lib/blocks/verification.py:43`. Constructor: implicit. `validate(self, block: VerificationCoverageBlock, ...)` — no ID kwargs (DR-118 §4 claim verified).
- **`__all__` / re-exports**:
  - `blocks/verification.py:281` (origin module). No re-export elsewhere.
- **External call sites**: **NONE.** All 25 references in the rg matches are inside `blocks/verification_test.py` and `blocks/verification_metadata_test.py`.
- **Test-fixture sites**:
  - `blocks/verification_test.py` — 25 instantiations across many test cases. The existing hand-rolled-validator test surface.
  - `blocks/verification_metadata_test.py` — 1 instantiation (line 29). Parallel-test file present.
- **External-state coupling**: none. **Foundational confirmation: DR-118 §4 ordering principle holds.** This is the safest P03 swap candidate — no ID kwargs, no external sites, dense unit-test coverage. Should be Phase 2 swap commit #1 per DR-118 §4 ordering.
- **Completeness assertion**: rg matches 1 class def + 1 `__all__` + 25 test references = 27 total. No production callers.

### 3.5 Plan trio — `PlanOverviewValidator`, `PhaseOverviewValidator`, `PhaseTrackingValidator`

All three live in `supekku/scripts/lib/blocks/plan.py`.

- **Classes**:
  - `PlanOverviewValidator` at `plan.py:52`. `validate(self, block: PlanOverviewBlock) -> list[str]`. No ID kwargs.
  - `PhaseOverviewValidator` at `plan.py:166`. `validate(self, block: PhaseOverviewBlock) -> list[str]`. No ID kwargs.
  - `PhaseTrackingValidator` at `plan.py:235`. `validate(self, block: PhaseTrackingBlock) -> list[str]`. No ID kwargs.
- **`__all__` / re-exports**: All three at `plan.py:667-671`. No re-exports elsewhere.
- **External call sites**: **NONE for all three.** All references confined to `plan.py` (definitions) + the test files below.
- **Test-fixture sites**:
  - `blocks/plan_metadata_test.py` — covers `PlanOverviewValidator` (line 36) and `PhaseOverviewValidator` (line 354). Parallel-test file exists for these two.
  - `blocks/tracking_test.py` — covers `PhaseTrackingValidator` only. **No parallel `tracking_metadata_test.py` exists.** Gap analogous to `RelationshipsBlockValidator`. P03 swap commit for the plan trio must either add a parallel-test fixture for tracking (preferred) or extend `plan_metadata_test.py` to cover all three.
- **External-state coupling**: none for any of the three. **All three are pure structural validators**; metadata-driven swap is direct.
- **DR-118 §3 grouping**: "PlanOverviewValidator + PhaseOverviewValidator + PhaseTrackingValidator (single commit)" — verified appropriate. All three share `plan.py`, none has external state, all retire together cleanly.
- **Completeness assertion**: rg matches the class defs + `__all__` entries + test references only. No production callers.

## 4. Findings that refine DR-118 §4

Issues raised in P01 that should feed P03 commit-message authoring (not blockers):

1. **`DeltaRelationshipsValidator` external-site enumeration omits `requirements/sync.py:132` type annotation** (and the actual `validate(...)` call at `sync.py:171`, reached via the parameter). DR-118 §3 said "external sites in `changes/artifacts.py:122` and `requirements/registry.py:243`" — incomplete. The full set is: `artifacts.py:122`, `registry.py:243`, `sync.py:11/132/171`. The P03 swap must update all five.
2. **`validate_spec_capabilities` wrapper is convenience, not retirement.** No hand-rolled `SpecCapabilitiesValidator` class exists. P03 should land the wrapper as ergonomics, but the commit message should not frame it as a validator retirement.
3. **`tracking_metadata_test.py` and `relationships_metadata_test.py` are missing.** The established parallel-test pattern is partially honoured. P03 commits for the plan trio and `RelationshipsBlockValidator` need to add (or extend an existing file) the metadata-validator parallel coverage **before** the swap, not as part of the swap commit. Two-step locally; can be one PR.
4. **`changes/blocks/__init__.py:48,57` only carries `RevisionBlockValidator`.** DR-118 §3 mentions "re-export at `changes/blocks/__init__.py:48,57` removed" — that's accurate for `RevisionBlockValidator` and only that. No other validator class is re-exported through this shim. P04 cleanup of `__init__.py` is therefore confined to the revision-validator removal + accompanying `__all__` entry.

These refinements live here; DR-118 itself does not need an amend pass since none of them invalidate a design decision. DR-118 §4 ordering and §9 risks remain correct.

## 5. P04 handover — OQ-NAMING-COLLISIONS sites

Enumerated opportunistically during inventory. Not exhaustive — focused on the two names DR-118 §3 called out.

### `RELATIONSHIPS_MARKER`

- `blocks/delta.py:15` — `"supekku:delta.relationships@v1"`
- `blocks/relationships.py:15` — `"supekku:spec.relationships@v1"`

Both names exported via the originating module's `__all__`. Disambiguated only at re-export shims:

- `changes/blocks/__init__.py:23,60` — `RELATIONSHIPS_MARKER as DELTA_RELATIONSHIPS_MARKER`.
- `specs/__init__.py:21,40` — `RELATIONSHIPS_MARKER as SPEC_RELATIONSHIPS_MARKER`.

**Footgun**: a future `from supekku.scripts.lib.blocks.delta import RELATIONSHIPS_MARKER` and `from supekku.scripts.lib.blocks.relationships import RELATIONSHIPS_MARKER` in the same module would silently alias one over the other. Today's call sites all go through the disambiguated re-exports, so it works — but the names themselves remain colliding. P04 fix: rename the originating constants to `DELTA_RELATIONSHIPS_MARKER` and `SPEC_RELATIONSHIPS_MARKER` in their source modules; drop the aliasing re-exports.

### `VALID_STATUSES`

Four definitions with three distinct semantics:

- `changes/lifecycle.py:20` — `set[ChangeStatus]` (delta/audit/revision lifecycle).
- `requirements/lifecycle.py:14` — `set[RequirementStatus]`.
- `blocks/verification.py:24` — `{"planned", "in-progress", "verified", "failed", "blocked"}` (verification-coverage statuses, inline literal).
- (Plus `blocks/verification_metadata.py:16` imports `VALID_STATUSES` from… presumably one of the above.)

Existing disambiguation pattern (already in code):

- `supekku/cli/schema_test.py:441-447` — `VALID_STATUSES as VER_STATUSES / CHANGE_STATUSES / REQ_STATUSES`.
- `spec_driver/orchestration/enums.py:20-30` — same alias pattern.

**Footgun**: same as `RELATIONSHIPS_MARKER` — the colliding name leaks into any naïve `from … import VALID_STATUSES`. P04 fix: rename source constants to `CHANGE_STATUSES`, `REQUIREMENT_STATUSES`, `VERIFICATION_STATUSES` in their origin modules; drop the alias-on-import workarounds. **Larger blast radius than the marker rename** — touch every cli/orchestration import.

P04 phase planning will scope and sequence this. Recording sites here so phase-04.md does not have to re-enumerate.

## 6. Hand-off to IP-118-P02

Inventory complete. P02 may begin.

Pre-P02 checklist (from this inventory):

- [x] All 7 retiring validators located and signature-confirmed.
- [x] External call-site set for each: zero (5 of 7) or fully enumerated (2 of 7 require wrapper helpers).
- [x] Parallel-test file presence audited; **2 gaps recorded** (`tracking_metadata_test.py`, `relationships_metadata_test.py`) for P03 to address before swap.
- [x] Validate baseline captured; regression rule documented.
- [x] R7 pre-check resolved as vacuous; synthetic-corpus requirement noted for P03 sessions swap.
- [x] OQ-NAMING-COLLISIONS sites enumerated for P04.
- [x] Refinements to DR-118 §3 / §4 captured (none invalidate the design).

P02 entry: `MetadataValidator.strict_unknown_keys` constructor flag, `FieldMetadata.additional_properties`, Optional `BlockSchema.renderer`, snapshot-compare harness. No retirements yet.

---

## IP-118-P02.5 — Declaration Fidelity (2026-05-09)

P02 harness surfaced 39 verdict disagreements (post-revert of the in-flight `interactions[].description` patch) — all in the direction `hand-rolled: PASS, metadata: FAIL`. DR-118 §2's premise (uniform hand-rolled rejection) was wrong for six of seven validators. Resolution: widen the affected `BlockMetadata` declarations to match the observed lax contract.

### Pre-P02.5 baseline (after revert)

| Block type | Disagreements |
| --- | --- |
| phase.tracking | 12 |
| spec.relationships | 10 |
| plan.overview | 8 |
| phase.overview | 7 |
| delta.relationships | 2 |
| **Total** | **39** |

Note: original `/consult` summary listed 5 `spec.capabilities` and 4 `verification.coverage` disagreements. These were actually malformed-YAML cases counted under the same files; once the harness output is filtered to true `DISAGREEMENT` records, neither block type has a real fidelity gap. Harness output structure separates `DISAGREEMENT` (verdict mismatch) from `MALFORMED` (YAML parse failure).

### Patches landed

- **`spec_metadata.py` — SPEC_RELATIONSHIPS_METADATA**: added `interactions[].description` (covered the 10 spec.relationships disagreements; PROD-009's two `interactions[].summary` cases were renamed to `description` in the artefact rather than widening the declaration further — one-off authoring drift).
- **`delta_metadata.py` — DELTA_RELATIONSHIPS_METADATA**: added top-level `backlog_items` (array of strings); added `phases[].goal` and `phases[].status` (legacy authoring fields surfaced in DE-007).
- **`plan_metadata.py` — PLAN_OVERVIEW_METADATA**: added `phases[].status`, `phases[].completion_date`, `phases[].notes`.
- **`plan_metadata.py` — PHASE_OVERVIEW_METADATA**: added top-level `name` and `status`.
- **`tracking_metadata.py` — PHASE_TRACKING_METADATA**:
  - Top-level: `status`, `started`, `completed`, `last_updated`, `tasks_completed` (int), `tasks_total` (int), `tasks_done` (int), `tasks_blocked` (int), `notes`, `progress` (array of timestamped objects with `timestamp`/`task`/`status`/`note`/`notes`).
  - `entrance_criteria[].notes` and `exit_criteria[].notes` (added for symmetry; only `exit_criteria[].notes` surfaces in real corpus).
  - `tasks[].notes`.
  - `progress[].notes` (plural-form alias for `progress[].note`; both observed in real corpus).

### Artefact patches

- `PROD-009.md`: renamed two `interactions[].summary` to `interactions[].description` (one-off authoring; widening the declaration for one artefact would normalise an idiosyncrasy rather than the contract).

### Lint debt cleared (P02-territory but surfaced now)

- `snapshot_compare.py:175` — split long function signature.
- `snapshot_compare.py:292` — replaced `Path(".")` with `Path()` (PTH201).
- `plan_metadata.py:141`, `tracking_metadata.py:45`, `tracking_metadata.py:75` — shortened long descriptions.

### Final gate

- `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` → **0 disagreements**.
- `uv run ruff check supekku` → all checks passed.
- `uv run python -m pytest supekku` → 4807 passed, 4 skipped.
- `uv run spec-driver validate` → 8 audit-gate warnings (baseline-identical).

### Malformed-YAML files (informational, not gating)

The harness flags 18 files where YAML parse fails inside a known block marker. These are pre-existing data-quality bugs (backticks/unquoted scalars in YAML), unrelated to validator drift. Harness `Report.ok` ignores them per DEC-007's "verdict equivalence" framing — they will continue to fail YAML parsing regardless of which validator path runs them.

Files (block type in brackets):

- `.spec-driver/deltas/DE-021-kanban-card-support/IP-021.md` [verification.coverage]
- `.spec-driver/deltas/DE-030-unit_vs_assembly_spec_classification/IP-030.md` [verification.coverage]
- `.spec-driver/deltas/DE-033-memory_records_schema_and_command_surface/phases/phase-03.md` [phase.overview]
- `.spec-driver/deltas/DE-033-memory_records_schema_and_command_surface/phases/phase-08.md` [phase.overview]
- `.spec-driver/deltas/DE-039-workflow_command_surface_completion_and_strict_mode_lock_in/phases/phase-02.md` [phase.overview]
- `.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-10.md` [phase.overview]
- `.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-11.md` [phase.overview]
- `.spec-driver/deltas/DE-058-govern_pylint_signal_and_document_lint_standard/IP-058.md` [plan.overview]
- `.spec-driver/deltas/DE-058-govern_pylint_signal_and_document_lint_standard/IP-058.md` [verification.coverage]
- `.spec-driver/deltas/DE-064-spec_driver_doctor_workspace_health_diagnostics/phases/phase-01.md` [phase.overview]
- `.spec-driver/deltas/DE-071-cli_verb_noun_taxonomy_consistency_pass/IP-071.md` [verification.coverage]
- `.spec-driver/deltas/DE-072-remove_installer_backward_compat_symlinks/phases/phase-02.md` [phase.overview]
- `.spec-driver/deltas/DE-090-cli_relational_navigation_filters_show_output_and_cross_entity_queries/phases/phase-04.md` [phase.overview]
- `.spec-driver/product/PROD-002/PROD-002.md` [spec.capabilities]
- `.spec-driver/product/PROD-003/PROD-003.md` [spec.capabilities]
- `.spec-driver/product/PROD-014/PROD-014.md` [spec.capabilities]
- `.spec-driver/product/PROD-015/PROD-015.md` [spec.capabilities]
- `.spec-driver/tech/SPEC-122/SPEC-122.md` [spec.capabilities]

Recommendation: file as a single backlog issue ("Fix malformed YAML in 18 spec-driver block instances surfaced by snapshot harness") for separate triage. Not blocking any DE-118 work; not consumer-visible (every consumer repo's harness run will catch its own equivalent set).

### Hand-off to IP-118-P03

P02.5 fidelity landed; harness green; baseline-clean. P03 may begin per DR-118 §4 ordering — VerificationCoverageValidator first (zero external call sites; densest unit-test coverage; safest first swap).

---

## IP-118-P03 — Per-block migration (2026-05-11)

### C1 — VerificationCoverageValidator retired

**Discovery refining P01 inventory**: `VerificationCoverageValidator` has *zero production callers*. Beyond "no external sites with ID kwargs" (P01 §3.4 conclusion), the class itself is never instantiated in production code — only by tests and the snapshot harness. Production consumers (`requirements/coverage.py`, `changes/coverage_check.py`) use `load_coverage_blocks` for extraction only; no validation invocation. C1 therefore reduced to: delete class, trim tests, prune harness adapter map. No "loader swap" needed (DR-118 §4's framing of "Loader uses MetadataValidator(...)" is vacuous for this block — there was no loader).

This is good news for the retirement: removing dead code with no production callers carries zero behaviour-change risk. The `subject_id` kwarg in the retired signature was similarly unused by any production caller (only `verification_test.py`'s `test_validator_with_subject_id_*` exercised it).

**Patches landed:**

- `verification.py`: deleted `VerificationCoverageValidator` class (`:43–160`); dropped `classify_artifact_id` import; dropped `VALID_SUBJECT_KINDS` constant (only the class referenced it); removed `"VerificationCoverageValidator"` from `__all__`. Net: -120 LOC.
- `verification_test.py`: rewrote to retain only 6 extraction/load tests; deleted 25 hand-rolled-validator tests. Net: -370 LOC.
- `verification_metadata_test.py`: converted from dual-validation to MetadataValidator-only with `strict_unknown_keys=True`. Split into three classes (`TopLevelValidationTest`, `EntryValidationTest`, `StrictModeBehaviourTest`, `MetadataDescriptorTest`) to stay under `too-many-public-methods` threshold. Added two new strict-mode tests (unknown top-level key, unknown entry key) documenting the strict path. Header comment per DEC-007 limitation.
- `snapshot_compare.py`: removed `VerificationCoverageBlock` / `VerificationCoverageValidator` imports; deleted `_adapt_verification_coverage`; removed `"verification.coverage"` entry from `HAND_ROLLED_ADAPTERS`. Added docstrings to `Disagreement.{hand_rolled_passed,metadata_passed,render}`, `MalformedBlock.render`, `_print_report`, `main` to clear pre-existing pylint debt on a file I touched.

**Gate evidence:**

- `uv run ruff check supekku` — all checks passed.
- `uv run python -m pytest supekku` — 4786 passed, 4 skipped (was 4807 before C1; -21 reflects 25 deleted validator tests + 2 added strict-mode tests + 1 ported entry-not-object test, minus dual-validation overhead consolidation).
- `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` — OK (zero disagreements). 701 blocks dual-validated (was ~877), 176 blocks now counted as `metadata-only` (the 176 verification.coverage instances previously dual-validated now run metadata-only — as designed).
- `uv run spec-driver validate` — 8 audit-gate warnings + 2 install-skew lines = baseline-identical.
- `pylint-files` on touched files: 2 messages remaining (both `wrong-import-position` in `verification.py:164,165`, a repo-wide `# noqa: E402` pattern for schema registration; outside C1 scope).

**Refinement to phase-03.md**: C1 task detail described a loader swap. In practice, no production loader exists. Future P03 phase sheets / commit messages should not assume every retirement has a production loader to swap — some classes (this one, at least) are pure test-fixture artefacts at the production boundary.

**Next**: C2 (plan trio: PlanOverview + PhaseOverview + PhaseTracking).

### C2 — Plan trio retired

**Discovery, reinforces C1**: all three classes (`PlanOverviewValidator`, `PhaseOverviewValidator`, `PhaseTrackingValidator`) had **zero production callers** — confirmed by ripgrep of `supekku/` excluding tests + the harness. P01 §3.5 said "no external production sites" for the trio; C2 verified the inference. Same shape as C1: pure delete + test conversion + adapter prune. No "loader swap" anywhere.

**Test placement decision** (resolves phase-03 §11 R11 for the plan trio): created new `tracking_metadata_test.py`. Rationale:
- `tracking_metadata.py` is a separate file from `plan_metadata.py`; the test-file mirror should follow source-file boundaries.
- `plan_metadata_test.py` was 906 lines pre-C2; absorbing PhaseTracking corpus would push past 1000.
- Matches C1's `verification_metadata_test.py` precedent (one metadata module ↔ one metadata test file).
- **Rule for C3–C5**: `<source>_metadata_test.py` mirrors `<source>_metadata.py`. No "extend or new" question if both source files exist.

**Patches landed:**

- `plan.py`: deleted `PlanOverviewValidator` (`:52–163`), `PhaseOverviewValidator` (`:166–232`), `PhaseTrackingValidator` (`:235–358`); removed 3 entries from `__all__` (`:667/669/671` pre-edit). Net: -312 LOC. The three `BlockSchema` registrations at `plan.py:691/703/715` (now lines `:379/391/403`) remain — block validation flows through `MetadataValidator(BLOCK_SCHEMAS[…].metadata, strict_unknown_keys=True)` via the harness and any future caller; no production call site required wiring changes because none exists.
- `plan_metadata_test.py`: converted in place from dual-validation to MetadataValidator-only with `strict_unknown_keys=True`. Split structure preserved (`PlanMetadataValidationTest` + `PhaseMetadataValidationTest` + `PlanPhasesMetadataTest` + `JSONSchemaGenerationTest`). Added new `StrictModeBehaviourTest` with 3 strict-mode tests (unknown top-level key for plan, unknown phase-entry key for plan, unknown top-level key for phase). DEC-007 header comment per C1 convention.
- `tracking_metadata_test.py`: **new file**. 23 tests across 5 classes (`TopLevelValidationTest`, `CriteriaValidationTest`, `TasksValidationTest`, `FilesValidationTest`, `StrictModeBehaviourTest`). Mirrors the negative branches of the retired `PhaseTrackingValidator` plus C1-pattern strict-mode coverage.
- `tracking_test.py`: trimmed from 408 to 195 LOC. Dropped all `PhaseTrackingValidator()` instantiations (12 of them) and their tests; retained 9 extraction + completion-calculation tests. File header reframes the file as extraction-only and points readers to `tracking_metadata_test.py` for validation coverage.
- `snapshot_compare.py`: removed `PhaseOverviewBlock` / `PhaseOverviewValidator` / `PhaseTrackingBlock` / `PhaseTrackingValidator` / `PlanOverviewBlock` / `PlanOverviewValidator` imports; deleted `_adapt_plan_overview`, `_adapt_phase_overview`, `_adapt_phase_tracking`; removed `"plan.overview"`, `"phase.overview"`, `"phase.tracking"` entries from `HAND_ROLLED_ADAPTERS`. `HAND_ROLLED_ADAPTERS` now contains 3 entries: `revision.change`, `delta.relationships`, `spec.relationships`.

**Gate evidence:**

- `uv run ruff check supekku` — all checks passed (one E501 fixed mid-flight in `plan_metadata_test.py:255`).
- `uv run python -m pytest supekku` — 4802 passed, 4 skipped (+16 from the 4786 C1 baseline: +52 in `plan_metadata_test.py` net of -48 dual-validation, +23 in new `tracking_metadata_test.py`, -10 in `tracking_test.py` trim).
- `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` — OK (zero disagreements). 191 blocks dual-validated (was ~701 at C1 close), 686 metadata-only (was 176). 510 blocks shifted from dual-validated to metadata-only — the plan trio's footprint across `.spec-driver/`.
- `uv run spec-driver validate` — 8 audit-gate warnings + 2 install-skew lines = baseline-identical.
- `uv run python -m supekku.scripts.pylint_report` on touched files: score 9.90/10, 7 messages — all pre-existing on `plan.py` (3× `too-many-arguments` and 1× `too-complex` on render functions; 3× `wrong-import-position` for the schema registration pattern with `# noqa: E402`). Zero new pylint debt from C2.

**Next**: C3 (DeltaRelationshipsValidator + `validate_delta_relationships` wrapper; first commit with actual external call sites — 3 of them, plus the `requirements/sync.py:132` annotation surfaced in P01 §4).
