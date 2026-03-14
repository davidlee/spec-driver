---
id: IP-077.PHASE-02
slug: 077-cli_ux_schema_discoverability_and_flag_parsing-phase-02
name: 'IP-077 Phase 02: Verification and polish'
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-077.PHASE-02
plan: IP-077
delta: DE-077
objective: >-
  Full test suite green, both linters clean, integration smoke test
entrance_criteria:
  - Phase 1 complete
exit_criteria:
  - just passes (all checks)
  - No regressions in existing create command tests
verification:
  tests:
    - VT-077-schema-hints
    - VT-077-schema-hints-integration
    - VT-077-from-backlog
  evidence: []
tasks:
  - id: "2.1"
    description: Run full test suite
  - id: "2.2"
    description: Run both linters on full codebase
  - id: "2.3"
    description: Manual smoke test of create commands
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-077.PHASE-02
```

# Phase 2 — Verification and polish

## 1. Objective

Ensure no regressions, both linters clean on full codebase, manual smoke test of key create commands.

## 2. Links & References

- **Delta**: DE-077
- **Phase 1**: `phases/phase-01.md`

## 3. Entrance Criteria

- [ ] Phase 1 exit criteria satisfied

## 4. Exit Criteria / Done When

- [ ] `just test` passes (full suite)
- [ ] `just lint` passes (ruff, zero warnings)
- [ ] `just pylint-report` score not regressed
- [ ] Smoke: `create delta --from-backlog --help` shows help
- [ ] Smoke: `create delta` output includes schema hints

## 5. Verification

- `just` — all checks
- Manual: `uv run spec-driver create delta --from-backlog --help`
- Manual: verify schema hint output on a test creation

## 7. Tasks & Progress

| Status | ID  | Description                        | Parallel? | Notes         |
| ------ | --- | ---------------------------------- | --------- | ------------- |
| [ ]    | 2.1 | `just test`                        |           |               |
| [ ]    | 2.2 | `just lint` + `just pylint-report` |           |               |
| [ ]    | 2.3 | Manual smoke tests                 |           | After 2.1–2.2 |
