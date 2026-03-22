---
id: IP-108-P02
slug: "108-review_cli_contract_for_structured_machine_consumption-phase-02"
name: "Existing commands — JSON output for prime, complete, teardown"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
plan: IP-108
delta: DE-108
---

# Phase 02 — Existing commands: JSON output for prime, complete, teardown

## 1. Objective

Add `--format json` to the three existing review commands. Each command produces a correct JSON envelope on success and error, with appropriate exit codes. Human-readable output is unchanged when `--format` is absent.

## 2. Links & References

- **Delta**: [DE-108](../DE-108.md)
- **Design Revision Sections**: DR-108 §6.1 (prime), §6.2 (complete), §6.3 (teardown), §5 (envelope rules)
- **Design Decisions**: DEC-108-002 (full SHA), DEC-108-006 (action enum), DEC-108-009 (--format uniformly), DEC-108-010 (stderr suppression)
- **Specs / PRODs**: PROD-010, PROD-011
- **File**: `supekku/cli/workflow.py`

## 3. Entrance Criteria

- [ ] Phase 01 complete — exit codes and envelope helpers available in `common.py`

## 4. Exit Criteria / Done When

- [ ] `review prime --format json` produces correct payload (delta_id, action, bootstrap_status, judgment_status, review_round, paths)
- [ ] `review prime` action values correct: `created` / `rebuilt` / `refreshed`
- [ ] `review prime` uses full 40-char SHA in JSON, short SHA in human output
- [ ] `review complete --format json` produces correct payload (round, outcome, previous_state, new_state, findings_path, teardown)
- [ ] `review complete` outcome values: `approved` / `changes_requested`
- [ ] `review teardown --format json` produces correct payload (removed files list)
- [ ] Error cases produce structured error envelopes with correct exit codes (2 for precondition, 3 for guard)
- [ ] JSON mode never writes to stderr
- [ ] Human-readable output unchanged (no `--format` defaults to table/text)
- [ ] Tests in `workflow_review_test.py` extended
- [ ] Lint clean (STD-002)

## 5. Verification

- `pytest supekku/cli/workflow_review_test.py`
- Per command: success JSON, precondition error JSON, guard violation JSON (complete only)
- Stderr capture in JSON mode — must be empty
- Human output regression — existing test assertions still pass

## 6. Assumptions & STOP Conditions

- Assumes `FormatOption` from `common.py` is compatible with Typer command signatures on review commands
- STOP if adding `--format` to existing commands changes their Click/Typer parameter ordering in a breaking way

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 2.1 | Add `FormatOption` param to `review_prime_command` | | |
| [ ] | 2.2 | Implement JSON success branch for prime (action enum, full SHA, bootstrap/judgment status) | | DEC-108-002, DEC-108-006 |
| [ ] | 2.3 | Implement JSON error branches for prime (precondition: no state, invalid state) | | DEC-108-010 pattern |
| [ ] | 2.4 | Add `FormatOption` param to `review_complete_command` | | |
| [ ] | 2.5 | Implement JSON success branch for complete (outcome enum, state transition, teardown) | | |
| [ ] | 2.6 | Implement JSON error branches for complete (precondition + guard violation) | | Exit code 3 for approval guard |
| [ ] | 2.7 | Add `FormatOption` param to `review_teardown_command` | | |
| [ ] | 2.8 | Implement JSON success/error branches for teardown | | |
| [ ] | 2.9 | Tests: JSON envelope validation for all 3 commands | | Success + error paths |
| [ ] | 2.10 | Tests: human output regression | | Existing assertions unchanged |
| [ ] | 2.11 | Tests: stderr silence in JSON mode | | |
| [ ] | 2.12 | Lint check | | STD-002 |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Stderr leakage from Typer/Click internals in JSON mode | DEC-108-010: early format check, all errors routed through envelope | open |
| `--format` conflicts with existing param names | Check Typer signature; review commands currently have no format param | open |

## 9. Decisions & Outcomes

_To be filled during execution._

## 10. Findings / Research Notes

_To be filled during execution._

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to Phase 03
