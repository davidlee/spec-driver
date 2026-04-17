---
id: IP-133-P01
slug: "133-installer_support_for_claude_agents_agent_sync_pipeline-phase-01"
name: IP-133 Phase 01 — Implement agent sync
created: "2026-04-17"
updated: "2026-04-17"
status: in-progress
kind: phase
plan: IP-133
delta: DE-133
---

# Phase 1 — Implement agent sync

## 1. Objective

Add agent definition sync to the installer: package source → `.claude/agents/`.

## 2. Links & References

- **Delta**: DE-133
- **Design Revision**: DR-133 §5

## 3. Entrance Criteria

- [x] DR-133 drafted and aligned with DE-133

## 4. Exit Criteria / Done When

- [ ] `supekku/agents/` exists with `dispatch-worker.md`
- [ ] `_install_agents()` implemented in `install.py`
- [ ] Called from `initialize_workspace()`
- [ ] Unit tests passing (new, update, unchanged, dry-run)
- [ ] `just lint` clean
- [ ] `spec-driver install --dry-run` shows agent sync output

## 5. Verification

- `just test` — new tests for `_install_agents()`
- `just lint` — zero warnings
- `spec-driver install --dry-run` — manual check

## 6. Assumptions & STOP Conditions

- Assumes `copy_with_write_permission` from `file_ops` is sufficient (no executable bit needed for `.md`)
- STOP if agent definitions need format validation beyond file copy

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | --- | --- | --- |
| [ ] | 1.1 | Create `supekku/agents/` package source | [P] | |
| [ ] | 1.2 | Move `dispatch-worker.md` to package source | [P] | |
| [ ] | 1.3 | Implement `_install_agents()` in `install.py` | | after 1.1 |
| [ ] | 1.4 | Wire into `initialize_workspace()` | | after 1.3 |
| [ ] | 1.5 | Write unit tests | | after 1.3 |
| [ ] | 1.6 | Lint + full test suite | | after 1.5 |

## 8. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
