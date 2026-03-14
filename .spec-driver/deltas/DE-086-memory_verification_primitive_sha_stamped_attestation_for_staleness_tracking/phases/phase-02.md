---
id: IP-086.PHASE-02
slug: 086-memory_verification_primitive_sha_stamped_attestation_for_staleness_tracking-phase-02
name: 'IP-086 Phase 02: CLI and staleness'
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-086.PHASE-02
plan: IP-086
delta: DE-086
objective: >-
  Wire SHA-stamped verification into the CLI edit command, implement batched
  staleness computation, and add tiered staleness listing to the memory list
  command.
entrance_criteria:
  - Phase 01 complete (core primitives tested and committed)
exit_criteria:
  - edit memory --verify stamps verified, verified_sha, updated — tested
  - edit memory --verify refuses without git — tested
  - edit memory --verify and --status are mutually exclusive — tested
  - staleness.py computes batch staleness with single git invocation — tested
  - staleness.py handles paths, globs, unscoped, unattested — tested
  - list memories --stale shows three-tier output — tested
  - ruff + pylint clean on all touched files
verification:
  tests:
    - VT-cli-edit-verify
    - VT-memory-staleness
    - VT-cli-list-stale
  evidence: []
tasks:
  - id: "2.1"
    description: Create memory/staleness.py module
  - id: "2.2"
    description: Add --verify flag to edit memory CLI
  - id: "2.3"
    description: Add staleness formatter to memory_formatters.py
  - id: "2.4"
    description: Add --stale flag to list memories CLI
risks:
  - description: Complex glob patterns don't translate to git pathspecs
    mitigation: Current corpus uses simple directory prefixes; warn on untranslatable
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-086.PHASE-02
```

# Phase 02 — CLI and Staleness

## 1. Objective

Wire the Phase 01 foundation into user-facing CLI commands. Implement batched staleness computation as a domain module and surface it through `list memories --stale` with three-tier output.

## 2. Links & References

- **Delta**: [DE-086](../DE-086.md)
- **Design Revision**: [DR-086](../DR-086.md) §5.6–§5.8
- **Specs**: SPEC-132 (memory), SPEC-110 (CLI)

## 3. Entrance Criteria

- [x] Phase 01 complete (core primitives tested and committed)

## 4. Exit Criteria / Done When

- [ ] `edit memory --verify` stamps `verified`, `verified_sha`, `updated` via `update_frontmatter_fields`
- [ ] `edit memory --verify` refuses when `get_head_sha()` returns None
- [ ] `edit memory --verify` and `--status` are mutually exclusive
- [ ] `staleness.py` implements `StalenessInfo` dataclass and `compute_batch_staleness()`
- [ ] Single batched `git log` invocation for all scoped memories
- [ ] Both `scope.paths` and `scope.globs` included in staleness computation
- [ ] Unscoped/unattested memories fall back to `days_since`
- [ ] `list memories --stale` shows three-tier output with correct sort order
- [ ] `just lint` clean on all touched files
- [ ] `just pylint-files` clean on all touched files

## 5. Verification

- Run: `just test`
- Run: `just lint`
- Run: `just pylint-files supekku/cli/edit.py supekku/cli/list.py supekku/scripts/lib/memory/staleness.py supekku/scripts/lib/formatters/memory_formatters.py`

## 6. Assumptions & STOP Conditions

- Assumes Phase 01 code is committed and stable
- STOP if `update_frontmatter_fields` doesn't handle `verified_sha` insertion correctly
- STOP if list.py refactoring temptation arises — note it but don't pursue in this phase

## 7. Tasks & Progress

| Status | ID  | Description                      | Parallel? | Notes                            |
| ------ | --- | -------------------------------- | --------- | -------------------------------- |
| [x]    | 2.1 | Create `memory/staleness.py`     | [P]       | DR §5.7 — 17 tests, pylint 10/10 |
| [x]    | 2.2 | Add `--verify` to `edit memory`  | [P]       | DR §5.6 — 5 tests, pylint 10/10  |
| [x]    | 2.3 | Add staleness formatter          | —         | DR §5.8 — 7 tests, pylint 10/10  |
| [x]    | 2.4 | Add `--stale` to `list memories` | —         | DR §5.8 — 2 CLI tests            |

### Task Details

- **2.1 Create `memory/staleness.py`**
  - **Files**: `supekku/scripts/lib/memory/staleness.py` (new), `supekku/scripts/lib/memory/staleness_test.py` (new)
  - **Design**: DR §5.7 — `StalenessInfo` dataclass, `compute_batch_staleness(records, root)`. Single `git log` invocation. Convert globs to pathspecs. Fallback to `days_since` for unscoped.
  - **Testing**: Mock subprocess for git log. Test scoped+attested, scoped+unattested, unscoped. Test glob conversion. Test empty corpus.

- **2.2 Add `--verify` to `edit memory`**
  - **Files**: `supekku/cli/edit.py`, `supekku/cli/edit_test.py`
  - **Design**: DR §5.6 — `--verify` flag, mutex with `--status`. Refuses without git. Stamps via `update_frontmatter_fields`.
  - **Testing**: Verify stamps fields. Mutex error. Git-unavailable refusal. Confirmation output with short_sha.

- **2.3 Add staleness formatter**
  - **Files**: `supekku/scripts/lib/formatters/memory_formatters.py`, formatter test file
  - **Design**: DR §5.8 — three-tier table with tier headers, confidence column, stale column.
  - **Testing**: Tier ordering. Sort within tiers. Edge cases (empty tiers).

- **2.4 Add `--stale` to `list memories`**
  - **Files**: `supekku/cli/list.py`, `supekku/cli/list_test.py`
  - **Design**: DR §5.8 — `--stale` flag triggers staleness computation + tiered formatter.
  - **Testing**: CLI integration with mocked staleness. Output format.

## 8. Risks & Mitigations

| Risk                          | Mitigation                                                               | Status   |
| ----------------------------- | ------------------------------------------------------------------------ | -------- |
| Complex globs → git pathspecs | Current corpus is simple prefixes; warn on untranslatable                | Low risk |
| list.py growing large         | Note for backlog; keep addition minimal, delegate to domain + formatters | Accepted |

## 9. Decisions & Outcomes

- All design decisions closed in DR-086 prior to phase start.
- 2026-03-10: Distinguished "git failed" (returns None) from "0 commits" (returns empty list) in `_query_git_log` to avoid falsely reporting 0 commits when git is unavailable.
- 2026-03-10: `_verify_memory` extracted as a helper in edit.py to keep the command function thin.
- 2026-03-10: Staleness formatter uses plain text (not Rich table) for tiered output — simpler, avoids coupling to Rich for a special-purpose view.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: 3773 passed, 0 failed; ruff clean; pylint 10/10 on new files
- [ ] Hand-off to Phase 03
- [ ] Backlog item created for list.py factoring review
