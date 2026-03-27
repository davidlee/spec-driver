---
id: IP-128-P04
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-04"
name: "Tier 3 — migrate agent_docs, preboot, sync_preferences"
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
phase: IP-128-P04
plan: IP-128
delta: DE-128
objective: >-
  Migrate final 3 tier-3 modules to spec_driver/core/. After this phase,
  all genuine core modules are migrated and spec_driver.core is complete.
entrance_criteria:
  - Phase 3 complete (tier 0 + 1 + 2 landed)
exit_criteria:
  - agent_docs, preboot, sync_preferences in spec_driver/core/
  - Internal imports use relative paths
  - All tests pass
  - Both import-linter contracts pass
  - No genuine core module remains only in supekku/scripts/lib/core/
  - spec_driver/core/__init__.py updated if needed
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
    - uv run spec-driver validate
  evidence:
    - Final module count in spec_driver/core/
tasks:
  - Copy 3 tier-3 modules to spec_driver/core/
  - Update internal imports to relative
  - Create re-export shims
  - Final verification
risks:
  - agent_docs depends on config + paths + templates (3 tiers deep)
```

# Phase 4 — Tier 3: final modules

## 1. Modules

| Module | Lines | Depends on | Notes |
|--------|-------|-----------|-------|
| `agent_docs.py` | 74 | `config`, `paths`, `templates` | Deepest dependency chain |
| `preboot.py` | 163 | `config`, `paths` | Agent boot helpers |
| `sync_preferences.py` | 64 | `config`, `paths` | Sync preference loading |

## 2. Exit Criteria

- [ ] All 3 modules in `spec_driver/core/` with relative imports
- [ ] Re-export shims at legacy locations
- [ ] All tests pass
- [ ] Both contracts pass
- [ ] Migration complete: 23 modules in `spec_driver/core/`

## 3. Post-migration checklist

- [ ] `spec_driver/core/__init__.py` updated if public API surface changes
- [ ] `spec-driver validate` passes
- [ ] Notes updated with final module count and any surprises
