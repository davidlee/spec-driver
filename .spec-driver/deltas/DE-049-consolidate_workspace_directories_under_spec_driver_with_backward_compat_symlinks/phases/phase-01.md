---
id: IP-049.PHASE-01
slug: "049-consolidate_workspace_directories_under_spec_driver_with_backward_compat_symlinks-phase-01"
name: IP-049 Phase 01 — Structural migration
created: "2026-03-06"
updated: "2026-03-21"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-049.PHASE-01
plan: IP-049
delta: DE-049
objective: >-
  Move content directories into .spec-driver/ via git mv, create backward-compat
  symlinks at old locations. Pure structural change — no code modifications.
entrance_criteria:
  - DR-049 approved
  - ADR-004 accepted
  - DE-048 completed
exit_criteria:
  - All content under .spec-driver/ (tech/, product/, decisions/, policies/, standards/, deltas/, revisions/, audits/, backlog/, memory/)
  - Compat symlinks at old locations resolve correctly
  - Git working tree clean (committed)
  - No broken cross-references via symlinks
verification:
  tests:
    - VT-049-migration
  evidence:
    - Manual verification that old paths resolve via symlinks
tasks:
  - id: "1.1"
    description: Delete derived symlinks (spec index, contract mirror, decision status)
  - id: "1.2"
    description: git mv content directories into .spec-driver/
  - id: "1.3"
    description: Create backward-compat symlink structures
  - id: "1.4"
    description: Verify old paths resolve, commit
