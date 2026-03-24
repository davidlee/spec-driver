# Notes for DE-127

## 2026-03-24 — Phase 1 execution

- Moved `artifact_view.py` (456 lines) and `enums.py` (111 lines) from
  `supekku/scripts/lib/core/` to `spec_driver/orchestration/`.
- Both moved as verbatim copies — no code changes needed.
- `artifact_view.py`'s 10 registry imports were already lazy (inside factory
  functions), so no import-time coupling. `enums.py`'s 11 lifecycle imports
  are leaf constants (correct dependency direction).
- Re-export shims created at both legacy locations. `artifact_view` shim
  includes private names (`_REGISTRY_FACTORIES`, `_detect_bundle_dir`, etc.)
  because the test file imports them directly.
- `core/` now has zero cross-area imports — verified by audit script.
- 4656 tests passed, 2 import-linter contracts kept, ruff clean.

### Commits

- `9f656be9` — reclassify both modules + shims

All `.spec-driver` changes committed promptly alongside code per doctrine.

## 2026-03-24 — Post-implementation audit of remaining core/ modules

Audited all 22 remaining modules. None are misclassified — all have zero
cross-area imports and are genuinely foundational. The classification table in
DR-127 §3.1 is confirmed correct.

### Natural clusters for future migration to `spec_driver.core`

| Cluster | Modules | Lines | Migration complexity |
|---------|---------|-------|---------------------|
| Pure leaf utilities | `strings`, `filters`, `relation_types`, `artifact_ids`, `version`, `cli_utils` | 356 | Trivial — zero internal deps |
| Frontmatter I/O | `frontmatter_schema`, `spec_utils`, `frontmatter_writer` | 674 | Medium — tightly coupled chain; `frontmatter_schema` unblocks DE-125 legacy-core imports in `domain/relations/manager.py` |
| Workspace infra | `repo`, `paths`, `config` | 698 | High — 68 combined consumer sites; `paths.py` alone has 40 |
| Toolchain | `git`, `go_utils`, `npm_utils` | 448 | Low — few consumers |
| Agent/template | `templates`, `agent_docs`, `preboot` | 397 | Medium — `templates.py` uses jinja2 |
| Events/sync | `events`, `sync_preferences` | 248 | Medium — `events.py` has module-level state, 11 consumers |
| Editor | `editor` | ~50 | Trivial |

### Recommended migration order for follow-on delta

1. Pure leaf utilities (zero deps, cheapest)
2. Frontmatter cluster (unblocks `domain/relations/` legacy-core imports)
3. Workspace infra (highest consumer count, do last)

### Follow-up

- DE-127 closes as a successful audit + reclassification.
- Next delta: migrate genuine core modules to `spec_driver.core`, starting
  with leaf utilities and the frontmatter cluster.
