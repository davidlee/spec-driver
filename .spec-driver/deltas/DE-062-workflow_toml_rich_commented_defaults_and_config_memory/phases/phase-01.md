---
id: IP-062.PHASE-01
slug: 062-workflow_toml_rich_commented_defaults_and_config_memory-phase-01
name: IP-062 Phase 01 - template generator, install wiring, config memory
created: '2026-03-08'
updated: '2026-03-08'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-062.PHASE-01
plan: IP-062
delta: DE-062
objective: >-
  Write a template generator that renders DEFAULT_CONFIG as commented TOML,
  wire it into install.py, and create agent memory for the config surface.
entrance_criteria:
  - DE-062 accepted
exit_criteria:
  - Generated template contains all DEFAULT_CONFIG keys as comments
  - Generated template is valid TOML when uncommented
  - install.py uses new generator
  - Agent memory is queryable
  - just passes (tests + lint)
verification:
  tests:
    - VT-062-01: template completeness
    - VT-062-02: template TOML validity
    - VT-062-03: install integration
  evidence:
    - VA-062-01: memory accuracy check
tasks:
  - id: 1.1
    description: Write generate_default_workflow_toml() in config.py
  - id: 1.2
    description: Tests for template generator
  - id: 1.3
    description: Wire into install.py
  - id: 1.4
    description: Create agent memory record
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-062.PHASE-01
```

# Phase 1 – Template generator, install wiring, config memory

## 1. Objective

Replace the spartan 2-line workflow.toml init with a richly-commented template generated from DEFAULT_CONFIG. Create agent memory documenting the config surface.

## 2. Links & References

- **Delta**: DE-062
- **Config source**: `supekku/scripts/lib/core/config.py`
- **Install target**: `supekku/scripts/install.py` (lines 671-681)

## 3. Entrance Criteria

- [x] DE-062 scoped and accepted

## 4. Exit Criteria / Done When

- [ ] `generate_default_workflow_toml(exec_cmd)` exists and is tested
- [ ] `install.py` calls generator instead of inline write
- [ ] Memory record `mem.reference.spec-driver.workflow-config` created
- [ ] `just` passes

## 5. Verification

- `just test` — all existing + new tests pass
- `just lint` — zero warnings
- `uv run spec-driver show memory mem.reference.spec-driver.workflow-config` works

## 6. Assumptions & STOP Conditions

- Assumptions: generating from DEFAULT_CONFIG dict is sufficient; no need for schema metadata
- STOP when: if template generation needs to handle types beyond str/bool/int/list, consult

## 7. Tasks & Progress

| Status | ID | Description | Notes |
| --- | --- | --- | --- |
| [ ] | 1.1 | `generate_default_workflow_toml(exec_cmd)` in config.py | Renders DEFAULT_CONFIG as commented TOML |
| [ ] | 1.2 | Tests for generator | Completeness, validity, exec_cmd substitution |
| [ ] | 1.3 | Wire into install.py | Replace lines 678-680 |
| [ ] | 1.4 | Agent memory record | `mem.reference.spec-driver.workflow-config` |

### Task Details

- **1.1**: Function takes `exec_cmd` param (detected at install time), renders each DEFAULT_CONFIG section as `# [section]` / `# key = value` with human-readable comments explaining each section's purpose. The `[tool]` section is uncommented (active) since `exec` is install-specific.

- **1.2**: Test that all keys from DEFAULT_CONFIG appear in output. Test that stripping `#` prefix yields valid TOML. Test exec_cmd substitution.

- **1.3**: Replace `workflow_toml.write_text(f'[tool]\nexec = "{exec_cmd}"\n')` with call to generator.

- **1.4**: Memory covering: section inventory, key descriptions, ceremony modes, merge behaviour, where each key is used.
