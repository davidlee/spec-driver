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

### C3 — `DeltaRelationshipsValidator` retired + first wrapper landed

**First swap with actual production callers** (C1/C2 were delete-only). All three sites + the `requirements/sync.py:132` validator annotation migrated to the new `validate_delta_relationships(block, *, delta_id=None)` helper. Wrapper lives alongside `DELTA_RELATIONSHIPS_METADATA` in `delta_metadata.py` per phase-03 §10 ("alongside metadata declaration"), preserving the POL-003 boundary (`validation/` not touched).

**Wrapper shape decisions:**

- Module-scope singleton `_DELTA_RELATIONSHIPS_VALIDATOR = MetadataValidator(..., strict_unknown_keys=True)` — instantiated once per process, not per call. Mirrors the harness pattern.
- Free function, not a class. Callers were already passing the validator as a kwarg to `_apply_delta_relations`; the kwarg evaporated and the helper is imported directly. `requirements/registry.py:239-243` lazy import + instantiation block removed entirely.
- ID-equality check preserves the legacy `elif delta_id and delta_value != delta_id` truthy semantics (`delta_id=None` and `delta_id=""` both skip), and the exact mismatch error string format. "Missing delta id" path moves to metadata-driven required-field enforcement; callers only saw the truthy/falsy verdict, so the message-shape change is invisible at the call sites.

**Patches landed:**

- `delta.py`: deleted `DeltaRelationshipsValidator` (lines `:28-87`, 60 LOC); removed `"DeltaRelationshipsValidator"` from `__all__` (`:171` pre-edit).
- `delta_metadata.py`: added `MetadataValidator` import; added `DeltaRelationshipsBlock` to existing `.delta` import; added module-scope strict validator; added `validate_delta_relationships(block, *, delta_id=None) -> list[str]`; exported in `__all__`.
- `delta_metadata_test.py`: converted `_validate_both` to call the wrapper instead of the legacy class (variable rename `old_errors → wrapper_errors`); fixed the stale "doesn't support delta_id yet" comment on `test_delta_id_mismatch` (now asserts metadata-only validator returns `[]` when ID equality is purely a wrapper concern); added new `WrapperTest` class with 5 wrapper-specific cases (match accepts, `None`/empty skip, strict unknown keys, combined metadata+ID errors).
- `changes/artifacts.py`: dropped class import, added wrapper import, swapped `DeltaRelationshipsValidator().validate(block, delta_id=...)` → `validate_delta_relationships(block, delta_id=...)` at `:122`.
- `requirements/registry.py`: removed lazy-import + instantiation block at `:239-243`; `_apply_delta_relations` now called without `validator=` kwarg.
- `requirements/sync.py`: top-of-file import migrated (class → wrapper); `_apply_delta_relations` kwarg `validator: DeltaRelationshipsValidator` removed entirely (the annotation cited in P01 §4 finding 1 is now obsolete, not migrated); body call site at `:171` (pre-edit) uses the wrapper directly.
- `snapshot_compare.py`: dropped `DeltaRelationshipsBlock` / `DeltaRelationshipsValidator` imports; deleted `_adapt_delta_relationships`; removed `"delta.relationships"` from `HAND_ROLLED_ADAPTERS`. Map now contains 2 entries: `revision.change`, `spec.relationships`.

**Gate evidence:**

- `uv run ruff check supekku` — all checks passed (after 2 E501 fixes in test assertion messages; `validate_delta_relationships` body itself reformatted to a single-line f-string by `ruff format`).
- `uv run python -m pytest supekku` — 4807 passed, 4 skipped (+5 from the C2 baseline of 4802: +5 in new `WrapperTest`).
- `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` — OK (zero disagreements). 52 dual-validated (was 191), 825 metadata-only (was 686). 139 delta-relationships blocks shifted from dual to metadata-only.
- `uv run spec-driver validate` — 8 audit-gate warnings + 2 install-skew lines = baseline-identical.
- `uv run python -m supekku.scripts.pylint_report` on touched files: total 32 messages (was 42 pre-C3). Net −10 messages, all from the deleted validator class and the registry's lazy-import block. Zero new pylint debt from C3.

**Findings refresh:**

