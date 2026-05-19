---
id: ISSUE-056
slug: spec_driver_install_ergonomics_refresh_workflow_toml_schema_version_without_full_re_install
name: "spec-driver install ergonomics: refresh workflow.toml schema_version without full re-install"
created: "2026-05-19"
updated: "2026-05-19"
status: open  # one of: in-progress | open | resolved | triaged
kind: issue  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
categories: []
severity: p3  # one of: p1 | p2 | p3 | p4
impact: user  # one of: user | systemic | process
---

# spec-driver install ergonomics: refresh workflow.toml schema_version without full re-install

## Symptom

`uv run spec-driver <any-cmd>` emits:

```
Warning: spec-driver may need re-install (workflow.toml has 0.9.2, running 0.9.7).
  Run: spec-driver install
```

Drift is cosmetic — no behavioural divergence observed for `validate file`,
`validate workspace`, `admin migrate`, `complete delta` surfaces.

## Cause

`workflow.toml [schema_version] spec_driver_installed_version` is bumped only
on `spec-driver install`. CLI version rolled forward (0.9.2 → 0.9.7) without
an intervening re-install. Re-install would refresh the key plus other
install-tracked state (claude config, hooks, agents, memory seeds), which is
heavier than the single-line bump the user wants.

## Proposed Resolution

Add an install-side `--refresh-version` (or equivalent) flag that bumps only
`[schema_version] spec_driver_installed_version` without re-applying templates
or re-prompting for optional dependencies. Acceptance: warning silences on
next invocation after a single command run.

## References

- Originated from DE-137 AUD-026 FIND-010 (2026-05-19, conformance audit).
- Touches `supekku/scripts/install.py` (version bump logic).

