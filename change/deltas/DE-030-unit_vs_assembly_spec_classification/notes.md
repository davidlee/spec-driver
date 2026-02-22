# DE-030 Implementation Notes (Handoff)

This delta operationalizes ADR-003 via **non-breaking taxonomy metadata** and **navigation tooling**.

## Locked decisions
- Reserved tech spec taxonomy values:
  - `category: unit` (1:1 with a language unit)
  - `category: assembly` (cross-unit / subsystem / integration)
- Mapping guidance: `unit` → `c4_level: code` (warn if inconsistent; do not block).
- **Warn-only** validation in v1.
- No filesystem/prefix migration in this delta (no `UNIT-*` / `ASM-*` roots).
- `list specs` defaults to `--category assembly,unknown` (hides unit tech specs). `--category all` to show everything.
- `--category` / `--c4-level` filters apply to tech specs only; PROD specs always pass through.
- `create spec` defaults to `category: assembly` (DEC-030-04).

## Progress

### Phase 1 — COMPLETE ✓
All tasks done, tests passing, lint clean.

- **1.1** `Spec` model: added `category` and `c4_level` properties + `to_dict` inclusion (`specs/models.py`)
- **1.2** `build_frontmatter`: accepts `category`/`c4_level` params; defaults tech specs to `category: assembly` (`specs/creation.py`)
- **1.3** Sync stub creation: sets `category: unit`, `c4_level: code` (`sync_specs.py`)
- **1.4** Frontmatter schema: updated `category` description with reserved values (`core/frontmatter_metadata/spec.py`)
- **1.5** CLI: added `--category` (default `assembly,unknown`) and `--c4-level` (default `all`) to `list specs` (`cli/list.py`)
- **1.6** Tests: 24 new tests across `models_test.py`, `creation_test.py`, `sync_specs_test.py`, `list_test.py`

### Phase 2 — COMPLETE ✓

- **2.1** ✓ `SpecIndexBuilder`: added `by-category` symlink views (`specs/index.py`)
- **2.2** ✓ `SpecIndexBuilder`: added `by-c4-level` symlink views (`specs/index.py`)
  - Helper methods `_clean_flat_view_dir` and `_create_flat_view_link` added
  - 3 new tests in `index_test.py`
- **2.3** ✓ `WorkspaceValidator`: added `_validate_spec_taxonomy` method (`validation/validator.py`)
  - Warns on missing `category` or `c4_level` for tech specs (`kind: spec`)
  - Warns on inconsistent combo (`category: unit` + `c4_level` != `code`)
  - Scoped to tech specs only; PROD specs excluded
  - Warn-only: uses `self._warning()`, never `self._error()`
- **2.4** ✓ Tests for VT-030-005 + VT-030-006 (`validation/validator_test.py`)
  - 10 new tests: missing category, missing c4_level, both missing, inconsistent combo,
    consistent unit/code, assembly/component, PROD exclusion, never-errors, regression

### Test counts
- 1693 passed, 3 skipped, 0 failed
- `just lint` clean, pylint: validator.py 9.70/10, validator_test.py 10/10

## Don'ts (scope control)
- Don't tighten the schema to an enum for `category` in v1 (too breaking; existing freeform use may exist).
- Don't introduce a new top-level folder split yet (defer migration until taxonomy proves value).

## ADR-003
Status changed from `draft` → `accepted` at start of implementation.
