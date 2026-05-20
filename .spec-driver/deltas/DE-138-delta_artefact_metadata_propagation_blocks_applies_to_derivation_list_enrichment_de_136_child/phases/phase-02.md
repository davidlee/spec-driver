---
id: IP-138-P02
slug: "138-delta_artefact_metadata_propagation_blocks_applies_to_derivation_list_enrichment_de_136_child-phase-02"
name: IP-138 Phase 02
created: "2026-05-20"
updated: "2026-05-20"
status: completed
kind: phase
plan: IP-138
delta: DE-138
---

# Phase 02 — Migration step (code only, no sweep)

## 1. Objective

Land the `spec_driver/migrations/v0_10_0_001_delta_blocks/` migration package — `DeltaBlocksStep(BaseMigrationStep)`, frozen-local block emitters, idempotence short-circuit, FM↔block reconciliation, drift logging, and partial-shape handling per DR-138 §7. No in-repo corpus mutation in this phase: `applies_to`/`preview`/`apply` are exercised exclusively against the in-package fixture corpus. `admin migrate delta --check` and `--dry-run` produce a sane preview against the live workspace as a smoke gate but write nothing.

Phase deliverable is a workspace where:
- The migration package is discoverable by `_folder.parse_migration_folder` and exported `STEP` adheres to the `MigrationStep` Protocol (frozen-forever per DEC-137-26).
- The `Migrations isolation` import-linter contract still holds (no `supekku.*` / no `spec_driver.{core,models,domain,orchestration,presentation}` imports anywhere under the new package).
- VTs for migration mechanics, FM↔block reconciliation, relationships-block synthesis, body reshape (§7 Risks deletion + renumber + `## Outcome` insertion), and `create delta` round-trip are green.
- `admin migrate delta --check` / `--dry-run` against the in-repo workspace previews drift cleanly without mutating any file.

## 2. Links & References

- **Delta**: DE-138.
- **Design Revision Sections**:
  - DR-138 §5.3 (migration normalisation rules — context_inputs + risk_register).
  - DR-138 §6.2 (transition-window semantics) + §6.3 (self-bootstrap timing: P03 sweeps DE-138 itself; P02 stops at code).
  - DR-138 §7 (migration step — module layout §7.1, step class §7.2, `apply()` 11-step mechanics §7.3, idempotence + partial-shape §7.4, drift handling §7.5, POL-003 boundary §7.6, frozen-local emitters §7.7, sweep command surface §7.8).
  - DR-138 §9.4 (`create delta` block emission).
  - DR-138 §10.1 VT rows: MIG-001, MIG-002, MIG-003, RELSYNTH-001, BODY-001, CREATE-001.
  - DR-138 DEC-138-03 (folder naming + sibling precedent), DEC-138-05 (drift logging vs DL- promotion), DEC-138-07 (body §7 → drift log → VA-reconcile), DEC-138-11 (FM↔block specs reconciliation), DEC-138-12 (frozen-local emitters + byte-equality VT).
  - DR-137 §5.6 (admin migrate orchestrator surface DE-138 consumes).
- **Specs / PRODs**: PROD-004.FR-007 (first compaction-infra exercise — VT fixture corpus + idempotence per DEC-138-06).
- **Support Docs**:
  - `spec_driver/migrations/_protocol.py` (frozen `MigrationStep` / `BaseMigrationStep` / `StepPreview` / `StepResult`).
  - `spec_driver/migrations/_helpers.py` (frozen `split_frontmatter` / `atomic_write` / `replace_in_frontmatter_block`).
  - `spec_driver/migrations/_folder.py` (folder-name parser; pattern `v<MAJOR>_<MINOR>_<PATCH>_<NNN>_<slug>`).
  - `pyproject.toml` import-linter contract `Migrations isolation` (forbids `supekku` + all of `spec_driver.{core,models,domain,orchestration,presentation}`).

## 3. Entrance Criteria

- [x] IP-138-P01 closed (schemas + load-time synthesis landed; FM-fallback intact).
- [x] `just check` + `uvx import-linter lint` green on P01 head (baseline preserved).
- [x] DR-138 §7 stable (no pending adversarial finding that would shift step mechanics).
- [x] DE-138 status: `in-progress` (already set at P01 entrance).

## 4. Exit Criteria / Done When

