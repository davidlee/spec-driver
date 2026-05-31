---
id: IP-128-P01
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-01"
name: "Tier 0 — migrate leaf core modules"
created: "2026-03-24"
updated: "2026-05-31"
status: draft
kind: phase
plan: IP-128
delta: DE-128
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-128-P01
plan: IP-128
delta: DE-128
objective: >-
  Migrate the 16 tier-0 core modules (zero internal core deps) to
  spec_driver/core/, moving each module's test with it and leaving a re-export
  shim at the legacy module path. `slugify` folds into existing string_utils.py.
entrance_criteria:
  - DR-128 re-validated (2026-05-31); inventory + tiers current
  - spec_driver/core/ already holds file_ops, string_utils, yaml_emit
exit_criteria:
  - 15 new tier-0 modules live in spec_driver/core/ (strings merged into string_utils)
  - each migrated module's *_test.py moved to spec_driver/core/, legacy test deleted
  - re-export shim at each legacy module path (public names only)
  - uvx import-linter lint passes (both contracts)
  - uv run pytest supekku spec_driver -x passes
  - uv run ruff check clean
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
  evidence:
    - import-linter output (clean)
    - pytest summary
tasks:
  - Migrate 12 verbatim tier-0 modules (+ tests) to spec_driver/core/
  - Migrate dates, ids, io (new leaves) (+ tests)
  - Fold slugify from strings.py into spec_driver/core/string_utils.py
  - Create re-export shims at all legacy module paths
  - Verify (lint, tests, contracts)
risks:
  - Shim must export every public name the (legacy + migrated) tests import
  - strings.py shim must still export slugify from string_utils
```

# Phase 1 — Tier 0: migrate leaf core modules

## 1. Objective

Move the 16 zero-dependency core modules to `spec_driver/core/`. True leaves —
no internal core deps — so they migrate in one batch. Each module's `*_test.py`
moves with it (POL-003); the legacy module path becomes a re-export shim.

## 2. Modules (16)

| Module | Lines | Third-party | Target | Key export |
|--------|-------|-------------|--------|------------|
| `repo.py` | 32 | — | new file | `find_repo_root()` |
| `strings.py` | 39 | — | **merge → `string_utils.py`** | `slugify()` |
| `dates.py` | 38 | — | new file | `parse_date` |
| `ids.py` | 34 | — | new file | id helpers |
| `io.py` | 50 | — | new file | I/O helpers |
| `filters.py` | 40 | — | new file | `parse_multi_value_filter()` |
| `relation_types.py` | 40 | — | new file | `RELATION_TYPES`, `REFERENCE_SOURCES` |
| `artifact_ids.py` | 140 | — | new file | `normalize_artifact_id()` (unblocks domain graph) |
| `version.py` | 19 | — | new file | version constant |
| `cli_utils.py` | 78 | yaml | new file | CLI argument helpers |
| `editor.py` | 122 | — | new file | editor subprocess wrapper |
| `git.py` | 145 | — | new file | git operations |
| `go_utils.py` | 116 | — | new file | go toolchain |
| `npm_utils.py` | 187 | — | new file | npm toolchain |
| `pylint_report.py` | 157 | — | new file | lint reporting |
| `frontmatter_schema.py` | 213 | pydantic | new file | `Relation`, `FrontmatterValidationResult` (unblocks domain manager) |

## 3. Procedure (per module)

Standard case (15 modules):
1. Copy `supekku/scripts/lib/core/<m>.py` → `spec_driver/core/<m>.py` (verbatim —
   no internal core deps to rewrite).
2. Move `supekku/scripts/lib/core/<m>_test.py` → `spec_driver/core/<m>_test.py`;
   repoint its imports to `spec_driver.core.<m>`; delete the legacy test.
3. Replace legacy `supekku/scripts/lib/core/<m>.py` with a re-export shim
   (`from spec_driver.core.<m> import …` + matching `__all__`). Mirror the
   proven `supekku/scripts/lib/file_ops.py` shim shape.
4. Shim must export **every** public name imported anywhere (grep
   `core.<m> import` and `from .<m> import`).

`strings.py` special case:
- Move `slugify` into existing `spec_driver/core/string_utils.py` (which already
  holds `closest_match`); add its test cases to `string_utils_test.py`.
- Legacy `strings.py` becomes a shim re-exporting `slugify` from
  `spec_driver.core.string_utils`.

## 4. Verification

- `uvx import-linter lint` — both contracts clean.
- `uv run pytest supekku spec_driver -x` — full pass.
- `uv run ruff check` — clean.

## 5. Exit Criteria

- [ ] 15 new tier-0 modules in `spec_driver/core/`; `slugify` merged into `string_utils`
- [ ] each migrated test moved to `spec_driver/core/`, legacy test deleted
- [ ] re-export shim at every legacy module path
- [ ] `import-linter` both contracts pass
- [ ] full pytest passes
- [ ] ruff clean
