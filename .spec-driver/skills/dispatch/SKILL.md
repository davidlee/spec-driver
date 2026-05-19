---
name: dispatch
description: >
  Orchestrate parallel implementation via sub-agents. Drives an entire delta
  to completion across all phases — planning, dispatching, merging, and
  continuing automatically. Batches tasks by token budget, routes to
  appropriate models (sonnet/opus), and dispatches workers in isolated worktrees.
  Use instead of /execute-phase when a phase has parallelizable work.
---

You are the dispatch orchestrator for delta `$ARGUMENTS`.

You coordinate implementation work by dispatching sub-agents. You run in
the main agent context with full spec-driver access. Sub-agents are
non-interactive workers in isolated worktrees.

**Your goal is to drive the entire delta to completion** — not just one
phase. After each phase completes, automatically proceed to the next phase
(planning it if needed) until all phases are done or a hard blocker stops
you. Only pause for: unresolved blockers, governance concerns requiring
user decision, or explicit user instruction to stop.

## 1. Read artefacts

Read the delta bundle:

```
spec-driver find card $ARGUMENTS
```

Read in order:
1. `DE-XXX.md` — scope, constraints, resolved decisions
2. `DR-XXX.md` — design intent (canonical reference)
3. `IP-XXX.md` — phase overview, verification coverage
4. Active phase sheet(s) — task breakdown, exit criteria

If the delta still says `draft`, immediately change it to `in-progress` (`spec-driver edit delta DE-123 --status in-progress`).

If no phase sheet exists for the next phase, stop and run `/plan-phases`.

## 2. Analyse tasks

For each task in the active phase sheet, determine:

### 2.1 Dependencies

Build a dependency graph from what is explicitly stated:
- **Explicit**: `depends_on` fields in task descriptions (when present)
- **Stated file scope**: Tasks that name the same files/modules must be
  sequential or in the same batch
- **Phase ordering**: Phases execute in IP order unless explicitly independent

When structured metadata is absent (no `depends_on`, no file lists), assume
tasks are dependent. Parallelism requires positive evidence of disjointness.

### 2.2 Complexity signals

For each task, assess complexity:

| Signal | Complexity |
|--------|-----------|
| Task description mentions architecture, design decisions, cross-cutting concerns | high |
| Task touches >5 files or multiple packages | high |
| Task involves new abstractions or API design | high |
| Task is mechanical: rename, format, boilerplate, test scaffolding | low |
| Task touches 1-3 files in a single module | low |
| No clear signal | medium (default) |

### 2.3 Token cost estimation

Estimate per-task token cost (rough heuristic):
- Low complexity: ~10-20k tokens
- Medium complexity: ~20-40k tokens
- High complexity: ~40-80k tokens

These are execution tokens (tool calls, reasoning, edits), not input tokens.

## 3. Batch tasks

Pack tasks into batches targeting the worker's available budget (~85-95k
tokens of work capacity per worker):

**Rules:**
1. Respect dependency ordering — dependent tasks go in the same batch or
   in sequentially ordered batches
2. Tasks with file-scope overlap go in the same batch (avoids merge conflicts)
3. If any task in a batch is high complexity, the batch gets opus
4. Otherwise the batch gets sonnet
5. Maximum batch size = one full phase
6. If a single task exceeds the budget estimate, it gets its own batch

**Parallelism:** Default to sequential execution. Only parallelize batches when:
- File-scope disjointness is explicit in the phase sheet or obvious from
  named file paths in the task descriptions
- No data dependencies exist between the batches
- No ambiguity about task boundaries

When structured metadata (`depends_on`, `touches`, `parallelizable`) is
absent from the phase sheet, treat that as a reason to stay sequential,
not a reason to guess. Parallelism is an optimisation applied with positive
evidence, not a default.

**Isolation follows from this classification** — only safely parallel
batches get `isolation="worktree"`; sequential and single-batch-phase
batches run in the main tree (§6.1).

## 4. Present dispatch plan

Before executing, present the plan to the user:

```
## Dispatch Plan for DE-XXX Phase NN

### Batches

| Batch | Tasks | Model | Isolation | Dependencies |
|-------|-------|-------|-----------|-------------|
| B1 | 1.1, 1.2 | sonnet | worktree | none |
| B2 | 1.3 | opus | worktree | none |
| B3 | 1.4, 1.5 | sonnet | **main** | B1, B2 |

### Parallel groups
- Group 1 (parallel): B1, B2
- Group 2 (sequential, after group 1): B3 — runs in main tree so it sees
  B1/B2 commits; see §6.1

### Estimated context
- Per-batch orchestrator prompt: ~Nk tokens
- Worker available budget: ~85-95k tokens

Proceed? (adjust batches / model assignments / ordering if needed)
```

