---
id: IP-064.PHASE-02
slug: 064-spec_driver_doctor_workspace_health_diagnostics-phase-02
name: IP-064 Phase 02 — Remaining checks (refs, registries, lifecycle)
created: '2026-03-08'
updated: '2026-03-08'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-064.PHASE-02
plan: IP-064
delta: DE-064
objective: >-
  Implement the remaining 3 check categories (refs, registries, lifecycle),
  register them in CHECK_REGISTRY, and write comprehensive tests so that
  all 6 doctor categories produce results.
entrance_criteria:
  - Phase 1 complete (model, runner, deps/config/structure checks working)
  - DR-064 §6 reviewed for check specifications
exit_criteria:
  - check_refs delegates to WorkspaceValidator and translates results correctly
  - check_registries loads all registries and reports load errors
  - check_lifecycle detects stale in-progress deltas with configurable threshold
  - All 3 checks registered in CHECK_REGISTRY
  - Tests for all 3 checks (pass and fail paths)
  - just check passes (tests + both linters)
verification:
  tests:
    - tests/diagnostics/test_checks_refs.py
    - tests/diagnostics/test_checks_registries.py
    - tests/diagnostics/test_checks_lifecycle.py
  evidence: []
tasks:
  - id: "2.1"
    description: "Implement check_refs — delegate to validate_workspace, translate ValidationIssue"
  - id: "2.2"
    description: "Implement check_registries — load all registries, catch exceptions"
  - id: "2.3"
    description: "Implement check_lifecycle — stale in-progress deltas, configurable threshold"
  - id: "2.4"
    description: "Register all 3 checks in CHECK_REGISTRY"
  - id: "2.5"
    description: "Lint and test pass"
risks:
  - risk: WorkspaceValidator may raise on broken workspaces instead of returning issues
    mitigation: Wrap in try/except, translate exception to fail result
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-064.PHASE-02
```

# Phase 2 — Remaining checks (refs, registries, lifecycle)

## 1. Objective

Implement the final 3 check categories so `spec-driver doctor` covers all 6
categories defined in DR-064. Each check follows the established pattern from
Phase 1: pure function `(Workspace) -> list[DiagnosticResult]`.

## 2. Links & References
- **Delta**: DE-064
- **Design Revision**: DR-064 §6 (check implementations), §5 (validator bridge)
- **Existing code**:
  - `supekku/scripts/lib/validation/validator.py` — `validate_workspace()`, `ValidationIssue`
  - `supekku/scripts/lib/workspace.py` — registry accessors
  - `supekku/scripts/lib/core/config.py` — `load_workflow_config()`
  - `supekku/scripts/lib/diagnostics/checks/__init__.py` — CHECK_REGISTRY

## 3. Entrance Criteria
- [x] Phase 1 complete (deps, config, structure checks working)
- [x] DR-064 §6 reviewed during preflight
- [x] validator.py and workspace.py APIs confirmed

## 4. Exit Criteria / Done When
- [x] `check_refs(ws)` delegates to `validate_workspace()`, translates error→fail, warning→warn, info→pass
- [x] `check_registries(ws)` loads specs, deltas, revisions, audits, decisions without error
- [x] `check_lifecycle(ws)` detects in-progress deltas older than N days (default 5, from config)
- [x] All 3 registered in CHECK_REGISTRY (total: 6 categories)
- [x] Tests written and passing for all 3 checks (23 new tests)
- [x] `just lint` passes; `just test` passes (2 pre-existing failures only)

## 5. Verification
- `just test` — new test files pass
- `just lint` — zero warnings on new files
- `just pylint-files` on all new/modified files

## 6. Assumptions & STOP Conditions
- Assumptions:
  - `validate_workspace()` returns issues rather than raising on broken refs
  - Registry `.collect()` raises on parse errors (the value we're testing)
  - `ChangeArtifact.updated` is an ISO date string parseable with `date.fromisoformat()`
  - `load_workflow_config()` returns deep-merged dict; `config.get("doctor", {})` safe
- STOP when: validator or registry API behaves unexpectedly

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | check_refs: delegate to validate_workspace | [P] | 7 tests |
| [x] | 2.2 | check_registries: load all registries, catch errors | [P] | 6 tests |
| [x] | 2.3 | check_lifecycle: stale in-progress deltas | [P] | 10 tests |
| [x] | 2.4 | Register in CHECK_REGISTRY | | 6 categories total |
| [x] | 2.5 | Lint and test pass | | 3143 pass, 2 pre-existing fail |

### Task Details

- **2.1 check_refs**
  - **Files**: `supekku/scripts/lib/diagnostics/checks/refs.py`
  - **Testing**: `tests/diagnostics/test_checks_refs.py`
  - Call `validate_workspace(ws)`, translate each `ValidationIssue`
  - error→fail, warning→warn, info→pass
  - Use `issue.artifact` as the check `name`

- **2.2 check_registries**
  - **Files**: `supekku/scripts/lib/diagnostics/checks/registries.py`
  - **Testing**: `tests/diagnostics/test_checks_registries.py`
  - Load: ws.specs, ws.delta_registry, ws.revision_registry, ws.audit_registry, ws.decisions
  - Each: try `.collect()`, pass on success, fail on exception
  - Out of scope: silent dedup detection (IMPR-012)

- **2.3 check_lifecycle**
  - **Files**: `supekku/scripts/lib/diagnostics/checks/lifecycle.py`
  - **Testing**: `tests/diagnostics/test_checks_lifecycle.py`
  - Load deltas via `ws.delta_registry.collect()`
  - Filter status == "in-progress", parse `updated` date
  - Compare against today - staleness_days (from `load_workflow_config`)
  - Stale → warn with suggestion to review

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Validator raises instead of returning issues | Wrap in try/except, translate to fail | Open |
| Registry collect() doesn't raise on parse errors | Verify during implementation; adjust if needed | Open |

## 9. Decisions & Outcomes
- 2026-03-08 — Silent ID dedup detection deferred to IMPR-012

## 10. Findings / Research Notes
- See preflight in conversation

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Phase sheet updated with outcomes
- [ ] Hand-off notes to Phase 3
