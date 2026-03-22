---
id: IP-108-P03
slug: "108-review_cli_contract_for_structured_machine_consumption-phase-03"
name: "New commands — status, finding subgroup, IO helpers"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
plan: IP-108
delta: DE-108
---

# Phase 03 — New commands: status, finding subgroup, IO helpers

## 1. Objective

Implement `review status`, `review finding add`, `review finding dispose`, `review finding list`, and the supporting finding-level IO helpers in `review_io.py`. All commands support both human and JSON output modes.

## 2. Links & References

- **Delta**: [DE-108](../DE-108.md)
- **Design Revision Sections**: DR-108 §6.4 (status), §6.5 (finding subgroup), §7 (code impact for review_io.py)
- **Design Decisions**: DEC-108-003 (finding subgroup), DEC-108-004 (IO helpers), DEC-108-005 (--round filter), DEC-108-011 (ID assignment), DEC-108-012 (not-found error)
- **Specs / PRODs**: PROD-010, PROD-011
- **Files**: `supekku/cli/workflow.py`, `supekku/scripts/lib/workflow/review_io.py`

## 3. Entrance Criteria

- [ ] Phase 02 complete — existing commands have JSON output, envelope pattern established

## 4. Exit Criteria / Done When

- [ ] `review status` returns bootstrap_status, judgment_status, workflow_status, active_role, round, findings_summary, staleness inputs
- [ ] `review status --format json` produces correct envelope
- [ ] `review status` with no review state returns cold/not_started gracefully
- [ ] `add_finding_to_round()` in review_io.py: appends finding, assigns ID (R{round}-{seq}), handles cold start (no findings file)
- [ ] `dispose_finding()` in review_io.py: updates disposition, derives status per DR-109, enforces authority/rationale constraints
- [ ] `review finding add` creates finding with server-assigned ID, round, created_at
- [ ] `review finding dispose` updates finding, returns previous/new status
- [ ] `review finding dispose` with non-existent finding ID → EXIT_PRECONDITION (2)
- [ ] `review finding list` returns all findings across all rounds by default
- [ ] `review finding list --round N` filters to single round
- [ ] Each finding in list output carries its `round` number
- [ ] All new commands support `--format json` with correct envelope
- [ ] Tests in `workflow_review_test.py` and `review_io_test.py` extended
- [ ] Lint clean (STD-002)

## 5. Verification

- `pytest supekku/cli/workflow_review_test.py`
- `pytest supekku/scripts/lib/workflow/review_io_test.py`
- Per command: JSON success, JSON error, human output
- IO helpers: cold start, ID assignment sequence, dispose constraints, atomic write
- Finding list: multi-round accumulation, --round filter
- Finding dispose: each disposition action (fix/defer/waive/supersede) with correct status derivation

## 6. Assumptions & STOP Conditions

- Assumes `review_state_machine.py` enums/models are stable (DR-109 already implemented)
- Assumes `review-findings.yaml` schema supports per-finding metadata (id, round, created_at) — verify against `REVIEW_FINDINGS_METADATA`
- STOP if findings schema needs extension (would require workflow_metadata.py changes → possible DE-109 coordination)

## 7. Tasks & Progress

### IO helpers (review_io.py)

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.1 | Implement `add_finding_to_round()` — append finding, assign R{round}-{seq} ID, cold start handling | | DEC-108-011 |
| [ ] | 3.2 | Implement `dispose_finding()` — find by ID, update disposition, derive status | | DEC-108-004 |
| [ ] | 3.3 | Unit tests for 3.1–3.2 | | Cold start, ID seq, dispose constraints, not-found |

### review status command

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.4 | Implement `review_status_command` — read state + index + findings, derive bootstrap/judgment/summary/staleness | [P] | Independent of 3.6–3.9 |
| [ ] | 3.5 | Tests for review status (JSON + human, with/without review state) | [P] | |

### review finding subgroup

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.6 | Register `finding` Typer subgroup under `review_app` | | DEC-108-003 |
| [ ] | 3.7 | Implement `review finding add` command | | Uses 3.1 |
| [ ] | 3.8 | Implement `review finding dispose` command | | Uses 3.2, DEC-108-012 |
| [ ] | 3.9 | Implement `review finding list` command (--round N optional) | | DEC-108-005 |
| [ ] | 3.10 | Tests for finding add/dispose/list (JSON + human, error paths) | | |

### Wrap-up

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.11 | Lint check | | STD-002 |
| [ ] | 3.12 | Full test suite pass | | All phases |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Findings schema may not support per-finding created_at | Check REVIEW_FINDINGS_METADATA early; extend if needed | open |
| Finding subgroup nesting (review → finding → add) may hit Typer depth limits | Typer supports nested subgroups; verify with smoke test | open |
| Read-modify-write race on review-findings.yaml | Atomic write already in review_io.py; single-process CLI, no concurrency concern | mitigated |

## 9. Decisions & Outcomes

_To be filled during execution._

## 10. Findings / Research Notes

_To be filled during execution._

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] All review commands functional in JSON + human mode
- [ ] Delta/Plan updated with outcomes
