---
phase: IP-051-P01
name: Core migration + agent doc regeneration
status: complete
---

# Phase 1 — Core migration + agent doc regeneration

## Entrance Criteria

- [x] Delta DE-051 scoped and accepted
- [x] IP-051 drafted with verification plan

## Tasks

### 1. Add `tomlkit` dependency

- [ ] Add `tomlkit` to `pyproject.toml` dependencies
- [ ] `uv sync` to install

### 2. Add `[sync]` section to DEFAULT_CONFIG

- [ ] Add `"sync": {"spec_autocreate": False}` to `DEFAULT_CONFIG` in `config.py`

### 3. Rewrite `sync_preferences.py` for TOML-backed read/write

- [ ] `spec_autocreate_enabled(root)`:
  - Load workflow config via `load_workflow_config(root)`
  - Return `config["sync"]["spec_autocreate"]`
  - If key is False, check marker file as fallback (backward compat)
- [ ] `persist_spec_autocreate(root)`:
  - Read `workflow.toml` via `tomlkit` (round-trip preserving)
  - Set `sync.spec_autocreate = true`
  - Write back
  - If marker file exists, delete it
- [ ] Remove `MARKER_FILENAME` constant (or keep private for migration only)

### 4. Tests for sync_preferences

- [ ] VT-051-001: reads `True` from TOML `[sync] spec_autocreate = true`
- [ ] VT-051-002: falls back to marker file when TOML key is `false` but marker exists
- [ ] VT-051-003: persist writes `[sync] spec_autocreate = true` to workflow.toml, preserving comments
- [ ] VT-051-004: persist deletes marker file after writing TOML
- [ ] Migration scenario: marker exists, no TOML key → persist migrates → marker gone, TOML key set
- [ ] Clean slate: no marker, no TOML key → returns False
- [ ] TOML wins: TOML says true, no marker → returns True

### 5. Extract `_render_agent_docs` to `core/agent_docs.py`

- [ ] Move `_render_agent_docs` and `_discover_agent_templates` from `install.py` to `supekku/scripts/lib/core/agent_docs.py`
- [ ] `install.py` imports from new location
- [ ] Function signature: `render_agent_docs(target_root, package_root, *, dry_run=False)`

### 6. Call agent doc render early in `sync`

- [ ] Import `render_agent_docs` in `sync.py`
- [ ] Call it early in the sync command (before spec/contract sync)
- [ ] Emit brief status line: `"Regenerating agent docs from workflow.toml..."`

### 7. Tests for agent doc regeneration

- [ ] VT-051-006: `render_agent_docs` produces expected files from templates + config
- [ ] VT-051-005: existing sync behavior unchanged (run existing sync tests)

### 8. Lint + test

- [ ] `just lint` passes
- [ ] `just pylint` passes
- [ ] `just test` passes

## Exit Criteria

- [ ] All VTs (001–006) pass
- [ ] `just` green
- [ ] No new lint warnings
