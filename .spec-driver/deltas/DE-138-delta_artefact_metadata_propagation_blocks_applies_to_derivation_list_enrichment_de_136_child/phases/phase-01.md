---
id: IP-138-P01
slug: "138-delta_artefact_metadata_propagation_blocks_applies_to_derivation_list_enrichment_de_136_child-phase-01"
name: IP-138 Phase 01
created: "2026-05-20"
updated: "2026-05-20"
status: completed
kind: phase
plan: IP-138
delta: DE-138
---

# Phase 01 — Schemas + load-time synthesis

## 1. Objective

Land the two new `BlockMetadata` schemas (`supekku:delta.context_inputs@v1`, `supekku:delta.risk_register@v1`) and the load-time synthesis refactor in `supekku/scripts/lib/changes/artifacts.py` (`_derive_applies_to` + `_derive_revision_link_relations`). Update `create delta`, the delta template, and the delta FM metadata declarations so that **new** deltas emit the target shape (empty blocks, no FM cut keys). No corpus sweep in this phase — existing in-repo deltas continue to load via FM-fallback because the loader is unconditionally tolerant (DEC-138-10).

Phase deliverable is a workspace where:
- supekku-side schemas + render helpers exist and are unit-tested green.
- The artifacts loader is single-source on the relationships block (with FM fallback intact).
- `create delta` writes the new shape.
- All P01 VTs are green; in-repo workspace remains loadable and `validate workspace --kind delta` (tolerant) stays clean.

## 2. Links & References

- **Delta**: DE-138.
- **Design Revision Sections**:
  - DR-138 §5 (block schemas, normalisation rules, validation surface).
  - DR-138 §6.1 / §6.5 (load-time synthesis; `ChangeArtifact.to_dict()` unchanged).
  - DR-138 §9.3 / §9.4 (template + `create delta` update).
  - DR-138 frontmatter `code_impacts[]` — canonical paths × current/target.
  - DR-138 §10.1 VT inventory rows for CTX-001, CTX-002, RISK-001, DERIVE-001, COLLAB-001, RELLINK-001, MALFORMED-001, TPL-001.
  - DR-138 DEC-138-01, -02, -10, -11, -12 (load-time synthesis + tolerant-loader posture + collaborators union + boundary-driven duplication).
- **Specs / PRODs**: PROD-004.FR-001 (single validation layer); SPEC-115 (changes/blocks).
- **Support Docs**: DR-136 §§4-6 (parent placement); DR-137 §§5.1-5.4 (alias machinery already operational); AUD-026 (foundations evidence).

## 3. Entrance Criteria

- [x] DR-138 approved for execution (flipped to `accepted` 2026-05-20 with operator sign-off).
- [x] DE-137 closed; AUD-026 conformance evidence on file.
- [x] Workspace baseline: `just check` green pre-P01 (ruff lint + format + 4894 tests pass).
- [x] `uvx import-linter lint` green pre-P01 (3/3 contracts kept).

## 4. Exit Criteria / Done When

- [x] `supekku/scripts/lib/blocks/delta_metadata.py` declares `DELTA_CONTEXT_INPUTS_METADATA` + `DELTA_RISK_REGISTER_METADATA` with strict canonical schemas, field aliases per DR-138 §5.1/§5.2, and tolerated_alias `unknown` registered for `entries[].type` per DEC-138-02.
- [x] `supekku/scripts/lib/blocks/delta.py` exposes `extract_delta_context_inputs` / `render_delta_context_inputs_block` and `extract_delta_risk_register` / `render_delta_risk_register_block`, mirroring `delta_relationships` pattern.
- [x] `supekku/scripts/lib/changes/artifacts.py` lines 111-149 (dual FM+block applies_to merge) deleted; replaced by `_derive_applies_to(block, frontmatter)` per DR-138 §6.1. Lines 151-154 revision_links projection lifted into `_derive_revision_link_relations(block)` and re-invoked.
- [x] `supekku/scripts/lib/changes/delta_creation.py` writes `delta.context_inputs@v1` + `delta.risk_register@v1` empty blocks (`entries: []`, `risks: []`) alongside the relationships block; no FM source emitted for `applies_to`/`context_inputs`/`risk_register`/`outcome_summary`.
- [x] `supekku/scripts/lib/core/frontmatter_metadata/delta.py` removes the four cut-key declarations; `audit_gate` / `audit_gate_rationale` / base 7 / relations / tags / ext_id / ext_url unchanged.
- [x] `supekku/templates/delta.md` body §§1-8 (§7 Risks deleted; §§8-9 renumbered to §§7-8); FM template regenerated via `admin regenerate-templates`; empty `delta.context_inputs@v1` + `delta.risk_register@v1` blocks present below the relationships block; `## Outcome` absent (added post-execution).
- [x] VTs green: VT-DE138-CTX-001, VT-DE138-CTX-002, VT-DE138-RISK-001, VT-DE138-DERIVE-001, VT-DE138-COLLAB-001, VT-DE138-RELLINK-001, VT-DE138-MALFORMED-001, VT-DE138-TPL-001.
- [x] In-repo workspace stays loadable: `validate workspace --kind delta` (tolerant) returns 0 errors; existing FM `applies_to` artefacts continue to satisfy coverage gates via FM-fallback.
- [x] `just check` + `uvx import-linter lint` clean (ruff + format + pytest + import-linter green; pylint score 9.69, no new findings on touched files).

