---
id: IP-109-P03
slug: "109-review_state_machine_formalisation-phase-03"
name: "CLI commands — disposition subcommands, prime/complete updates, guard enforcement"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
plan: IP-109
delta: DE-109
---

# Phase 3 — CLI commands

## 1. Objective

Wire review state machine into CLI: disposition subcommands (`review finding resolve|defer|waive|supersede`), update `review prime` to set judgment via transition, update `review complete` to enforce `can_approve()` guard and write `judgment_status`, wire summary into round metadata.

## 2. Links & References

- **Delta**: DE-109
- **Design Revision Sections**: DR-109 §4.1 (disposition commands), §4.3 (existing command updates), §5.3 (disposition test cases), §5.4 (CLI integration test cases)
- **Specs / PRODs**: PROD-011
- **Phase 1 output**: `review_state_machine.py` — enums, models, guards, transitions
- **Phase 2 output**: `review_io.py` — `update_finding_disposition()`, `find_finding()`, v2 accumulative model

## 3. Entrance Criteria

- [x] Phase 2 complete — accumulative rounds, v2 schema, review_io helpers ready
- [x] `update_finding_disposition()` and `find_finding()` available in review_io.py

## 4. Exit Criteria / Done When

- [x] `review finding resolve` command works with `--resolved-at` option
- [x] `review finding defer` command works with `--rationale` (required) and `--backlog-ref`
- [x] `review finding waive` command works with `--rationale` (required) and `--authority`
- [x] `review finding supersede` command works with `--superseded-by` (required)
- [x] Finding not found → clear error with available IDs
- [x] `review prime` sets `judgment_status: in_progress` via `apply_review_transition()`
- [x] `review complete --status approved` enforces `can_approve()` guard
- [x] `review complete` writes `judgment_status` to review-index
- [x] `review complete --summary` wires summary into round metadata
- [x] VT-109-005: CLI guard enforcement tests passing
- [x] VT-109-008: Disposition command tests passing
- [x] Lint clean on all touched files

## 5. Verification

- `uv run python -m pytest supekku/cli/workflow_review_test.py -v`
- `uv run ruff check supekku/cli/workflow.py`
- `just pylint-files supekku/cli/workflow.py`

## 6. Assumptions & STOP Conditions

- Assumes `review_state_machine.py` functions are stable (Phase 1 complete, 59 tests)
- Assumes `review_io.py` v2 API is stable (Phase 2 complete)
- STOP if `workflow.py` exceeds 150-line skinny CLI guidance for review section — extract helper module

## 7. Tasks & Progress

| Status | ID  | Description                                                           | Parallel? | Notes                  |
| ------ | --- | --------------------------------------------------------------------- | --------- | ---------------------- |
| [x]    | 3.1 | Add `review finding` subcommand group with 4 disposition commands     |           | DR-109 §4.1            |
| [x]    | 3.2 | Update `review prime` to set judgment via `apply_review_transition()` | [P]       | DR-109 §4.3            |
| [x]    | 3.3 | Update `review complete` to enforce `can_approve()` guard             |           | DR-109 §4.3            |
| [x]    | 3.4 | Update `review complete` to write `judgment_status` to review-index   |           | DR-109 §4.3            |
| [x]    | 3.5 | Wire `--summary` into round metadata                                  |           | Loose end from Phase 2 |
| [x]    | 3.6 | Write disposition command tests (VT-109-008)                          |           | DR-109 §5.3            |
| [x]    | 3.7 | Write CLI guard enforcement tests (VT-109-005)                        |           | DR-109 §5.4            |
| [x]    | 3.8 | Lint clean                                                            |           | ruff + pylint          |

### Task Details

- **3.1 Disposition commands** — 4 subcommands under `review finding`. Each: read findings → validate constraints → `update_finding_disposition()` → write. Finding not found → error listing available IDs. Thin CLI: all logic in review_io + review_state_machine.

- **3.2 Prime judgment** — After building review-index, apply `ReviewTransitionCommand.BEGIN_REVIEW` via `apply_review_transition()`. Set `judgment_status` in the index data.

- **3.3 Guard enforcement** — When status is `approved`, call `can_approve(collect_blocking_findings(rounds))`. If guard fails, print reasons and exit non-zero.

- **3.4 Judgment status write** — After guard passes, write `judgment_status` to review-index (read → update → write).

- **3.5 Summary** — Pass `--summary` value through to `build_round_entry()` / `append_round()` as round-level metadata.

- **3.6-3.7 Tests** — Red/green TDD. Cover all disposition commands, constraint validation, guard enforcement on approve, judgment status write-through.

## 8. Risks & Mitigations

| Risk                                                   | Mitigation                                                                                      | Status  |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | ------- |
| workflow.py review section grows too large             | Extract disposition commands to separate module if needed                                       | monitor |
| summary parameter threading requires review_io changes | build_round_entry already accepts arbitrary kwargs via session; may need explicit summary field | check   |
