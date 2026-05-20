# Notes for DE-138

## 2026-05-20 - Adversarial review prep

- Read DE-138 and found `DR-138.md` exists but is still the stock draft template; substantive review should wait until it is rewritten.
- Review anchors: DE-138 scope, DR-136 section 6 for delta placement/list/migration commitments, DR-136 section 11.4-11.5 for migration package boundaries and narrative duplication limits, ADR-010 for placement heuristic, POL-001/POL-002/POL-003, STD-001/STD-003/STD-004.
- Main scrutiny points for DR-138:
  - It must restate and not weaken all five DR-136 section 6 outcomes: derived `applies_to`, `context_inputs` block, `risk_register` block, `outcome_summary` prose placement, `list deltas` enrichment, and `v02_delta_blocks.py` migration.
  - It must justify every ADR-010 exception. In particular, `applies_to` being derived from a block is an exception to frontmatter-first stable tooling metadata, so the design must make the canonical source and fallback window explicit.
  - It must preserve the transition-window contract: block-first, frontmatter-second until strict flip; frontmatter `applies_to` becomes strict-mode error after the sweep; cleanup delta removes dead fallback later.
  - Migration design must be idempotent, file-level, atomically written, log-emitting, drift-producing for irreconcilable disagreements, and independent of validation/registry imports.
  - Formatter/CLI enrichment must keep CLI skinny and avoid body parsing in formatters; list columns should be derived from frontmatter, relationships blocks, and lookups only.
  - Verification must cover coverage-gate parity, migration synthesis/removal, list output, strict/tolerant behavior, outcome insertion before Implementation Notes or EOF, and realistic corpus exercise for PROD-004.FR-007.
- SPEC-115 is still a stub, so DR-138 cannot lean on it for concrete behavioral authority without either filling the gap via the DR or creating follow-up spec work.
- `uv run spec-driver` warned that workflow.toml has 0.9.2 while runtime is 0.9.7; this was observed during inspection only.

## 2026-05-20 - External hostile review integration

- External reviewer raised F-138-14..25 (5 high / 5 medium / 2 low) against DR-138 §§1-17.
- All 12 findings integrated in-place per internal-pass convention:
  - **F-138-14** (import-linter violation): §7.6 restated, §7.7 split to frozen-local emitters with byte-equality VT; DEC-138-12.
  - **F-138-15** (collaborators dropped): §6.1 union primary + collaborators; §7.3 step 6 reconciliation; VT-DE138-COLLAB-001; DEC-138-11.
  - **F-138-16** (revision_links projection loss): §6.1 `_derive_revision_link_relations` discrete helper; VT-DE138-RELLINK-001; `code_impacts[]` artifacts.py expanded.
  - **F-138-17** (universal-only files skipped): §7.2 regex extended.
  - **F-138-18** (strict plumbing collapsed): DEC-138-10 — loader unconditionally tolerant; validator owns strict; §3.2/§3.3/§6.1/§6.2 restated.
  - **F-138-19** (audit glyph mismatch): §8.2 + §8.3 use `audited_delta_ids` from FM `delta_ref`; DEC-138-13.
  - **F-138-20** (Workspace facades): §8.3 rewritten with `delta_registry`/`audit_registry`; filter preservation explicit.
  - **F-138-21** (malformed/duplicate blocks): VT-DE138-MALFORMED-001.
  - **F-138-22** (rollback overclaim): §11.5 split A/B; §11.2 pre-sweep checkpoint anchor.
  - **F-138-23** (gate is no-op): `code_impacts[]` adds `spec_driver/presentation/cli/validate/workspace.py` wiring; §10.5/§11.2 gate pinned to wiring; VT-DE138-GATE-001; DEC-138-14. **Severity promoted external→final: medium → high.**
  - **F-138-24** (deferred follow-up governance): §15.1 requires tracking-artefact filing before acceptance.
  - **F-138-25** (stale DE-138 §5 paths): §17.1 supersession table.
