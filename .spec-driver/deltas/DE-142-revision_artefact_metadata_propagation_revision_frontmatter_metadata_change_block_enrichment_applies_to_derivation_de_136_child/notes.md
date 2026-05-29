# Notes for DE-142

## Session 2026-05-29 (6) — P04 consult (migration design locked)

P04 is the consult gate, not a mechanical phase. Ran a 4-agent read-only evidence
workflow (`de-142-p04-consult-evidence`) to ground the open decisions, then consulted.
**The evidence corrected the handover's central claim** and reshaped DR §8.

### Evidence (verified against current code/corpus, supersedes some recon claims)
- **Block ID patterns are NOT uniformly "SPEC-only".** Each field carries a
  kind-appropriate regex. The killer is `requirements[].requirement_id`
  (`revision_metadata.py:206`): `^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$`
  (+ 6 sibling copies at :99/:109/:119/:129/:275 and `destination.requirement_id`).
- **97 legitimate refs across ~24 records violate it** on two axes: (1) container
  prefix `PROD-*`/`ISSUE-*` (first-class spec-likes), not `SPEC-`; (2) requirement
  token `NF-` (and dotted suffix `FR-016.001`), not `(FR|NFR)`. **99 `NF-`
  requirements exist repo-wide** vs 437 `FR-` — `NF` is canonical, never matched.
- **Handover's `r".+"` delta-block claim was WRONG.** `DELTA_RELATIONSHIPS_METADATA`
  declares **NO** ID patterns (type=string only). The `r".+"` lives in
  `delta.context_inputs`/`risk_register` (different blocks). So the closest sibling
  runs pattern-free.
- **A partial canonical constant already exists, unused here:**
  `verification_metadata.py:22` `REQUIREMENT_ID_PATTERN = ^(SPEC|PROD)-\d{3,}...(FR|NFR)...`.
  Revision hardcodes SPEC-only ×7 (POL-001 dup). Even this constant misses `NF`/`ISSUE`.
- **`lifecycle` + `lifecycle.status` are both `required=False`** (`:297`,`:302`).
- **Zero corpus blocks use `action: move`** — 27 blocks are all `modify` (the
  `updated` counts are the separate `specs[].action` enum). FM-only records carry
  `source_specs == destination_specs` (in-place) or dest-only. So DR §8's
  synthesise-as-`move` is unimplementable (move requires `origin`, which nothing has).
- **DEC-05 confirmed**: `write_drift_ledger`/`_next_drift_id` are bespoke to
  `migrations/spec_requirements/migration.py:346`, called only by `migrate_requirements.py`.
  Generic `admin migrate` orchestrator captures `StepResult.drift_entries` but **never
  writes DL files** (only a per-run log). Mechanism architecturally incomplete.

### User decisions (consult, 2026-05-29) — all 4 ratified
- **DEC-CONSULT-04 → BROADEN to shared patterns.** Hoist/extend two shared constants
  and reuse across revision + verification blocks (POL-001, kills the dup + the latent
  NF bug):
  - `REQUIREMENT_ID_PATTERN = ^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NF|NFR)-[A-Z0-9.-]+$`
  - `SPEC_ID_PATTERN = ^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*$` (for `specs[].spec_id`,
    `destination.spec`, `destination.additional_specs[]`).
  - `RE-`/`DE-`/`AUD-` patterns (`metadata.revision`, `lifecycle.introduced_by/
    implemented_by/verified_by`) stay — they're correct.
  - F-F-safe: pure relaxation (no previously-valid block becomes invalid; not a `@v2`).
  - Rationale beats narrow/strict default: narrow here = MASSIVE real lossage (97 legit
    records) → the standing rule itself points to loosening.
- **DEC-CONSULT-03 → DISSOLVED. Synthesise `action: modify`, OMIT `lifecycle`.** No
  `unknown` value, no touching shared `REQUIREMENT_STATUSES` (3-5 consumers), R-142-02
  leak gone. **Supersedes approved DEC-142-04's `unknown` tolerated_alias** (ratified).
- **DEC-CONSULT-05 → NO auto-drift in this migration. Backlog the gap = ISSUE-061.**
  Broadened patterns + faithful modify-synthesis is a lossless reformat, not
  spec-vs-reality divergence → no drift entries warranted. Residual strict errors
  (expected ~0) dispositioned manually. Don't build the orchestrator drift helper
  speculatively in DE-142 (write-less / YAGNI).
- **DEC-CONSULT-07 → manual `[validation.strict].revision = true` AFTER
  VA-142-CORPUS-001 disposition**, decoupled from the migrate run (DR-136 §11.2 order).

