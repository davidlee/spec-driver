---
id: IP-128-P02
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-02"
name: "Tier 1 — migrate paths, spec_utils, frontmatter_writer, events"
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
phase: IP-128-P02
plan: IP-128
delta: DE-128
objective: >-
  Migrate 4 tier-1 modules, update their internal imports to relative,
  then update domain/relations/ to import from spec_driver.core.
entrance_criteria:
  - Phase 1 complete (tier 0 landed)
exit_criteria:
  - paths, spec_utils, frontmatter_writer, events in spec_driver/core/
  - Internal imports use relative paths (e.g. from .repo import find_repo_root)
  - domain/relations/ imports updated to spec_driver.core (legacy-core debt eliminated)
  - All tests pass
  - Both import-linter contracts pass
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
tasks:
  - Copy 4 tier-1 modules to spec_driver/core/
  - Update internal imports to relative
  - Create re-export shims
  - Update domain/relations/ imports to spec_driver.core
  - Verify
risks:
  - paths.py has 40 consumers — shim failure widely visible
  - events.py has lazy imports of repo/paths — must use spec_driver.core paths
```

# Phase 2 — Tier 1: migrate dependent core modules + fix domain imports

## 1. Objective

Move the 4 tier-1 modules, update their internal imports to use relative paths
within `spec_driver.core`, then eliminate the legacy-core import debt in
`spec_driver/domain/relations/`.

## 2. Modules

| Module | Lines | Depends on | Key change |
|--------|-------|-----------|------------|
| `paths.py` | 234 | `repo` | `from .repo import find_repo_root` |
| `spec_utils.py` | 92 | `frontmatter_schema` | `from .frontmatter_schema import ...` |
| `frontmatter_writer.py` | 369 | `spec_utils` | `from .spec_utils import ...` (was absolute) |
| `events.py` | 184 | `repo`, `paths` (lazy) | Lazy imports update to `spec_driver.core.*` |

## 3. Domain import debt cleanup

After tier 1 lands, update:

| File | Old | New |
|------|-----|-----|
| `domain/relations/manager.py:8` | `supekku.scripts.lib.core.frontmatter_schema` | `spec_driver.core.frontmatter_schema` |
| `domain/relations/manager.py:9` | `supekku.scripts.lib.core.spec_utils` | `spec_driver.core.spec_utils` |
| `domain/relations/graph.py:19` | `supekku.scripts.lib.core.artifact_ids` | `spec_driver.core.artifact_ids` |

## 4. Exit Criteria

- [ ] 4 tier-1 modules in `spec_driver/core/` with relative internal imports
- [ ] Re-export shims at legacy locations
- [ ] Domain/relations imports updated to `spec_driver.core`
- [ ] No `supekku.scripts.lib.core` imports remain in `spec_driver/domain/`
- [ ] All tests pass
- [ ] Both contracts pass