- Five DECs added (DEC-138-10..14); seven verification IDs added (VT-DE138-COLLAB-001, RELLINK-001, MALFORMED-001, GATE-001, MIG-003).
- §16 index now split into 16.1 (internal) + 16.2 (external) panels.
- DR-138 status remains `draft`; ready for next review pass or shape-revision sign-off before plan-phases.

## 2026-05-20 - External hostile review pass 2 integration

- Reviewer raised F-138-26..33 against pass-1 integrations (2 high / 5 medium / 2 low). All hollow/inconsistent.
- Two structural defects from pass 1 corrected:
  - **F-138-26**: §7.3 still referenced `load_markdown_file`/`dump_markdown_file` (forbidden supekku.* imports; `dump_markdown_file` removed in IP-137-P02). Rewrote step sequence to use `_helpers.split_frontmatter` + `yaml.safe_load` + `_helpers.atomic_write` + local emitters; explicit isolation note added.
  - **F-138-27**: migration did not synthesise `delta.relationships@v1` block when FM `applies_to` non-empty + block absent. Added §7.3 step 3 + §7.4 partial-shape row + §7.5 drift kind + VT-DE138-RELSYNTH-001. In-repo only 2 deltas hit this shape (empty applies_to), but consumer repos may carry non-empty FM.
- Five mediums:
  - **F-138-28**: §7.2 regex used wrong cut set; corrected to DR-136 §4 (`lifecycle, aliases, auditers, source` — NOT owners).
  - **F-138-29**: §8.3 used nonexistent `.all()` method; rewrote to `ChangeRegistry.iter(status=...)`.
  - **F-138-30**: VT-DE138-DERIVE-001 carried stale strict-parameter language; rewrote per DEC-138-10.
  - **F-138-31**: §5.3 emitted `summary: null` for plain-string normalisation; schema is non-nullable str; switched to key omission; VT-DE138-CTX-002.
  - **F-138-32**: §5.4 contradicted §5.1 on `unknown` handling; rewrote to distinguish literal tolerated alias from truly unrecognised values; VT-DE138-CTX-002 covers both.
- Two lows:
  - **F-138-33**: §15 summary undid §11.5 A/B split; mirrored.
- Three VTs added (VT-DE138-RELSYNTH-001, VT-DE138-CTX-002, VT-DE138-DERIVE-001 rewrite).
- §16.3 panel added; revision_log entry added.
- Step-number references chased across §7.3 → §9.2, F-138-D, F-138-H, F-138-15 index rows.
- DR-138 status remains `draft`; recommend third pass to verify hollows closed.

## 2026-05-20 — P01 close — Schemas + load-time synthesis landed

- DR-138 promoted to `accepted`; DE-138 to `in-progress` at phase entrance. Baseline pre-P01: ruff + format clean, 4894 pytest pass, 3/3 import-linter contracts kept.
- Code changes (all in supekku/):
  - `blocks/delta.py`: added CTX/RISK constants (`DELTA_CONTEXT_INPUTS_MARKER`, `DELTA_RISK_REGISTER_MARKER`, schemas, versions), dataclasses (`DeltaContextInputsBlock`, `DeltaRiskRegisterBlock`), `extract_delta_context_inputs` / `extract_delta_risk_register` / `render_delta_context_inputs_block` / `render_delta_risk_register_block`, plus `register_block_schema` calls for both new schemas.
  - `blocks/delta_metadata.py`: declared `DELTA_CONTEXT_INPUTS_METADATA` (strict + `unknown` tolerated_alias on `entries[].type`, field_aliases ref→id, note→summary, annotation→summary) and `DELTA_RISK_REGISTER_METADATA` (strict + `description→title` alias, status default `open`). Added validator helpers `validate_delta_context_inputs` / `validate_delta_risk_register`.
  - `blocks/metadata/__init__.py`: re-exported `ToleratedAlias` to keep the public surface coherent.
  - `changes/artifacts.py`: added `_derive_applies_to(block, frontmatter)` and `_derive_revision_link_relations(block)` per DR-138 §6.1. Deleted the lines 111-149 merge region and the lines 151-154 revision-link projection. Loader is now unconditionally tolerant per DEC-138-10. `_derive_applies_to` unions `specs.primary ∪ specs.collaborators` per DEC-138-11.
  - `changes/delta_creation.py`: drops FM `applies_to` / `context_inputs` keys; renders empty CTX + RISK blocks alongside the relationships block; populated CTX entries land in the block when caller passes them.
  - `changes/creation.py`: `create_plan` now reads `applies_to` via `load_change_artifact` (single derivation path).
  - `core/frontmatter_metadata/delta.py`: stripped the four FM declarations (`applies_to`, `context_inputs`, `risk_register`, `outcome_summary`); base + audit-gate fields unchanged. Updated complete-example fixture to match the new shape.
  - `templates/delta.md`: hand-authored body §§1-8 (§7 Risks deleted, §§8-9 renumbered to §§7-8); template includes `{{ delta_relationships_block }}`, `{{ delta_context_inputs_block }}`, `{{ delta_risk_register_block }}` placeholders.