### DR §8 corrections (ratified — see DR-142 §8/§12/§13 updates this session)
1. Synthesis action `move` → **`modify`**; `origin` from source_specs → **dropped**;
   `lifecycle.status: unknown` → **lifecycle omitted**.
2. Per-record drift emission → **removed** (no synthesis drift; manual residual).
3. Add pattern-broadening as work item (was implicit/absent).

### What's next
- **`/plan-phases`** → author `phases/phase-04.md`. Migration folder
  `v0_10_0_005_revision_metadata`. P04 tasks: (a) broaden+hoist the two ID-pattern
  constants, reuse in revision+verification blocks; (b) migration step (cut §4 +
  hand-rolled FM keys; synthesise modify-blocks for FM-only; idempotent; block-wins);
  (c) template cut (`supekku/templates/revision.md`); (d) sweep + VA-142-CORPUS-001;
  (e) manual strict flip. No drift-helper work (→ ISSUE-061).

## Session 2026-05-29 (5) — P03 executed (list revisions enrichment)

### Done (TDD)
- **Domain** `changes/revision_check.py` (NEW): `RevisionChangeSummary(sources,
  destinations, requirements)` + cell methods + `revision_change_summary(artifact)`.
  sources ← `requirements[].origin[].ref` (kind=spec); destinations ←
  `requirements[].destination.spec`; requirements ← `requirement_id`. Sorted+deduped,
  tolerant load, multi-block union. Mirrors `audit_check.AuditFindingsSummary`.
- **Columns** `REVISION_COLUMNS` (ID, Name, Status, Source, Destination, Requirements).
- **Formatter** `format_revision_list_row/json/table` (`change_formatters.py`). Strips
  `"Spec Revision - "` name prefix. **Adaptive Source-hide** (DEC-CONSULT-06, user-approved):
  Source column dropped in the TABLE view when no revision has an origin; TSV + JSON keep
  the full schema. `RevisionChangeSummary` imported top-level (no cycle → cleaner than the
  audit inner-import mirror).
- **CLI** `list_revisions` wired thin: `{r.id: revision_change_summary(r)}` +
  `format_revision_list_table` (replaced generic `format_change_list_table`). Filters kept.

### User decision this session
- **DEC-CONSULT-06 → adaptive Source column** (not fixed 6-col, not dropped). User asked
  "can we cheaply hide it if no non-nil values?" — yes (~mirrors `show_external` pattern).

### Verification
- VT-142-LIST-001/002/003/004 + adaptive-hide: 82 targeted pass. Live `list revisions`:
  Source HIDDEN (corpus has zero origins), Destination/Requirements populated; `--json`
  stable schema. Regression (cli/list + changes + formatters): 770 passed, only the 2
  pre-existing width-wrap delta-list failures. ruff/ty clean; pylint net **+1** (one
  `too-complex` on `format_revision_list_table`, McCabe 12 == its `format_audit_list_table`
  sibling — faithful mirror; no new message types). Phase-03 validated + `completed`;
  IP §6 VT-142-LIST-* → verified, §9 P03 checked.

### Housekeeping
- Stray untracked telemetry dirs (`.spec-driver/deltas/.spec-driver/run/` + the DE-142
  bundle one) **deleted** (user-approved) → `show_test::test_path_and_json_mutually_exclusive`
  now passes (pre-existing failures: 3 → 2, both width-wrap). Underlying CWD-resolution bug
  filed as **ISSUE-060**.

### Future DRY (noted, not done)
- `format_revision_list_table` + `format_audit_list_table` share an identical row-cell
  styling loop (id/status markup). Extracting `_styled_change_cell` would drop both below
  the `too-complex` threshold. Out of P03 scope (touches audit).

---

## Session 2026-05-29 (4) — P02 executed (FM completion + applies_to derivation)

### Done (TDD red→green→refactor)
- **FM class** (`core/frontmatter_metadata/revision.py`): completed the DE-137 stub to
  the NARROW shape via explicit BASE key-picks (id,name,slug,kind,status,created,
  updated,relations,tags,ext_id,ext_url) — NOT a `**BASE` splat (which would re-admit
  the universal-cut keys). `status` enum-replaced; docstring de-stubbed; 2 examples.
