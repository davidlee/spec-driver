---
id: IP-064.PHASE-01
slug: "064-spec_driver_doctor_workspace_health_diagnostics-phase-01"
name: "IP-064 Phase 01 — Model, runner, first checks, CLI wiring"
created: "2026-03-08"
updated: "2026-03-08"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-064.PHASE-01
plan: IP-064
delta: DE-064
objective: >-
  Establish the diagnostics package with core model, runner, two check
  categories (deps, structure), text formatter, and CLI wiring so that
  `spec-driver workspace doctor` produces working output end-to-end.
entrance_criteria:
  - DR-064 approved
  - Existing code reviewed (validator.py, workspace.py, npm_utils.py, paths.py)
exit_criteria:
  - DiagnosticResult and CategorySummary model with tests
  - Runner orchestrates checks, filters by --check
  - deps and structure checks implemented with tests
  - Text formatter produces human-readable output
  - `workspace doctor` CLI command wired and producing output
  - `just check` passes (tests + both linters)
verification:
  tests:
    - tests/diagnostics/test_models.py
    - tests/diagnostics/test_runner.py
    - tests/diagnostics/test_checks_deps.py
    - tests/diagnostics/test_checks_structure.py
    - tests/formatters/test_diagnostic_formatters.py
    - tests/cli/test_workspace_doctor.py
  evidence: []
tasks:
  - id: "1.1"
    description: Create diagnostics/models.py with DiagnosticResult and CategorySummary
  - id: "1.2"
    description: Create diagnostics/runner.py with run_checks orchestrator
  - id: "1.3"
    description: Create diagnostics/checks/ with deps.py and structure.py
  - id: "1.4"
    description: Create formatters/diagnostic_formatters.py for text output
  - id: "1.5"
    description: Wire workspace doctor CLI command
  - id: "1.6"
    description: Lint and test pass