- Test deltas: +13 VTs in `artifacts_test.py` (DERIVE/COLLAB/RELLINK), +25 VTs in `delta_metadata_test.py` (CTX/RISK/MALFORMED), +4 VTs in `templates_test.py` (TPL-001), plus updates to `creation_test`, `compaction_test`, `cli/compact_test`. Total: 5330 pytest pass (up from 4894), 4 skipped.
- Verification: VT-DE138-CTX-001, CTX-002, RISK-001, MALFORMED-001, DERIVE-001, COLLAB-001, RELLINK-001, TPL-001 all green. IP-138 `verification.coverage@v1` entries flipped to `verified`.
- Tolerant baseline: `validate workspace --kind delta` exit 0 — only pre-existing warnings (7× audit-gate-not-found, 1× DR-030 unresolved). DE-138 self-load via FM-fallback confirmed (no block yet — P03 sweep synthesises it).
- Quality gates: ruff lint + format clean. `uvx import-linter lint` 3/3 contracts kept (architectural layers, domain internals, migrations isolation). pylint 9.69/10 with no new findings on touched files (the listed too-complex / too-many-* are pre-existing on the same files; my changes net-removed code from `load_change_artifact`).
- Deferred / hand-off:
  - VT-DE138-MALFORMED-001 duplicate-strict sub-case is at the validate-file/workspace layer (DEC-138-10) — lands with the strict-flip wiring in P04 alongside VT-DE138-FLIP-001 / VT-DE138-GATE-001.
  - VT-DE138-CREATE-001 full assertion lives in P02 (round-trips new deltas through migration `apply()` for idempotence); P01 ships only the smoke coverage via `creation_test`.
  - P02 entry: migration package skeleton lives at `spec_driver/migrations/v0_10_0_001_delta_blocks/` per DR-138 §7.1; frozen-local emitters (DEC-138-12) and `Migrations isolation` import-linter contract are the next gate.
- DR-138 / IP-138 / DE-138 frontmatter unchanged in scope (no execution-driven refinement needed); structured execution docs reconciled via `/update-delta-docs`.

## 2026-05-20 - Phase planning (IP-138 + P01 sheet)

- Created `IP-138.md` via `spec-driver create plan --delta DE-138`; refined boilerplate with:
  - `supekku:plan.overview@v1` block: P01..P04 phases; aligns_with DR-138.
  - `supekku:verification.coverage@v1` block: 22 entries spanning the full DR-138 §10 inventory (19 VTs + 2 VAs + 1 VH), phase-anchored.
  - Phase Overview table: P01 schemas+synthesis, P02 migration step (code only), P03 sweep+reconciliation, P04 strict-flip+post-flip gate — mirrors DR-138 §11.1.
  - Entrance/exit criteria pinned to DR-138 sections; risks roll up from §14 + DEC-138-14 wiring; open questions OQ-138-01..03 surfaced.
