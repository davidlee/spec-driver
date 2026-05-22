# Notes for DE-139

## P02 — List enrichment + packages removal (2026-05-22)

### Done

- **Packages removal chain**: Spec.packages property, find_by_package, SpecIndexEntry.packages field, package_dir in index builder, format_package_list, _format_packages, include_packages param, PACKAGES_COLUMN, --packages/--package/--package-path/--for-path CLI flags + all filter logic.
- **Enriched columns**: SPEC_COLUMNS now [ID, Name, Status, Category, C4, Sources]. C4_GLYPHS mapping in column_defs.py. format_c4_glyph + format_sources_cell pure formatters. Tags opt-in via `--tags` flag (DEC-139-09).
- **Spec.sources property** added to model (was missing — only accessed from raw FM in index.py).
- **VT-DE139-LIST-001**: 19 tests (C4 glyphs, sources cell, enriched table, tags opt-in).
- 5066 tests passing, lint clean.

### Surprises / Adaptations

- `--for-path` flag help text confirmed package-only ("Filter specs whose packages include PATH") — safe removal.
- `find_by_package` on registry had no production callers, only tests — clean removal.
- `SpecIndexEntry.packages` field removed; dataclass had it as required positional, so test fixtures needed updating.
- Mock objects in test helpers needed `spec.sources = []` added — Mock auto-creates attrs but iterating a Mock attr raises TypeError.
- Two separate regression test sites in column_defs_test.py asserted old SPEC_COLUMNS labels.
- `replace_all` on `spec.packages = []` → `spec.ext_id = ""` created one duplicate in a mock that already had ext_id. Fixed manually.

### Commit

`87ddd401` — `.spec-driver` artefacts committed with code per doctrine.

### Verification

`just test` (5066 passed) + `just lint` (clean) run after final changes.

### Follow-up

- P03 next: migration step, sweep, template updates.
- `format_spec_list_json` still doesn't emit category/c4_level/sources in JSON output — may want to enrich in P03 or follow-up.

## P03 — Migration + sweep + template (2026-05-22)

### Done

- **v0_10_0_002_spec_blocks migration step**: cuts `packages` from FM (50 specs), handles concerns/hypotheses/decisions→blocks and scope→prose (0 files in practice), defaults missing category/c4_level to `unknown`. 33 VT tests (VT-DE139-MIG-001).
- **v0_10_0_003_prod_blocks migration step**: cuts `hypotheses`/`decisions`/`verification_strategy`/`scope` from PROD FM. PROD-014 `scope` moved to prose body. 18 VT tests (VT-DE139-MIG-002).
- **Template wiring**: spec.md template now has `{{ spec_concerns_block }}`, `{{ spec_hypotheses_block }}`, `{{ spec_decisions_block }}` variables. creation.py renders all 6 blocks. VT-DE139-CREATE-001 + VT-DE139-TPL-001 passing.
- **Dead code cleanup**: removed by-package symlink creation from creation.py (dead after packages cut). Added new block variables to backfill.py.
- **In-tree sweep**: `spec-driver admin migrate spec` applied to 50/53 specs. `spec-driver admin migrate prod` applied to 1/16 prods (PROD-014). Watermark advanced to `v0_10_0_003_prod_blocks`.
- **Post-sweep validation** (VA-DE139-SWEEP-001): zero specs with `packages:`, zero prods with `scope:`, zero files with `concerns:`/`hypotheses:`/`decisions:`/`verification_strategy:` in FM.
- 5549 tests passing, lint clean.

### Surprises / Adaptations

- Pre-existing `_INTENT_HEADING_RE` regex matched only "Intent" not "Intent & Summary" — scope insertion split mid-heading. Fixed by adding `[^\n]*` to match full line.
- `admin migrate --dry-run` displays "would touch 0" due to pre-existing bug: uses empty `results` list instead of `previews`. Not in DE-139 scope.
- `admin migrate --list` shows all steps as "[applied]" due to inverted `_name_is_before_or_at` logic. Pre-existing bug, not in scope.
- Two migration packages needed per DEC-137-16 (one kind per step) despite PROD having only 1 affected file.
- Pre-existing lint in column_defs_test.py (line too long from P02) fixed as cleanup.

### Verification

- `just test` (5549 passed) + `just lint` (clean).
- Post-sweep grep: zero legacy FM keys in tree.
- Migration logs written to `.spec-driver/run/`.

### Follow-up

- `format_spec_list_json` JSON enrichment still deferred.
- Dry-run/list display bugs in migration orchestrator — file as backlog issue.

## P04 — Strict flip + close (2026-05-22)

### Done

- **Spec block validation wiring**: Added `_validate_spec_blocks` to `WorkspaceValidator` (mirrors `_validate_delta_blocks` from DE-138). Validates concerns/hypotheses/decisions blocks against schema under strict mode. Extractors and validators from P01 now consumed at workspace level.
- **Public validators**: Renamed `_SPEC_CONCERNS_VALIDATOR`, `_SPEC_HYPOTHESES_VALIDATOR`, `_SPEC_DECISIONS_VALIDATOR` → public (no underscore) + exported in `__all__`. Matches `DELTA_CONTEXT_INPUTS_VALIDATOR` naming convention.
- **VT-DE139-FLIP-001**: Enforcement test — spec with concerns block missing required `spec` field errors under strict. Follows DE-138 P04 pattern exactly.
- **Workflow.toml flip**: `[validation.strict] spec = true` + `[schema_version] spec = "0.10.0+003"`.
- **Post-flip verification**: spec-kind baseline unchanged (1 pre-existing FR-007 warning). Whole-corpus baseline unchanged (7× audit-gate + 1× DR-030). `complete delta DE-139 --dry-run` passes. `list specs` renders correctly.
- 5580 tests passing, lint clean.

### Surprises / Adaptations

- None. Pattern from DE-138 P04 transferred cleanly.

### Verification

- `just test` (5580 passed) + `just lint` (clean).
- Post-flip `validate workspace --kind spec --strict`: 1 warning (FR-007, pre-existing).
- Post-flip `validate workspace --strict`: 9 issues (all pre-existing, matches DE-138 baseline).

### Follow-up

- Close DE-139 via `spec-driver complete delta DE-139`.