- **`kind` enum pinned to `["revision"]`** — surfaced at RED: the shared BASE `kind`
  enum OMITS `revision` (lists `design_revision`, not RE-* `revision`). Latent
  pre-existing bug (never tripped — revision strict validation isn't on). Fixed
  locally (no shared-BASE widening). Left the BASE omission as an observation.
- **applies_to deriver** (`changes/artifacts.py`): `_derive_revision_applies_to(blocks,
  frontmatter)` — unions `specs[].spec_id` / `requirements[].requirement_id` across all
  blocks (`extract_revision_blocks` returns a list), `sorted(set())`, block-first /
  FM-fallback, per-block `parse()` tolerant skip. Hooked `elif kind == "revision":` in
  `load_change_artifact`. Kept local (POL-001 — 2 call sites, different block shapes).
- **R-142-04 confirmed MINOR**: no kind-specific check code; the generic
  `validator.py:128` declared-fields unknown-key check is armed for revision by the
  narrow field set alone. VT-142-DERIVE-002 proves it (strict error / strict=False ok).
- **Tests**: `revision_test.py` (FM-001/002 + DERIVE-002); 8 deriver cases + RE-050
  integration leg in `artifacts_test.py` (DERIVE-001). 37 targeted + 9 subtests pass.

### Verification evidence
- Full `pytest supekku`: **5244 passed, 4 skipped**; only the **3 known pre-existing
  failures** (2 width-wrap `ListDeltasMalformedFrontmatterTest`; 1 stray-telemetry
  `show_test::test_path_and_json_mutually_exclusive`). Zero new.
- ruff check/format + ty clean on touched files; whole-repo `ruff check` passes.
  pylint **net-improved**: `use-implicit-booleaness-not-comparison` 4→0 (fixed my 2 +
  4 pre-existing); zero new message types. `load_change_artifact`'s pre-existing
  `too-complex`/`too-many-*` (present at HEAD) nudged by the 1-line `elif`, count
  unchanged — left as pre-existing observation.
- `validate file phase-02.md`: clean. Phase-02 → `completed`. IP §6 coverage
  VT-142-FM-001/002 + DERIVE-001/002 → `verified`; IP §9 P02 checked.

### Handoff → P03 (list enrichment)
- Reuse `_rev_block(data)` fixture helper (artifacts_test.py) + RE-042/RE-040 corpus.
- The source/destination SPLIT (origin vs `destination.spec`) is recomputed in
  `changes/revision_check.py` (NEW), NOT read from `applies_to` (which is the deduped
  union). `RevisionChangeBlock.parse()` is on-demand.
- **Open UX consult (DEC-CONSULT-06)**: `list revisions` columns — Source is empty for
  all 42 current records. Bring the rendered mockup before wiring the formatter.
- P03 work is parallelisable (domain summary / column_defs / formatter / CLI / 4 list
  tests) → candidate for a small implementation workflow.

### Deferred (unchanged)
- P04 block-pattern + `unknown`-enum decisions (DEC-CONSULT-03/04), drift-write
  mechanism (05), flip timing (07), stray-dir deletion (08) — bring at P03/P04.

---

## Session 2026-05-29 (3) — recon workflow + P02 planning + consult

### Done
- **Recon workflow** (`de-142-recon`, 6 agents, read-only): mapped P02-P04 code
  reality vs DR-142 and surfaced an 8-item decision register. Key outcomes:
  - **R-142-04 resolved MINOR** (was flagged ARCH): the FM-beside-block strict
    check needs NO bespoke/kind-specific code. `validator.py:128-134` is a generic
    declared-fields unknown-key check; revision is already registered
    (`__init__.py:52`); `get_strict_map` reads `[validation.strict].revision`
    generically. P02 verifies via VT-142-DERIVE-002, adds no check code.
  - **Corpus FM survey (42 revisions)**: only
    `id,name,slug,kind,status,created,updated,relations,aliases,destination_specs,
    requirements,source_specs` present. **None** carry
    `lifecycle/auditers/source/owners/summary` → narrow FM shape is **lossless**.
  - **P04 corpus issue (deferred)**: the `revision.change@v1` block patterns are
    SPEC-only (`^SPEC-\d{3}`) while the sibling **delta** block uses `pattern=r".+"`.
    Corpus pervasively references `PROD-*` (first-class spec), `ADR-*`, `ISSUE-*`,
    `NF-`. Strict would drift-track ~38/42 legit records, and a dest-only synthesised
    `move` trips P01's origin+destination rule (RE-030). DR §8's synthesis is partly
    unimplementable as written → needs a pattern decision at P04 (DEC-CONSULT-03/04).
  - Baseline: targeted suite 1298 passed/0 failed @ default width. The "3 failures"
    split: `show_test` mutually-exclusive is the stray-telemetry dir; the two
    `ListDeltasMalformedFrontmatterTest` are terminal-width wrap artifacts. Suite is
    width-brittle BOTH ways.

### User decisions this session (consult)
- **DEC-CONSULT-01 → NARROW FM shape** (zero corpus lossage). Declared set = DR §5
  table exactly: Base 7 + relations + tags + ext_id + ext_url; omit
  lifecycle/auditers/source/owners/summary.
- **DEC-CONSULT-02 → NARROW applies_to.specs** (DR §6): `specs` from
  `block.specs[].spec_id` only; source/dest split recomputed in P03, not folded in.
- **P04 decisions (03/04 patterns+`unknown`, 05 drift-write, 06 list UX, 07 flip
  timing, 08 stray-dir delete) DEFERRED** — bring researched proposals at P03/P04.
- User interaction preference captured to memory `user-decision-density-preference`:
  unpack consequential decisions with example YAML; lean narrow/strict unless real
  data shows lossage; no dense multi-question batches.

### Done (planning)
- `phases/phase-02.md` authored (6 tasks, ~4 files, TDD). P01 wrap-up handoff closed.

### What's next
- **`/execute-phase` for IP-142-P02** (TDD per phase-02 §7). Inline (small, sequential
  TDD) — reserve workflow orchestration for P03 (parallel: domain/columns/formatter/CLI/tests)
  and P04. Then plan P03, then consult+plan P04.

---

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
- **Status**: DE-142 `in-progress`. **P01/P02/P03 COMPLETE** (commits `44c54f58`, `084e8616`, + P03). P04 NOT started — it is the consequential gate.

### Next activity — **P04 (migration + sweep + flip): CONSULT FIRST, then plan**
P04 is NOT a mechanical mirror like P02/P03 — recon proved the DR §8 plan is partly
unimplementable against the real corpus. **Do not start coding P04. Bring a focused
consult round** (the user wants UX/schema/arch decisions unpacked with example YAML;
lean narrow/strict unless the corpus shows real lossage — see memory
`user-decision-density-preference`). Open decisions (DR-142 §13 + recon register):
- **DEC-CONSULT-04 (SCHEMA, the big one)**: block ID patterns are SPEC-only
  (`^SPEC-\d{3}`) but the corpus pervasively uses `PROD-*` (a first-class spec),
  `ADR-*`, `ISSUE-*`, `NF-` (not `NFR-`). The sibling DELTA block uses `pattern=r".+"`.
  Strict flip would drift-track ~38/42 legit records; dest-only synthesised `move`
  (RE-030) trips P01's origin+dest rule. Decide: broaden patterns (likely right —
  arguably additive, not a redefinition) vs SPEC-only + drift-track. Bring before/after YAML.
