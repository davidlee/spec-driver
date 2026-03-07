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
  verify repo-level lint output remains authoritative and more useful, including
  a compact reporting workflow for touched files and full-repo runs.
entrance_criteria:
- Delta and DR reviewed
- Existing pylint configuration inspected
exit_criteria:
- STD-002 authored with concrete guidance
- Recursive test-file ignore patterns updated in pyproject.toml
- Repo-level pylint verification captured
- Compact summary targets implemented and validated
verification:
  tests:
  - just pylint
  evidence:
  - VA-DE-058-001
  - VA-DE-058-002
  - VA-DE-058-003
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
- id: '1.4'
  title: Implement compact pylint summary workflow
  status: done
- id: '1.5'
  title: Validate full-report and touched-file targets
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
test-ignore configuration, and add compact pylint report workflows that keep
repo-level verification authoritative without forcing agents to read the full
raw stream every time.

## 2. Links & References
- **Delta**: DE-058
- **Design Revision Sections**: DR-058 sections 2-7
- **Specs / PRODs**: PROD-003.NF-001
- **Support Docs**: `pyproject.toml`, `STD-002`
- **Support Docs**: `pyproject.toml`, `STD-002`, `Justfile`

## 3. Entrance Criteria
- [x] Delta created and moved to in-progress
- [x] Existing pylint configuration inspected
- [x] Plugin behavior reviewed to confirm recursive glob requirement

## 4. Exit Criteria / Done When
- [x] STD-002 states lint prioritization and anti-rationalization posture
- [x] Test-file per-file ignores use recursive patterns
- [x] Repo-level pylint verification captured
- [x] Compact summary targets implemented and validated

## 5. Verification
- Run `just pylint`
- Run `just pylint-report`
- Run `just pylint-files ...`
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
| [x] | 1.4 | Implement compact pylint summary workflow | [ ] | Added helper, thin script, and Justfile targets |
| [x] | 1.5 | Validate summary targets | [ ] | `just pylint-report` and `just pylint-files ...` both verified |

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
- **1.4 Description**
  - **Design / Approach**: Keep the Justfile thin by putting parsing/rendering
    logic in a pure helper and leaving the wrapper script as orchestration.
  - **Files / Components**: `Justfile`, `supekku/scripts/pylint_report.py`,
    `supekku/scripts/lib/core/pylint_report.py`
- **1.5 Description**
  - **Design / Approach**: Validate both full-repo and touched-file workflows,
    including persisted json artifacts.
  - **Files / Components**: `.spec-driver/run/pylint/`
  - **Observations & AI Notes**: `just pylint-report` prints score, counts,
    top files, and first high-severity messages while writing full json to
    `.spec-driver/run/pylint/full.json`. `just pylint-files ...` gives the same
    compact view for touched files and caught a warning in the new test file
    before final verification.

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
- `2026-03-07` - Use persisted json plus compact summaries for pylint reporting
  instead of relying on raw streamed output or score-only reading.

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