- [x] `spec_driver/migrations/v0_10_0_001_delta_blocks/` package exists with `__init__.py` + `_emitters.py` + `migration.py` (`DeltaBlocksStep(BaseMigrationStep)`). `step = DeltaBlocksStep()` defined at module level in `migration.py` because the orchestrator's loader does `getattr(module, "step", ...)` on the file directly (DR-138 §7.1 implicitly assumed package init; corrected during execution).
- [x] `parse_migration_folder("v0_10_0_001_delta_blocks")` returns a `ParsedFolder` with `version=0.10.0`, `ordinal=1`, `slug="delta_blocks"`.
- [x] `DeltaBlocksStep` API: `applies_to_kind = "delta"`; `description` set; `applies_to(path)` uses head-of-file regex against DR-138 §7.2 cut set `{applies_to, context_inputs, risk_register, outcome_summary, lifecycle, aliases, auditers, source}` (F-138-17 + F-138-28); `preview(path)` + `apply(path)` implemented per §7.3.
- [x] `apply()` performs all 11 steps from §7.3 verbatim — split/cut universals/synthesise relationships block when FM `applies_to` non-empty + block absent (§7.3 step 3, F-138-27)/synthesise context_inputs block/synthesise risk_register block/move outcome_summary → body `## Outcome`/reconcile FM↔block specs+requirements (DEC-138-11)/remove FM keys/handle body §7 Risks (full content captured in drift)/renumber §§8-9 → §§7-8 (top-level only)/atomic-write via `_helpers.atomic_write`.
- [x] Frozen-local emitters present in package (`render_context_inputs_block`, `render_risk_register_block`, `render_relationships_block` in `_emitters.py`); no `supekku.*` import inside the package.
- [x] `uvx import-linter lint` clean (`Migrations isolation` contract holds).
- [x] Idempotence: re-running `apply()` against an already-migrated file is a no-op (returns `StepResult(touched=[], skipped=[path])`). Parametrised VT covers all 7 fixture shapes.
- [x] Partial-shape table (§7.4) handled — block matches FM (cut silently) / block disagrees with FM (keep block + `fm_block_disagreement` drift) / block absent + FM present (synthesise) / block absent + FM absent (no-op).
- [x] Drift log entries emitted per §7.5 with stable `kind:` field (`relationships_block_synthesised_from_fm`, `fm_specs_unmatched`, `fm_requirements_unmatched`, `fm_block_disagreement`, `body_risk_narrative`, `body_renumber`, `context_input_unmapped_type`, `risk_missing_likelihood`, `risk_missing_impact`, `outcome_overwrite_conflict`).
- [x] VTs green: VT-DE138-MIG-001 (apply over 7 fixture deltas + idempotence + byte-equality between supekku-side and migration-local emitters per DEC-138-12), VT-DE138-MIG-002 (preview = no writes; touched/skipped/drift lists match), VT-DE138-MIG-003 (FM↔block specs + requirements reconciliation drift entries), VT-DE138-RELSYNTH-001 (relationships-block synthesis), VT-DE138-BODY-001 (single-line / folded / literal scalar outcome insertion + §7 deletion + renumber), VT-DE138-CREATE-001 (`create delta` writes blocks + no FM cut keys, round-trip through `apply()` is a no-op).
- [x] `admin migrate delta --check` + `--dry-run` against in-repo workspace runs to completion writing **zero files**, surfaces preview drift summary; in-repo deltas still load (no regression vs P01 head).
- [x] `just check` clean.

## 5. Verification

- **Unit suites (per VT, all under `spec_driver/migrations/v0_10_0_001_delta_blocks/`)**:
  - `migration_test.py` — applies_to() regex coverage; preview/apply mechanics across fixture matrix; idempotence; partial-shape table; emitter byte-equality against supekku-side helpers (test-only cross-package import is *test* code, not the migration step itself — covered by import-linter `ignore_imports` patterns where the contract permits).
  - Fixture corpus: 5-7 fixture deltas committed under `tests/fixtures/migrations/v0_10_0_001/` (or sibling test-data dir; placement decided at task 2.2). Each fixture matches one DR-138 §7 shape:
    1. Clean target shape (idempotence — apply is no-op).
    2. FM applies_to + relationships block both present + agreement (silent FM cut).
    3. FM applies_to + relationships block disagreement (drop FM + `fm_block_disagreement` drift).
    4. FM applies_to non-empty + relationships block absent (synthesise per §7.3 step 3).
    5. FM context_inputs heterogeneous (plain string + ref→id + note→summary + unknown type).
    6. FM risk_register with `description` alias + missing likelihood/impact.
    7. Body §7 Risks present (multi-paragraph) + outcome_summary as folded scalar + §§8-9 renumber.
