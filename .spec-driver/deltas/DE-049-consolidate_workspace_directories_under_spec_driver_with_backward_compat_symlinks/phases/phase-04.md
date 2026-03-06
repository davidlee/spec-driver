---
id: IP-049.PHASE-04
slug: 049-consolidate_workspace_directories_under_spec_driver_with_backward_compat_symlinks-phase-04
name: IP-049 Phase 04 — Regression, skill symlinks, and cleanup
created: '2026-03-06'
updated: '2026-03-06'
status: active
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-049.PHASE-04
plan: IP-049
delta: DE-049
objective: >-
  Refactor skill sync to install to .spec-driver/skills/ with dir-level
  symlinks for agent targets. Update agent instruction files and memories
  that reference old paths. Full regression pass.
entrance_criteria:
  - Phase 3 committed (4cedc0a)
exit_criteria:
  - Skill sync installs to .spec-driver/skills/, agent targets are symlinks
  - Agent instruction files reference .spec-driver/ paths (not specify/change/)
  - mem.signpost.spec-driver.file-map updated
  - just passes (full regression)
  - Both linters clean
verification:
  tests:
    - VT-049-regression
    - VA-049-agent
  evidence:
    - Full test suite passes
    - Agent instruction files reference correct paths
tasks:
  - id: "4.1"
    description: Refactor skill sync — install to .spec-driver/skills/, symlink targets
  - id: "4.2"
    description: Update skill sync tests
  - id: "4.3"
    description: Scan agent instruction files for old path references
  - id: "4.4"
    description: Update mem.signpost.spec-driver.file-map
  - id: "4.5"
    description: Full regression (just)
risks:
  - description: Skill sync refactor changes behavior for all installs
    mitigation: Existing tests cover install/prune semantics; symlink is additive
  - description: Agent instructions scattered across generated and hand-authored files
    mitigation: Grep sweep; compat symlinks keep old paths working regardless
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-049.PHASE-04
```

# Phase 4 — Regression, skill symlinks, and cleanup

## 1. Objective

Refactor skill sync to use `.spec-driver/skills/` as the single canonical
install location, with dir-level symlinks for agent targets (`.claude/skills`,
`.agents/skills`). Update agent instruction files and memories that reference
old directory paths. Full regression pass.

## 2. Links & References
- **Delta**: DE-049
- **DR-049**: DEC-049-03 (symlink strategy)
- **Predecessor**: Phase 3 (installer + callers, commit 4cedc0a)
- **Notes**: Phase 3 hand-off in notes.md

## 3. Entrance Criteria
- [x] Phase 3 committed (4cedc0a)

## 4. Exit Criteria / Done When
- [ ] `sync.py` installs skills to `.spec-driver/skills/` (not directly to targets)
- [ ] `.claude/skills` and `.agents/skills` are dir-level symlinks to `../.spec-driver/skills`
- [ ] Prune operates on `.spec-driver/skills/` only
- [ ] Skill sync tests updated
- [ ] Agent instruction files scanned and updated for `.spec-driver/` paths
- [ ] `mem.signpost.spec-driver.file-map` updated
- [ ] `just` passes (VT-049-regression)
- [ ] Both linters clean

## 5. Verification
- `uv run pytest supekku/scripts/lib/skills/sync_test.py -v`
- `uv run pytest supekku/cli/skills_test.py -v`
- `just`

## 6. Assumptions & STOP Conditions
- **Assumption**: All agent targets see the same skill set (same allowlist)
- **Assumption**: No per-agent skill differentiation needed today
- **STOP**: If any agent target needs different skills, switch to per-skill symlinks

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 4.1 | Refactor skill sync | No | Install to .spec-driver/skills/, symlink targets |
| [ ] | 4.2 | Update skill sync tests | No | Test symlink creation, idempotency, prune |
| [ ] | 4.3 | Scan/fix agent instruction files | Yes | Old path refs in .spec-driver/agents/*.md etc |
| [ ] | 4.4 | Update file-map memory | Yes | mem.signpost.spec-driver.file-map |
| [ ] | 4.5 | Full regression | No | just (lint + test) |

### Task Details

- **4.1 Refactor skill sync**
  - `install_skills_to_target()`: change to install into
    `repo_root / .spec-driver / skills /` instead of each target dir
  - New function `_ensure_target_symlinks()`: for each target in
    `SKILL_TARGET_DIRS`, create dir-level symlink to `../.spec-driver/skills`
    (idempotent, skip if correct symlink exists, don't clobber real dirs)
  - `prune_skills_from_target()`: operate on `.spec-driver/skills/` only
  - `sync_skills()`: call install once, then ensure symlinks per target
  - Update `SKILL_TARGET_DIRS` usage accordingly

- **4.2 Update skill sync tests**
  - Test that skills are installed under `.spec-driver/skills/`
  - Test that target dirs are symlinks pointing to correct location
  - Test idempotency of symlink creation
  - Test prune removes from canonical dir

- **4.3 Scan/fix agent instruction files**
  - Grep for `specify/`, `change/`, `backlog/`, `memory/` in generated agent
    docs under `.spec-driver/agents/` and templates
  - Check hand-authored files (CLAUDE.md, etc.)
  - Update paths to `.spec-driver/` equivalents where appropriate
  - Note: compat symlinks mean old paths still work, so this is cosmetic cleanup

- **4.4 Update file-map memory**
  - `uv run spec-driver show memory mem.signpost.spec-driver.file-map --raw`
  - Update to reflect new layout

- **4.5 Full regression**
  - `just` (ruff + pylint + pytest)

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Skill sync refactor breaks install | Existing tests; symlink is simpler than copy | Open |
| Generated agent docs have old paths | Compat symlinks keep them working | Low |

## 9. Decisions & Outcomes

(To be filled during execution)

## 10. Findings / Research Notes

(To be filled during execution)

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated (notes.md — Phase 4 section)
- [ ] Delta ready for closure
