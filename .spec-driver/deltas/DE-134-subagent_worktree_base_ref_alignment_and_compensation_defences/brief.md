# Brief: Stale-fork and silent-compensation defences for spec framework subagents

## Context

Empirical evidence shows Claude Code's `isolation: worktree` does not fork from the parent session's current HEAD. In an observed case, the supervisor was working at a local `main` that had progressed 38 commits beyond `origin/main` across two completed delta cycles; the spawned worktree was forked from `origin/main` (the upstream tracking ref), missing all in-flight work the supervisor was actively building on. The exact resolution rule used by Claude Code's worktree machinery is not documented and should not be assumed — the only reliable observation is that it is not the supervisor's working tip.

The worker subagent in the observed case responded to its missing-files state by manually re-staging files from elsewhere into the worktree branch, producing a branch that was unmergeable against `main` (would re-add files identical to trunk) and was only diagnosable by inspecting the actual diff base. The compensation pattern is the second-order problem: a loud failure is recoverable, a silent compensation produces plausible-looking output that reveals itself at integration time.

## Goal

Three-layer defence so subagents declared with `isolation: worktree` start from a known-correct base ref, refuse to compensate when their worktree state contradicts expectations, and surface stale-fork or compensation incidents at handback time rather than at merge time.

## Layers

**Layer 1 — SubagentStart hook: force worktree to parent HEAD.** Configure in project `settings.json`:

```json
"SubagentStart": [
  { "hooks": [{ "type": "command", "command": ".claude/scripts/align-worktree-to-parent.sh" }] }
]
```

`align-worktree-to-parent.sh` reads agent_id and worktree CWD from the hook input JSON. If CWD is not a git worktree distinct from the project root, exit 0 (non-isolated subagent, nothing to do). Otherwise:

1. Resolve the parent session's working directory and capture its HEAD via `git -C $PARENT_CWD rev-parse HEAD`. Store in `.claude/state/agent-base-ref/{agent_id}` for use by the SubagentStop hook.
2. Inside the worktree, run `git reset --hard $PARENT_HEAD`. This unconditionally aligns the worktree to the supervisor's current commit, overriding whatever Claude Code's default resolution produced.
3. Optional override: if `.claude/agent-base-ref` exists at project root, read it and use that ref instead. This accommodates projects on release-train workflows or stacked-branch conventions where parent HEAD isn't the right default.
4. Per-subagent override: if the subagent's frontmatter sets a documented opt-out flag, skip the reset. This covers the rare WIP-carry case where the subagent legitimately needs to start from whatever Claude Code provides.

The hook fails loudly (exit 1 with stderr) if the reset fails — better to abort spawn than start a subagent in an undefined state.

**Layer 2 — Compensation-refusal directive in subagent prompts.** Update the framework's subagent template so every definition that sets `isolation: worktree` includes:

```
## Worktree state discipline

Your worktree is forked from a specific commit assigned by the supervisor. If at any point you find that:

- expected files or directories are missing
- expected commits are not in the log
- the codebase is in an unexpectedly older state than your delegation prompt implies

STOP immediately. Report the discrepancy in your final message. Do NOT copy files from elsewhere on the filesystem, re-stage state from another branch, restore missing files from memory or context, or otherwise reconstruct the worktree to match expectations. The supervisor will diagnose and reset.

Compensation produces branches that look plausible in isolation but are unmergeable against trunk because their diff baseline is wrong. Loud failure is recoverable; silent compensation is not.
```

If the framework has a shared preload-skill convention, put it there and reference by name.

**Layer 3 — SubagentStop hook: merge-base sanity check.** Configure in project `settings.json`:

```json
"SubagentStop": [
  { "hooks": [{ "type": "command", "command": ".claude/scripts/verify-worktree-base.sh" }] }
]
```

`verify-worktree-base.sh` reads agent_id and worktree path from hook input. If no captured base ref exists (non-isolated subagent), clean up state and exit 0. Otherwise:

1. Compute `git merge-base $WORKTREE_BRANCH $CAPTURED_BASE_REF` inside the worktree.
2. If the merge-base equals the captured base ref, the branch is cleanly descended — pass.
3. If the merge-base is an ancestor of the captured base ref but not equal to it, the branch forked from a stale point — surface as a warning in stderr with the gap commit count and the divergent commits list. Do not block handback; the supervisor needs the result to diagnose.
4. If the merge-base is on a different ancestry line entirely, surface as a hard error — the branch is not a descendant of where it should be, indicating compensation or worktree confusion.
5. Additionally, scan the branch's commits for added files that already exist identically at the captured base ref (the compensation signature). Flag any matches.
6. Clean up the per-agent state file regardless of outcome.

Output goes to stderr and to `.claude/state/worktree-incidents.log` with timestamp, agent ID, and finding category, so patterns across multiple delegations can be reviewed.

## Acceptance criteria

- A subagent spawned with `isolation: worktree` starts at the supervisor's HEAD-at-delegation, regardless of what Claude Code's default worktree resolution would have produced.
- A subagent whose worktree state contradicts its delegation prompt expectations stops and reports rather than compensating.
- At handback, a worktree branch with a stale merge-base or a different-ancestry merge-base is surfaced before the supervisor accepts the result.
- The compensation signature (added files identical to base-ref state) is detected and flagged.
- Subagents without `isolation: worktree` are unaffected — hooks no-op cleanly.
- Project-level base-ref override is supported via `.claude/agent-base-ref`.
- Per-subagent opt-out for WIP-carry is supported via documented frontmatter flag.
- No state files persist after subagent completion.
- `.claude/state/worktree-incidents.log` accumulates incidents across delegations for pattern review.
- Framework template/generator update is single-source — existing subagent definitions inherit the directive without per-file edits.
- `.claude/scripts/README.md` documents the design, especially the parent-HEAD-vs-trunk policy choice and how to override it per-project.

## Out of scope

Path enforcement during subagent execution (separate concern, separate brief if needed). Read sandboxing. Replacing Claude Code's worktree creation entirely. Process or network isolation. Automatic resolution of stale-fork incidents — the supervisor diagnoses, the hook only surfaces.

## Open questions to resolve before implementation

1. Confirm the exact JSON shape and field names of SubagentStart and SubagentStop hook inputs by capturing real invocations. In particular, confirm how to reliably retrieve the parent session's working directory from within a SubagentStart hook — if not directly available in the hook input, derive from the worktree's `.git/worktrees/{name}/gitdir` pointer or from `git worktree list --porcelain` run from inside the worktree.
2. Confirm Claude Code's actual base-ref resolution rule for `isolation: worktree` so the override behaviour is documented accurately. The empirical observation (forks from `origin/main` or similar tracking ref, not parent HEAD) should be verified against the source or via additional controlled spawns before the brief's framing is treated as canonical.
3. Decide whether stale-fork warnings (merge-base is ancestor of base ref but not equal) should hard-block on the supervisor side via a SubagentStop blocking exit code, or only surface as warnings the supervisor must read. Default position: warn-only, on the principle that the supervisor needs the worktree result to diagnose.
4. Decide the policy for `.claude/agent-base-ref` precedence when both project-level config and per-subagent frontmatter override are present. Default: per-subagent frontmatter wins, project config is the framework-level default.
