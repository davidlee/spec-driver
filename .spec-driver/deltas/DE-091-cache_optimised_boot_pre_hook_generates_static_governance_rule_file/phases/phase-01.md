---
id: IP-091.PHASE-01
slug: 091-cache_optimised_boot_pre_hook_generates_static_governance_rule_file-phase-01
name: IP-091 Phase 01
created: "2026-03-12"
updated: "2026-03-12"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-091.PHASE-01
plan: IP-091
delta: DE-091
objective: >-
  Implement core preboot module and admin preboot CLI command with tests.
entrance_criteria:
  - DR-091 accepted
exit_criteria:
  - spec-driver admin preboot generates correct output file
  - All tests pass (just test)
  - Lints clean (just lint, just pylint-report)
verification:
  tests:
    - VT-preboot-concat
    - VT-preboot-idempotent
    - VT-preboot-tsv
  evidence: []
tasks:
  - id: "1.1"
    summary: Create preboot.py core module
  - id: "1.2"
    summary: Add admin preboot CLI subcommand
  - id: "1.3"
    summary: Write tests for preboot
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-091.PHASE-01
```

# Phase 01 — Core preboot command and tests

## 1. Objective

Implement `supekku/scripts/lib/core/preboot.py` and wire it into `spec-driver admin preboot`. The command reads 7 boot-sequence files, shells out to the CLI for 3 governance listings (TSV), and writes the concatenated result to `.agents/spec-driver-boot.md`.

## 2. Links & References

- **Delta**: [DE-091](../DE-091.md)
- **Design Revision**: [DR-091](../DR-091.md) — §3 Architecture Intent, §4 Code Impact, §8 Generated File Format
- **Spec**: SPEC-129 (sync installer-component)

## 3. Entrance Criteria

- [x] DR-091 reviewed and accepted

## 4. Exit Criteria / Done When

- [x] `spec-driver admin preboot` generates `.agents/spec-driver-boot.md` with correct content
- [x] Generated file contains all 7 boot-sequence source files
- [x] Generated file contains 3 governance listings as TSV
- [x] Running twice produces identical output (idempotent)
- [x] `just test` passes (3849 passed)
- [x] `just lint` passes
- [x] `just pylint-report` — no new warnings in touched files

## 5. Verification

- `just test` — new `preboot_test.py` tests
- `just lint` — ruff
- `just pylint-files supekku/scripts/lib/core/preboot.py supekku/cli/admin.py`

## 6. Assumptions & STOP Conditions

- Assumes `admin` CLI group exists or can be created
- Assumes workflow.toml `exec` key provides the correct CLI invocation prefix
- STOP if: exec command resolution from workflow.toml is more complex than expected

## 7. Tasks & Progress

| Status | ID  | Description                        | Parallel?    | Notes                                        |
| ------ | --- | ---------------------------------- | ------------ | -------------------------------------------- |
| [x]    | 1.1 | Create `preboot.py` core module    |              | Pure logic: read files, run CLI, concatenate |
| [x]    | 1.2 | Add `admin preboot` CLI subcommand |              | Thin CLI wiring                              |
| [x]    | 1.3 | Write `preboot_test.py`            | [P] with 1.1 | TDD — 14 tests covering all VT criteria      |

### Task Details

- **1.1 — Create `supekku/scripts/lib/core/preboot.py`**
  - **Approach**: Module with a `generate_preboot_content(repo_root: Path) -> str` function that:
    1. Reads 7 boot-sequence files in order (dogma, exec, glossary, workflow, policy, memory, doctrine)
    2. Resolves exec command from workflow.toml
    3. Shells out to `{exec} list adrs -s accepted --format=tsv`, `{exec} list policies -s required --format=tsv`, `{exec} list standards -s required --format=tsv`
    4. Concatenates per DR-091 §8 format
  - And a `write_preboot_file(repo_root: Path) -> Path` that writes to `.agents/spec-driver-boot.md`
  - **Files**: `supekku/scripts/lib/core/preboot.py`

- **1.2 — Add `admin preboot` CLI subcommand**
  - **Approach**: Thin CLI — parse repo root arg (default `.`), call `write_preboot_file`, print path
  - **Files**: `supekku/cli/admin.py` (or wherever admin group lives)

- **1.3 — Write `supekku/scripts/lib/core/preboot_test.py`**
  - **Key test cases**:
    - File concatenation includes all 7 source files with correct section headers
    - TSV governance listings appear after policy section
    - Idempotent: two runs produce byte-identical output
    - Missing source file: appropriate error/handling
    - Exec command resolution from workflow.toml
  - **Files**: `supekku/scripts/lib/core/preboot_test.py`

## 8. Risks & Mitigations

| Risk                          | Mitigation                                 | Status |
| ----------------------------- | ------------------------------------------ | ------ |
| admin CLI group doesn't exist | Create it or add to existing group         | Open   |
| exec resolution edge cases    | Check existing `detect_exec_command` usage | Open   |

## 9. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Phase tracking updated
- [ ] Hand-off notes for P02 (integration)

## Hand-off to P02

P01 delivered:

- `supekku/scripts/lib/core/preboot.py` — `generate_preboot_content()` and `write_preboot_file()`
- `supekku/cli/admin.py` — `preboot` subcommand under `admin` group
- 14 tests in `preboot_test.py`
- Generated output at `.agents/spec-driver-boot.md` (197 lines)

P02 needs:

- Wire `startup.sh` to call `uv run spec-driver admin preboot "$PWD"` before JSON output
- Installer creates `.claude/rules/spec-driver-boot.md` symlink → `../../.agents/spec-driver-boot.md`
- Boot skill (`supekku/skills/boot/SKILL.md`) becomes lightweight validator
- Admin CLI group already exists; no `admin` subcommand concerns remain