- **Integration**:
  - `admin migrate delta --check` smoke against in-repo workspace (writes nothing; surfaces drift summary).
  - `admin migrate delta --dry-run` smoke; assert byte-zero mutation.
  - `create delta` end-to-end via Typer test harness (CREATE-001 fully lands here; P01 deferred).
- **Tooling/commands**:
  - `just test`.
  - `uvx import-linter lint` (mandatory exit gate — `Migrations isolation` contract).
  - `uv run spec-driver admin migrate delta --check`.
  - `uv run spec-driver admin migrate delta --dry-run`.
- **Evidence to capture**:
  - Test run log for `migration_test.py`.
  - `--check` + `--dry-run` output against in-repo corpus (no diffs written to tracked files).
  - Import-linter contract output (green).
  - Verification coverage block entries flipped `planned` → `verified` for MIG-001/002/003, RELSYNTH-001, BODY-001, CREATE-001.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - P01 schemas + load-time synthesis behaviour stable; `_derive_applies_to` semantics from §6.1 are the post-sweep contract the migration step must emit blocks compatible with.
  - `_helpers.split_frontmatter` + `atomic_write` cover the bytes-level IO surface; no need to extend `_helpers`.
  - `_protocol.py` Protocol surface is sufficient; `applies_to_kind="delta"` is honoured by the orchestrator kind-filter.
  - In-repo corpus tolerates `--check` / `--dry-run` with zero mutation (orchestrator respects no-write flags).
- **STOP** when:
  - Import-linter contract regresses (any new `supekku.*` import inside the migration package) — `/consult` before relaxing the contract; remediation is to move logic, not loosen rules.
  - Frozen-local emitters drift from supekku-side helpers (byte-equality VT fails) — `/consult`; do **not** patch the migration emitter silently. The drift may be a supekku-side render bug; resolution likely involves updating both, but only the supekku side counts as "fix", the migration emitter follows in a new ordinal step `v0_10_0_002_*` per DR-137 DEC-137-26.
  - `apply()` produces non-idempotent output on second run — halt; idempotence is foundational for orchestrator semantics.
  - `--check` / `--dry-run` mutates any file under `.spec-driver/` — orchestrator/flag bug; halt.
  - Step mechanics surface a DR-138 §7 hole that cannot be resolved by re-reading the DR (i.e. a real design gap) — `/draft-design-revision` to refine DR-138 §7 before continuing.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Scaffold package: `v0_10_0_001_delta_blocks/{__init__.py, migration.py}`; module-level `step = DeltaBlocksStep()` per orchestrator loader contract | [ ] | Bedrock; orchestrator expects `module.step`, NOT `__init__.step` (DR-138 §7.1 corrected during exec) |
| [x] | 2.2 | Fixture corpus inline in `migration_test.py` as constant strings (7 shapes per §5) | [P] | Inline fixtures keep the VT body self-contained |
| [x] | 2.3 | Frozen-local emitters in `_emitters.py` (`render_relationships_block`, `render_context_inputs_block`, `render_risk_register_block`); byte-equality VT lives in `supekku/scripts/lib/blocks/migration_byte_equality_test.py` (supekku-side; contract is one-way) | [P] | DEC-138-12; 6 byte-equality VTs across empty + populated for each emitter |
| [x] | 2.4 | `applies_to(file_path)` head-of-file regex per §7.2 (cut set: 4 delta-specific + `lifecycle/aliases/auditers/source`); 11 unit VTs cover each cut key + clean-target skip + `owners/summary` residue not triggering | [P] | F-138-17 + F-138-28 |
| [x] | 2.5 | Normalisation helpers: `_normalise_context_input` (plain str → tolerated `unknown` with `id`; `ref→id`, `note/annotation→summary` with key omission on empty; type alias map; tolerated `unknown`); `_normalise_risk` (`description→title`, status default `open`, drift on missing likelihood/impact) | [P] | Pure functions; drift entries flow up to `apply()` |
| [x] | 2.6 | `apply(file_path)` 11-step mechanics per §7.3 + idempotence short-circuit + partial-shape table (§7.4) + drift entry emission (§7.5) | [ ] | Main impl unit; broken into `_transform` + per-step private helpers |
| [x] | 2.7 | `preview(file_path)` — no writes; shares mechanics with `apply` via the same `_transform` function | [ ] | Returns `StepPreview(touched, skipped, drift)` |
| [x] | 2.8 | `create delta` finalisation: dropped hardcoded `aliases: []` from `delta_creation.py` FM dict; VT-DE138-CREATE-001 asserts round-trip is `applies_to=False` + `apply` no-op | [ ] | One-line FM dict edit unblocked round-trip |
| [x] | 2.9 | `admin migrate delta --check` + `--dry-run` smoke against in-repo workspace; zero `.spec-driver/deltas/**` mutation observed; 141 deltas preview cleanly | [ ] | `--dry-run` summary line shows misleading "would touch 0" (orchestrator UI bug — sums empty results list under dry_run); zero-mutation property holds; sibling issue filed |
| [x] | 2.10 | `uvx import-linter lint` final pass (3/3 contracts kept including Migrations isolation); `just check` proxy (ruff + format + full pytest) green: 5367 passed, 4 skipped (up from 5330 at P01 close — +37 tests landed) | [ ] | Phase exit gates clean |

