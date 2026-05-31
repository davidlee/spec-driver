---
id: IP-128-P04
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-04"
name: "Tier 3 — migrate agent_docs, preboot, sync_preferences"
created: "2026-03-24"
updated: "2026-05-31"
status: completed
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
  Migrate the final 3 tier-3 modules (+ tests) to spec_driver/core/. All
  already use relative imports — verbatim moves. After this phase, all
  genuine core modules are migrated and spec_driver.core is complete.
entrance_criteria:
  - Phase 3 complete (tier 0 + 1 + 2 landed, config + templates in core)
  - import-linter 3/3 KEPT; core/config.py has zero frontmatter_metadata refs
  - core/spec_utils.py + core/config.py imports no orchestration/domain symbols
exit_criteria:
  - agent_docs, preboot, sync_preferences (+ tests) in spec_driver/core/
  - Re-export shims at legacy locations; legacy tests deleted
  - All tests pass; both import-linter contracts pass; ruff clean
  - No genuine core module remains only in supekku/scripts/lib/core/ (shims aside)
  - 28 core modules in spec_driver/core/ — migration complete
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
  evidence:
    - Final module count in spec_driver/core/
    - grep for supekku.scripts.lib.core (non-shim, non-__init__) in core/
tasks:
  - Migrate agent_docs (verbatim — already relative imports; no test) (task 1) ✅
  - Migrate preboot + preboot_test; repoint test imports + @patch path (task 2) ✅
  - Migrate sync_preferences + sync_preferences_test; repoint test imports (task 3) ✅
  - Create re-export shims for all 3 modules (task 4) ✅
  - Final verification (task 5) ✅
risks:
  - agent_docs depends on config + paths + templates — deepest chain; all already in core
  - preboot_test.py @patch path needs repointing (supekku → spec_driver)
  - sync_preferences depends on tomlkit (third-party, path-independent)
  - preboot_test may have collection issues (nix-env missing click/typer)
assumptions:
  - agent_docs has no test file (confirmed: no agent_docs_test.py anywhere)
  - agent_docs consumers (install.py, cli/sync.py) go through legacy shim
  - preboot consumers (install.py, cli/admin.py) go through legacy shim
  - tomlkit is available in nix env (sync_preferences dependency)
---

# Phase 4 — Tier 3: final modules

## 1. Objective

Move the last 3 tier-3 core modules into `spec_driver.core`. All already use
relative internal imports — **verbatim copies**. This is the final phase:
after completion, all 26 genuine core modules are migrated and the
`spec_driver.core` outer layer contract is truthful.

## 2. Modules

| Module | Lines | Depends on | Third-party | Test | Imports |
|--------|-------|-----------|-------------|------|---------|
| `agent_docs.py` | 74 | `config`, `paths`, `templates` | — | none | `from .config`, `.paths`, `.templates` — already relative |
| `preboot.py` | 163 | `config`, `paths` | — | `preboot_test.py` (276L) | `from .config`, `.paths` — already relative |
| `sync_preferences.py` | 64 | `config`, `paths` | tomlkit | `sync_preferences_test.py` (119L) | `from .config`, `.paths` — already relative |

All three are deepest-tier consumers — they depend on tier-0 + tier-1 + tier-2
modules already migrated in P01-P03. No decoupling work needed.

## 3. Task Breakdown

### Task 1 — Migrate `agent_docs`

1. Copy `supekku/scripts/lib/core/agent_docs.py` → `spec_driver/core/agent_docs.py`.
   Imports already relative: `from .config`, `from .paths`, `from .templates`.
   No changes needed — verbatim copy.
2. No test file exists — confirmed: `agent_docs_test.py` not found anywhere.
3. Create legacy shim `supekku/scripts/lib/core/agent_docs.py`:
   ```python
   """Re-export shim — see spec_driver.core.agent_docs."""
   from spec_driver.core.agent_docs import (
       render_agent_docs,
   )

   __all__ = [
       "render_agent_docs",
   ]
   ```
   (The public export is `render_agent_docs` — confirmed via `importlib`
   inspection and the single consumer `install.py:18`.)

### Task 2 — Migrate `preboot`

4. Copy `supekku/scripts/lib/core/preboot.py` → `spec_driver/core/preboot.py`.
   Imports already relative: `from .config import load_workflow_config`,
   `from .paths import SPEC_DRIVER_DIR`. No changes needed — verbatim copy.

5. Move `supekku/scripts/lib/core/preboot_test.py` → `spec_driver/core/preboot_test.py`.
   Repoint imports:
   - `from supekku.scripts.lib.core.preboot import …` →
     `from spec_driver.core.preboot import …`
   - `_SUBPROCESS_TARGET = "supekku.scripts.lib.core.preboot.subprocess.run"` →
     `_SUBPROCESS_TARGET = "spec_driver.core.preboot.subprocess.run"`
   Delete legacy test file.

