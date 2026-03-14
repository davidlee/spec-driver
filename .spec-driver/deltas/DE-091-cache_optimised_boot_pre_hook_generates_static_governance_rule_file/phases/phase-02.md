---
id: IP-091.PHASE-02
slug: 091-cache_optimised_boot_pre_hook_generates_static_governance_rule_file-phase-02
name: IP-091 Phase 02
created: '2026-03-12'
updated: '2026-03-12'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-091.PHASE-02
plan: IP-091
delta: DE-091
objective: >-
  Wire preboot into startup hook, installer symlink, and boot skill validator.
entrance_criteria:
  - P01 complete — preboot command works
exit_criteria:
  - startup.sh calls preboot before JSON output
  - Installer creates .claude/rules/ symlink
  - Boot skill is lightweight validator
  - All tests pass
  - Lints clean
verification:
  tests:
    - VA-boot-validator
    - VA-graceful-degradation
  evidence: []
tasks:
  - id: "2.1"
    summary: Update startup.sh to call preboot
  - id: "2.2"
    summary: Installer creates symlink and .agents/ dir
  - id: "2.3"
    summary: Boot skill becomes lightweight validator
  - id: "2.4"
    summary: Tests for installer changes
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-091.PHASE-02
```

# Phase 02 — Integration: hook, installer, boot skill

## 1. Objective

Wire the preboot command into the session lifecycle: startup hook invokes it, installer manages the symlink, boot skill validates rather than reads.

## 2. Links & References

- **Delta**: [DE-091](../DE-091.md)
- **Design Revision**: [DR-091](../DR-091.md) — §3 Data Flow, §4 Code Impact
- **P01 hand-off**: [phase-01.md](./phase-01.md)

## 3. Entrance Criteria

- [x] P01 complete — `spec-driver admin preboot` works

## 4. Exit Criteria / Done When

- [x] `startup.sh` calls `spec-driver admin preboot` before JSON output
- [x] Installer creates `.agents/` dir and `.claude/rules/spec-driver-boot.md` symlink
- [x] Boot skill checks for preboot file, warns if missing, prints sigil
- [x] `just test` passes (3856 passed)
- [x] `just lint` passes

## 5. Verification

- `just test`
- `just lint`
- `just pylint-files` on touched files
- VA: manual inspection of boot skill behaviour

## 6. Assumptions & STOP Conditions

- Package hook source (`supekku/claude.hooks/startup.sh`) is installer-managed and overwritten on install
- STOP if: hook JSON output format has undocumented constraints

## 7. Tasks & Progress

| Status | ID  | Description                                | Parallel? | Notes                                                  |
| ------ | --- | ------------------------------------------ | --------- | ------------------------------------------------------ |
| [x]    | 2.1 | Update `startup.sh` to call preboot        |           | Add one line before JSON output                        |
| [x]    | 2.2 | Installer creates symlink + `.agents/` dir |           | In `install.py` — `_ensure_preboot_symlink()`          |
| [x]    | 2.3 | Boot skill becomes lightweight validator   |           | `supekku/skills/boot/SKILL.md`                         |
| [x]    | 2.4 | Tests for installer symlink creation       |           | 7 tests in `install_test.py::TestEnsurePrebootSymlink` |

### Task Details

- **2.1 — Update `supekku/claude.hooks/startup.sh`**
  - Add `uv run spec-driver admin preboot "$PWD" 2>/dev/null` before JSON echo
  - Errors swallowed so failed preboot doesn't break session

- **2.2 — Installer creates symlink**
  - In `initialize_workspace()`: create `.agents/` dir, create symlink `.claude/rules/spec-driver-boot.md` → `../../.agents/spec-driver-boot.md`
  - Idempotent: skip if symlink already exists and points correctly

- **2.3 — Boot skill validator**
  - Replace `@` file references with: check `.agents/spec-driver-boot.md` exists, warn if missing, print sigil, enforce routing
  - No file reads

- **2.4 — Tests**
  - Installer test: symlink created, idempotent, correct target

## 8. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Phase tracking updated
- [ ] Hand-off notes for P03 (verification)
