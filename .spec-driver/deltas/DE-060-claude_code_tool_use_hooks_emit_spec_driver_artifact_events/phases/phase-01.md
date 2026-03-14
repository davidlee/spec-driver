---
id: IP-060.PHASE-01
slug: "060-claude_code_tool_use_hooks_emit_spec_driver_artifact_events-phase-01"
name: IP-060 Phase 01
created: "2026-03-08"
updated: "2026-03-08"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-060.PHASE-01
plan: IP-060
delta: DE-060
objective: >-
  Create self-contained artifact event hook script, register in settings,
  write tests, verify end-to-end.
entrance_criteria:
  - DR-060 reviewed
  - Claude Code hook API understood
exit_criteria:
  - artifact_event.py classifies all spec-driver artifact path patterns
  - Non-artifact paths silently ignored
  - Events append to JSONL log with v1 schema
  - Hook registered in .claude/settings.json
  - just passes (lint + test)
verification:
  tests:
    - VT-060-01
    - VT-060-02
    - VT-060-03
  evidence:
    - VH-060-01
tasks:
  - id: "1.1"
    description: Create artifact_event.py hook script
  - id: "1.2"
    description: Register PostToolUse hook in .claude/settings.json
  - id: "1.3"
    description: Write tests for path classification and event emission
  - id: "1.4"
    description: VH-060-01 manual smoke test
risks:
  - Run dir may not exist when hook fires
```

# Phase 1 - Hook script, registration, and tests

## 1. Objective

Create the self-contained Python hook script that detects spec-driver
artifact file touches and emits events, register it in Claude Code
settings, and verify with tests.

## 2. Links & References

- **Delta**: DE-060
- **Design Revision**: DR-060 (DEC-060-01, DEC-060-02, DEC-060-03)

## 3. Entrance Criteria

- [x] DR-060 reviewed
- [x] Claude Code hook API understood (PostToolUse, async, JSON schema)

## 4. Exit Criteria / Done When

- [ ] `artifact_event.py` classifies spec-driver artifact paths
- [ ] Non-artifact paths silently ignored
- [ ] Events written to JSONL with v1 schema
- [ ] Hook registered in `.claude/settings.json`
- [ ] `just` green

## 5. Verification

- VT-060-01: Path classification correctness
- VT-060-02: Non-artifact paths ignored
- VT-060-03: Event schema correctness
- VH-060-01: Manual smoke — agent edits delta, TUI shows event

## 6. Tasks

| Status | ID  | Description                                          |
| ------ | --- | ---------------------------------------------------- |
| [ ]    | 1.1 | Create `supekku/claude.hooks/artifact_event.py`      |
| [ ]    | 1.2 | Register PostToolUse hook in `.claude/settings.json` |
| [ ]    | 1.3 | Write tests                                          |
| [ ]    | 1.4 | VH-060-01 manual attestation                         |
