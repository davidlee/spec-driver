---
id: IP-108-P01
slug: "108-review_cli_contract_for_structured_machine_consumption-phase-01"
name: "Foundation — exit codes and envelope helpers"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
plan: IP-108
delta: DE-108
---

# Phase 01 — Foundation: exit codes and envelope helpers

## 1. Objective

Add granular exit code constants and CLI-generic JSON envelope helpers to `supekku/cli/common.py`. This is the foundation all subsequent phases depend on.

## 2. Links & References

- **Delta**: [DE-108](../DE-108.md)
- **Design Revision Sections**: DR-108 §4 (Exit Codes), §5 (JSON Envelope)
- **Design Decisions**: DEC-108-001 (envelope in common.py), DEC-108-008 (exit codes), DEC-108-010 (stderr suppression pattern)
- **Specs / PRODs**: PROD-010

## 3. Entrance Criteria

- [x] DR-108 approved with adversarial review integrated
- [x] IP-108 phase plan accepted

## 4. Exit Criteria / Done When

- [ ] `EXIT_PRECONDITION = 2` and `EXIT_GUARD_VIOLATION = 3` constants in `common.py`
- [ ] `cli_json_success(command, data)` returns correct envelope dict
- [ ] `cli_json_error(command, exit_code, kind, message)` returns correct error envelope dict
- [ ] `emit_json_and_exit(payload)` prints JSON to stdout and raises `typer.Exit` with correct code
- [ ] Unit tests for all three helpers + constants
- [ ] Lint clean (STD-002)

## 5. Verification

- `pytest supekku/cli/common_test.py` (or equivalent test location)
- Envelope structure: version=1, command, status, exit_code, data/error fields typed correctly
- Error kinds: precondition, guard_violation, validation, unexpected — all constructible
- `emit_json_and_exit` captures stdout and verifies valid JSON + correct exit code

## 6. Assumptions & STOP Conditions

- Assumes `common.py` is the right home — POL-001 says yes, but STOP if import cycles appear
- STOP if existing tests break from new constants (unlikely — additive)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 1.1 | Add `EXIT_PRECONDITION`, `EXIT_GUARD_VIOLATION` constants | | Near `EXIT_SUCCESS`/`EXIT_FAILURE` |
| [ ] | 1.2 | Implement `cli_json_success()` | | Returns envelope dict |
| [ ] | 1.3 | Implement `cli_json_error()` | | Returns error envelope dict |
| [ ] | 1.4 | Implement `emit_json_and_exit()` | | Prints JSON, raises typer.Exit |
| [ ] | 1.5 | Unit tests for 1.1–1.4 | | Envelope shape, exit code, valid JSON |
| [ ] | 1.6 | Lint check | | STD-002 |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Import cycle if common.py imports typer differently | `emit_json_and_exit` already in a module that imports typer | open |

## 9. Decisions & Outcomes

_To be filled during execution._

## 10. Findings / Research Notes

_To be filled during execution._

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to Phase 02