6. Create legacy shim `supekku/scripts/lib/core/preboot.py`:
   ```python
   """Re-export shim — see spec_driver.core.preboot."""
   from spec_driver.core.preboot import (
       BOOT_SEQUENCE,
       GENERATED_HEADER,
       GOVERNANCE_LISTINGS,
       PI_OUTPUT_DIR,
       PI_OUTPUT_FILE,
       PREBOOT_OUTPUT_DIR,
       PREBOOT_OUTPUT_FILE,
       generate_preboot_content,
       write_preboot_file,
   )

   __all__ = [
       "BOOT_SEQUENCE",
       "GENERATED_HEADER",
       "GOVERNANCE_LISTINGS",
       "PI_OUTPUT_DIR",
       "PI_OUTPUT_FILE",
       "PREBOOT_OUTPUT_DIR",
       "PREBOOT_OUTPUT_FILE",
       "generate_preboot_content",
       "write_preboot_file",
   ]
   ```
   (Verify public names match exactly what the test + consumers import.)

### Task 3 — Migrate `sync_preferences`

7. Copy `supekku/scripts/lib/core/sync_preferences.py` → `spec_driver/core/sync_preferences.py`.
   Imports already relative: `from .config import load_workflow_config`,
   `from .paths import SPEC_DRIVER_DIR`, `import tomlkit`. No changes needed
   — verbatim copy.

8. Move `supekku/scripts/lib/core/sync_preferences_test.py` →
   `spec_driver/core/sync_preferences_test.py`.
   Repoint imports:
   - `from supekku.scripts.lib.core.sync_preferences import …` →
     `from spec_driver.core.sync_preferences import …`
   No `@patch` paths to update. Delete legacy test file.

9. Create legacy shim `supekku/scripts/lib/core/sync_preferences.py`:
   ```python
   """Re-export shim — see spec_driver.core.sync_preferences."""
   from spec_driver.core.sync_preferences import (
       persist_spec_autocreate,
       spec_autocreate_enabled,
   )

   __all__ = [
       "persist_spec_autocreate",
       "spec_autocreate_enabled",
   ]
   ```

### Task 4 — Verify

10. `uv run pytest spec_driver/core/preboot_test.py -x` — all tests pass.
    (May fail to collect if nix-env is missing click/typer — same class as
    yaml_emit/spec_utils/frontmatter_writer/events/templates tests.)

11. `uv run pytest spec_driver/core/sync_preferences_test.py -x` — all tests pass.

12. `uvx import-linter lint` — 3/3 contracts KEPT. Core provably free of
    upward deps.

13. `uv run pytest spec_driver/core/ -x` — all core tests pass (excluding known
    nix-env gaps).

14. `uv run pytest supekku/scripts/lib/core/ -x` — remaining legacy non-migrated
    content (artifact_view_test, enums_test, plus any stragglers) passes through
    shims.

15. `uv run ruff check spec_driver/core/ supekku/scripts/lib/core/` — clean.

16. Final decoupling assertion:
    ```bash
    grep -rn 'frontmatter_metadata\|orchestration\|domain' spec_driver/core/ \
      --include='*.py' -l | grep -v __init__ | grep -v _test
    ```
    Should return only `spec_utils.py` (which mentions orchestration/domain
    in its **docstring** describing the decoupling — P02 verified this, it's
    a false positive). All other core modules must be clean.

17. Module count: `ls spec_driver/core/*.py | wc -l` — confirm 28+ files
    (file_ops, string_utils, yaml_emit + 26 migrated units; `slugify` folded
    into string_utils so not a separate file; `registry_migration` excluded).

## 4. Verification (VT/VA)

| Step | Type | What | Evidence |
|------|------|------|----------|
| import-linter | **VT** | 3/3 contracts KEPT; core→orchestration/domain forbidden | 165 files, 545 deps, 3 kept / 0 broken |
| pytest core/ | **VT** | All migrated test suites pass (excl. nix-env gaps) | 370 passed (excl. yaml/jinja2/tomlkit gaps); preboot 17/17 |
| pytest supekku shims | **VT** | Legacy consumers pass through shims | preboot + sync_preferences shims import OK; agent_docs shim OK |
| ruff check | **VT** | Zero lint warnings | All checks passed |
| module count | **VA** | 27 non-test modules in spec_driver/core/ | All 26 genuine migrated + 3 original (slugify merged, not separate) |
| decoupling grep | **VA** | Core modules import no domain/orchestration (excl. spec_utils docstring) | No actual imports — only docstring mentions (relation_types/config/yaml_emit/spec_utils, all FPs) |
| legacy non-shim audit | **VA** | No genuine module in supekku/scripts/lib/core/ (shims aside) | Only artifact_view_test.py + enums_test.py remain (out of scope, orchestration tests) |

## 5. Out of Scope

- `artifact_view_test.py`, `enums_test.py` — already shims to orchestration
  (DR-128 §2.5); tests stay at legacy paths.
- `frontmatter_metadata/` subpackage — domain knowledge, not core.
- Retiring re-export shims — tracked as separate DE-125 follow-on debt.
- `spec_driver/orchestration/` legacy-core imports — follow-on.
- `spec_driver/core/__init__.py` — currently empty except docstring; no
  public re-exports needed (consumer code imports specific modules).

## 6. Post-migration Checklist

- [x] All 26 genuine core modules migrated to `spec_driver/core/`
- [x] Decoupling holds: `core/spec_utils.py` + `core/config.py` import no orchestration/domain symbols
- [x] `import-linter` 3/3 KEPT — outer layer contract truthful
- [x] `spec-driver validate file phase-04.md` clean
