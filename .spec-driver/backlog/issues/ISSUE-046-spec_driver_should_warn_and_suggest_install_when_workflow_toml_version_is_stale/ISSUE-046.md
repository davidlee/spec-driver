---
id: ISSUE-046
name: spec-driver should warn and suggest install when workflow.toml version is stale
created: '2026-03-09'
updated: '2026-03-09'
status: open
kind: issue
categories: []
severity: p2
impact: user
---

# spec-driver should warn and suggest install when workflow.toml version is stale

## Problem

After upgrading the spec-driver package, `workflow.toml` retains the old
`spec_driver_installed_version`. Users get no indication that `spec-driver
install` should be re-run to update agent docs, skills, and workspace structure.

## Proposed solution

1. **CLI callback warning** — in `_app_callback` (`main.py`), compare
   `spec_driver_installed_version` from loaded config against the current
   package version. If they differ (or the key is missing), emit a stderr
   warning suggesting `spec-driver install`. Skip the warning when the
   command being invoked is `install` itself.

2. **Doctor check** — add a version-staleness diagnostic to
   `diagnostics/checks/config.py` so `spec-driver doctor` also reports it.

3. **Shared helper** — extract `_get_package_version()` from `install.py` to
   a shared location (e.g. `core/version.py`) so both sites can use it
   without import cycles.

