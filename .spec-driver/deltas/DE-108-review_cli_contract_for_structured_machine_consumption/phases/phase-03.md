---
id: IP-108-P03
slug: "108-review_cli_contract_for_structured_machine_consumption-phase-03"
name: "New commands + finding disposition JSON"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
plan: IP-108
delta: DE-108
---

# Phase 03 — New commands + finding disposition JSON

## 1. Objective

Add `--format json` to `workflow status` and the 4 existing `review finding` disposition commands. Add new `review finding list` command. All commands support both human and JSON output modes with correct envelope and exit codes.

## 2. Links & References

- **Delta**: [DE-108](../DE-108.md)
- **Design Revision Sections**: DR-108 §6.4 (status), §6.5 (finding subgroup)
- **Design Decisions**: DEC-108-003 (existing finding commands), DEC-108-004 (existing IO helpers), DEC-108-005 (--round filter), DEC-108-012 (not-found error)
- **Specs / PRODs**: PROD-010, PROD-011
- **Files**: `supekku/cli/workflow.py`

## 3. Entrance Criteria

- [ ] Phase 02 complete — existing review commands have JSON output, envelope pattern established

## 4. Exit Criteria / Done When

- [ ] `workflow status --format json` returns bootstrap_status, judgment_status, workflow_status, active_role, round, findings_summary, staleness inputs
- [ ] `workflow status` with no review state returns cold/not_started gracefully
- [ ] `review finding resolve/defer/waive/supersede --format json` produce correct envelope via shared `_disposition_finding()`
- [ ] Finding disposition not-found yields EXIT_PRECONDITION (2) with structured error
- [ ] `review finding list` returns all findings across all rounds by default
- [ ] `review finding list --round N` filters to single round
- [ ] Each finding in list output carries round number and severity category
- [ ] All commands support `--format json` with correct envelope
- [ ] Tests in `workflow_review_test.py` extended
- [ ] Lint clean (STD-002)

## 5. Verification

- `pytest supekku/cli/workflow_review_test.py`
- Per command: JSON success, JSON error, human output
- Workflow status: with/without review-index, with/without findings
- Finding list: multi-round accumulation, --round filter, empty findings
- Finding disposition JSON: each action type, not-found error

## 6. Assumptions & STOP Conditions

- Assumes `_disposition_finding()` can be extended for JSON without breaking existing callers
- STOP if findings schema doesn't carry enough info for the list view

## 7. Tasks & Progress

### workflow status JSON

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.1 | Add `FormatOption` to `workflow_status` command | [P] | Independent of 3.4-3.7 |
| [ ] | 3.2 | JSON branch: read review-index + findings, derive bootstrap/judgment/summary/staleness | [P] | |
| [ ] | 3.3 | Tests for workflow status JSON (with/without review state) | [P] | |

### review finding disposition JSON

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.4 | Add `format` param to `_disposition_finding()` shared orchestration | | Affects all 4 commands |
| [ ] | 3.5 | JSON success/error branches in `_disposition_finding()` | | Not-found → EXIT_PRECONDITION |
| [ ] | 3.6 | Tests for disposition JSON (each action type, not-found) | | |

### review finding list (new)

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.7 | Implement `review finding list` command | | DEC-108-005 |
| [ ] | 3.8 | `--round N` optional filter | | |
| [ ] | 3.9 | Tests for finding list (multi-round, --round filter, empty, JSON + human) | | |

### Wrap-up

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.10 | Lint check | | STD-002 |
| [ ] | 3.11 | Full test suite pass | | All phases |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| `_disposition_finding()` format param may need threading through all 4 callers | Single shared function — one change point | open |
| Typer nested subgroup depth (review → finding → list) | Already works for resolve/defer/waive/supersede | mitigated |

## 9. Decisions & Outcomes

_To be filled during execution._

## 10. Findings / Research Notes

_To be filled during execution._

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] All review commands functional in JSON + human mode
- [ ] Delta/Plan updated with outcomes