risks:
  - description: Large diff even after derived symlink cleanup
    mitigation: Separate commit for derived symlink deletion
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-049.PHASE-01
```

# Phase 1 — Structural migration

## 1. Objective

Move all content from `specify/`, `change/`, `backlog/`, `memory/` into
`.spec-driver/` using `git mv`. Create backward-compat symlinks so old paths
continue to resolve. No code changes in this phase.

## 2. Links & References

- **Delta**: DE-049
- **Design Revision**: DR-049 §4 (path model before/after), §7 DEC-049-03 (targeted symlinks), DEC-049-05 (migration sequence)
- **IMPR-008 spike**: Q4 (symlink feasibility), Q6 (migration scope)

## 3. Entrance Criteria

- [x] DR-049 approved (2 rounds of adversarial review)
- [x] ADR-004 accepted
- [x] DE-048 completed

## 4. Exit Criteria / Done When

- [x] Derived symlinks deleted and committed (843f9b1)
- [x] Content `git mv`'d into `.spec-driver/` and committed (4d5649a)
- [x] Compat symlink structures created and committed (981abac)
- [x] Old paths resolve correctly via symlinks (manual spot check)
- [x] Git working tree clean

## 5. Verification

- Manual: `ls -la specify/tech/` shows symlink → `../.spec-driver/tech/`
- Manual: `cat specify/tech/SPEC-001/SPEC-001.md` resolves content
- Manual: `cat change/deltas/DE-049-*/DE-049.md` resolves content
- Manual: `cat backlog/improvements/IMPR-008-*/spike.md` resolves content
- Manual: `cat memory/` shows memory files

## 6. Assumptions & STOP Conditions

- **Assumption**: `git mv` preserves history for moved directories
- **Assumption**: Relative symlink targets work cross-platform (Linux/macOS/WSL)
- **STOP**: If any `git mv` fails due to existing `.spec-driver/` subdirs conflicting with content dirs (e.g., `.spec-driver/registry/` already exists as a real dir)

## 7. Tasks & Progress

| Status | ID  | Description                       | Parallel? | Notes                                  |
| ------ | --- | --------------------------------- | --------- | -------------------------------------- |
| [x]    | 1.1 | Delete derived symlinks           | No        | 388 entries deleted, committed 843f9b1 |
| [x]    | 1.2 | git mv content into .spec-driver/ | No        | 526 renames, committed 4d5649a         |
| [x]    | 1.3 | Create compat symlink structures  | No        | 10 symlinks, committed 981abac         |
| [x]    | 1.4 | Verify and final commit           | No        | All 5 spot-checks pass, tree clean     |

### Task Details

- **1.1 Delete derived symlinks**
  - **Scope**: Delete all derived/rebuilt symlinks before `git mv` to reduce diff noise
  - **Targets**:
    - `specify/tech/by-slug/`, `by-package/`, `by-language/`, `by-category/`, `by-c4-level/` (SpecIndexBuilder)
    - `specify/tech/assemblies`, `units`, `c4` alias symlinks
    - `specify/tech/SPEC-*/contracts/` (ContractMirrorTreeBuilder compat links)
    - `specify/decisions/accepted/`, `specify/decisions/draft/` (decision status symlinks)
  - **Method**: `git rm -r` for tracked symlinks; verify with `git status`
  - **Commit**: Separate commit "DE-049: delete derived symlinks before structural migration"

- **1.2 git mv content into .spec-driver/**
  - **Scope**: Move content directories, handling conflicts with existing `.spec-driver/` subdirs
  - **Sequence**:
    1. `git mv specify/tech .spec-driver/tech`
    2. `git mv specify/product .spec-driver/product`
    3. `git mv specify/decisions .spec-driver/decisions`
    4. `git mv specify/policies .spec-driver/policies`
    5. `git mv specify/standards .spec-driver/standards`
    6. `git mv change/deltas .spec-driver/deltas`
    7. `git mv change/revisions .spec-driver/revisions`
    8. `git mv change/audits .spec-driver/audits`
    9. `git mv backlog .spec-driver/backlog`
    10. `git mv memory .spec-driver/memory`
  - **Cleanup**: Remove empty `specify/`, `change/` dirs after content moved
  - **Conflict check**: `.spec-driver/` already has `registry/`, `agents/`, `hooks/`, `templates/`, `about/` — no overlap with content dirs
  - **Commit**: "DE-049: git mv content directories into .spec-driver/"

- **1.3 Create compat symlink structures**
  - **Per DEC-049-03**: Targeted symlinks inside real directories
  - **Create**:
    ```
    mkdir specify change
    ln -s ../.spec-driver/tech specify/tech
    ln -s ../.spec-driver/product specify/product
    ln -s ../.spec-driver/decisions specify/decisions
    ln -s ../.spec-driver/policies specify/policies
    ln -s ../.spec-driver/standards specify/standards
    ln -s ../.spec-driver/deltas change/deltas
    ln -s ../.spec-driver/revisions change/revisions
    ln -s ../.spec-driver/audits change/audits
    ln -s .spec-driver/backlog backlog
    ln -s .spec-driver/memory memory
    ```
  - **Commit**: "DE-049: create backward-compat symlinks"

- **1.4 Verify and final commit**
  - Spot-check 4-5 paths through symlinks
  - `git status` clean
  - No further commit needed if 1.3 is clean

## 8. Risks & Mitigations

| Risk                                  | Mitigation                                                        | Status                                |
| ------------------------------------- | ----------------------------------------------------------------- | ------------------------------------- |
| `.spec-driver/` subdir name conflicts | Pre-checked: no overlap between content and existing managed dirs | Clear                                 |
| Large diff                            | Derived symlink deletion in separate commit (1.1)                 | Mitigated — 388 entries in own commit |
| Broken cross-references               | Compat symlinks tested in 1.4                                     | Clear — all 5 spot-checks pass        |

## 9. Decisions & Outcomes

- Also deleted `registry_v2.json` (derived file) during 1.1 — reduces diff noise
- `by-language/` dir survived derived symlink deletion (it's a real dir with content, not a symlink) — will be handled naturally by git mv in 1.2
- Captured migration steps as reusable shell script: `supekku/scripts/migrate_to_consolidated_layout.sh` (3280914). Final home TBD.

## 10. Findings / Research Notes

- Exact counts: 388 derived entries deleted (1.1), 526 renames (1.2), 10 compat symlinks (1.3)
- No conflicts with existing `.spec-driver/` subdirs as predicted
- All git mv operations preserved rename detection (100% similarity)

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (spot-checks documented above)
- [x] Notes updated (notes.md — Phase 1 section)
- [x] Hand-off notes to Phase 2 (in notes.md)