- Created phase sheet `phases/phase-01.md` via `spec-driver create phase --plan IP-138`; refined with:
  - Objective: land block schemas + `_derive_applies_to`/`_derive_revision_link_relations` refactor + `create delta`/template/FM-metadata updates. No corpus sweep (loader stays tolerant; FM-fallback preserves in-repo loadability).
  - 12-task breakdown with `[P]` parallelism markers on schema work (1.1-1.3).
  - Exit gates: VTs CTX-001/002, RISK-001, DERIVE-001, COLLAB-001, RELLINK-001, MALFORMED-001, TPL-001 green; tolerant baseline + import-linter clean.
  - STOP conditions: any loader regression on in-repo corpus, tolerant-vs-strict invariant violation (DEC-138-10), or non-idempotent template regen.
- Both IP-138.md and phase-01.md validate clean.
- DR-138 still `draft`; promotion to `accepted` (or operator sign-off) is a P01 entrance gate.
- DR-138 + IP-138 + P01 sheet tell the same story; ready for `/execute-phase` once entrance gates are clean.

## 2026-05-20 — P02 implementation — Migration step landed

- Phase sheet `phases/phase-02.md` populated from DR-138 §7 + §code_impacts (10 tasks, exit gates pinned to import-linter contract + zero-mutation smoke).
- Code landed:
  - `spec_driver/migrations/v0_10_0_001_delta_blocks/__init__.py` — re-exports `step` + `DeltaBlocksStep`.
  - `spec_driver/migrations/v0_10_0_001_delta_blocks/_emitters.py` — frozen-local emitters byte-equivalent to `supekku/scripts/lib/blocks/delta.py` render helpers (DEC-138-12). Local `_format_yaml_list` + `_normalise_entry` + `_render_block` mirror supekku-side patterns. No supekku imports.
  - `spec_driver/migrations/v0_10_0_001_delta_blocks/migration.py` — `DeltaBlocksStep(BaseMigrationStep)` with `applies_to_kind = "delta"`. Implements the full DR-138 §7.3 11-step pipeline: cut universals (`lifecycle/aliases/auditers/source`) + cut 4 delta-specific keys, synthesise relationships/context_inputs/risk_register blocks from FM when absent (RELSYNTH-001, F-138-27), reconcile FM ↔ block specs/requirements (DEC-138-11), normalise per §5.3, insert `## Outcome` (single-line/folded/literal scalar fixtures), delete `## 7. Risks & Mitigations` section, renumber `## 8/9` → `## 7/8` top-level only (F-138-D), atomic write. `head-of-file` regex per §7.2 (cut set per F-138-28). Drift kinds exposed as module-level constants for VT assertions.
  - `step = DeltaBlocksStep()` lives at the bottom of `migration.py` because the orchestrator's loader does `getattr(module, "step", ...)` on the module from `spec_from_file_location("_sd_migration.<name>", migration.py)` — `__init__.py` is not loaded by the orchestrator (DR-138 §7.1 implicitly assumed package loading; corrected here in execution).
  - `supekku/scripts/lib/changes/delta_creation.py` — dropped the hardcoded `aliases: []` from the delta FM dict (universal-cut keys not emitted at create time) so newly-created deltas pass `applies_to(path) == False` and round-trip the migration step as no-op (VT-DE138-CREATE-001).
- Orchestrator defect fixed in `spec_driver/presentation/cli/admin/migrate.py`:
  - `_import_step_module` did not `sys.modules[spec.name] = module` before `exec_module(module)`. Python 3.13 dataclass introspection (`dataclasses._is_type`) needs the module registered in `sys.modules` to resolve `cls.__module__.__dict__`. Without the fix, ANY step that uses `@dataclass(frozen=True)` under `from __future__ import annotations` crashes with `AttributeError: 'NoneType' object has no attribute '__dict__'` at the first `@dataclass` decorator. Never surfaced in DE-137 because the fake-step fixtures only used plain classes; DE-138 is the first real step.
  - 1-line fix per F-35 (bug-fix-allowed). Regression test added: `TestDiscovery::test_loads_step_using_local_dataclass`.
