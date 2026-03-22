---
id: IP-123-P01
slug: "123-list_deltas_to_hide_completed_by_default_all_to_show_them-phase-01"
name: IP-123 Phase 01
created: "2026-03-22"
updated: "2026-03-22"
status: completed
kind: phase
plan: IP-123
delta: DE-123
---

# Phase 1 - Implementation & Verification

## 1. Objective

Implement `--all` flag and default filtering for `list deltas`.

## 2. Links & References

- **Delta**: DE-123
- **Design Revision**: [DR-123](../DR-123.md)

## 3. Entrance Criteria

- [x] DR-123 accepted
- [x] IP-123 refined

## 4. Exit Criteria / Done When

- [ ] `list deltas` hides completed deltas by default.
- [ ] `list deltas --all` shows completed deltas.
- [ ] VA-123-01 verification passed.

## 5. Verification

- VA-123-01: Manual CLI verification.

## 7. Tasks & Progress

| Status | ID  | Description                                      | Parallel? | Notes |
| ------ | --- | ------------------------------------------------ | --------- | ----- |
| [x]    | 1.1 | Add `--all` option to `list_deltas` in `list.py` | [ ]       | Done  |
| [x]    | 1.2 | Implement default filtering logic                | [ ]       | Done  |
| [x]    | 1.3 | Update help text and docstrings                  | [ ]       | Done  |
| [x]    | 1.4 | Verify behavior (VA-123-01)                      | [ ]       | Done  |

### Task Details

- **1.1 Add `--all` option**
  - **Files**: `supekku/cli/list.py`
- **1.2 Implement default filtering**
  - **Files**: `supekku/cli/list.py`
- **1.3 Update help text**
  - **Files**: `supekku/cli/list.py`
- **1.4 Verify behavior**
  - **Steps**:
    - `uv run spec-driver list deltas` (should hide DE-002, etc.)
    - `uv run spec-driver list deltas --all` (should show DE-002, etc.)
    - `uv run spec-driver list deltas -s completed` (should show DE-002, etc.)
