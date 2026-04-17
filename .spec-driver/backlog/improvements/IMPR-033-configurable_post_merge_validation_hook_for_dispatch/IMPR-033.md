---
id: IMPR-033
name: Configurable post-merge validation hook for dispatch
created: "2026-04-17"
updated: "2026-04-17"
status: idea
kind: improvement
relations:
  - type: relates_to
    target: DE-132
---

# Configurable post-merge validation hook for dispatch

## Context

Source: vk DE-105 field analysis (DR-132 amendment appendix). Recommendation
R5.

After merging a worktree branch, the orchestrator currently runs
`just check` (or the project's verification command). In the vk DE-105
incident, the post-merge check (clippy) caught all stale references — so
the safety net worked. R5 would shorten the feedback loop by running
targeted checks (e.g., grep for patterns known to be risky across a
state restructure) *before* the full verification command.

## Why this is deferred from DR-132

- Requires a new config surface (likely `workflow.toml [dispatch]
  post_merge_checks = [...]` or similar) — out of scope for a
  clarification amendment.
- The existing verification command already catches the failure mode this
  targets. R5 is a latency optimisation, not a correctness fix.
- Design question: is this a dispatch-specific hook or a general
  `/execute-phase` / `complete delta` hook? That decision shapes where
  the config lives and who else benefits. Needs a broader look at hook
  framework design.

## Design surface

Open questions:
- Config location: `workflow.toml`, `.spec-driver/hooks/`, per-delta?
- Scope: dispatch-only, or general post-merge hook point shared with
  `/execute-phase` and `complete delta`?
- Failure mode: advisory vs blocking; how to present results to user
- Check primitives: shell commands only, or also agent-run checks?

## Acceptance sketch

- Project can declare post-merge validation checks that run before the
  generic verification command
- Checks are visible to the user, with pass/fail status
- Failures block auto-merge and escalate to the user per DEC-132-08

## Related

- DEC-132-08 (auto-merge on green) — this hook runs *before* the green
  check used for auto-merge
