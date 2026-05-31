---
id: IP-128-P03
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-03"
name: "Tier 2 — migrate config (decouple), templates"
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
phase: IP-128-P03
plan: IP-128
delta: DE-128
objective: >-
  Migrate 2 tier-2 modules (+ tests) with relative imports. DECOUPLE config:
  inject known_kinds into load_workflow_config so core stops importing the
  domain frontmatter_metadata subpackage. Templates migrates verbatim
  (already uses relative `.paths` import).
entrance_criteria:
  - Phase 2 complete (all tier-0 + tier-1 modules + tests in spec_driver/core/; all shims in place)
  - spec_driver/domain/relations/ imports repointed (zero legacy-core in domain/)
  - import-linter 3/3 KEPT; core/spec_utils.py has no upward deps
exit_criteria:
  - 2 tier-2 modules (+ tests) in spec_driver/core/ with relative imports
  - core/config.py imports NO frontmatter_metadata (linter/grep-verified)
  - load_workflow_config takes known_kinds; validate/file.py passes the registry
  - strict-kind warning VT pins warn-when-injected + silent-when-not
  - supekku/scripts/lib/core/__init__.py config imports repointed through shim
  - All tests pass; both import-linter contracts pass; ruff clean
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
  evidence:
    - grep showing core/config.py has no frontmatter_metadata import
    - pytest output showing strict-kind VT (warn + silent paths)
    - grep confirming validate/file.py passes known_kinds
tasks:
  - Decouple config: add known_kinds param, gate _warn_unknown_strict_kinds, drop frontmatter_metadata import (tasks 1–3)
  - Wire validate/file.py to pass FRONTMATTER_METADATA_REGISTRY.keys() (task 4)
  - Update config_test.py: repoint imports + new VT for both warning paths (task 5)
  - Migrate config (+ test) to spec_driver/core/; create shim (task 6)
  - Update supekku/scripts/lib/core/__init__.py config imports through shim (task 7)
  - Migrate templates (+ test) to spec_driver/core/; create shim (task 8)
  - Verify (task 9)
risks:
  - config DI must not silently drop the strict-kind warning — a VT tests both paths
  - 7 non-test consumers of load_workflow_config — all go through legacy shim, unchanged
  - config_test.py has many tests; repointing imports is mechanical but broad
  - templates_test.py patches supekku-prefixed paths — must repoint all @patch targets
  - events_test.py lazy imports of config will resolve through legacy shim (created in this phase)
  - config.py imports `from .paths import SPEC_DRIVER_DIR` — already relative, no change needed
assumptions:
  - registry_migration.py does not exist in the source tree (zero consumers); excluded from P03
  - jinja2 is available in the test environment (templates.py dependency)
  - events_test.py lazy imports of supekku.scripts.lib.core.config stay working through the legacy shim
---

# Phase 3 — Tier 2: config (decouple), templates

## 1. Objective

Move the 2 tier-2 modules (with their tests) into `spec_driver.core`.
**Decouple `config`** from its upward dependency on the domain-level
`frontmatter_metadata` subpackage via dependency injection (DEC-128-005,
DR-128 §2.4). `templates` migrates cleanly — it already uses a relative
`.paths` import.

> **Note**: `registry_migration.py` was listed in the original DR as a tier-2
> module (added by DE-146) but does not exist in the source tree and has zero
> consumers. Excluded from this phase. If it lands later, it follows the same
> migration pattern.

## 2. Modules

| Module | Lines | Depends on | Third-party | Key change |
|--------|-------|-----------|-------------|------------|
| `config.py` | 545 | `paths` | tomllib | **decouple** from `frontmatter_metadata` (DI); `from .paths import SPEC_DRIVER_DIR` |
| `templates.py` | 160 | `paths` | jinja2 | verbatim — `from .paths import get_templates_dir` already relative |

## 3. config decoupling (DEC-128-005 / adversarial F3)

### Current architecture

`_warn_unknown_strict_kinds` (called eagerly at line 145 of
`load_workflow_config`) calls `_registered_kinds()` which lazy-imports
`FRONTMATTER_METADATA_REGISTRY` from the domain-level
`core.frontmatter_metadata` subpackage. If config lands in `spec_driver.core`
as-is, the `core→domain` edge violates POL-003 and fails `import-linter`.

The "break cycle" comment on the lazy import is **stale** —
`frontmatter_metadata` no longer imports `config`.

### Solution

**Dependency injection**: `load_workflow_config` gains an optional
`known_kinds: set[str] | None = None` parameter. The strict-kind warning
only fires when `known_kinds` is provided (i.e. at the validating entrypoint).
Core `config` drops all knowledge of `frontmatter_metadata`.

