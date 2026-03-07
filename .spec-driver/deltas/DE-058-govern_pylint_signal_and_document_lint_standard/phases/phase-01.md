---
id: IP-058.PHASE-01
slug: 058-govern_pylint_signal_and_document_lint_standard-phase-01
name: IP-058 Phase 01
created: '2026-03-07'
updated: '2026-03-07'
status: in-progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-058.PHASE-01
plan: IP-058
delta: DE-058
objective: >-
  Author a lint-governance standard, fix recursive pylint test-file ignores, and
  verify repo-level lint output remains authoritative and more useful.
entrance_criteria:
- Delta and DR reviewed
- Existing pylint configuration inspected
exit_criteria:
- STD-002 authored with concrete guidance
- Recursive test-file ignore patterns updated in pyproject.toml
- Repo-level pylint verification captured
verification:
  tests:
  - just pylint
  evidence:
  - VA-DE-058-001
  - VA-DE-058-002
tasks:
- id: '1.1'
  title: Author STD-002 with lint prioritization and anti-rationalization guidance
  status: done
- id: '1.2'
  title: Update pylint per-file ignores to recursive test globs
  status: done
- id: '1.3'
  title: Run repo-level pylint and capture outcome
  status: done
risks:
- Recursive glob matches unintended files outside tests
- Standard wording weakens repo-level lint expectations if phrased imprecisely
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-058.PHASE-01
```

# Phase 1 - Standard and Config Update

## 1. Objective
Publish a default Standard for lint posture, fix the broken recursive
test-ignore configuration, and verify the repo-level pylint run after the
change.

## 2. Links & References
- **Delta**: DE-058
- **Design Revision Sections**: DR-058 sections 2-7
- **Specs / PRODs**: PROD-003.NF-001
- **Support Docs**: `pyproject.toml`, `STD-002`

## 3. Entrance Criteria
- [x] Delta created and moved to in-progress
- [x] Existing pylint configuration inspected
- [x] Plugin behavior reviewed to confirm recursive glob requirement

## 4. Exit Criteria / Done When
- [x] STD-002 states lint prioritization and anti-rationalization posture
- [x] Test-file per-file ignores use recursive patterns
- [x] Repo-level pylint verification captured

## 5. Verification
- Run `just pylint`
- Capture outcome as VA-DE-058-002
- Optionally run targeted pylint sub-runs for diagnosis only; do not treat them
  as the governing gate

## 6. Assumptions & STOP Conditions
- Assumptions:
  - Suppressing test docstring/protected-access warnings is aligned with the
    desired lint posture when test names are already descriptive.
- STOP when:
  - Verification shows the recursive glob catches non-test files or masks
    production-code warnings.

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Author STD-002 with prioritization guidance | [ ] | Standard set to `default` and linked to DE-058 |
| [x] | 1.2 | Patch recursive pylint test-file ignore globs | [ ] | Replace root-only glob with recursive patterns |
| [x] | 1.3 | Run repo-level pylint and capture evidence | [ ] | `just pylint` exited 0; `missing-function-docstring` reduced to 6 |

### Task Details
- **1.1 Description**
  - **Design / Approach**: Encode lint-prioritization guidance in a Standard so
    review posture is explicit rather than conversational.
  - **Files / Components**: `STD-002`
- **1.2 Description**
  - **Design / Approach**: Fix config bug narrowly; do not disable checks
    globally.
  - **Files / Components**: `pyproject.toml`
- **1.3 Description**
  - **Design / Approach**: Use repo-level pylint as the governing signal.
  - **Files / Components**: repo-wide
  - **Observations & AI Notes**: `just pylint` exited successfully after the config change. `missing-function-docstring` now reports 6 occurrences, all in non-test TUI modules. `just lint` also passed.

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Recursive glob matches non-test files | Restrict to `*_test.py` and `test_*.py` naming patterns | active |
| Standard language becomes an excuse to ignore low-priority warnings indefinitely | Keep repo-level lint gate language explicit | active |

## 9. Decisions & Outcomes
- `2026-03-07` - Treat repo-level lint verification as authoritative; use
  file-local pylint only for diagnosis.
- `2026-03-07` - Reduce docstring noise by fixing broken test-file ignores
  rather than disabling docstring checks for production code.

## 10. Findings / Research Notes
- The installed `pylint-per-file-ignores` plugin expands patterns with
  `glob.glob(..., recursive=True)`, so non-recursive `*_test.py` only matches
  repo-root files.
- The repo contains both `*_test.py` and `test_*.py` naming conventions.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase (if any)