- Test coverage:
  - `migration_test.py` (in-package): 30 VTs covering applies_to regex, idempotence (clean target + parametrised over 7 fixtures), relationships-block synthesis (RELSYNTH-001), FM-block agreement/disagreement (MIG-003), collaborators union, context_inputs normalisation (CTX-001, CTX-002, F-138-31, F-138-32), risk_register normalisation (RISK-001), body §7 deletion + renumber + `## Outcome` insertion across single-line / folded / literal scalars (BODY-001), preview() zero-mutation (MIG-002), Protocol surface.
  - `supekku/scripts/lib/blocks/migration_byte_equality_test.py` (supekku side, allowed): 6 byte-equality VTs across the three emitter pairs (empty + populated). Lives supekku-side because the contract is one-way — supekku may depend on migrations, migrations may not depend on supekku.
  - `creation_test.py`: VT-DE138-CREATE-001 — `create delta` → migration `apply()` is no-op.
  - `migrate_test.py`: 1 dataclass regression test for orchestrator.
- Smoke gates: `uvx import-linter lint` 3/3 contracts kept (Migrations isolation intact); `admin migrate --list` + `admin migrate delta --check` + `admin migrate delta --dry-run` all succeed with zero file mutation on `.spec-driver/deltas/**`.
- Preview against the in-repo corpus (141 deltas): would touch 141; drift kinds = body_renumber (118), body_risk_narrative (137), context_input_unmapped_type (3), fm_requirements_unmatched (2), fm_specs_unmatched (3). Zero errors. Ready for P03 sweep (separate phase — pre-sweep checkpoint commit required first).
- `--dry-run` summary line `would touch 0` is a separate orchestrator UI bug (sums `results` which is empty under dry_run; should sum `previews`). Filed as a sibling issue; not blocking P02. Zero-mutation property holds.
- Quality gates: ruff lint + format clean on touched files. Full test suite re-run in progress at notes-write time; result expected ~+38 tests vs P01 close (30 + 6 + 1 + 1).

## 2026-05-20 — P03 close — Sweep + reconciliation

- DR-138 §8 list-deltas enrichment landed in commit `46976634` (P03.1). New helpers + `format_delta_list_row` + `format_delta_list_table` + `format_delta_list_json` in `change_formatters.py`; `DELTA_COLUMNS` + `DELTA_TAGS_COLUMN` in `column_defs.py`; `ChangeArtifact.audit_gate` field + loader read; CLI `deltas.py` routes through new formatter with `--tags` opt-in; `_collect_audited_delta_ids` walks completed audits via FM `delta_ref` (DEC-138-13).
- VT-DE138-LIST-001: 9 helper VTs in `change_formatters_test.py::TestDeltaListEnrichmentVTLIST001` + 8 CLI matrix VTs in `list_test.py::ListDeltasEnrichmentVTLIST001Test`. Both green pre-sweep + post-sweep.
- Pre-sweep tag `de-138-pre-sweep` @ `46976634` — load-bearing recovery anchor for DR-138 §11.5B; must not be deleted until cleanup delta closes.
- Sweep commit `2afc0833`: 141 deltas touched; `workflow.toml` gains `[migrations] last_applied = v0_10_0_001_delta_blocks` (bundled because reverting sweep must also revert orchestrator state).
- Drift kinds (recovered post-sweep by replaying `_transform()` against pre-sweep tree; orchestrator `_write_log` does not surface drift detail from `StepResult.drift_entries: list[Path]` — orchestrator gap noted as P04+ improvement, out of DE-138 scope per DR-137 DEC-137-26 freeze):
  - body_renumber (118) — disposition: auto_resolved.
  - body_risk_narrative (137) — disposition: dl_filed (via VA-RISK-RECON-001).
  - context_input_unmapped_type (3, all DE-006 plain-string entries) — disposition: accepted_noise (tolerated_alias `unknown` per §5.1).
  - fm_requirements_unmatched (2) — DE-020 ISSUE-025, DE-106 5× PROD-006 reqs — disposition: dl_filed → DL-048.002/.003.
  - fm_specs_unmatched (3) — DE-016 PROD-011, DE-020 PROD-010/SPEC-110/SPEC-113, DE-106 PROD-006/PROD-011 — disposition: dl_filed → DL-048.001/.002/.003.
