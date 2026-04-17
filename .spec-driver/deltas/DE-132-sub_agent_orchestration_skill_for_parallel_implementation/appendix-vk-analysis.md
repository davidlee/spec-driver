---
name: DR-132 Appendix — vk field-analysis of worktree branching failure
source: ~/dev/vk (DE-105 dispatch, 2026-04-17)
archived: "2026-04-17"
kind: external_analysis
---

# Dispatch Worktree Branching: Failure Analysis

**Context**: DE-105 dispatch, 2026-04-17
**Author**: orchestrator observation during two-phase dispatch (vk project)
**Archived here**: 2026-04-17, as the first real-world exercise of VH-002 and
the evidentiary basis for the DR-132 DEC-132-02 clarification (see DR §9).

## What happened

During DE-105 Phase 02 dispatch, Batch 1 (3-pane layout, minimap) was
dispatched as an isolated worktree worker via `Agent(isolation="worktree")`.
The worktree branched from `main` at the current HEAD — which was the P01
implementation commit (`4eff7886`).

However, the worktree agent received **the pre-P01 codebase**. Specifically,
the worktree branch was created from the commit *before* P01 was committed,
not from the actual HEAD. This meant:

- `DayViewportState` still had `slot_minutes` (P01 removed it)
- `DayState` still had `detail_visible` and `browsed_links_folded`
- `render_timeline` still took the old signature
- `screen.rs` didn't have the P01 overlay width changes

The B1 worker completed its work (~800k tokens, ~13 minutes) building
against this stale base, producing code that referenced fields and
signatures that no longer existed in the real `main`.

## Impact

### Direct cost
- ~240k tokens and ~4 minutes spent on a manual merge agent to reconcile
  the worktree output with the actual P01 state
- The merge was non-trivial: 4 files with structural conflicts
  (`ds.viewport.slot_minutes` → `state.day_view_prefs.slot_minutes`,
  function signature changes, call site adaptations)
- Risk of subtle merge errors (e.g., a stale `ds.detail_visible` reference
  that compiles against the wrong struct field on a different type)

### Indirect cost
- P01 was a sequential prerequisite for P02 — the whole point of the
  phase ordering was that P02 builds on P01's state restructure
- The dispatch skill's sequential batch design (B1 then B2 within a phase)
  was correctly applied in P01, but the worktree isolation mechanism
  undermined it by forking from the wrong commit

### What went right
- Clippy caught the stale references immediately after merge
- The structural nature of the conflicts (missing struct fields, wrong
  function signatures) made them compile-time failures, not silent bugs
- The merge agent was able to resolve all conflicts in one pass

## Root cause analysis

### 1. Worktree branch point is not guaranteed to be HEAD

The `Agent(isolation="worktree")` mechanism creates a git worktree. The
branch point depends on when the worktree is created relative to uncommitted
changes in the main working tree.

In this case, P01 changes were committed to `main` before B1 dispatch, but
the worktree creation may have forked from an earlier commit or may not have
picked up the commit.

### 2. Sequential batches within a phase share a mutable codebase

The dispatch skill's batch model assumes sequential batches see each
other's output:

> **Sequential execution:** Wait for dependent batches to complete.
> Include relevant results from prior batches in the next batch's prompt.

But with worktree isolation, "include relevant results" means *prompt
context*, not *code state*. The worktree forks from a git ref, not from
the accumulated working tree state of prior batches.

### 3. The skill conflates two isolation needs

The dispatch skill uses worktree isolation for two different purposes:
- **Parallel batches**: need isolation to avoid merge conflicts (correct use)
- **Sequential batches**: need the *opposite* — they need to see prior work

The current skill text uses worktree for parallel batches and implies
non-worktree for sequential, but doesn't enforce this distinction or
warn about the hazard when the orchestrator makes judgment calls.

## Recommendations for spec-driver skill design

### R1: Explicit branch-point verification

After creating a worktree for a dispatch worker, the orchestrator should
verify the worktree's HEAD matches the expected commit:

```
# After Agent(isolation="worktree") returns the worktree branch:
git -C <worktree_path> log --oneline -1
# Verify this matches the commit that includes all prior batch work
```

If it doesn't match, abort and re-create.

### R2: Sequential batches should not use worktree isolation

The dispatch skill should enforce:

> Sequential batches (those with dependencies on prior batches) MUST NOT
> use `isolation="worktree"`. They run in the main working tree, seeing
> all accumulated changes from prior batches.

Worktree isolation is only for parallel batches that have been verified
as file-scope disjoint.

### R3: Single-batch phases skip isolation entirely

The existing rule is correct but should be more prominent:

> **Single-batch phases:** If the entire phase fits in one batch, dispatch
> without worktree isolation (no merge needed).

### R4: The skill should warn about cross-phase state dependencies

When a phase depends on a prior phase's state restructure (not just
feature completion), the dispatch skill should flag this explicitly:

> **State dependency detected**: P02 entrance criteria reference P01's
> state changes (DayViewPrefs hoist). Worktree isolation for P02 batches
> requires that P01's commit is the worktree branch point. Verify after
> worktree creation.

### R5: Diff-based merge validation

After merging a worktree branch, the orchestrator should run a targeted
check beyond `just check`:

```
# Verify no references to pre-hoist fields survived the merge
grep -rn 'ds\.viewport\.slot_minutes\|ds\.detail_visible\|ds\.browsed_links_folded' tui/src/
```

This catches stale references that might compile (e.g., if a similarly-named
field exists on a different type).

### R6: Document the worktree timing model

The dispatch skill should document:

> Worktree isolation creates a new git branch from the current HEAD of the
> repository at the time the Agent tool executes. If the main working tree
> has uncommitted changes, those changes are NOT included in the worktree.
> If a commit was made between the orchestrator's plan and the agent spawn,
> the worktree includes that commit.
>
> **Implication**: All prior batch work must be committed before spawning
> a worktree-isolated batch that depends on it. Uncommitted changes in the
> main tree are invisible to worktree workers.

## Appendix: What the skill says vs what happened

| Skill instruction | What happened | Gap |
|---|---|---|
| "Sequential batches — dispatch after dependencies complete" | B1 (P02) dispatched after P01 committed | Correct sequencing |
| "Wait for prior batch results before dispatching" | P01 results committed to main | Correct |
| Worker gets worktree isolation | Worktree forked from stale commit | **Branch point wrong** |
| "Include relevant results from prior batches in the next batch's prompt" | Design context described P01 changes in prose | Prose was correct but code base was stale |
| "Run the project's verification command on the merged result" | Clippy caught all stale refs | Verification worked as designed |

## Disposition in this delta (DR-132)

Scope captured: R1, R2, R3, R6 (see DR §9 "Amendment Log").
Deferred as backlog: R4, R5 (IMPR references recorded in DE-132 notes).