**Auto-proceed** when the plan is straightforward:
- Single batch (entire phase handled by one worker)
- All batches sequential with sonnet (no parallelism, no opus escalation)

**Require user approval** when the plan involves:
- Multiple parallel workers (worktree isolation, merge risk)
- Opus model escalation for any batch
- Non-obvious reordering or batch splitting

The user may adjust batches, model assignments, or ordering before
approving.

## 5. Assemble per-batch context

For each batch, construct the worker's prompt. This is the dynamic context
that varies per batch. Read the source material and distil — do not just
point at files the worker would need to read.

### 5.1 Policy digest

Read and extract the project's verification commands and code standards from:
- `CLAUDE.md` — verification commands, code standards, conventions
- `.spec-driver/hooks/doctrine.md` — project conventions
- `.spec-driver/workflow.toml` — verification hook configuration (if present)

The verification command is **mandatory**. Every batch prompt must include
the exact command(s) the worker should run to verify their work. Do not
hard-code commands — read them from the project configuration.

Condense into a compact block:

```
## Project Policy
- Verification command: [exact command from project config]
- Code standards: [extract key points from CLAUDE.md]
- Workers do not commit. Leave changes in the worktree.
```

If you cannot determine the verification command from the project config,
ask the user before dispatching.

### 5.2 Design context

Extract relevant sections from DR-XXX that apply to this batch's tasks.
Include only the sections the worker needs — not the full DR.

### 5.3 Pre-fetched memories

For each file path the batch's tasks are expected to touch:
```
spec-driver list memories -p <path>
```

Include relevant memory content verbatim in the prompt. Workers can also
query memories themselves for files discovered during work.

### 5.4 Governance excerpts

If the orchestrator's context (from its own boot) includes ADRs, policies,
or standards relevant to the batch's work, extract the pertinent sections.

### 5.5 Task specification

For each task in the batch:
- Task ID and description from phase sheet
- File scope: which files/modules to touch
- Design notes: relevant DR excerpt or spec requirement
- Exit criteria: what "done" looks like for this task
- AC evidence: what verification evidence to record

### 5.6 Budget check

Estimate the total prompt size. If it exceeds ~15k tokens, consider:
- Trimming governance/design excerpts to essentials
- Splitting the batch
- Warning the user that work budget is squeezed

## 6. Dispatch workers

### 6.1 Isolation selection

Pick isolation by batch type. This is a rule, not a judgment call:

| Batch type | `isolation` |
|------------|-------------|
| Parallel, verified file-scope disjoint | `"worktree"` |
| Sequential, depends on prior batch or phase work | omit (main tree) |
| Single-batch phase | omit (main tree) |

Sequential batches that depend on prior work MUST NOT use
`isolation="worktree"` — regardless of whether that prior work is
committed or in-flight. The worktree forks from a git ref at spawn
time; even committed work can be missing from the fork if the Agent
tool's branch point lags HEAD (the vk DE-105 failure mode).
Independent-but-ordered batches may use worktree isolation; the
"depends on" clause is what forbids it.

**Timing.** A worktree forks from the main branch's HEAD at spawn time.
Uncommitted main-tree changes are invisible to the worker. Therefore,
any prior batch work that a worktree-isolated batch relies on must be
committed before spawn. (Main-tree batches share the working tree and
see uncommitted state directly.)

**Branch-point check.** Before each worktree spawn, capture
`git rev-parse HEAD`. After spawn, compare to `git -C <worktree> log -1
--format=%H`. Mismatch → default is **re-dispatch**; the user must
explicitly override to proceed. This catches orchestrator ordering
errors (forgot to commit prior work). It does not catch Agent-tool
internal staleness if the fork is stale in a way that doesn't change
the ref — if the symptom recurs after this check passes, stop and
escalate to the user.

### 6.2 Spawn

```python
Agent(
    subagent_type="dispatch-worker",
    prompt=assembled_prompt,
    isolation="worktree",    # omit for sequential / single-batch; see §6.1
    model="sonnet",          # or "opus" per batch assignment
    description="DE-XXX P0N batch N: brief description",
)
```

**Parallel group:** launch all independent batches in a single message
with multiple Agent calls.
**Sequential chain:** wait for the prior batch to return; if the next
batch will be worktree-isolated, commit the main-tree work first.

### 6.3 What workers return

Workers do not commit. Worktree workers leave changes in their worktree
branch; main-tree workers leave changes in the main working tree. The
orchestrator merges worktree branches (§9) and commits main-tree work
between batches as needed (required only before spawning a later
worktree-isolated batch; otherwise good hygiene).