- Drift log commit `717fced5` (VA-DE138-DRIFT-001 closure): `p03-sweep-drift-log.md` (durable record) + DL-048 (4 persistent entries; owner unassigned; cleanup delta scope).
- Reconciliation commit `6a7fe70b` (VA-DE138-RISK-RECON-001 closure): all 137 `body_risk_narrative` entries uniformly disposed as `file_dl` against pre-sweep tag. Per-delta narrative promotion into `risks[].mitigation` deferred to cleanup delta — rationale in `p03-risk-recon-log.md` §2:
  - 115/137 swept deltas are `status: completed` — body §7 prose is historical record.
  - For DE-118+-era deltas, body prose duplicates FM `risk_register` (which the sweep moved into the block).
  - 1500+ risk entries × 137 deltas inverts DE-138 scope; selective `keep_into_mitigation` for the 22 active deltas is appropriate cleanup-delta work.
  - Per-file recovery: `git show de-138-pre-sweep:<delta-path>`.
- VT-DE138-COV-001 (`coverage_check_test.py::test_de138_self_bootstraps_via_derived_applies_to_vt_cov_001`): live DE-138 derives `applies_to.specs == [PROD-004, SPEC-115]` + `applies_to.requirements == [PROD-004.FR-001/-002/-007]` via the `supekku:delta.relationships@v1` block; `check_coverage_completeness` processes without erroring (the strict-vs-status check at P04 will assert PROD-004 FRs reach `verified` after umbrella audit per F-138-L).
- Tolerant validate `validate workspace --kind delta`: exit 0, only pre-existing 7× audit-gate + 1× DR-030 warnings (identical baseline to P01 close).
- Corpus-level idempotence: `admin migrate delta --check` post-sweep returns "no pending migrations" (orchestrator state); per-file `applies_to(path)` short-circuits cleanly because cut keys are absent.
- PROD-004 coverage block flipped: 3 new entries (VT-DE138-LIST-001 → FR-001, VT-DE138-FLIP-001 → FR-002, VT-DE138-MIG-001 → FR-007) all `status: in-progress` (F-138-L lifecycle behaviour; umbrella audit at DE-136 P04 promotes to `verified`).
- IP-138 verification coverage entries flipped `planned` → `verified` for VT-DE138-LIST-001, VT-DE138-COV-001, VA-DE138-RISK-RECON-001, VA-DE138-DRIFT-001.
- DE-138.md §6 Verification Strategy populated with concrete coverage statements drawn from DR-138 §10.
- Hand-off to P04: pre-flip checklist (DR-138 §11.2) status — tolerant validate clean, both VAs closed, three sweep commits in place + pre-sweep tag retained. Outstanding for P04 entrance:
  - `--no-tolerated-aliases` wiring through `spec_driver/presentation/cli/validate/workspace.py` (DEC-138-14, F-138-23).
  - VT-DE138-GATE-001 (tolerated_alias artefact fails gate under `--no-tolerated-aliases`).
  - VT-DE138-FLIP-001 (post-flip workspace baseline strict clean).
  - VH-DE138-FLIP-001 (operator attestation pre-flip).
  - §9.5 follow-up audit tracking artefact filing (F-138-24).
- Orchestrator drift-detail gap (P04+ improvement candidate, out of DE-138 scope): `StepResult.drift_entries: list[Path]` carries paths only; `_write_log` cannot surface kind/detail. Extending the Protocol surface would need a scope-delta given DR-137 DEC-137-26 freeze. Current workaround (replay `_transform()` against pre-sweep tree) is operator-driven, not pipeline-emitted — adequate for one-off DE-138 close but not durable for sibling per-artefact deltas.