## 5. Verification

- **Unit suites**:
  - `supekku/scripts/lib/blocks/delta_test.py` — new render/extract assertions + alias + tolerated_alias normalisation (CTX-001, CTX-002, RISK-001, MALFORMED-001).
  - `supekku/scripts/lib/changes/artifacts_test.py` — `_derive_applies_to` matrix (block-only / block+FM-shadowed / FM-fallback / both absent); `_derive_revision_link_relations` projection; COLLAB-001 union path; RELLINK-001 ADR-002 compliance check.
- **Integration**:
  - `admin regenerate-templates` snapshot diff (TPL-001) — idempotent regen, cut keys absent, enum hints inline.
  - `create delta` smoke (deferred CREATE-001 fixture lands here; full assertion in P02).
- **Tooling/commands**:
  - `just test` — unit + snapshot suites.
  - `uv run spec-driver validate workspace --kind delta` — tolerant baseline.
  - `uvx import-linter lint` — contract green.
- **Evidence to capture**:
  - Snapshot of regenerated `supekku/templates/delta.md`.
  - Test run log for new suites.
  - Workspace validate output (0 errors).

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `MetadataValidator` strict-mode + `FieldMetadata.aliases` + `tolerated_aliases` machinery from DE-137 are operational (AUD-026 evidence).
  - `BlockMetadata` registration plumbing (used by `delta.relationships@v1`) is intact and reusable.
  - In-repo corpus tolerates the loader refactor because FM-fallback is preserved.
- **STOP** when:
  - Loader refactor breaks existing delta loading (any in-repo delta fails `validate workspace --kind delta` tolerant) — likely indicates fallback path bug; halt and run `/consult`.
  - Schema registration interacts with strict validator in a way that fires on tolerant mode (DEC-138-10 invariant violation) — halt and run `/consult`.
  - `admin regenerate-templates` produces non-idempotent output (TPL-001 fails second run) — likely a template metadata regression; halt.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Declare `DELTA_CONTEXT_INPUTS_METADATA` + tests (CTX-001, CTX-002) | [P] | Block schema + aliases + tolerated_alias; landed `blocks/delta_metadata.py` |
| [x] | 1.2 | Declare `DELTA_RISK_REGISTER_METADATA` + tests (RISK-001) | [P] | Block schema + `description→title` alias + status default `open` |
| [x] | 1.3 | Extract/render helpers in `blocks/delta.py` (mirror relationships pattern) | [P] | Added `DeltaContextInputsBlock`/`DeltaRiskRegisterBlock` dataclasses, extract/render, schema-registry registration; `ToleratedAlias` exported from `blocks.metadata.__init__` |
| [x] | 1.4 | `_derive_applies_to` + `_derive_revision_link_relations` in `artifacts.py`; delete merge region | [ ] | Lines 111-149 + 151-154 replaced; loader unconditionally tolerant per DEC-138-10 |
| [x] | 1.5 | VTs: DERIVE-001, COLLAB-001, RELLINK-001 against `_derive_applies_to` / `_derive_revision_link_relations` | [ ] | 13 VTs across `artifacts_test.py` |
| [x] | 1.6 | Malformed-block VT (MALFORMED-001) | [ ] | 6 VTs covering malformed YAML / non-mapping / `entries: null` vs `[]` / first-match-wins. Duplicate-strict-error subcase deferred to P04 (validate-file layer — DEC-138-10) |
| [x] | 1.7 | Remove four FM field declarations in `core/frontmatter_metadata/delta.py` | [ ] | applies_to/context_inputs/risk_register/outcome_summary stripped; example updated; compaction tests adjusted (FM keys pass through unchanged until P03 sweep) |
| [x] | 1.8 | Update `delta_creation.py` to emit blocks (empty + populated for relationships) and stop writing FM cut keys | [ ] | Renders empty CTX + RISK blocks; populated CTX when caller provides entries; FM cut keys removed |
| [x] | 1.9 | Hand-author `supekku/templates/delta.md` body §§1-8 (§7 deleted, §§8-9 → §§7-8) + empty blocks | [ ] | Template carries CTX + RISK block placeholders; §§8-9 renumbered to §§7-8 |
| [x] | 1.10 | `admin regenerate-templates` regen; TPL-001 snapshot assertion (idempotence) | [ ] | Templates already canonical (no drift). VT-DE138-TPL-001 added in `spec_driver/orchestration/templates_test.py` (4 sub-cases: cut keys absent, idempotent, validate-clean, enum hints preserved) |
| [x] | 1.11 | Tolerant-load smoke against in-repo corpus (`validate workspace --kind delta`); FM-fallback verified live | [ ] | `validate workspace --kind delta` exit 0; warnings are pre-existing (audit-gate + DR-030 stub). DE-138 self-load via FM-fallback confirmed |
| [x] | 1.12 | `just check` + `uvx import-linter lint` clean | [ ] | ruff lint + format clean; pytest 5330 pass / 4 skipped; import-linter 3/3 contracts kept; pylint 9.69/10 (no new findings on touched files) |

