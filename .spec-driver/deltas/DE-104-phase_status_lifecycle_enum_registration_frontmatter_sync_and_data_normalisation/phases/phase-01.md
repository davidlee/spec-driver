---
id: IP-104.PHASE-01
slug: "104-phase_status_lifecycle_enum_registration_frontmatter_sync_and_data_normalisation-phase-01"
name: IP-104 Phase 01
created: "2026-03-21"
updated: "2026-03-21"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-104.PHASE-01
plan: IP-104
delta: DE-104
objective: >-
  Register phase.status enum, extend canonical status map, make phase start and
  phase complete update frontmatter before state.yaml, fix idempotency guard,
  use STATUS_DRAFT constant in create_phase.
entrance_criteria:
  - DR-104 approved with review findings integrated
exit_criteria:
  - phase.status in ENUM_REGISTRY with values matching _change_statuses()
  - CANONICAL_STATUS_MAP extended with done, active, in_progress variants
  - phase start updates frontmatter to in-progress before state.yaml
  - phase complete updates frontmatter to completed before state.yaml
  - Idempotency guard handles both STATUS_COMPLETED and STATUS_COMPLETE
  - create_phase uses STATUS_DRAFT constant
  - All new and modified tests pass
  - Lint clean
verification:
  tests:
    - uv run pytest supekku/scripts/lib/core/enums_test.py -x
    - uv run pytest supekku/cli/workflow_phase_complete_test.py -x
    - uv run pytest supekku/cli/workflow_test.py -x
  evidence: []
tasks:
  - "1.1 Register phase.status in ENUM_REGISTRY"
  - "1.2 Extend CANONICAL_STATUS_MAP"
  - "1.3 phase_start frontmatter update"
  - "1.4 phase_complete frontmatter update + idempotency fix"
  - "1.5 create_phase STATUS_DRAFT constant"
  - "1.6 Tests"
risks:
  - "update_frontmatter_status returns False on files without status field — acceptable silent no-op"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-104.PHASE-01
entrance_criteria:
  - item: "DR-104 approved with review findings integrated"
    completed: true
exit_criteria:
  - item: "phase.status in ENUM_REGISTRY"
    completed: false
  - item: "CANONICAL_STATUS_MAP extended with observed variants"
    completed: false
  - item: "phase start updates frontmatter to in-progress before state.yaml"
    completed: false
  - item: "phase complete updates frontmatter to completed before state.yaml"
    completed: false
  - item: "Idempotency guard handles both STATUS_COMPLETED and STATUS_COMPLETE"
    completed: false
  - item: "create_phase uses STATUS_DRAFT constant"
    completed: false
  - item: "All new and modified tests pass"
    completed: false
  - item: "Lint clean"
    completed: false