## 2026-05-20 — P04 partial — wiring + GATE/FLIP VTs landed; flip pending

- Phase sheet `phases/phase-04.md` authored (commit `728267a1`) + amended with baseline carve-out (commit `4bc87694`) + tasks 4.2/4.3/4.7 ticked.
- **4.1 pre-wiring strict baseline** — `validate workspace --kind delta --strict` exit 1: 7× audit-gate warnings (sibling drafts) + 1× error "References unresolved artifact 'DR-030' (via relation.introduces)" on DE-030. DR-030.md exists on disk but registry-resolution does not find it; filed as **ISSUE-057** (pre-existing baseline noise; not introduced by DE-138). DR-138 §11.2/§11.4/§10.5 amended to acknowledge this carve-out (post-flip gate tolerates `{7× audit-gate warnings + 1× DR-030 error}`; new errors beyond this fail the gate). /consult routed; user approved Option A.
- **4.2 wiring** (commit `6c638eea`) — DEC-138-14 / F-138-23. Threaded `accept_tolerated` (= `not no_tolerated_aliases`) through:
  - CLI: `spec_driver/presentation/cli/validate/workspace.py` — dropped `_ = no_tolerated_aliases` no-op.
  - Validator entry: `supekku/scripts/lib/validation/validator.py::validate_workspace` + `WorkspaceValidator.__init__` accept `accept_tolerated: bool = True` kwarg.
  - New method `WorkspaceValidator._validate_delta_blocks(delta_registry)` extracts context_inputs + risk_register blocks per delta, calls `DELTA_*_VALIDATOR.validate(block.data, strict=self.strict, accept_tolerated=self.accept_tolerated)`, dispatches each `ValidationError` at native severity via `_block_issue` helper (warning → `_warning`, error → `_error`).
  - `supekku/scripts/lib/blocks/delta_metadata.py`: validator instances `DELTA_CONTEXT_INPUTS_VALIDATOR` + `DELTA_RISK_REGISTER_VALIDATOR` unprivatised; added to `__all__`.
- **4.3 VT-DE138-GATE-001** green (commit `6c638eea`):
  - CLI end-to-end: `spec_driver/presentation/cli/validate/workspace_test.py::TestWorkspaceCliSmoke::test_no_tolerated_aliases_promotes_de006_tolerated_to_errors` exercises live-repo DE-006 (carries 3× `context_inputs[].type=unknown`); default `--strict` produces warnings, `--strict --no-tolerated-aliases` promotes to errors.
  - Validator-boundary: `validator_test.py::TestDeltaBlockTolerationGateVTDE138GATE001::*` (2 VTs) — synthetic fixtures DE-901/DE-902 isolate the per-kind path.
