---
id: IP-109-P01
slug: "109-review_state_machine_formalisation-phase-01"
name: "Domain model — enums, Pydantic models, state machines, guards"
created: "2026-03-22"
updated: "2026-03-22"
status: in-progress
kind: phase
plan: IP-109
delta: DE-109
---

# Phase 1 — Domain model

## 1. Objective

Create `workflow/review_state_machine.py` as a leaf module containing all review lifecycle enums, Pydantic models, state machine functions, and guard predicates. Full test coverage in `review_state_machine_test.py`.

## 2. Links & References

- **Delta**: DE-109
- **Design Revision Sections**: DR-109 §3.1 (module), §3.2 (bootstrap), §3.3 (judgment), §3.4 (disposition), §3.7 (cross-round collection)
- **Specs / PRODs**: PROD-011
- **Prior Art**: `workflow/state_machine.py` (pattern), `core/frontmatter_metadata/audit.py` (disposition)

## 3. Entrance Criteria

- [x] DR-109 approved (4 passes of adversarial review, all findings resolved)
- [x] IP-109 created with phase breakdown

## 4. Exit Criteria / Done When

- [x] `review_state_machine.py` exists with all enums, models, functions
- [x] VT-109-001: Bootstrap derivation tests passing
- [x] VT-109-002: Judgment transition table tests passing
- [x] VT-109-003: Approval guard + disposition constraint tests passing
- [x] VT-109-006: Status derivation tests passing
- [x] VT-109-007: Cross-round collection tests passing
- [x] `just lint` clean on new files
- [x] No I/O or external dependencies in the module (leaf)

## 5. Verification

- `just test` — new test file `review_state_machine_test.py`
- `just lint` — ruff on new files
- `just pylint-files supekku/scripts/lib/workflow/review_state_machine.py`

## 6. Assumptions & STOP Conditions

- Assumes Pydantic is already a dependency (check `pyproject.toml`)
- STOP if Pydantic is not available — would need to add dependency first
- STOP if `state_machine.py` pattern doesn't translate cleanly to review lifecycle

## 7. Tasks & Progress

| Status | ID  | Description                                                                                                   | Parallel? | Notes                                                                                                   |
| ------ | --- | ------------------------------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------- |
| [x]    | 1.1 | Define StrEnums: BootstrapStatus, ReviewStatus, FindingStatus, FindingDispositionAction, DispositionAuthority | [P]       | DR-109 §3.2-§3.4                                                                                        |
| [x]    | 1.2 | Define Pydantic models: FindingDisposition, ReviewFinding                                                     | [P]       | DR-109 §3.4                                                                                             |
| [x]    | 1.3 | Implement derive_bootstrap_status() with validity matrix                                                      |           | DR-109 §3.2. Extended matrix with idempotent self-transitions (cold→cold, stale→stale, invalid→invalid) |
| [x]    | 1.4 | Implement apply_review_transition() with transition table                                                     |           | DR-109 §3.3                                                                                             |
| [x]    | 1.5 | Implement derive_finding_status()                                                                             |           | DR-109 §3.4                                                                                             |
| [x]    | 1.6 | Implement can_approve() and collect_blocking_findings()                                                       |           | DR-109 §3.3, §3.7. Extracted \_check_disposition() to reduce McCabe complexity                          |
| [x]    | 1.7 | Write exhaustive tests for all of the above                                                                   |           | 59 tests. VT-109-001 through VT-109-003, VT-109-006, VT-109-007                                         |
| [x]    | 1.8 | Lint clean                                                                                                    |           | ruff clean, pylint 9.97/10 (1 too-many-arguments on derive_bootstrap_status — inherent)                 |

### Task Details

- **1.1 StrEnums** — 5 enums, all from DR-109. Follow `WorkflowState(StrEnum)` pattern from `state_machine.py`. Remove `warming` from bootstrap, `blocked` from judgment.

- **1.2 Pydantic models** — `FindingDisposition(BaseModel)` with `ConfigDict(extra="ignore")`. `ReviewFinding(BaseModel)` with optional disposition. Validity constraints as model validators or standalone functions.

- **1.3 Bootstrap derivation** — Pure function taking index dict + context, returning BootstrapStatus. Optional `previous_status` for validity matrix assertion. No I/O.

- **1.4 Judgment transitions** — Transition table as dict, `apply_review_transition()` following `apply_transition()` pattern. `TransitionError` for invalid transitions.

- **1.5 Status derivation** — `derive_finding_status(disposition | None) → FindingStatus`. Mapping: fix→resolved, waive→waived, supersede→superseded, defer→open, None→open.

- **1.6 Guard** — `can_approve(blocking_findings)` checks disposition presence and constraints. `collect_blocking_findings(rounds)` collects from all rounds (IDs are round-scoped, no dedup needed).

- **1.7 Tests** — Red/green TDD. Cover all transitions (valid + invalid), all guard scenarios (including fix-without-resolved_at, defer-without-backlog_ref, waive-by-agent), cross-round collection, status derivation, validity matrix assertions.
