---
id: IP-062.PHASE-01
slug: 062-workflow_toml_rich_commented_defaults_and_config_memory-phase-01
name: IP-062 Phase 01 - template generator, install wiring, config memory
created: "2026-03-08"
updated: "2026-03-08"
status: completed
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
    - VT-062-01: template completeness — verified
    - VT-062-02: template TOML validity — verified
    - VT-062-03: install integration — verified
  evidence:
    - VA-062-01: memory accuracy — verified
tasks:
  - id: 1.1
    description: Write generate_default_workflow_toml() in config.py
    status: done
  - id: 1.2
    description: Tests for template generator
    status: done
  - id: 1.3
    description: Wire into install.py
    status: done
  - id: 1.4
    description: Create agent memory record
    status: done
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
- **Install target**: `supekku/scripts/install.py`

## 3. Entrance Criteria

- [x] DE-062 scoped and accepted

## 4. Exit Criteria / Done When

- [x] `generate_default_workflow_toml(exec_cmd)` exists and is tested
- [x] `install.py` calls generator instead of inline write
- [x] Memory record `mem.reference.spec-driver.workflow-config` created
- [x] `just` passes (3031 tests, lint clean)

## 7. Tasks & Progress

| Status | ID  | Description                                             | Notes                                                                                                                    |
| ------ | --- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| [x]    | 1.1 | `generate_default_workflow_toml(exec_cmd)` in config.py | Uses `##` for prose, `#` for config                                                                                      |
| [x]    | 1.2 | Tests for generator                                     | 7 tests: completeness, TOML validity, tool uncommented, exec substitution, sections commented, prose comments, roundtrip |
| [x]    | 1.3 | Wire into install.py                                    | Replaced lines 678-680, added import                                                                                     |
| [x]    | 1.4 | Agent memory record                                     | `mem.reference.spec-driver.workflow-config` — full config reference                                                      |

## 9. Decisions & Outcomes

- 2026-03-08 — Used `##` for prose comments and `#` for config lines. This lets users uncomment config with a single `#` strip while prose explanations remain as TOML comments. Cleaner than single-prefix approach.
- 2026-03-08 — Extracted `_prose()`, `_emit_prose()`, `_emit_section()` helpers to keep `generate_default_workflow_toml` under McCabe threshold.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: all tests pass, memory queryable
- [x] Phase complete