### Task Details

- **1.1 / 1.2 / 1.3 — Block schemas + helpers**
  - **Design / Approach**: Mirror `delta_relationships` pattern verbatim. Schemas are strict (`MetadataValidator` rejects unknown fields under strict); field aliases per DR-138 §5.1/§5.2; tolerated_alias `unknown` registered for `entries[].type` only.
  - **Files / Components**: `supekku/scripts/lib/blocks/delta_metadata.py`, `supekku/scripts/lib/blocks/delta.py`, sibling tests.
  - **Testing**: CTX-001 (accept canonical + reject unknown strict + alias normalisation + tolerated_alias path); CTX-002 (plain-string normalisation key omission per DR-138 §5.3, F-138-31; literal `unknown` vs truly unrecognised per F-138-32); RISK-001 (accept canonical + reject missing likelihood/impact strict + `description→title` + status default `open`).
  - **Observations**: schema is non-nullable str for `entries[].summary` — emitters MUST omit key, never emit `null`.
- **1.4 — Loader refactor**
  - **Design / Approach**: Two new private helpers (`_derive_applies_to`, `_derive_revision_link_relations`); delete lines 111-149 merge region and 151-154 revision_links projection block, replacing both with helper invocations. No `strict` parameter on either helper (DEC-138-10).
  - **Files / Components**: `supekku/scripts/lib/changes/artifacts.py`.
  - **Testing**: DERIVE-001 unit matrix (block sole-source / FM-fallback / both absent → empty dict / FM is dict-vs-non-dict guard); COLLAB-001 (specs.primary ∪ specs.collaborators union); RELLINK-001 (revision_links projection — `type: introduces|supersedes`, ADR-002 backlinks rule preserved because projection derives from authored block content).
  - **Observations**: `ChangeArtifact.to_dict()` lines 63-64 unchanged — same registry payload.
- **1.6 — Malformed handling**
  - **Design / Approach**: VT-DE138-MALFORMED-001 covers malformed YAML inside fence (strict error / tolerant warn), duplicate strict blocks of same schema (last-wins under tolerant; strict error), `entries: null` vs `[]`, non-mapping block raises. Behaviour is validator-layer per DEC-138-10; loader passes through.
- **1.7 / 1.8 / 1.9 / 1.10 — FM metadata + template + `create delta`**
  - **Design / Approach**: Strip four field declarations from `core/frontmatter_metadata/delta.py`. Template body hand-authored; FM template regenerated. `create delta` now writes empty `context_inputs`/`risk_register` blocks + populated `relationships` block; flag mapping per DR-138 §9.4 (`--spec` → `specs.primary[]`; `--requirement` → `requirements.implements[]` preserving `delta_creation.py:89` semantics).
  - **Files / Components**: `supekku/scripts/lib/core/frontmatter_metadata/delta.py`, `supekku/templates/delta.md`, `supekku/scripts/lib/changes/delta_creation.py`.
  - **Testing**: TPL-001 (regen idempotent; cut keys absent; enum hints inline per DR-136 §5.1 (Y)). Full CREATE-001 lands in P02 once migration step exists to round-trip new deltas through `apply()` for idempotence assertion.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Loader refactor accidentally drops `revision_links` projection (F-138-16 regression) | RELLINK-001 VT covers projection explicitly; helper invoked unconditionally in `load_change_artifact` | open |