- The "wrapper signature is `(block, *, delta_id)`" pattern works cleanly; the kwarg-on-helper pattern (`_apply_delta_relations(..., validator=...)`) was unnecessary plumbing introduced by the per-validator class. C4 and C5 should drop their analogous validator-kwarg threading the same way unless other state needs propagating.
- Per-call-site wrapper migrations are ~3 lines of diff each (import swap + call shape). No semantic surprises on this swap.

**Next**: C4 (RelationshipsBlockValidator + spec relationships/capabilities wrappers; new `relationships_metadata_test.py` per the `<source>_metadata_test.py` mirror rule).

### C4 — `RelationshipsBlockValidator` retired + spec wrappers landed

**Two wrappers in one commit.** Per DR-118 §4 / phase-03 §3.4:

- `validate_spec_relationships(block, *, spec_id=None)` — direct mirror of C3's `validate_delta_relationships`. ID-equality preserved with the exact legacy error string `"relationships block spec {spec_value} does not match expected {spec_id}"`.
- `validate_spec_capabilities(block, *, spec_id=None)` — ergonomic. `spec_id` accepted for API symmetry and explicitly `del`'d in the body with a docstring note. Adding ID-equality here would tighten validation beyond the DE-118 invariant-preserving scope (no legacy `SpecCapabilitiesValidator` ever existed), so it remains caller-driven. The metadata declaration already enforces `spec` field presence + string type.

**Test-file placement.** Phase-03 §3.4 named `relationships_metadata_test.py` as the new file; the C2 `<source>_metadata_test.py` mirror rule (resolved on 2026-05-11) makes `spec_metadata_test.py` the correct name. Wrapper code lives in `spec_metadata.py`, not `relationships.py`, so the mirror points there. 32 tests across 3 classes (`SpecRelationshipsWrapperTest` 18, `SpecCapabilitiesWrapperTest` 8, `MetadataOnlyTest` 5 + JSON-schema sanity case).

**Patches landed:**

- `relationships.py`: deleted `RelationshipsBlockValidator` (lines `:32-95`, 64 LOC); removed `"RelationshipsBlockValidator"` from `__all__`.
- `spec_metadata.py`: added `MetadataValidator` to existing metadata import; added `RelationshipsBlock` to the `.relationships` import; added two module-scope strict validators; added `validate_spec_relationships` and `validate_spec_capabilities`; both exported.
- `spec_metadata_test.py`: **new file** (35 tests including DEC-007 header note).
- `requirements/registry.py`: dropped `RelationshipsBlockValidator` import (line `:12`); removed `relationships_validator = RelationshipsBlockValidator()` instantiation (was `:162`); `_apply_spec_relationships` called without `validator=` kwarg (was `:236`).
- `requirements/sync.py`: hoisted `extract_relationships` + `validate_spec_relationships` to module-top imports (alongside the C3 delta-block imports); dropped the inner-import block in `_apply_spec_relationships`; removed `validator: Any` kwarg from the function signature. The `:132` annotation finding from P01 §4 is now historical — no validator instance exists to type.
- `snapshot_compare.py`: dropped `RelationshipsBlock` / `RelationshipsBlockValidator` imports; deleted `_adapt_spec_relationships`; removed `"spec.relationships"` from `HAND_ROLLED_ADAPTERS`. Map now contains 1 entry: `revision.change`.

**Gate evidence:**

- `uv run ruff check supekku` — all checks passed (test file reformatted once by `ruff format`).
- `uv run python -m pytest supekku` — 4839 passed, 4 skipped (+32 from C3 baseline of 4807: all in new `spec_metadata_test.py`).
- `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` — OK (zero disagreements). 26 dual-validated (was 52), 851 metadata-only (was 825). 26 spec.relationships blocks shifted off dual.
- `uv run spec-driver validate` — 8 audit-gate warnings = baseline-identical.
- `uv run python -m supekku.scripts.pylint_report` on touched files: net −4 messages (30 → 26). Notable: hoisting the spec_relationships imports to module-top removed the 2 `import-outside-toplevel` warnings in `_apply_spec_relationships` that would otherwise have been preserved; the `del spec_id` pattern resolved the `unused-argument` warning on the ergonomic wrapper without breaking the symmetry-of-API intent.

**Findings refresh:**

