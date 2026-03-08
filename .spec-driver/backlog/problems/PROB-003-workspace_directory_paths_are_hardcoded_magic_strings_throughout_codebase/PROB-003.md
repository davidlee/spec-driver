---
id: PROB-003
name: Workspace directory paths are hardcoded magic strings throughout codebase
created: '2026-03-05'
updated: '2026-03-05'
status: resolved
kind: problem
severity: moderate
tags: [maintainability, paths, magic-strings, refactor]
policies: [POL-002]
---

# Workspace directory paths are hardcoded magic strings throughout codebase

## Problem

The four workspace directory names (`specify/`, `change/`, `backlog/`, `memory/`)
are scattered as raw string literals across ~60-70 Python source files and ~30+
test files. There is no central definition for these paths despite `paths.py`
already centralizing the `.spec-driver` directory name.

## Evidence

- `"specify"` appears in ~49 Python files
- `"change/"` appears in ~44 Python files
- `"backlog"` appears in ~22 Python files
- `"memory/"` appears in ~8 Python files
- `paths.py` centralizes `SPEC_DRIVER_DIR` but not workspace dirs
- No config mechanism exists to override directory names

## Impact

- **Rename brittleness**: changing any directory name requires a codebase-wide
  hunt-and-replace with high risk of missed references
- **Policy violation**: directly violates POL-002 (avoid magic strings)
- **Configurability blocked**: cannot offer directory name customization to
  downstream users without first centralizing the constants
- **Agent drift**: AI agents independently "discover" and re-hardcode these
  strings rather than importing a constant

## Success Criteria

- All workspace directory names defined as constants in `core/paths.py`
- All production code references replaced with constant imports
- Test fixtures use constants (or helpers that use them)
- Optional: directory names configurable via `workflow.toml`

## Resolution Progress

- **DE-044 (completed)**: Centralized all workspace directory names as constants
  in `core/paths.py`. All production code and test fixtures now use constants.
  First 3 success criteria met.
- **IMPR-008**: Configurable directory layout (remaining success criterion).
  Spike complete — see `backlog/improvements/IMPR-008-*/spike.md`.

## References

- `supekku/scripts/lib/core/paths.py` — existing path centralization
- `supekku/scripts/lib/core/config.py` — existing config loading
- POL-002: Avoid magic strings and numbers