| Schema strict-mode fires under tolerant load (DEC-138-10 violation) | Tolerant baseline gate (task 1.11); DERIVE-001 + MALFORMED-001 boundary cases | open |
| Template regen non-idempotent | TPL-001 asserts second-run diff is empty | open |
| Cut FM keys still referenced by other supekku consumers | Grep sweep before 1.7; document any consumer requiring temporary fallback (none expected per DR-138 §4.1) | open |

## 9. Decisions & Outcomes

- **DEC-P01-A** — `ToleratedAlias` was not re-exported from `supekku/scripts/lib/blocks/metadata/__init__.py`. Added the re-export rather than reaching through to `schema.py` from consumer code; keeps the public surface coherent with `BlockMetadata` / `FieldMetadata`.
- **DEC-P01-B** — `create_plan` (in `changes/creation.py`) previously read `applies_to` from delta FM. Switched it to read via `load_change_artifact(delta_file).applies_to`, routing through the single derivation path (DR-138 §6.1). Kept the local-import pattern already used by `delta_creation.py:60` to avoid a `creation.py ↔ artifacts.py` cycle.
- **DEC-P01-C** — Block emitters use `yaml.safe_dump` for populated entries (after normalising keys to canonical order) and a hand-formatted literal for the empty `entries: []` / `risks: []` case. Trades a few lines of code for deterministic key order without piping the entire payload through `format_yaml_list` plumbing.
- **DEC-P01-D** — Updated `artifacts_test::test_structured_delta_updates_applies_and_relations` to expect the unioned `specs.primary ∪ specs.collaborators` (DEC-138-11) rather than primary-only. Refactored the four FM-centric `compaction_test` cases to drop the cut keys from their fixtures and added a "passes through unchanged until P03 sweep" assertion. Same intent for `cli/compact_test::test_compact_removes_empty_defaults`.
- **DEC-P01-E** — Duplicate-block strict-error sub-case of MALFORMED-001 stays deferred to P04 (validate-file/workspace layer per DEC-138-10); P01 covers first-match-wins behaviour at the extract layer only. Phase scope unchanged.

## 10. Findings / Research Notes

- `MetadataValidator.validate(strict=…, accept_tolerated=…)` semantics (validator.py:83-93) match DEC-138-10 cleanly: pass `accept_tolerated=False` for the `--no-tolerated-aliases` gate (P04 wiring). Tolerated entries emit warning at strict / error at no-tolerated; permanent aliases emit warning at strict / are silent at non-strict.
- `FieldMetadata.field_aliases` on object-typed items is honoured by `_validate_object` (validator.py:493). Tests confirm `ref→id`, `note→summary`, `annotation→summary` (CTX) and `description→title` (RISK) all round-trip without warnings under non-strict; warnings only under strict.
- `BlockMetadata.fields["entries"]` declared as `required=True` with `type=array` accepts `[]` cleanly (array validation walks items only when non-empty); `entries: null` fails because YAML resolves it to `None`, which is not a list.
- `admin regenerate-templates` returned "templates already canonical" on first run after the hand-authored template rewrite — confirms `DELTA_FRONTMATTER_METADATA` after task 1.7 + the new hand-authored body produce the canonical projection.
- In-repo workspace baseline (`validate workspace --kind delta` tolerant) returned exit 0 with 8 pre-existing warnings (7× audit-gate-not-found, 1× unresolved DR-030 reference). No new errors introduced.
- `pyproject.toml` ignores `PLC0415` per-file in some places but not in `supekku/scripts/lib/changes/creation.py`; the existing `_render_plan` import in `delta_creation.py` already uses `# noqa: PLC0415`. The new local import in `creation.py` carries `# noqa: PLC0415, I001` because ruff's `I001` flags the local-block-import shape.

## 11. Wrap-up Checklist

- [x] All exit criteria satisfied (§4)
- [x] VT evidence captured: 5330 pytest pass (up from 4894 baseline = +436 incl. P01 new VTs across delta_metadata_test, artifacts_test, templates_test); ruff + import-linter green
- [x] DR-138 / IP-138 amended if execution surfaced any DR refinement — no DR refinement needed; assumptions in DR-138 §5/§6 held exactly
- [x] Hand-off note to P02 — see notes.md "2026-05-20 — P01 close" entry for migration-package skeleton location confirmation and fixture-corpus scoping