## 7. Collect results

Each worker returns a structured summary (defined in dispatch-worker agent):
- Tasks completed (with status)
- AC evidence per task
- Files changed
- Verification results
- Blockers & deferred items
- Governance concerns
- Observations (rough spots, shortcuts, drift, decisions, guesses)
- Memories created

Aggregate these into a phase-level view. Pay particular attention to
the Observations section — workers are instructed to report honestly
about things that felt wrong or uncertain.

## 8. Review at phase boundary

After all batches in a phase complete:

### 8.1 Check exit criteria

Compare aggregated results against the phase sheet's exit criteria.
Flag any gaps.

### 8.2 Check AC evidence

For each task's acceptance criteria, verify the worker provided evidence.
Record evidence in the IP's verification coverage block.

### 8.3 Check for governance concerns

If any worker flagged governance concerns, surface them to the user.
Do not attempt to resolve governance issues — present them and wait.

### 8.4 Tighter review (when warranted)

If the phase sheet marks tasks with `review: tight` or tasks have tight
cross-dependencies that are easy to get wrong, review per-batch completion
before dispatching dependent batches (i.e. before step 6 for sequential
batches).

## 9. Merge worktree branches

This step applies **only to worktree-isolated batches** (parallel batches
with `isolation="worktree"`). Main-tree batches (sequential and
single-batch-phase) have no branch to merge — their changes are already
in the main working tree, and the orchestrator commits them directly
after review (see §6.5).

After a worktree-isolated batch passes review:

1. Check the worktree branch for changes (Agent tool returns branch info)
2. Attempt to merge the branch into the current branch:
   ```
   git merge <worktree-branch> --no-edit
   ```
3. If merge succeeds:
   - Run the project's verification command on the merged result
   - If checks pass: merge is good
   - If checks fail: report failure to user, do not force
4. If merge conflicts:
   - Report conflicting files to user
   - Do not attempt automatic resolution
   - User decides: manual resolution, re-dispatch, or sequential re-execution

## 10. Report and update

After all batches are processed:

### 10.1 Summary to user

```
## Dispatch Complete: DE-XXX Phase NN

### Results
| Batch | Status | Tasks | Model | Duration |
|-------|--------|-------|-------|----------|
| B1 | complete | 1.1, 1.2 | sonnet | — |
| B2 | complete | 1.3 | opus | — |
| B3 | partial | 1.4 (done), 1.5 (blocked) | sonnet | — |

### Merge status
- B1: merged, checks pass
- B2: merged, checks pass
- B3: merged, lint warning (details)

### Blockers
- Task 1.5: [blocker description from worker]

### Governance concerns
- [any flagged concerns from workers]

### Observations (from workers)
- [aggregated rough spots, shortcuts, drift, decisions — surface to user]

### Verification evidence
- [aggregated AC evidence]
```

### 10.2 Update artefacts (orchestrator-only)

The orchestrator is the sole writer of workflow artefacts. Workers report
structured results; the orchestrator translates them into artefact updates.

After each batch completes:
- Update phase sheet task statuses: `[x]` for completed, `[blocked]` for
  blocked, `[ ]` for remaining. Update as batches complete, not only at
  the end — the phase sheet should reflect reality as it progresses.

After all batches in a phase:
- Aggregate AC evidence into the IP's verification coverage block
- Run `/notes` once with the aggregated summary (not per-batch)
- Surface worker observations (rough spots, shortcuts, drift, decisions)
  to the user — these may warrant action before proceeding
- If phase exit criteria are met, proceed to 10.3 (next phase)

### 10.3 Continue to next phase

**Default behaviour: keep going.** Do not stop at a phase boundary unless
forced to.

After a phase completes successfully:
1. Run `spec-driver phase complete DE-XXX` to close the phase
2. Check if the IP has a next phase sheet
   - If yes: loop back to step 2 (Analyse tasks) for the next phase
   - If no phase sheet exists: run `/plan-phases` to create it, then loop
3. Continue until all phases are complete

**Stop only when:**
- Unresolved blockers prevent meaningful progress
- A worker flagged a governance concern that requires user decision
- The user explicitly asked to stop after a specific phase
- All phases are complete — proceed to 10.4

When stopping for blockers or governance, clearly state what is needed to
resume and that you will continue once it is resolved.

### 10.4 Delta completion

When all phases are done:
1. Run `/notes` with a full-delta summary
2. Suggest `/audit-change` → `/close-change` to the user
3. If audit and closure are straightforward and the user has not asked
   to review first, offer to proceed immediately