- **Signature**: `load_workflow_config(repo_root, known_kinds=None)`.
- **The one validating entrypoint** that needs the warning is
  `spec_driver/presentation/cli/validate/file.py:263`:
  `get_strict_map(load_workflow_config(repo_root))` →
  `get_strict_map(load_workflow_config(repo_root, known_kinds=set(FRONTMATTER_METADATA_REGISTRY.keys())))`.
  It already imports `FRONTMATTER_METADATA_REGISTRY` — zero new imports.
- **7 other non-test consumers** call `load_workflow_config` with no
  `known_kinds`; the warning is silently skipped (deliberate — they shouldn't
  warn on user kind config during infra reads).

### Behaviour change (deliberate, tested)

The strict-kind warning (`F-47`) fires **only** at the validating entrypoint,
not on every config read. This is a tested behaviour change: a VT must pin
both the warn-when-injected and silent-when-not paths.

### gory detail: `_registered_kinds()` → `_warn_unknown_strict_kinds(merged, known_kinds)`

The cleanest implementation:

1. Remove `_registered_kinds()` entirely.
2. Change `_warn_unknown_strict_kinds(config: dict, known_kinds: set[str] | None = None) → None`:
   ```python
   def _warn_unknown_strict_kinds(config: dict, known_kinds: set[str] | None = None) -> None:
       if known_kinds is None:
           return
       strict_section = config.get("validation", {}).get("strict", {}) or {}
       if not isinstance(strict_section, dict):
           return
       for key in strict_section:
           if key not in known_kinds:
               warnings.warn(
                   f"workflow.toml [validation.strict]: unknown kind '{key}'; ignored",
                   UserWarning,
                   stacklevel=3,
               )
   ```
3. `get_strict_map` also needs updating — it currently calls `_registered_kinds()`
   internally. Change to accept `known_kinds`:
   ```python
   def get_strict_map(config: dict, known_kinds: set[str] | None = None) -> dict[str, bool]:
       ...
       if known_kinds is None:
           return {}
       return {kind: bool(value) for kind, value in strict_section.items() if kind in known_kinds}
   ```
   Wait — this would break all non-validating callers of `get_strict_map`.
   Alternative: `get_strict_map` stays as-is (filtering + coercion) but without
   the domain lookup. Since `get_strict_map` is only called from one place
   (`validate/file.py:263`), we can also just remove `get_strict_map`'s
   dependency on `_registered_kinds` and have the caller filter. But the
   simplest approach:

   Keep `get_strict_map` filtering on `known_kinds` when provided; return all
   keys unfiltered when `None`. The one caller (`validate/file.py`) always
   passes `known_kinds`, so it will filter. Other callers don't exist.

   Actually, let me check: who calls `get_strict_map`?
   - `validate/file.py:263` — the only caller.
   - `core/__init__.py` does NOT re-export it.
   - tests call it directly.

   So the cleanest fix: `get_strict_map(config, known_kinds=None)`. When
   `known_kinds` is `None`, return the unfiltered map (all keys, coerced to
   bool). When provided, filter to known kinds. This keeps the function
   testable without the registry.

   Actually even simpler — `get_strict_map` can just accept `known_kinds` and
   always filter. The test already constructs its own known set. The one
   production caller always passes it.

   **Simplest implementation:**
   ```python
   def get_strict_map(config: dict, known_kinds: set[str]) -> dict[str, bool]:
       """Return per-kind strict-mode map, filtered to known_kinds."""
       strict_section = config.get("validation", {}).get("strict", {}) or {}
       if not isinstance(strict_section, dict):
           return {}
       return {kind: bool(value) for kind, value in strict_section.items() if kind in known_kinds}
   ```

   And `validate/file.py` passes:
   ```python
   strict_map = get_strict_map(
       load_workflow_config(repo_root, known_kinds=set(FRONTMATTER_METADATA_REGISTRY.keys())),
       known_kinds=set(FRONTMATTER_METADATA_REGISTRY.keys()),
   )
   ```

   This is clean — no domain import in core, filtering explicit.

4. Remove `from .frontmatter_metadata import FRONTMATTER_METADATA_REGISTRY` (the
   lazy import inside `_registered_kinds`) — the entire `_registered_kinds()`
   function is deleted.

## 4. Task Breakdown

### Task 1 — Decouple config: signature + `_warn_unknown_strict_kinds`