risks:
  - risk: Test directory structure for diagnostics may not exist
    mitigation: Create tests/diagnostics/ with __init__.py
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-064.PHASE-01
```

# Phase 1 — Model, runner, first checks, CLI wiring

## 1. Objective

Stand up the full vertical slice: model → checks → runner → formatter → CLI.
Two categories (deps, structure) prove the pattern works end-to-end. Remaining
categories follow in Phase 2.

## 2. Links & References

- **Delta**: DE-064
- **Design Revision**: DR-064 §4 (code impact), §5 (data model), §6 (check implementations), §8 (package structure)
- **Existing code**:
  - `supekku/scripts/lib/core/paths.py` — directory helpers for structure checks
  - `supekku/scripts/lib/core/npm_utils.py` — ts-doc-extract/node detection for deps checks
  - `supekku/cli/workspace.py` — where `doctor` command will live
  - `supekku/scripts/lib/formatters/` — formatter conventions

## 3. Entrance Criteria

- [x] DR-064 authored and approved
- [x] Existing code reviewed during preflight

## 4. Exit Criteria / Done When

- [ ] `DiagnosticResult` and `CategorySummary` dataclasses with severity aggregation tested
- [ ] `run_checks(ws)` returns `list[CategorySummary]`, supports `categories` filter
- [ ] `check_deps(ws)` tests python, git, node, ts-doc-extract — pass and fail paths tested
- [ ] `check_structure(ws)` tests directory presence, orphan detection — pass and fail paths tested
- [ ] `format_doctor_text()` renders categorised output with ✓/⚠/✗ and summary line
- [ ] `workspace doctor` produces text output with correct exit codes (0/1/2)
- [ ] `just check` passes

## 5. Verification

- `just test` — all new test files pass
- `just lint` — zero warnings on new files
- `just pylint-files` on all new/modified files
- Manual: `uv run spec-driver workspace doctor` runs in this workspace

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `Workspace` class provides sufficient accessors (root, config)
  - Python version detectable via `sys.version_info`
  - `shutil.which` sufficient for binary detection
- STOP when: Workspace class needs changes beyond current public API

## 7. Tasks & Progress

| Status | ID   | Description                                                                     | Parallel? | Notes                               |
| ------ | ---- | ------------------------------------------------------------------------------- | --------- | ----------------------------------- |
| [x]    | 1.1  | Model: DiagnosticResult, CategorySummary, severity helpers                      |           | 14 tests                            |
| [x]    | 1.2  | Runner: run_checks orchestrator with CHECK_REGISTRY                             |           | 8 tests                             |
| [x]    | 1.3a | Check: deps (python, git, go, gomarkdoc, zig, zigmarkdoc, node, ts-doc-extract) | [P]       | 11 tests; expanded per user request |
| [x]    | 1.3b | Check: structure (directories, orphan bundles)                                  | [P]       | 8 tests                             |
| [x]    | 1.3c | Check: config (workflow.toml, CLAUDE.md, skills allowlist, skills exposure)     | [P]       | 8 tests; pulled forward from P2     |
| [x]    | 1.4  | Formatter: format_doctor_text, format_doctor_json                               |           | 13 tests; both fully implemented    |
| [x]    | 1.5  | CLI: wire top-level `doctor` command                                            |           | --check, --json, --verbose, --root  |
| [x]    | 1.6  | Lint + test pass                                                                |           | 3120 pass, 2 pre-existing fail      |

### Task Details

- **1.1 Model**
  - **Files**: `supekku/scripts/lib/diagnostics/__init__.py`, `models.py`
  - **Testing**: `tests/diagnostics/test_models.py`
  - Test severity aggregation: all-pass, mixed, all-fail
  - Test frozen dataclass behaviour

- **1.2 Runner**
  - **Files**: `supekku/scripts/lib/diagnostics/runner.py`
  - **Testing**: `tests/diagnostics/test_runner.py`
  - `run_checks(ws, categories=None)` iterates CHECK_REGISTRY
  - `categories` param filters to subset
  - Each check fn: `(Workspace) -> list[DiagnosticResult]`
  - Runner wraps results into `CategorySummary`

- **1.3a Deps check**
  - **Files**: `supekku/scripts/lib/diagnostics/checks/__init__.py`, `deps.py`
  - **Testing**: `tests/diagnostics/test_checks_deps.py`
  - Mock `shutil.which`, `sys.version_info`, `npm_utils` for isolation

- **1.3b Structure check**
  - **Files**: `supekku/scripts/lib/diagnostics/checks/structure.py`
  - **Testing**: `tests/diagnostics/test_checks_structure.py`
  - Use `tmp_path` fixtures with minimal directory trees

- **1.4 Formatter**
  - **Files**: `supekku/scripts/lib/formatters/diagnostic_formatters.py`
  - **Testing**: `tests/formatters/test_diagnostic_formatters.py`
  - Pure function: `format_doctor_text(summaries, verbose=False) -> str`
  - Stub: `format_doctor_json(summaries) -> str` (full impl in Phase 3)

- **1.5 CLI wiring**
  - **Files**: `supekku/cli/workspace.py`
  - **Testing**: `tests/cli/test_workspace_doctor.py`
  - Add `doctor` command to workspace app
  - Options: `--check`, `--json`, `--verbose`, `--root`
  - Exit code logic: map worst status to 0/1/2

- **1.6 Lint + test**
  - `just check` green
  - `just pylint-files` on all new/modified files

## 8. Risks & Mitigations

| Risk                                | Mitigation                                                | Status |
| ----------------------------------- | --------------------------------------------------------- | ------ |
| Test isolation for binary detection | Mock `shutil.which` and npm_utils                         | Open   |
| Orphan bundle detection edge cases  | Start simple (dir without matching .md), extend if needed | Open   |

## 9. Decisions & Outcomes

- 2026-03-08 — Phase 1 covers deps + structure only; remaining 4 categories in Phase 2

## 10. Findings / Research Notes

- See preflight notes in conversation

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Phase sheet updated with outcomes
- [ ] Hand-off notes to Phase 2
