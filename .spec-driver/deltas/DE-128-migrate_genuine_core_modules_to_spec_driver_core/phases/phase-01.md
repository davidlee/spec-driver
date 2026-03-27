---
id: IP-128-P01
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-01"
name: "Tier 0 — migrate leaf core modules"
created: "2026-03-24"
updated: "2026-03-24"
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
  Migrate all 13 tier-0 core modules (zero internal deps) to spec_driver/core/,
  create re-export shims at legacy locations.
entrance_criteria:
  - DE-127 confirmed all modules are clean
  - DR-128 dependency tiers documented
exit_criteria:
  - All 13 tier-0 modules live in spec_driver/core/
  - Re-export shims at legacy locations for all 13
  - All tests pass
  - Both import-linter contracts pass
  - ruff clean
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
  evidence:
    - import-linter output
tasks:
  - Copy 13 tier-0 modules to spec_driver/core/
  - Create re-export shims at legacy locations
  - Verify
risks:
  - Shim needs to include private names used by tests
```

# Phase 1 — Tier 0: migrate leaf core modules

## 1. Objective

Move all 13 zero-dependency core modules to `spec_driver/core/`. These are true
leaves — no internal core deps, so they can all move in one batch.

## 2. Modules

| Module | Lines | Third-party | Key export |
|--------|-------|-------------|------------|
| `repo.py` | 32 | — | `find_repo_root()` |
| `strings.py` | 39 | — | `slugify()` |
| `filters.py` | 40 | — | `parse_multi_value_filter()` |
| `relation_types.py` | 40 | — | `RELATION_TYPES`, `REFERENCE_SOURCES` |
| `artifact_ids.py` | 140 | — | `normalize_artifact_id()` |
| `version.py` | 19 | — | version constant |
| `cli_utils.py` | 78 | yaml | CLI argument helpers |
| `editor.py` | 122 | — | editor subprocess wrapper |
| `git.py` | 145 | — | git operations |
| `go_utils.py` | 116 | — | go toolchain |
| `npm_utils.py` | 187 | — | npm toolchain |
| `pylint_report.py` | 157 | — | lint reporting |
| `frontmatter_schema.py` | 213 | pydantic | `Relation`, `FrontmatterValidationResult` |

## 3. Procedure (per module)

1. Copy to `spec_driver/core/<module>.py` (verbatim — no internal deps to update).
2. Replace legacy file with re-export shim.
3. Shim must include all names imported by tests (check `*_test.py` imports).

## 4. Verification

- `uvx import-linter lint`
- `uv run pytest supekku spec_driver -x`
- `uv run ruff check`

## 5. Exit Criteria

- [ ] All 13 tier-0 modules in `spec_driver/core/`
- [ ] Re-export shims at legacy locations
- [ ] All tests pass
- [ ] Both contracts pass
- [ ] ruff clean