1. In `supekku/scripts/lib/core/config.py`:
   a. Change `load_workflow_config(repo_root: Path) -> dict` →
      `load_workflow_config(repo_root: Path, known_kinds: set[str] | None = None) -> dict`.
      Pass `known_kinds` through to `_warn_unknown_strict_kinds`.
   b. Change `_warn_unknown_strict_kinds(config: dict) -> None` →
      `_warn_unknown_strict_kinds(config: dict, known_kinds: set[str] | None = None) -> None`.
      Gate: `if known_kinds is None: return`. Use `known_kinds` instead of
      `_registered_kinds()`.
   c. Change `get_strict_map(config: dict) -> dict[str, bool]` →
      `get_strict_map(config: dict, known_kinds: set[str]) -> dict[str, bool]`.
      Drop internal `_registered_kinds()` call; use passed `known_kinds`.
   d. Delete `_registered_kinds()` function and its lazy
      `from .frontmatter_metadata import FRONTMATTER_METADATA_REGISTRY`.
2. Verify the legacy config still works: `uv run pytest supekku/scripts/lib/core/config_test.py -x -k "strict"` —
   will fail on tests that call without `known_kinds` (expected; fix in Task 5).

### Task 2 — Wire `validate/file.py` entrypoint

3. In `spec_driver/presentation/cli/validate/file.py`:
   a. Change line 263 from:
      ```python
      strict_map = get_strict_map(load_workflow_config(repo_root))
      ```
      to:
      ```python
      known = set(FRONTMATTER_METADATA_REGISTRY.keys())
      strict_map = get_strict_map(load_workflow_config(repo_root, known_kinds=known), known_kinds=known)
      ```
   b. `FRONTMATTER_METADATA_REGISTRY` is already imported at line 37 — zero new imports.

### Task 3 — Update config tests for new contract

4. Move `supekku/scripts/lib/core/config_test.py` → `spec_driver/core/config_test.py`.
   Repoint imports:
   - `from supekku.scripts.lib.core.config import …` →
     `from spec_driver.core.config import …`
   - `from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR` →
     `from spec_driver.core.paths import SPEC_DRIVER_DIR`
   Delete legacy test file.

5. Update the strict-kind tests (lines ~514–578):
   a. `test_unknown_kind_emits_warning`: add `known_kinds={"delta", "spec"}` to
      `load_workflow_config` calls. The warning should fire for `foo`.
   b. `test_known_kind_no_warning`: add `known_kinds={"delta", "spec"}`.
   c. `test_mixed_warns_only_for_unknown`: add `known_kinds={"delta", "spec"}`.
   d. `test_returns_only_known_kinds`: update `get_strict_map(config, known_kinds={"delta", "spec"})`.
   e. Other `get_strict_map` calls: add `known_kinds={"delta", "spec"}` or
      an appropriate test set.
   f. **NEW VT**: `test_no_warning_when_known_kinds_is_none` — call
      `load_workflow_config(tmp_path)` (no `known_kinds`) with unknown kinds in
      TOML, assert NO warning is raised.
   g. **NEW VT**: `test_warning_when_known_kinds_provided` — call
      `load_workflow_config(tmp_path, known_kinds={"delta"})` with unknown
      `foo = true` in TOML, assert warning IS raised.

### Task 4 — Migrate config to `spec_driver/core/`

6. Copy `supekku/scripts/lib/core/config.py` → `spec_driver/core/config.py`.
   Ensure the relative import `from .paths import SPEC_DRIVER_DIR` is
   already correct (it was relative before migration). Verify no other
   imports need changing.
7. Confirm `core/config.py` has zero `frontmatter_metadata` references:
   `grep -n 'frontmatter_metadata\|_registered_kinds' spec_driver/core/config.py` → empty.

### Task 5 — Create config legacy shim + update `__init__.py`