- The kwarg-threading collapse generalises: both C3 and C4 dropped `validator=` kwargs from their `_apply_*` helpers without losing any semantic. C5 (`RevisionBlockValidator`) likely follows the same shape — `_apply_revision_blocks` in `requirements/sync.py:203` accepts the validator as a positional construction, not a kwarg, so the migration profile differs slightly but the wrapper-import shape is the same.
- Inner imports of `extract_relationships` + `validate_spec_relationships` were safe to hoist to module-top. The cyclic-import warning (1, pre-existing) is `relationships → spec_metadata` for the schema-registration import at `relationships.py:281`; it does not propagate through sync.py top imports.
- Phase-03 §6 said "spec.capabilities block has no `spec` field at the data layer". The metadata declaration (`spec_metadata.py:135`) **does** declare a required `spec` field. The phase-sheet phrasing was imprecise — what it really meant was "no legacy ID-equality enforcement existed". The wrapper docstring records the actual reason (invariant preservation), not the imprecise data-layer claim.

**Next**: C5 (RevisionBlockValidator + `_disallow_extra_keys` helper retirement; 2 external sites + `changes/blocks/__init__.py:48,57` re-export removal; extends `revision_metadata_test.py` with the 4 regex-bug cases per DR-118 §5).

### C5 — `RevisionBlockValidator` retired + harness adapter map empties (2026-05-16)

**Wrapper shape — divergent.** Phase-03 §3.5 prescribed direct `MetadataValidator(REVISION_CHANGE_METADATA, strict_unknown_keys=True)` swaps at call sites, no wrapper. C5 added `validate_revision_change(data) -> list[str]` in `revision_metadata.py` anyway, for two reasons:

- Two call sites benefit from a cached module-scope `MetadataValidator` instance (matches the C3/C4 `_DELTA_RELATIONSHIPS_VALIDATOR` / `_SPEC_RELATIONSHIPS_VALIDATOR` pattern).
- Symmetry with the three sibling wrappers makes the wrapper-or-direct decision rule consistent across `delta_metadata`, `spec_metadata`, and `revision_metadata` modules.

**Signature divergence — intentional.** Unlike the sibling wrappers (`validate_delta_relationships(block, ...)`, `validate_spec_relationships(block, ...)`), `validate_revision_change` accepts a **parsed `data` dict** rather than a `RevisionChangeBlock` instance. Reason: `RevisionChangeBlock` parses on demand via `.parse()` (no cached `.data` attribute) and `changes/updater.py` validates a mutable dict in place across an intervening status mutation — calling `.parse()` post-mutation would reset the mutation. Docstring documents the divergence and the caller pattern (`validate_revision_change(block.parse())`). No `revision_id` parameter — the legacy class never enforced ID equality, so adding the parameter would be the `validate_spec_capabilities` `del`-pattern footgun without the symmetry benefit (no caller passes the ID).

**Patches landed:**

