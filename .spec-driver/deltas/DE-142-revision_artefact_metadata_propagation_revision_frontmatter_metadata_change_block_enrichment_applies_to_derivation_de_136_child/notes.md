# Notes for DE-142

## Session 2026-05-29 — reconciliation + DR + planning

### Done
- **DR-136 §10.2/§10.5 erratum** (commit `45b756a1`): the canonical placement
  table sketched a *flat* `changes:` block that contradicted DE-118's shipped
  rich `metadata`/`specs`/`requirements` schema AND its own F-F scope-note
  ("additive enrichment, not redefinition"). Corrected in place to the shipped
  shape + field-mapping. Recorded in DE-136 phase-03 §9. Routed via /consult,
  user-approved erratum path (not a formal umbrella RE — DR-136 still draft,
  binding intent unchanged).
- **DR-142 authored + validated + internally adversarially reviewed** (commit
  `760d4984`). 7 work items, all grounded in current code reality. DE-142
  reconciled (scope/touchpoints/verification/OQs/risk register).
- **IP-142 + phase-01 sheet** (commit `b5363f73`). 4-phase plan; P01 ready.

### Key design facts (load-bearing — verified in code, not assumed)
- `supekku:revision.change@v1` is **DE-118's rich schema** (`blocks/revision_metadata.py`):
  top-level `metadata`/`specs`/`requirements`; `requirements[].action` enum
  (`introduce|modify|move|retire`) **already exists**. DE-142 is **additive only**
  (F-F) — NO `@v2`, NO block reshape.
- `REVISION_FRONTMATTER_METADATA` already exists as a **DE-137 stub** (Base +
  status only). DE-142 *completes* it (Base 7 + relations + tags + ext_id/ext_url).
- `ConditionalRule` (`blocks/metadata/schema.py`) is **top-level only** —
  `_validate_conditional_rules` does dot-path dict traversal, cannot reach
  `requirements[].action`. DE-142 P01 extends `FieldMetadata` with object-scoped
  `conditional_rules` applied in `_validate_object` (DEC-142-02). Only
  `test_engine.py` uses top-level rules today → low refactor blast radius.
- `applies_to` is **derived, never stored** (DEC-138-10 no-competing-truths);
  precedent `_derive_applies_to` in `changes/artifacts.py:29`. Revisions load via
  `ChangeRegistry(kind="revision")`.
- Migration folder is **`v0_10_0_005_revision_metadata`** (follows
  `v0_10_0_004_audit_findings`), NOT DR-136's ordinal "v06" (DEC-142-07,
  precedent DEC-141-05).
- `list revisions` lives in **`cli/list/reviews.py`** (same file as audits).

### What's next
- **`/execute-phase` for IP-142-P01** (engine + block conditional rules). Move
  DE-142 to `in-progress` at start. TDD per phase-01 §7 tasks 1.1–1.6.
- Then P02 (FM + applies_to), P03 (list), P04 (migration + sweep + strict flip).
- **Audit deferred to DE-136 umbrella close** (VA-DE136-CLOSE-001), per
  DE-139/DE-141 sibling precedent.
- After DE-142 closes + `[validation.strict].revision = true`: DE-136 P03 tasks
  3.9–3.11 (flip confirm, baseline check, phase wrap), then P04 umbrella close.

### Memory to capture once P01 lands (not yet — design only)
- "Object-level `FieldMetadata.conditional_rules` enable per-array-item
  validation" — capture as a metadata-engine capability memory after it's real.
  → **landed**; memory `mem.pattern.spec-driver.field-conditional-rules` written.

---

## Session 2026-05-29 — P01 executed (engine + block conditional rules)

### Done
- `FieldMetadata.conditional_rules` (additive, default `[]`) — `schema.py`.
- `_validate_conditional_rules` → `_apply_conditional_rules(obj, rules, path_prefix)`
  (`validator.py`). Top-level `validate()` passes `prefix=""` (no leading dot);
  `_validate_object` passes `field_path` → array-item errors read
  `requirements[2].origin`.
- Extracted `_validate_additional_keys` from `_validate_object` (the rule-call
  pushed McCabe 10→11; extraction restores it). Behaviour-identical.
- `requirements[]` item declares 3 `ConditionalRule`s: move→{origin,destination},
  introduce→{destination}, modify→{destination}; retire/`specs[]` unconstrained.
- Tests: `ObjectScopedConditionalRuleTest` (test_engine.py, ENGINE-001/002/003);
  `RequirementActionConditionalRuleTest` (new file
  `revision_metadata_conditional_test.py`, BLOCK-001/002/003). 121 targeted pass.

### Verification evidence
- Full `pytest supekku`: **5229 passed, 4 skipped**. **3 pre-existing failures**
  (`cli/list_test.py::ListDeltasMalformedFrontmatterTest` ×2,
  `cli/show_test.py::ShowPathFlagTest::test_path_and_json_mutually_exclusive`) —
  reproduce on clean HEAD with this work stashed; caused by stray untracked
  `.spec-driver/deltas/.spec-driver/run` telemetry polluting CLI discovery. Not P01.
- ruff/ruff-format/ty clean; pylint no new message types (validator matches HEAD
  baseline after the extraction).

