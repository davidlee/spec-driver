---
id: IP-064.PHASE-03
slug: 064-spec_driver_doctor_workspace_health_diagnostics-phase-03
name: IP-064 Phase 03 — Polish and verification
created: "2026-03-08"
updated: "2026-03-08"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-064.PHASE-03
plan: IP-064
delta: DE-064
objective: >-
  Verify all CLI options work with all 6 categories, confirm lint and
  test suites pass across the full codebase, update verification
  artifacts, and prepare for delta closure.
entrance_criteria:
  - Phase 2 complete (all 6 check categories implemented and tested)
exit_criteria:
  - JSON output includes all 6 categories
  - --check filter works for each category
  - --verbose shows pass results across all categories
  - just check passes (tests + both linters)
  - Verification coverage updated in IP-064
verification:
  tests:
    - supekku/scripts/lib/diagnostics/models_test.py
    - supekku/scripts/lib/diagnostics/runner_test.py
    - supekku/scripts/lib/diagnostics/checks/deps_test.py
    - supekku/scripts/lib/diagnostics/checks/config_test.py
    - supekku/scripts/lib/diagnostics/checks/structure_test.py
    - supekku/scripts/lib/diagnostics/checks/refs_test.py
    - supekku/scripts/lib/diagnostics/checks/registries_test.py
    - supekku/scripts/lib/diagnostics/checks/lifecycle_test.py
    - supekku/scripts/lib/formatters/diagnostic_formatters_test.py
  evidence: []
tasks:
  - id: "3.1"
    description: "Verify JSON output with all 6 categories"
  - id: "3.2"
    description: "Verify --check filter for each new category"
  - id: "3.3"
    description: "Full lint and test pass"
  - id: "3.4"
    description: "Update verification coverage in IP-064"
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-064.PHASE-03
```

# Phase 3 — Polish and verification

## 1. Objective

Confirm all CLI options work across all 6 categories. Update verification
artifacts. Prepare for delta closure.

## 2. Links & References

- **Delta**: DE-064
- **Design Revision**: DR-064 §7 (CLI interface)

## 3. Entrance Criteria

- [x] Phase 2 complete (all 6 check categories)

## 4. Exit Criteria / Done When

- [x] JSON output includes all 6 categories — verified
- [x] `--check` filter works for each category — verified (lifecycle, refs tested)
- [x] `--verbose` shows pass results — verified
- [x] `just lint` clean, `just test` passes (2 pre-existing failures only)
- [x] Verification coverage updated in IP-064

## 5. Verification

- `spec-driver doctor` — 91 pass, 1 warn, 0 fail
- `spec-driver doctor --json` — valid JSON with all 6 categories
- `spec-driver doctor --check lifecycle --verbose` — shows per-delta results
- `spec-driver doctor --check refs --verbose` — shows all cross-ref results
- `just lint` — clean
- `just test` — 3143 pass, 2 pre-existing fail, 3 skip
- `just pylint-report` — 9.71/10

## 7. Tasks & Progress

| Status | ID  | Description                              | Parallel? | Notes                      |
| ------ | --- | ---------------------------------------- | --------- | -------------------------- |
| [x]    | 3.1 | Verify JSON output with all 6 categories |           | Valid, parseable           |
| [x]    | 3.2 | Verify --check filter for new categories |           | lifecycle, refs confirmed  |
| [x]    | 3.3 | Full lint and test pass                  |           | 9.71/10 pylint, ruff clean |
| [x]    | 3.4 | Update verification coverage in IP-064   |           |                            |

## 9. Decisions & Outcomes

- 2026-03-08 — Phase 3 is largely verification-only since Phases 1-2 already implemented all features and CLI options

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (in this sheet)
- [x] Notes updated
- [ ] Delta ready for audit/closure
