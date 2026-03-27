---
id: IP-128-P03
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-03"
name: "Tier 2 — migrate config and templates"
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
phase: IP-128-P03
plan: IP-128
delta: DE-128
objective: >-
  Migrate config.py and templates.py to spec_driver/core/, update internal
  imports to relative.
entrance_criteria:
  - Phase 2 complete (tier 0 + 1 landed)
exit_criteria:
  - config and templates in spec_driver/core/
  - Internal imports use relative paths
  - All tests pass
  - Both import-linter contracts pass
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
tasks:
  - Copy config.py and templates.py to spec_driver/core/
  - Update internal imports to relative
  - Create re-export shims
  - Verify
risks:
  - templates.py depends on jinja2
```

# Phase 3 — Tier 2: config and templates

## 1. Modules

| Module | Lines | Depends on | Notes |
|--------|-------|-----------|-------|
| `config.py` | 432 | `paths` | `from .paths import SPEC_DRIVER_DIR` |
| `templates.py` | 160 | `paths`, jinja2 | `from .paths import get_templates_dir` |

## 2. Exit Criteria

- [ ] Both modules in `spec_driver/core/` with relative imports
- [ ] Re-export shims at legacy locations
- [ ] All tests pass
- [ ] Both contracts pass
