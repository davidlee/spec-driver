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
