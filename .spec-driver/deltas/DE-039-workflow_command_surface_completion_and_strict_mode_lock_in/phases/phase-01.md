---
id: IP-039.PHASE-01
slug: 039-workflow_command_surface_completion_and_strict_mode_lock_in-phase-01
name: IP-039 Phase 01
created: '2026-03-04'
updated: '2026-03-04'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-039.PHASE-01
plan: IP-039
delta: DE-039
objective: >-
  Finalize workflow completion command ergonomics for automation and align
  coverage-gate messaging/docs before expanding command surface.
entrance_criteria:
  - DE-039 and DR-039 approved for execution
  - PROD-016 requirements FR-002/FR-009/FR-010 mapped in plan
exit_criteria:
  - Non-interactive completion prompt behavior is deterministic and test-backed
  - Coverage-gate runtime guidance points to canonical active docs
  - Phase evidence recorded and linked in plan coverage entries
verification:
  tests:
    - uv run pytest -q supekku/scripts/complete_delta_test.py supekku/scripts/lib/changes/coverage_check_test.py
  evidence:
    - VT-039-002
tasks:
  - id: 1.1
    title: Validate and lock deterministic non-interactive prompt handling
    status: done
  - id: 1.2
    title: Update coverage-gate runtime documentation pointer and tests
    status: done
  - id: 1.3
    title: Re-run targeted verification and sync DE/IP notes
    status: done
risks:
  - risk: Prompt default changes could silently alter operator expectations.
    mitigation: Document defaults in memory/docs and add explicit tests.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-039.PHASE-01
```

# Phase 01 - Command UX + Messaging

## 1. Objective

Harden `complete delta` for non-interactive use and remove stale runtime guidance
so automation behavior is deterministic and discoverable.

## 2. Links & References

- **Delta**: DE-039
- **Design Revision Sections**:
  - DR-039 §2 Problem & Constraints
  - DR-039 §4 Code Impact Summary
- **Specs / PRODs**:
  - PROD-016.FR-009
  - PROD-016.FR-010
- **Support Docs**:
  - `change/deltas/DE-038-canonical_workflow_alignment/gaps-to-adoption.md`
  - `docs/commands-workflow.md`

## 3. Entrance Criteria

- [x] Delta scoped and linked to target requirements
- [x] Phase sheet created and plan references updated

## 4. Exit Criteria / Done When

- [x] Non-interactive completion path executes without stdin choreography
- [x] Coverage error message references canonical active docs
- [x] Targeted tests pass and evidence is recorded

## 5. Verification

- `uv run pytest -q supekku/scripts/complete_delta_test.py supekku/scripts/lib/changes/coverage_check_test.py`
- `uv run ruff check supekku/scripts/complete_delta.py supekku/scripts/complete_delta_test.py supekku/scripts/lib/changes/coverage_check.py`
- Evidence: VT-039-002 test output + diff references.

## 6. Assumptions & STOP Conditions

- Assumptions: this phase does not yet implement strict-mode runtime branching or new CLI verbs.
- STOP when: lifecycle semantics for revision/audit completion are ambiguous and require product decision.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                     | Parallel? | Notes                       |
| ------ | --- | --------------------------------------------------------------- | --------- | --------------------------- |
| [x]    | 1.1 | Validate and lock deterministic non-interactive prompt handling | [ ]       | `complete_delta.py` + tests |
| [x]    | 1.2 | Update coverage-gate runtime documentation pointer and tests    | [ ]       | `coverage_check.py`         |
| [x]    | 1.3 | Re-run focused verification and record evidence                 | [ ]       | pytest + lint               |

### Task Details

- **1.1 Description**
  - **Design / Approach**: Use TTY-aware prompt defaults with explicit fallback behavior.
  - **Files / Components**: `supekku/scripts/complete_delta.py`, `supekku/scripts/complete_delta_test.py`
  - **Testing**: 4 tests pass — non-interactive default, fallback-to-default, EOF handling, sync skip.
  - **Observations & AI Notes**: `_is_interactive_input_available()` + `non_interactive_default` kwarg pattern prevents headless abort. Sync prompt defaults to skip in non-interactive mode.
  - **Commits / References**: implemented by prior agent; verified passing.

- **1.2 Description**
  - **Design / Approach**: Replace stale `RUN.md` pointer with `docs/commands-workflow.md` in coverage gate error output.
  - **Files / Components**: `supekku/scripts/lib/changes/coverage_check.py:252`, `supekku/scripts/lib/changes/coverage_check_test.py:398`
  - **Testing**: 19 coverage_check tests pass; assertion updated to verify `docs/commands-workflow.md` presence.
  - **Observations & AI Notes**: `.spec-driver/RUN.md` never existed. Closes DE-038 carry-forward item.

- **1.3 Description**
  - **Design / Approach**: Re-run focused verification and update DE/IP/phase evidence notes.
  - **Files / Components**: DE-039 docs + phase sheet.
  - **Testing**: 23 tests pass (combined suite), ruff lint clean on all 4 files.
  - **Evidence**: VT-039-002 — `pytest -q` 23/23 pass; `ruff check` clean.

## 8. Risks & Mitigations

| Risk                                                 | Mitigation                                                   | Status |
| ---------------------------------------------------- | ------------------------------------------------------------ | ------ |
| Headless defaults cause unintended auto-confirmation | Keep sync default false; document completion/update defaults | Open   |

## 9. Decisions & Outcomes

- `2026-03-04` - Added deterministic non-interactive prompt policy to avoid stdin choreography in automation.
- `2026-03-04` - Locked strict-mode policy: universally block force-style bypass paths when `strict_mode=true`.
- `2026-03-04` - Coverage gate doc pointer updated from nonexistent `.spec-driver/RUN.md` to `docs/commands-workflow.md`.

## 10. Findings / Research Notes

- Existing `complete_delta` flow had unguarded `input()` calls causing EOF aborts in non-interactive use.
- `.spec-driver/RUN.md` was never created; the stale pointer was likely a placeholder from early scaffolding.
- Non-interactive default policy: sync=skip(false), completion-confirm=proceed(true), update-requirements=proceed(true).

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase: Phase 2 entrance criteria met (Phase 1 complete). Next: `create audit` and `complete revision` CLI flows per PROD-016.FR-010.
