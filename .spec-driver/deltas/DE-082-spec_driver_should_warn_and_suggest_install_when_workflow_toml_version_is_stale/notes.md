# Notes for DE-082

## Implementation summary

### Version-staleness warning (primary objective)

- Extracted `_get_package_version()` from `install.py` → `core/version.py` as `get_package_version()`
- `install.py` now delegates to the shared helper
- `_warn_if_version_stale()` added to `cli/main.py`, called from `_app_callback`
  - Compares `spec_driver_installed_version` in workflow.toml against running package version
  - Skips warning when command is `install`
  - Warns to stderr with actionable message
- Doctor check added: `_check_version_staleness()` in `diagnostics/checks/config.py`

### Default config change (secondary, bundled)

- `DEFAULT_CONFIG` in `core/config.py` updated:
  - `ceremony`: `pioneer` → `town_planner`
  - `kanban.enabled`: `True` → `False`
  - `policy.policies`: `False` → `True`
  - `policy.standards`: `False` → `True`
  - `sync.spec_autocreate`: `False` → `True`

### Files changed

- New: `core/version.py`, `core/version_test.py`, `cli/test_version_warning.py`
- Modified: `cli/main.py`, `scripts/install.py`, `diagnostics/checks/config.py`
- Modified: `core/config.py` (defaults)
- Test updates: `config_test.py`, `sync_defaults_test.py`, `sync_preferences_test.py`, `install_test.py`

### Verification

- 3629 tests pass, 4 skipped
- `just check` passes (ruff + pylint + tests)