```

# Phase 01 — Enum registration, lifecycle map, CLI frontmatter sync

## 1. Objective

Register `phase.status` in the enum infrastructure, extend the canonical status map with all observed variants, and make `phase start`/`phase complete` update phase sheet frontmatter (normative) before `state.yaml` (transient). Fix the idempotency guard and use constants in `create_phase`.

## 2. Links & References

- **Delta**: [DE-104](../DE-104.md)
- **Design Revision**: [DR-104](../DR-104.md) §4.1, §4.2, §4.5
- **Specs**: SPEC-161, SPEC-116

## 3. Entrance Criteria

- [x] DR-104 approved with review findings R1-R3, C1-C2 integrated

## 4. Exit Criteria / Done When

- [ ] `phase.status` in `ENUM_REGISTRY` returning `[completed, deferred, draft, in-progress, pending]`
- [ ] `CANONICAL_STATUS_MAP` includes `done` → `completed`, `active` → `in-progress`, `in_progress` → `in-progress`
- [ ] `phase start` calls `update_frontmatter_status(phase_path, STATUS_IN_PROGRESS)` before `write_state()`
- [ ] `phase complete` calls `update_frontmatter_status(phase_path, STATUS_COMPLETED)` before `write_state()`
- [ ] `phase complete` writes `STATUS_COMPLETED` to `state.yaml` (not `"complete"`)
- [ ] `phase complete` passes `phase_status=STATUS_COMPLETED` to `build_handoff()`
- [ ] Idempotency guard: `already_complete = phase.get("status") in (STATUS_COMPLETED, STATUS_COMPLETE)`
- [ ] `create_phase()` uses `STATUS_DRAFT` constant
- [ ] All tests pass, lint clean

## 5. Verification

- `uv run pytest supekku/scripts/lib/core/enums_test.py -x`
- `uv run pytest supekku/cli/workflow_phase_complete_test.py -x`
- `uv run pytest supekku/cli/workflow_test.py -x`
- `uv run pylint supekku/scripts/lib/core/enums.py supekku/scripts/lib/changes/lifecycle.py supekku/cli/workflow.py supekku/scripts/lib/changes/creation.py`

## 6. Assumptions & STOP Conditions

- Assumes `update_frontmatter_status()` works on phase files — same format as delta/revision files.
- STOP if `update_frontmatter_status()` fails on canonical phase files (not just the 10 historical ones).

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 1.1 | Register `phase.status` in `ENUM_REGISTRY` | [ ] | |
| [ ] | 1.2 | Extend `CANONICAL_STATUS_MAP` | [P] | Can parallel with 1.1 |
| [ ] | 1.3 | `phase_start` frontmatter update | [ ] | Depends on 1.1 for imports |
| [ ] | 1.4 | `phase_complete` frontmatter + idempotency | [ ] | Depends on 1.1 for imports |
| [ ] | 1.5 | `create_phase` constant | [P] | Independent |
| [ ] | 1.6 | Tests | [ ] | After 1.1–1.5 |

### Task Details

- **1.1 Register `phase.status` in `ENUM_REGISTRY`**
  - **Files**: `supekku/scripts/lib/core/enums.py`
  - **Approach**: Add `"phase.status": _change_statuses` to `ENUM_REGISTRY` dict. One line.
  - **Testing**: Extend `enums_test.py` — assert `get_enum_values("phase.status")` returns expected set.

- **1.2 Extend `CANONICAL_STATUS_MAP`**
  - **Files**: `supekku/scripts/lib/changes/lifecycle.py`
  - **Approach**: Add three entries: `"done": STATUS_COMPLETED`, `"active": STATUS_IN_PROGRESS`, `"in_progress": STATUS_IN_PROGRESS`.
  - **Testing**: Unit test `normalize_status()` with each new variant.

- **1.3 `phase_start` frontmatter update**
  - **Files**: `supekku/cli/workflow.py`
  - **Approach**: Per DR §4.2 sketch — after `_find_plan_and_phase()` discovers `phase_path`, before `write_state()`:
    ```python
    if phase_path:
        abs_phase = repo_root / phase_path
        if abs_phase.exists():
            update_frontmatter_status(abs_phase, STATUS_IN_PROGRESS)
    ```
    Import `STATUS_IN_PROGRESS` from `changes.lifecycle` and `update_frontmatter_status` from `core.frontmatter_writer`.
  - **Testing**: New test in `workflow_test.py` or dedicated file — create a phase file with `status: draft`, run `phase start`, assert frontmatter now says `in-progress`.

- **1.4 `phase_complete` frontmatter + idempotency**
  - **Files**: `supekku/cli/workflow.py`
  - **Approach**: Three changes:
    1. Before `write_state()`, update frontmatter: `update_frontmatter_status(abs_phase, STATUS_COMPLETED)`
    2. Change `state_data["phase"]["status"] = "complete"` → `state_data["phase"]["status"] = STATUS_COMPLETED`
    3. Change `already_complete = phase.get("status") == "complete"` → `already_complete = phase.get("status") in (STATUS_COMPLETED, STATUS_COMPLETE)`
    4. Change `phase_status="complete"` in `build_handoff()` call → `phase_status=STATUS_COMPLETED`
    Import `STATUS_COMPLETED`, `STATUS_COMPLETE` from `changes.lifecycle`.
  - **Testing**: Extend `workflow_phase_complete_test.py` — assert frontmatter `status: completed`; assert state.yaml has `completed`; test idempotency (second call is no-op).

- **1.5 `create_phase` constant**
  - **Files**: `supekku/scripts/lib/changes/creation.py`
  - **Approach**: Replace `"status": "draft"` with `"status": STATUS_DRAFT`. Import from `changes.lifecycle`.
  - **Testing**: Existing creation tests should pass unchanged.

- **1.6 Tests**
  - Run full test suites for affected modules.
  - Lint all modified files.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| `update_frontmatter_status` returns False on 10 historical files | Silent no-op; validate will warn in Phase 02 | Accepted |
| Existing tests assume `"complete"` in state.yaml | Search and update assertions | Open |

## 9. Decisions & Outcomes

- DR-104 review integrated: R1 (idempotency), R2 (write ordering), R3 (phase_start sketch), C1 (deferred exception), C2 (DEC-104-07)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to Phase 02
