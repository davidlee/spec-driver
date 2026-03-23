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