### Task Details

- **2.1 — Package scaffold**
  - **Design**: Folder name `v0_10_0_001_delta_blocks` matches `MIGRATION_FOLDER_PATTERN`. `__init__.py` imports `STEP = DeltaBlocksStep()` so orchestrator discovery via `_folder.parse_migration_folder` + module attribute resolution works. Inherit `BaseMigrationStep`; override `applies_to_kind`, `description`, `applies_to`, `preview`, `apply`.
  - **Files**: `spec_driver/migrations/v0_10_0_001_delta_blocks/__init__.py`, `migration.py`.
  - **Testing**: smoke that `parse_migration_folder("v0_10_0_001_delta_blocks")` succeeds; `isinstance(STEP, MigrationStep)` runtime-check (Protocol is `@runtime_checkable`).
- **2.2 — Fixture corpus**
  - **Design**: One markdown file per §5 shape under a `_fixtures/` tree. Each fixture is a complete delta artefact (frontmatter + body); the test loads, applies, and snapshots the output. Snapshot-driven coverage keeps the assertion surface readable.
  - **Files**: 7 fixture deltas + 7 expected-output snapshots.
  - **Testing**: VT-DE138-MIG-001 / MIG-002 / MIG-003 / RELSYNTH-001 / BODY-001 consume this corpus.
- **2.3 — Frozen-local emitters**
  - **Design**: Each emitter takes a normalised payload + returns the full ```yaml supekku:delta.<schema>@v1 ... ``` fenced block string. Use `yaml.safe_dump(sort_keys=False, default_flow_style=False)` to keep output deterministic + comment-free (migration emitter does not preserve YAML comments — see §7.3 step 11 note).
  - **Files**: `migration.py` (or sibling `_emitters.py` if module grows past ~300 lines).
  - **Testing**: byte-equality VT — emit via local helper + via `supekku/scripts/lib/blocks/delta.py` render helper; assert equal. Test-only cross-package import — confirm import-linter `Migrations isolation` permits *test* code outside the contract scope (contracts target source paths under `spec_driver.migrations`, not test paths).
- **2.4 — `applies_to(file_path)` regex**
  - **Design**: Single-pass compiled regex against `text[:4096]`. Pattern: `r"^(applies_to|context_inputs|risk_register|outcome_summary|lifecycle|aliases|auditers|source):"` with `MULTILINE`. Returns `True` if any match → file is in scope. Idempotence short-circuit (already-migrated files match nothing → return `False` → orchestrator skips).
- **2.5 — Normalisation helpers**
  - **Design**: Two pure functions: `_normalise_context_input(entry: str | dict) -> tuple[dict, list[drift]]` + `_normalise_risk(entry: dict) -> tuple[dict, list[drift]]`. Drift entries are dicts with `kind`, `file`, `detail`. Aggregated by `apply()` into the `StepResult.drift_entries` list (the protocol field carries paths; drift bodies are written to the migration log file by the orchestrator — DE-138 step emits paths + log lines, orchestrator owns the log surface per DR-137 §5.6).
