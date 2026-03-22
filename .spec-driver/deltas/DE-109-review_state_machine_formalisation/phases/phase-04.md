---
id: IP-109-P04
slug: "109-review_state_machine_formalisation-phase-04"
name: "Integration — workflow_metadata derivation, staleness refactor, end-to-end test"
created: "2026-03-22"
updated: "2026-03-22"
status: completed
kind: phase
plan: IP-109
delta: DE-109
---

# Phase 4 — Integration and cleanup

## 1. Objective

Derive `workflow_metadata.py` validation lists from StrEnums (POL-002), refactor `staleness.py` to import from `review_state_machine.py`, write end-to-end multi-round test, ensure `just check` green.

## 2. Links & References

- **Delta**: DE-109
- **Design Revision Sections**: DR-109 §3.2 (bootstrap derivation), §3.7 (cross-round), §5.4 (end-to-end test)
- **Specs / PRODs**: PROD-011
- **Phase 1–3 output**: review_state_machine.py, review_io.py, CLI commands

## 3. Entrance Criteria

- [x] Phase 3 complete — CLI disposition commands, guard enforcement, judgment_status
- [x] Full suite green (4562 passed)

## 4. Exit Criteria / Done When

- [ ] `BOOTSTRAP_STATUS_VALUES` derived from `BootstrapStatus` StrEnum
- [ ] `REVIEW_STATUS_VALUES` derived from `ReviewStatus` StrEnum
- [ ] `FINDING_STATUS_VALUES` derived from `FindingStatus` StrEnum
- [ ] `FINDING_DISPOSITION_ACTION_VALUES` derived from `FindingDispositionAction` StrEnum
- [ ] `DISPOSITION_AUTHORITY_VALUES` derived from `DispositionAuthority` StrEnum
- [ ] `staleness.py` imports `BootstrapStatus` from `review_state_machine` (plain class removed)
- [ ] `staleness_test.py` imports updated
- [ ] VT-109-009: End-to-end test passing (multi-round review with disposition and approval)
- [ ] `just check` green (lint + test)
- [ ] Notes updated

## 5. Verification

- `uv run python -m pytest supekku/scripts/lib/workflow/staleness_test.py -v`
- `uv run python -m pytest supekku/scripts/lib/blocks/workflow_metadata_test.py -v`
- `uv run python -m pytest supekku/cli/workflow_review_test.py -v`
- `uv run ruff check`
- `just check`

## 6. Assumptions & STOP Conditions

- Assumes Phase 1–3 modules are stable
- STOP if StrEnum derivation introduces circular imports (workflow_metadata ← review_state_machine)

## 7. Tasks & Progress

| Status | ID  | Description                                                             | Notes              |
| ------ | --- | ----------------------------------------------------------------------- | ------------------ |
| [ ]    | 4.1 | Derive workflow_metadata.py validation lists from StrEnums              | POL-002            |
| [ ]    | 4.2 | Refactor staleness.py: import BootstrapStatus from review_state_machine | Remove plain class |
| [ ]    | 4.3 | Write VT-109-009 end-to-end test                                        | DR-109 §5.4        |
| [ ]    | 4.4 | Lint + test green                                                       | `just check`       |
| [ ]    | 4.5 | Update notes.md                                                         | Phase 4 log        |

### Task Details

- **4.1 Derive validation lists** — Import StrEnums from `review_state_machine.py`, replace plain lists with `[e.value for e in EnumClass]`. No circular import risk: `workflow_metadata.py` → `review_state_machine.py` is leaf-ward.

- **4.2 Staleness refactor** — Remove `class BootstrapStatus` from `staleness.py`, import `BootstrapStatus` from `review_state_machine`. `evaluate_staleness()` already uses string values so the StrEnum is a drop-in replacement. Update test imports.

- **4.3 End-to-end test** — Per DR-109 §5.4: prime → complete (changes_requested with blocking finding) → resolve finding → re-prime → complete (approved) → success. Tests the full guard pipeline.

## 8. Risks & Mitigations

| Risk                                                        | Mitigation                                                      | Status   |
| ----------------------------------------------------------- | --------------------------------------------------------------- | -------- |
| Circular import in workflow_metadata → review_state_machine | review_state_machine is a leaf module; dependency is safe       | verified |
| staleness.py callers break on StrEnum                       | StrEnum is str subclass; existing string comparisons still work | low risk |