- `revision.py`: deleted `RevisionBlockValidator` class (`:362-892`, 530 LOC), `_disallow_extra_keys` helper (`:350-359`), and `ValidationMessage` dataclass (`:258-281`); `__all__` trimmed; removed unused `is_kind` + `Sequence` imports; module docstring updated.
- `revision_metadata.py`: added `MetadataValidator` import + `Any` typing import; introduced module-scope `_REVISION_CHANGE_VALIDATOR` + `validate_revision_change(data)`; `__all__` extended.
- `revision_test.py`: trimmed three hand-rolled-validator tests (`test_validator_accepts_minimal_valid_payload`, `test_validator_flags_missing_destination_for_move`, `test_validator_flags_invalid_additional_specs`); kept extraction + YAML rewrite coverage. Schema-shape tests live in `revision_metadata_test.py`.
- `revision_metadata_test.py`: full rewrite to wrapper + direct-validator dual assertion (was hand-rolled vs metadata). Three legacy "conditional-rule" tests (`test_requirement_origin_required_when_move`, `test_requirement_destination_required_when_introduce`, `test_requirement_destination_required_when_move`) dropped as intended DR-118 §5 drift — those allOf rules lived only in `REVISION_BLOCK_JSON_SCHEMA` (P04 deletion) and the retired class. Added `test_requirement_additional_specs_invalid_pattern` (ported from `revision_test.py`) and the 4 regex-bug regression tests per DR-118 §5 (canonical RE-/DE-/AUD- ids accepted in `metadata.revision`, `lifecycle.introduced_by`, `lifecycle.implemented_by`, `lifecycle.verified_by`). DEC-007 header note added. 41 tests, all green.
- `requirements/sync.py`: dropped `RevisionBlockValidator` import; added `validate_revision_change` import; `_apply_revision_blocks` validator-construction line removed (was inside the helper, not threaded as a kwarg — kwarg-collapse footprint zero this round).
- `changes/updater.py`: same import swap; pre/post-error diff now uses `set(validate_revision_change(data))` directly (the wrapper's `list[str]` return is set-keyable).
- `changes/blocks/__init__.py`: `RevisionBlockValidator` re-export removed (`:48`, `:57`).
- `snapshot_compare.py`: removed `RevisionBlockValidator` import and `_adapt_revision` adapter; `HAND_ROLLED_ADAPTERS` is now `{}` with a comment pointing at phase-03 §3.6 for the P04 lifecycle decision.

**Gate evidence:**

- `uv run ruff check supekku` — all checks passed.
- `uv run python -m pytest supekku -q` — 4837 passed, 4 skipped (test count net -2 from C4: -3 dropped conditional-rule tests, +4 regex-bug tests, +1 additional_specs test from `revision_test.py`, -3 hand-rolled `revision_test.py` cases, plus convergence to MetadataOnly-only assertions; tally checked at 41 in `revision_metadata_test.py`).
- `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` — OK (zero disagreements). 0 dual-validated (was 26 — `HAND_ROLLED_ADAPTERS` empty), all blocks counted under `blocks_metadata_only`. The harness now reports a pure metadata-only smoke pass, consistent with phase-03 §3.6 default (option a: keep, defer lifecycle to P04). Malformed-YAML noise (3 files) is pre-existing.
- `uv run spec-driver validate` — 8 audit-gate warnings = baseline-identical (modulo install-skew lines).
- `uv run python -m supekku.scripts.pylint_report` on the 7 touched files: net **−13 messages** (33 → 20), score 9.70 → 9.77. The bulk of the improvement comes from `revision.py` (16 → 3): retiring `RevisionBlockValidator` deletes three pre-existing `too-complex` methods (`_validate_requirement` at McCabe 43, `_validate_spec` at 20, `_check_root` at 11) plus their `too-many-branches` / `too-many-locals` companions. The pre-existing `revision → revision_metadata` cyclic-import warning persists (unchanged baseline; P04 will collapse REVISION_BLOCK_JSON_SCHEMA + the schema-registration hook). `revision_metadata_test.py` gains one `too-many-public-methods` (41/20) — was already over the 20 threshold at 36 in the C4 baseline; the +4 regex-bug + +1 additional_specs tests deepen it, but the class is intentionally flat for parallel-corpus readability per DEC-007.

**Findings refresh:**

- **Zero retired classes remain.** `rg "class.+Validator" supekku/scripts/lib/blocks/` returns nothing matching the seven hand-rolled retirees. `HAND_ROLLED_ADAPTERS` is `{}`. The dual-validate harness is now a metadata-only smoke test — phase-03 §3.6 default (option a) honoured; OQ-HARNESS-LIFECYCLE remains open for P04.
- The kwarg-collapse pattern (C3/C4) did **not** generalise to C5 — `_apply_revision_blocks` constructs the validator inside the helper (not via a kwarg), so there was nothing to collapse. The wrapper still removed the construction-then-method-call indirection, but no signature changes propagated to callers.
- DR-118 §2 regex-bug premise verified: the 4 `\\d` patterns in `REVISION_BLOCK_JSON_SCHEMA` (revision.py:43, :213, :217, :223) survived to P03 close because the hand-rolled validator used `is_kind` (a Python-level check) and no consumer evaluated the JSON Schema. The metadata declaration uses correctly escaped `\d` patterns; the 4 regex-bug regression tests pin the canonical-id acceptance so a P04 reintroduction of the double-backslash would fail unit tests before snapshot_compare even runs.
- `RevisionChangeBlock` is the only one of the three retired-validator block dataclasses without a cached `.data` attribute (`DeltaRelationshipsBlock` and `RelationshipsBlock` both store parsed `data` post-extraction). Wrapping a block-with-parse-on-demand is *fundamentally different* from wrapping a block-with-cached-data: the former cannot be re-validated post-mutation through the wrapper, so the wrapper accepts data. Future block introductions should default to the cached-`.data` shape unless mutation-cycle semantics genuinely require otherwise.

**P03 closure status:** 5/5 swap commits landed. `HAND_ROLLED_ADAPTERS` empty. All exit criteria from phase-03 §4 met. Hand-off to P04: `REVISION_BLOCK_JSON_SCHEMA` deletion + `_entry_shape` replacement + OQ-NAMING-COLLISIONS rename + OQ-HARNESS-LIFECYCLE settlement.

### P03 closure summary (2026-05-16)

- **Commits (5/5)**: C1 `deec4017` (VerificationCoverageValidator), C2 `075781a0` (plan trio: PlanOverview + PhaseOverview + PhaseTracking), C3 `9478980e` (DeltaRelationshipsValidator + `validate_delta_relationships` wrapper), C4 `0b1d6947` (RelationshipsBlockValidator + `validate_spec_relationships` + `validate_spec_capabilities` wrappers), C5 `2c5b7073` (RevisionBlockValidator + `_disallow_extra_keys` + `ValidationMessage` + `validate_revision_change(data)` wrapper). All within the R8 ≤4-week window (C1 → C5 same-day window: 2026-05-11 to 2026-05-16).
- **Hand-rolled validator residue**: zero. `rg "class.+Validator" supekku/scripts/lib/blocks/` returns no matches for the seven retirees.
- **Wrapper helpers (4 total)**: `validate_delta_relationships(block, *, delta_id=None)` in `delta_metadata.py`; `validate_spec_relationships(block, *, spec_id=None)` and `validate_spec_capabilities(block, *, spec_id=None)` (ergonomic-only; `del spec_id`) in `spec_metadata.py`; `validate_revision_change(data)` in `revision_metadata.py` (data signature divergence, intentional — see C5 finding).
- **Harness final state (HEAD = `5d555985`)**: `uv run python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` → `scanned 1656 files, 0 dual-validated, 877 metadata-only.` → `snapshot-compare: OK (zero disagreements).` `HAND_ROLLED_ADAPTERS = {}`; the dual-validate harness is now a pure metadata-only smoke pass (option a per phase-03 §3.6 default). Malformed-YAML noise (18 instances) is pre-existing and tracked separately per P02.5 §289.
- **`uv run spec-driver validate` final state**: 8 audit-gate warnings + 2 install-skew lines = baseline-identical against `validate-baseline.txt` (which remains the unchanged regression target through DE-118 close, per DR-118 §5).
- **OQ-HARNESS-LIFECYCLE**: still open; settles in P04 alongside OQ-NAMING-COLLISIONS and `REVISION_BLOCK_JSON_SCHEMA` deletion. Default option (a) — keep `snapshot_compare.py` with empty `HAND_ROLLED_ADAPTERS` as runnable infrastructure — is what HEAD ships.


## IP-118-P04 — Cleanup (2026-05-16)

### 4.1 — Delete `REVISION_BLOCK_JSON_SCHEMA` + 4 regex bugs

- **Pre-deletion grep** (`rg "REVISION_BLOCK_JSON_SCHEMA" supekku/ .spec-driver/`): only `revision.py:26` (definition) + `revision.py:482` (`__all__`) + test docstring/comment references (`revision_metadata_test.py:5,808`) + `.spec-driver/**` documentation references. Zero production consumers. Safe to delete.
- **Files touched**: `supekku/scripts/lib/blocks/revision.py` (literal + `__all__` entry + dead `REQUIREMENT_VALID_STATUSES` import deleted; deferred bottom imports promoted to top after cycle removed), `supekku/scripts/lib/blocks/revision_metadata.py` (now owns `REVISION_BLOCK_SCHEMA_ID` + `REVISION_BLOCK_VERSION`; cycle import removed).
- **Cyclic-import retirement APPLIED** (per phase-04 §9 decision). Net LOC delta well under the 50-LOC gate; canonical-declaration site for the two schema-identity constants moved to `revision_metadata.py` (better cohesion with the metadata declaration itself). `revision.py` now imports them via a single one-way top-level import. The pre-existing `# noqa: E402` markers on the bottom-deferred imports were removed.
- **Test behaviour**: `revision_metadata_test.py::test_metadata_generates_json_schema` already shape-asserts on `metadata_to_json_schema(REVISION_CHANGE_METADATA)` output; no rebase needed. The 4 `test_regex_bug_*` regression tests (P03 C5) continue as canonical guards against re-introducing the `\\d` bug. 41/41 tests pass.
- **Harness verification (post-edit)**: `uv run python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` → `scanned 1657 files, 0 dual-validated, 877 metadata-only.` → `snapshot-compare: OK (zero disagreements).` (1657 vs baseline 1656 = `.vscode/` untracked dir; not a regression.)
- **`spec-driver validate`**: byte-identical to `validate-baseline.txt` (8 audit-gate warnings + 2 install-skew lines).
- **Pylint on touched files**: 9.91/10, 1 message (`too-many-locals` at `revision.py:91` in `render_revision_change_block`, pre-existing). Cyclic-import warning gone.
- **Full test suite**: 4837 passed, 4 skipped, 0 failures (149s).


## New Agent Instructions

### Task card
- **Active delta**: DE-118 — Block schema unification: retire hand-rolled validators.
- **Active phase**: IP-118-P04 — Cleanup. Phase sheet authored (commit `1d9c5d1b`); seven tasks scoped (4.1–4.7); status `draft`. Next agent runs `/execute-phase DE-118 IP-118-P04 4.1` to start.
- **P03 status**: closed at commit `237cd99d` (chore close commit). 5/5 swap commits landed (C1 `deec4017`, C2 `075781a0`, C3 `9478980e`, C4 `0b1d6947`, C5 `2c5b7073`); `HAND_ROLLED_ADAPTERS` empty; harness final state recorded; IP-118 §9 ticked.
- **Worktree**: clean at HEAD `1d9c5d1b`. Untracked `.vscode/` is the user's IDE config (not project-owned).
- **Card path**: `.spec-driver/deltas/DE-118-block_schema_unification_retire_hand_rolled_validators_single_metadata_driven_validation_layer/DE-118.md`
- **Phase sheet**: `phases/phase-04.md` (same bundle; supersedes phase-03.md as active sheet)
- **Notes (you are here)**: `notes.md` (same bundle)

### Required reading (before 4.1)
1. `phases/phase-04.md` end-to-end — full task breakdown, §4 exit criteria, §5 verification expectations, §6 STOP conditions, §8 risk register (R7 / R12–R16), §9 pre-planned decision slots.
2. This `notes.md` "P03 closure summary" + C5 entry — pins the wrapper signature divergence + cyclic-import baseline that 4.1 may optionally retire.
3. `IP-118.md` §4 P04 row (updated 2026-05-16 to mention OQ-HARNESS-LIFECYCLE), §9 progress ledger.
4. `DR-118.md` §4 "Phase 3 — Cleanup" table (row-for-row source for tasks 4.1–4.3), §7 DEC-006 (IMPR-035 close-change audit gate — drives 4.7), §8 OQ-NAMING-COLLISIONS + OQ-HARNESS-LIFECYCLE, §9 R6 (DR-136 cross-ref is best-effort; IMPR-035 is the only durable record), §9 R7 (`_entry_shape` migration is *new enforcement*, not equivalence).
5. `notes.md` §5 — OQ-NAMING-COLLISIONS site enumeration for 4.4 / 4.5. Do not re-enumerate during execution unless a pre-rename grep widens the surface.

### Related docs
- `DE-118.md` (delta charter; §8 must reference IMPR-035 — verified in 4.7).
- `IP-118.md` (implementation plan; §9 ticks "IP-118-P04 complete" + "ready for audit-change" at 4.7).
- `validate-baseline.txt` (8-warning audit-gate baseline — **not** updated per DR-118 §5; immutable through DE-118 close).
- Parent umbrella: `.spec-driver/deltas/DE-136-.../DE-136.md`, `IP-136.md` (DE-118 is Phase 2 foundation for DE-136; DE-137 is the receiver for DEC-006 deferral).
- `.spec-driver/backlog/improvements/IMPR-035-…/IMPR-035.md` — load-bearing close-change record audited in 4.7.

### Key files for P04
- **4.1**: `supekku/scripts/lib/blocks/revision.py:28` (`REVISION_BLOCK_JSON_SCHEMA` literal + 4 regex bugs at `:43/:213/:217/:223`); `revision.py:1055` (`__all__` entry); `revision_metadata_test.py::test_metadata_generates_json_schema` (rebases onto metadata-derived schema); the 4 `test_regex_bug_*` tests (P03 C5; remain as regression guards). Optional cyclic-import retirement: move `REVISION_BLOCK_SCHEMA_ID` / `REVISION_BLOCK_VERSION` from `revision.py` to `revision_metadata.py`.
- **4.2**: `supekku/scripts/lib/blocks/sessions_schema.py:88` (`_entry_shape` sentinel → `additional_properties=_SESSION_ENTRY`); sibling test placement per `<source>_metadata_test.py` mirror rule.
- **4.3**: `supekku/scripts/lib/blocks/*_metadata.py` (grep `FieldMetadata(.*items=FieldMetadata(` to find array-of-object shapes).
- **4.4**: `blocks/delta.py:15`, `blocks/relationships.py:15`, `changes/blocks/__init__.py:23,60`, `specs/__init__.py:21,40` (per notes.md §5).
- **4.5**: `changes/lifecycle.py:20`, `requirements/lifecycle.py:14`, `blocks/verification.py:24`, `blocks/verification_metadata.py:16`, `cli/schema_test.py:441-447`, `spec_driver/orchestration/enums.py:20-30` (per notes.md §5).
- **4.6**: `supekku/scripts/lib/blocks/metadata/snapshot_compare.py` + `snapshot_compare_test.py`; `__all__` lines across `blocks/`, `changes/blocks/`, `requirements/`, `specs/`.
- **4.7**: `.spec-driver/backlog/improvements/IMPR-035-…/IMPR-035.md`; `DE-118.md` §8; `IP-118.md` §9.

### Relevant memories
- None DE-118-specific exist. Three patterns worth capturing via `/capturing-memory` at DE-118 close (track all three; do not drop any):
  1. **`<source>_metadata_test.py` mirror rule** (phase-03 §9, 2026-05-11) — test-file-placement convention that resolved R11. 4.2 will apply this when deciding `sessions_metadata_test.py` vs `sessions_schema_test.py`.
  2. **Block-class taxonomy** (phase-03 C5 finding) — `DeltaRelationshipsBlock` and `RelationshipsBlock` cache parsed `.data`; `RevisionChangeBlock` parses on demand via `.parse()`. The former is wrappable by-block; the latter must be wrapped by-data. Future block introductions should default to cached-`.data` shape unless mutation-cycle semantics genuinely require parse-on-demand.
  3. **Wrapper-signature divergence** (phase-03 C5 finding) — three sibling wrappers (`validate_delta_relationships`, `validate_spec_relationships`, `validate_spec_capabilities`) take blocks; `validate_revision_change` takes data. Document the asymmetry anywhere the wrappers are surveyed.

### Relevant doctrine
- `POL-001` — maximise reuse, minimise sprawl. 4.4 / 4.5 renames reduce sprawl by eliminating alias-on-import workarounds.
- `POL-003` — explicit module boundaries. P03 wrappers live in `*_metadata.py`; 4.1's optional cyclic-import retirement moves constants to their canonical declaration site (`revision_metadata.py`), reinforcing the boundary.
- `STD-003` — utility module placement; reinforces wrapper-alongside-metadata convention.
- `STD-004` — script lifecycle / orphan prevention. **Governs OQ-HARNESS-LIFECYCLE (4.6)**: the lifecycle decision must produce a documented owner + re-run trigger, regardless of which option is chosen.
- CLAUDE.md: "If you edit a file with pre-existing warnings — it is not an excuse to add more." P03 C3/C4/C5 all reduced pylint debt; P04 should continue. 4.1's optional cyclic-import retirement targets the pre-existing `revision → revision_metadata` warning specifically.
- CLAUDE.md: "Never delete a file with uncommitted/unstaged changes without user approval." 4.6 option (b) decommission deletes `snapshot_compare.py` + its test — the files are committed at HEAD so no user-approval gate triggers, but the irreversibility (R14) warrants explicit §9 decision logging.

### User instructions & decisions to honour
- **Don't combine tasks.** The user explicitly said "3.6 is bookkeeping the current phase, P04 is a fresh planning scope" (2026-05-16). P04 tasks 4.1–4.7 are independent commits; do not bundle 4.1 with 4.4, etc. Sequencing is by §7 task ordering, not bundling.
- **Wrappers go alongside the metadata declaration**, never in a new module (phase-03 §10). Already applied in P03; relevant if 4.1's optional cyclic-import retirement extends to moving constants.
- **The `del unused_param` idiom** for "API symmetry, no semantic" is the C4 `validate_spec_capabilities` precedent. C5 declined to use it because there was no symmetry benefit (`validate_revision_change` has no sibling-with-ID-equality). Be precise about *when* to invoke the pattern in P04 — generally don't unless a sibling wrapper takes the same kwarg.
- **Commit message format** (P03 lineage): `feat(DE-118): <subject> (P04 <N.M>)` for code-changing tasks (4.1–4.5); `chore(DE-118): <subject> (P04 <N.M>)` for cleanups (4.6) and close (4.7).
- **Do not update `validate-baseline.txt`.** DR-118 §5 marks it as the immutable regression target through DE-118 close.
- **Pre-planned decisions** (phase-04 §9 has slots; record rationale before committing): OQ-HARNESS-LIFECYCLE option (a/b/c) at 4.6; cyclic-import retirement apply/defer at 4.1; test-file placement at 4.2.

### Incomplete work / loose ends
- **P04 tasks 4.1–4.7** — see phase-04 §7. Each is independently landable; 4.4 / 4.5 / 4.7 have ordering dependencies (4.5 after 4.4; 4.7 after 4.6).
- **Phase-03 §6 imprecision** — the "no `spec` field at the data layer" phrasing for `spec.capabilities` is wrong; corrected in C4 notes. Trust the C4 entry over phase-03 §6's wording. P04 work doesn't touch this; flag persists for any future audit pass.
- **`revision_metadata_test.py` size** — 41 tests, one `too-many-public-methods` (41/20) warning. Intentional per DEC-007 (flat parallel-corpus readability). **Do not split prematurely.** P04 may revisit only if 4.1's regex-bug deletion adds tests that push past ~45.
- **Wrapper-signature audit** — capture as memory once DE-118 closes (notes.md "Relevant memories" candidate #3). Not a P04 task; do not derail.
- **Three carryover tensions surfaced for P04 explicitly** (user prompt 2026-05-16):
  1. OQ-HARNESS-LIFECYCLE — settle at 4.6 (default option a per phase-03 §3.6).
  2. revision_metadata_test.py 41-method warning — don't pre-split.
  3. Pre-existing revision → revision_metadata cyclic-import — optional retirement at 4.1.

### Commit-state guidance
- Worktree clean at HEAD `1d9c5d1b` (P04 phase-sheet authoring commit). Untracked `.vscode/` is the user's IDE config; not project-owned.
- Per project doctrine: bias toward small, frequent combined commits of `.spec-driver/**` + code. Each P04 task should ship as its own commit (notes + IP tick + code change for that task). The original C5 prompt scoped a single commit; P04 follows the same shape.
- Do **not** update `validate-baseline.txt`.
- 4.7's IP-118 §9 tick can ship in the same commit as the final notes.md P04 closure entry, or as a separate `chore(DE-118)` close — match what naturally lands first. The audit-change skill picks up regardless.

### Other advice for the next agent
- The snapshot harness (`uv run python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .`) reports `0 dual-validated, 877 metadata-only, 0 disagreements` at HEAD. Re-run after every P04 commit; any drift is a regression.
- **4.1 pre-deletion grep is non-negotiable** — `rg "REVISION_BLOCK_JSON_SCHEMA"` across `supekku/` and `.spec-driver/`. The P01 inventory confirmed no production consumers, but verify before deleting.
- **4.4 / 4.5 pre-rename grep is non-negotiable** — `rg "\bRELATIONSHIPS_MARKER\b"` and `rg "\bVALID_STATUSES\b"` across the whole repo. The notes.md §5 enumeration is "focused, not exhaustive"; widening is in-scope.
- **OQ-HARNESS-LIFECYCLE decision is irreversible if option (b)** — see R14. Prefer (a) keep unless a strong reason (STD-004 ownership concern, or 4.6 audit reveals dead code beyond the empty adapter map). Document rationale in phase-04 §9 *before* committing.
- **IMPR-035 audit (4.7) is the close-change gate** — if the IMP names neither DE-137 nor DE-136 as receiver, STOP and surface to user. Do not improvise a third receiver.
- **`/audit-change` is the next workflow step after 4.7** — not another phase. DE-118 has no P05.

### Pointer to the structured handoff
- No `workflow/state.yaml` exists for this delta (checked at P04 scoping). The prose handoff above is canonical; `/continuation` did not need to call `spec-driver create handoff`. If orchestration is added mid-P04, re-evaluate.