8. Replace `supekku/scripts/lib/core/config.py` with a re-export shim:
   ```python
   """Re-export shim — see spec_driver.core.config."""
   from spec_driver.core.config import (
       DEFAULT_CONFIG,
       detect_exec_command,
       generate_default_workflow_toml,
       get_strict_map,
       is_strict_mode,
       load_workflow_config,
   )

   __all__ = [
       "DEFAULT_CONFIG",
       "detect_exec_command",
       "generate_default_workflow_toml",
       "get_strict_map",
       "is_strict_mode",
       "load_workflow_config",
   ]
   ```
   (Private helpers `_is_project_dependency`, `_is_global_install` etc. are
   not re-exported — they aren't imported by any consumer; grep to confirm.)

9. Update `supekku/scripts/lib/core/__init__.py`:
   - Change `from .config import is_strict_mode, load_workflow_config` →
     `from spec_driver.core.config import is_strict_mode, load_workflow_config`
     (the shim would also work, but direct is cleaner since we're updating
     __init__ anyway).
   - Add `get_strict_map` to the imports if any consumer uses
     `from supekku.scripts.lib.core import get_strict_map` (grep to confirm
     — likely not; `validate/file.py` imports directly from config).
   - Actually — the __init__ currently re-exports config for backward compat.
     The shim at `supekku/scripts/lib/core/config.py` handles direct imports.
     The __init__ re-export should point to the shim path to avoid importing
     from the old module before it's replaced. Simplest: keep the `from .config`
     import — after step 8, `.config` IS the shim, so it resolves through
     `spec_driver.core.config` transitively. No change needed in __init__.py.

   Wait — actually this is cleaner: update `__init__.py` to import directly
   from `spec_driver.core.config` so there's no double-hop. But this is
   cosmetic; the double-hop through the local shim also works. Leave __init__.py
   alone for now — the `.config` import resolves through the shim automatically.

### Task 6 — Migrate templates to `spec_driver/core/`

10. Copy `supekku/scripts/lib/core/templates.py` → `spec_driver/core/templates.py`.
    The import `from .paths import get_templates_dir` is already relative — no
    change needed. Verify no other imports need changing.

11. Move `supekku/scripts/lib/core/templates_test.py` → `spec_driver/core/templates_test.py`.
    Repoint imports:
    - `from supekku.scripts.lib.core.templates import …` →
      `from spec_driver.core.templates import …`
    - All `@patch("supekku.scripts.lib.core.templates.…")` decorators →
      `@patch("spec_driver.core.templates.…")` (9 occurrences).
    - `from supekku.scripts.lib.core.paths import get_templates_dir` references
      inside patched tests — these mock the function, not the module, so no
      change needed at call sites.
    Delete legacy test file.

12. Create legacy shim `supekku/scripts/lib/core/templates.py`:
    ```python
    """Re-export shim — see spec_driver.core.templates."""
    from spec_driver.core.templates import (
        TemplateNotFoundError,
        extract_template_body,
        get_package_templates_dir,
        get_template_environment,
        load_template,
        render_template,
    )

    __all__ = [
        "TemplateNotFoundError",
        "extract_template_body",
        "get_package_templates_dir",
        "get_template_environment",
        "load_template",
        "render_template",
    ]
    ```

### Task 7 — Verify

13. `uv run pytest spec_driver/core/config_test.py spec_driver/core/templates_test.py -x` —
    all tests pass. Pay special attention to:
    - Strict-kind VT: warn-when-injected passes, silent-when-not passes
    - Template tests: all `@patch` paths resolve correctly

14. `uv run pytest supekku/scripts/lib/core/ -x` —
    remaining legacy tests (agent_docs, preboot, sync_preferences for P04) pass
    through shims. `events_test.py` lazy config imports resolve through the new
    config shim.

15. `uvx import-linter lint` — both contracts KEPT. Core must show zero upward
    edges (no core→domain, no core→orchestration).

16. `uv run pytest supekku spec_driver -x` — full suite passes.

17. `uv run ruff check spec_driver/core/ supekku/scripts/lib/core/` — clean.

18. **Decoupling assertions**:
    - `grep -n 'frontmatter_metadata\|_registered_kinds' spec_driver/core/config.py` → empty.
    - `grep -n 'known_kinds=.*FRONTMATTER_METADATA_REGISTRY' spec_driver/presentation/cli/validate/file.py` → found.

## 5. Verification (VT/VA)

| Step | Type | What | Evidence |
|------|------|------|----------|
| config_test VT | **VT** | `test_no_warning_when_known_kinds_is_none` passes | pytest output |
| config_test VT | **VT** | `test_warning_when_known_kinds_provided` passes | pytest output |
| config_test VT | **VT** | All existing strict-kind tests pass with `known_kinds` | pytest output |
| import-linter | **VT** | Both contracts KEPT; core→domain forbidden | CLI output |
| pytest core/ | **VT** | config_test + templates_test pass | pytest summary |
| pytest supekku shims | **VT** | Legacy consumers still work through shims | pytest summary |
| ruff check | **VT** | Zero lint warnings | ruff output |
| frontmatter_metadata grep | **VA** | `spec_driver/core/config.py` has zero references | Agent confirms |
| validate/file.py grep | **VA** | Entrypoint passes `known_kinds` | Agent confirms |
| _registered_kinds deleted | **VA** | Function no longer exists in core config | Agent confirms |

## 6. Out of Scope

- `registry_migration.py` — not in source tree (zero consumers).
- `frontmatter_metadata/` subpackage — domain knowledge, out of scope per
  DR-128 §2.5.
- `enums.py`, `artifact_view.py` — already shims to orchestration.
- Repointing `events_test.py` lazy config imports — they resolve through
  the legacy shim; follow-on cleanup.
- Updating other `supekku/scripts/lib/core/__init__.py` re-exports for editor,
  filters, npm_utils, strings — already pointing at shims from P01/P02, no
  change needed.
- `spec_driver/orchestration/` legacy-core imports — follow-on.