### Residual → P02+
- **JSON-schema gap**: `metadata_to_json_schema` emits `allOf` only from
  `BlockMetadata.conditional_rules`; per-item `FieldMetadata.conditional_rules`
  are NOT projected to JSON Schema. Runtime validation correct; doc/schema parity
  deferred. Flag if JSON-schema consumers need the if/then.

### Handoff → P02 (FM completion + applies_to derivation)
- R-142-04 still open: confirm FM-beside-block strict check generalises to
  `kind:revision` (may be delta-keyed).
- `applies_to.specs` dedup/order to finalise (DR-142 §13.2 / §7.1 split).
- F-F additive-only; DEC-138-10 derive-don't-store; DR-136 §11.1 engine/migration
  boundary still hold.

---

## New Agent Instructions

### Task card
- **This delta**: `.spec-driver/deltas/DE-142-revision_artefact_metadata_propagation_revision_frontmatter_metadata_change_block_enrichment_applies_to_derivation_de_136_child/`
- **Parent (umbrella)**: `.spec-driver/deltas/DE-136-metadata_schema_consolidation_program_propagate_adr_010_across_artefacts_and_close_prod_004/` (DE-142 is the last per-artefact child; tracked in DE-136 phase-03 task 3.8)
- **Status**: DE-142 `draft`; DR-142/IP-142 authored & validated; phase-01 sheet ready. Move DE-142 → `in-progress` when execution starts.

### Next activity
**`/execute-phase` for IP-142-P01** (engine + block conditional rules). TDD per `phases/phase-01.md` §7 tasks 1.1–1.6. Foundation phase; P02–P04 build on it.

### Required reading (in order)
1. `DR-142.md` §4 (engine extension + declared rules), §13 (adversarial residuals — esp. §13.1 behaviour-preservation, §13.2 applies_to composition, §13.3 alias blast radius)
2. `phases/phase-01.md` (task breakdown + VT specs + STOP conditions)
3. `IP-142.md` §4 (phase overview), §6 (test plan)
4. DR-136 §10 (reconciled placement table) + §11.1/§11.2 (engine/migration boundary, sweep procedure)
5. DE-136 `notes.md:78` (F-F scope-note — the binding additive directive)

### Key files (code, verified this session)
- `supekku/scripts/lib/blocks/metadata/schema.py` — `FieldMetadata`, `ConditionalRule`, `BlockMetadata`
- `supekku/scripts/lib/blocks/metadata/validator.py` — `_validate_conditional_rules` (:529), `_validate_object` (:476), `_validate_array` (:432)
- `supekku/scripts/lib/blocks/metadata/test_engine.py` — ONLY current top-level `conditional_rules` user; must stay green
- `supekku/scripts/lib/blocks/revision_metadata.py` — `REVISION_CHANGE_METADATA` (declare requirements[] rules here)
- `supekku/scripts/lib/core/frontmatter_metadata/revision.py` — DE-137 stub to complete (P02)
- `supekku/scripts/lib/changes/artifacts.py` — `_derive_applies_to` (:29) precedent (P02)
- `supekku/cli/list/reviews.py` — `list revisions` (:33) (P03)
- Real fixtures: `RE-042` (well-formed `modify`+`destination`, no `origin`) — regression guard

### Relevant memories
- `mem.pattern.validation.per-kind-block-wiring`
- `mem.pattern.spec-driver.block-class-data-taxonomy`
- `mem.pattern.spec-driver.metadata-validator-strictness`
- (run `/retrieving-memory` at execute start)

### Relevant doctrines
- **F-F (load-bearing)**: additive over DE-118; no block redefinition, no `@v2`.
- **DEC-138-10**: `applies_to` derived, never stored (no competing truths).
- **DR-136 §11.1**: metadata engine = application code (current-schema); migration = legacy-aware, stdlib+helpers only.
- POL-003 (no business logic in formatters); STD-002 (lint/pylint); ADR-008 (intent vs observed).

### User decisions this session
- Block-shape conflict → **pause + /consult** (not silent adoption).
- Reconciliation → **in-place erratum** on DR-136 §10.2 (not formal RE; not full re-derivation).
- Conditional-rule enforcement → **extend FieldMetadata** (declarative engine change), not hand-rolled per-item checks, not deferral.
- Scope locked: all 7 work items + OQ defaults accepted.
- Then → **/plan-phases** (done).

### Loose ends / unresolved (assess before coding)
- IP-level details (DR-142 §13): error-path prefix on generalised helper (no leading dot); `applies_to.specs` dedup/order; `unknown` alias sunset wording.
- R-142-04: confirm the FM-beside-block strict check generalises to `kind:revision` (may be delta-keyed) — P02 concern.
- R-142-01: legacy `action: move` blocks missing `origin` will error at strict flip — P04 sweep must drift-track first.

### Commit-state guidance
- Worktree clean re: this work. All DE-142/DE-136 artefacts committed (`45b756a1`, `760d4984`, `b5363f73`, `717c5872`).
- Pre-existing unrelated changes (NOT mine, do not commit): `.gitignore`, `flake.lock`, `flake.nix` (modified), `.vscode/` (untracked).
- **Stray junk**: `.spec-driver/deltas/.spec-driver/run/events.jsonl` — misdirected CLI telemetry (bad CWD); not staged; safe to ignore/remove.
- Repo doctrine: prefer frequent small `.spec-driver/**` commits; code + `.spec-driver` may commit together or separately. During P01, commit engine+block code with its tests (red/green/refactor).