- **4.7 VT-DE138-FLIP-001 row 2** green (commit `6c638eea`): synthetic fixture DE-903 with `context_inputs[{type: document, summary: missing id}]` surfaces as `error` under strict. Note: original §4 design pointed at a cut-FM-key fixture, but cut FM keys are caught at the kind-aware FM validator path, not the per-kind block path; the "is required" block-schema assertion is the more direct proof of strict-on-validate enforcement for delta block schemas.
- **Post-wiring corpus state**: `validate workspace --kind delta --strict` now surfaces (in addition to the documented baseline) 3× `warning`-level tolerated_alias entries on DE-006 (`context_inputs[0..2].type: 'unknown' is a tolerated alias for 'document'`). These were always present in the corpus but only became visible after the wiring landed (previously the per-kind block validators were not invoked from the workspace path at all). Under `--no-tolerated-aliases` the 3 warnings become errors.
- **Outstanding for P04 close** (in order):
  1. **DE-006 tolerated-alias decision** — 3× `context_inputs[].type=unknown` entries surface as warnings under tolerant validate + errors under `--no-tolerated-aliases`. The DR-138 §11.4 post-flip gate is "`validate workspace --kind delta --strict --no-tolerated-aliases` returns 0 errors beyond the documented pre-existing baseline (audit-gate + DR-030)." DE-006 tolerated_alias entries were NOT part of the documented baseline at carve-out time — they were invisible. Two paths:
     (a) Re-classify DE-006's 3 `type: unknown` entries to canonical `document` (operator manual edit; one delta touched; sets correct precedent for tolerated_alias sunset behaviour).
     (b) Extend the §11.4 baseline carve-out a second time to include "+ DE-006 tolerated_alias warnings" — concedes that tolerated_alias surface is acceptable post-flip and shifts the burden to the tolerated_alias sunset trigger (DR-138 §5.1: "sunset trigger = delta-sweep close"; we are at delta-sweep close, so this concession would defeat the sunset's own purpose).
     Recommendation: (a) is correct per DR-138 §5.1 sunset semantics; DE-006 is a known-fix-needed surface and the strict-flip gate is precisely the mechanism to force the fix.
  2. **VH-DE138-FLIP-001 attestation** (4.4) — operator confirms pre-flip checklist (DR-138 §11.2) item-by-item before workflow.toml edit lands. Pre-flip checklist status as of handover:
     - [x] P03 sweep applied; pre-sweep tag intact (`de-138-pre-sweep` @ `46976634`).
     - [x] Sweep + drift log + reconciliation discrete commits (`2afc0833`, `717fced5`, `6a7fe70b`).
     - [x] VA-DE138-RISK-RECON-001 + VA-DE138-DRIFT-001 closed.
     - [x] `validate workspace --kind delta` tolerant clean (modulo baseline).
     - [x] `validate workspace --kind delta --strict` clean modulo carve-out (commit `4bc87694`).
     - [x] `--no-tolerated-aliases` wiring landed + VT-DE138-GATE-001 green (commit `6c638eea`).
     - [ ] **DE-006 disposition decision** (above).
     - [ ] Operator types attestation (form: "VH-DE138-FLIP-001 attested" or equivalent).
  3. **4.5 flip** — append to `.spec-driver/workflow.toml`:
     ```toml
     [validation.strict]
     delta = true

     [schema_version]
     delta = "0.10.0+001"
     ```
     Discrete commit (no other staged changes); message: `feat(DE-138): IP-138-P04 strict-flip — workflow.toml [validation.strict] delta=true + [schema_version] delta=0.10.0+001`.
  4. **4.6 / 4.8 post-flip gates** — `validate workspace --kind delta --strict` (corpus baseline FLIP-001 row 1); `validate workspace --strict` (whole-corpus regression); `complete delta DE-138 --dry-run` (coverage gate); `list deltas` smoke.
  5. **4.9 F-138-24 backlog issue** — `uv run spec-driver create issue "audit delta-vs-IP verification asymmetry"` (per DR-138 §9.5 + §15.1); populate body with audit shape + DE-136 P04 umbrella consumption point.
  6. **4.10 execution-doc reconciliation** — IP-138 coverage entries → verified for GATE-001 (row 1 done, row 2 not in IP-138 yet but listed under FLIP-001 — confirm IP-138 row structure), FLIP-001 (both rows), VH-FLIP-001; IP-138 §9 progress tracking ticked; DE-138 frontmatter `updated:` refreshed; this notes file appended with full P04 close section.
  7. **4.11 quality gates** — `just check` clean (note: `just` not on PATH in this environment; substitute `uv run python -m pytest supekku spec_driver && uv run ruff check supekku spec_driver && uv run ruff format --check supekku spec_driver && uvx import-linter lint`); final test count.
- **Pytest state**: 5450 pass, 4 skipped (+64 vs P03's 5386 — established inheritance pattern of fixture-based test classes from `WorkspaceValidatorTest`).
- **Commit chain since P03 close**: `728267a1` (P04 phase sheet) → `4bc87694` (ISSUE-057 baseline carve-out) → `6c638eea` (wiring + GATE/FLIP VTs). Pre-sweep tag `de-138-pre-sweep` remains intact at `46976634`.