- **2.6 — `apply()` mechanics**
  - **Design**: Linear 11-step transform per DR-138 §7.3. Mutate the in-memory `frontmatter` dict + `body` string; serialise via `yaml.safe_dump(sort_keys=False)`; reassemble; write via `_helpers.atomic_write`. Each step is a private helper to keep `apply()` itself a thin orchestrator (≤30 lines). Idempotence short-circuit: if `applies_to(path)` returns `False`, the apply function short-circuits before any read (orchestrator already filters but defensive guard is cheap and tested).
  - **Concurrent-reader assumption (F-138-A)**: documented; single-process sweep guaranteed by DEC-137-22 lockfile.
- **2.7 — `preview()`**
  - **Design**: Identical mechanics to apply but routes the final write to an in-memory diff instead of `atomic_write`. Extract the read-transform pipeline into `_transform(file_path) -> tuple[str, list[drift]]`; `apply` writes, `preview` returns `StepPreview` populated from the transform diff.
- **2.8 — `create delta` finalisation**
  - **Design**: Ensures `delta_creation.py` round-trip is post-migration shape. CREATE-001 fixture: `spec-driver create delta ...` → load file → run migration step `apply()` → assert `StepResult(touched=[])` (no-op, file already matches target shape).
  - **Files**: `supekku/scripts/lib/changes/delta_creation.py` (revise if P01 left FM emission anywhere), corresponding test.
- **2.9 — Smoke against in-repo corpus**
  - **Design**: invoke `admin migrate delta --check` + `--dry-run`; assert zero file mtimes change under `.spec-driver/deltas/**`. Captures preview drift summary for archive purposes (paste into phase notes).
- **2.10 — Lint + test gate**
  - **Design**: `just check` (ruff + format + pytest); `uvx import-linter lint` (3/3 contracts hold).

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| `Migrations isolation` import-linter violation slips in via transitive import (e.g. `yaml` shim re-exporting from `supekku.*`) | Final `uvx import-linter lint` gate; per-file `from __future__ import annotations` + explicit stdlib-only imports at module head | open |
| Frozen-local emitter drifts from supekku-side render helper | Byte-equality VT in 2.3; CI re-runs on every change to either side | open |
| `apply()` non-idempotent — second run mutates a clean file | Idempotence VT in fixture matrix shape 1 (clean target); `applies_to(path)` short-circuit on cut-key absence | open |
| `--check`/`--dry-run` mutates files (orchestrator/flag bug) | Smoke gate 2.9 asserts zero mtime change | open |
| Body renumber miscounts top-level headings under sub-headings carrying numeric prefixes | F-138-D resolution: top-level `## N.` only; sub-heading `### N.M` left as-is; fixture 7 covers both | open |
| `outcome_summary` literal scalar inserts whitespace incorrectly into body | VT-DE138-BODY-001 fixture covers literal scalar (`|`) verbatim insertion | open |
| Drift kind names diverge from §7.5 listing | Drift kinds enumerated in module-level constants; VT-DE138-MIG-003 asserts exact kind strings | open |
| Migration step accidentally imports `supekku.scripts.lib.core.spec_utils` (`load_markdown_file`) from old habit | Code review against §7.3 / §7.6; import-linter is the backstop | open |

## 9. Decisions & Outcomes

- _(populate as phase executes)_

## 10. Findings / Research Notes

- _(populate as phase executes — fixture-corpus design notes, emitter byte-equality details, etc.)_

## 11. Wrap-up Checklist

- [x] All §4 exit criteria satisfied.
- [x] VT evidence captured — test run logs (5367 passed); `--check`/`--dry-run` smoke output recorded in notes (zero-mutation across 141 deltas).
- [x] IP-138 verification.coverage entries flipped `planned` → `verified` for MIG-001/002/003, RELSYNTH-001, BODY-001, CREATE-001.
- [x] DR-138 / IP-138 amended where execution surfaced refinement — `step` lives in `migration.py` not `__init__.py` per orchestrator loader contract; orchestrator defect fixed in `migrate.py` (sys.modules registration); P02 task table corrected with exec-discovered placements.
- [x] Hand-off note to P03 — pre-sweep checkpoint tag `de-138-pre-sweep` required before sweep; preview ran cleanly across in-repo corpus, drift kinds enumerated above; fixture-shape lessons (idempotence + collaborators union + relationships-synth) feed into DE-136 IP §5 sibling precedent (DEC-138-09).