- **DEC-CONSULT-03 (SCHEMA)**: `unknown` lifecycle status — DR DEC-142-04/§13.3 approved
  the WIDE shared-`REQUIREMENT_STATUSES`-enum path; recon recommends narrowing. Overriding
  the approved DEC needs ratification.
- **DEC-CONSULT-05 (ARCH)**: DL drift-write has no mechanism in the generic `admin migrate`
  orchestrator (only the bespoke migrate-requirements writes DLs). Recommend promoting
  `write_drift_ledger` to a shared migration helper.
- **DEC-CONSULT-07**: strict-flip timing — recommend manual `workflow.toml` flip AFTER
  VA-142-CORPUS-001 disposition (decoupled from the migrate run).
Then `/plan-phases` → author `phases/phase-04.md`; `/execute-phase`. Migration folder =
`v0_10_0_005_revision_metadata` (DEC-142-07). Next DL = DL-075.

### Corpus facts (verified — load-bearing for P04)
- 42 revisions: 27 carry a `supekku:revision.change` block, 15 are FM-only (need synth).
- ALL 42 carry hand-rolled `aliases` + (most) `source_specs`/`destination_specs`/
  `requirements` FM keys → cut by migration. ZERO carry `lifecycle/auditers/source/owners/summary`.
- ZERO have a populated `origin[]` (all completion-revisions, action=modify, dest only).
- Pattern-violating blocks (PROD/ADR/ISSUE/NF refs) ≈ 25/27 existing + ~13/15 synth targets.

### After P04 closes
- `[validation.strict].revision = true` in `workflow.toml`; then DE-136 P03 tasks 3.9–3.11
  (flip confirm, baseline) → DE-136 P04 umbrella close. Audit deferred to DE-136 umbrella
  (VA-DE136-CLOSE-001). DE-142 has no standalone audit.

### Historical (P01) — reference only
The P01-specific reading list below is retained for context; P01/P02/P03 are done.

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
