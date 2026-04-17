---
id: IP-132-P03
slug: "132-sub_agent_orchestration_skill_for_parallel_implementation-phase-03"
name: "P03 — Integration & verification"
created: "2026-04-16"
updated: "2026-04-17"
status: in-progress
kind: phase
plan: IP-132
delta: DE-132
---

# Phase 03 — Integration & verification

## 1. Objective

Wire skills into the install pipeline and verify end-to-end dispatch.

## 2. Links & References

- **Delta**: DE-132
- **P01 output**: dispatch-worker agent, sub-driver skill
- **P02 output**: dispatch skill

## 3. Entrance Criteria

- [x] P01 + P02 complete
- [x] All skill files exist in canonical locations

## 4. Exit Criteria / Done When

- [x] dispatch and sub-driver in skills.allowlist
- [x] Symlinks created in .claude/skills/ and resolving
- [x] Skills visible in Claude Code session
- [ ] VH-001: Parallel dispatch on real multi-phase IP
- [ ] VH-002: Worktree isolation verified (post-amendment re-run)
- [ ] VH-003: Model routing verified (sonnet/opus)
- [ ] VA-002: Isolation-rule literacy on revised SKILL.md

## 5. Verification

- VH-001/003: Deferred to first real use.
- VH-002: Initial attempt surfaced the stale-worktree failure mode (vk
  DE-105, 2026-04-17). Re-run against clarified DEC-132-02:
  1. Synthesise or select a multi-phase delta where P02 depends on P01's
     state (e.g., a struct-field rename or move).
  2. Invoke `/dispatch` on the delta. Capture the dispatch plan output.
  3. Assert: the plan lists P02's first batch with `main` isolation (not
     `worktree`), and any parallel group correctly uses `worktree`.
  4. On spawn of any worktree batch, assert branch-point check fires and
     matches `git rev-parse HEAD` captured pre-spawn.
  5. On completion, assert no structural merge conflicts of the vk kind
     (stale references to removed/renamed fields).
- VA-001: Skill format compliance confirmed during P01/P02.
- VA-002: Spawn a sonnet agent and give it the revised
  `.spec-driver/skills/dispatch/SKILL.md` (§3 + §6). Ask three questions
  in a single turn:
  1. "Phase P02's first batch depends on P01's committed state. What
     `isolation` kwarg should the orchestrator pass?"
     — Expected answer: omit (main tree).
  2. "Two batches in the same phase touch disjoint files. What
     `isolation` kwarg?"
     — Expected: `isolation="worktree"`.
  3. "The entire phase fits in one batch. What `isolation` kwarg?"
     — Expected: omit (main tree).
  Pass criterion: all three answered correctly with citation to §6.1.
  Failure → the skill text has not closed the ambiguity and needs
  another revision.

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
|--------|-----|-------------|-------|
| [x] | 3.1 | Add to skills.allowlist | dispatch + sub-driver |
| [x] | 3.2 | Create symlinks in .claude/skills/ | Verified resolving |
| [x] | 3.3 | Verify skills load in session | Confirmed in skill list |
| [x] | 3.4 | Create IMPR-029 | Per-skill target filtering backlog |
| [ ] | 3.5 | VH-001: Parallel dispatch test | Deferred to first real use |
| [ ] | 3.6 | VH-002: Worktree isolation test | Re-run post-amendment (§5) |
| [ ] | 3.7 | VH-003: Model routing test | Deferred to first real use |
| [ ] | 3.8 | VA-002: Isolation-rule literacy on revised SKILL.md | See §5 |

## 9. Decisions & Outcomes

- 2026-04-16 — Per-skill agent target filtering not in scope; backlogged
  as IMPR-029. dispatch/sub-driver appear in .agents/skills/ too (harmless).
- 2026-04-16 — VH tests deferred to first real use rather than synthetic
  exercise. Skills are wired and loading; live verification on real work
  will be more meaningful.
- 2026-04-17 — First real use (vk DE-105) surfaced stale-worktree failure
  mode. DR-132 DEC-132-02 clarified (amendment log §9); SKILL.md §3/§6
  tightened; VA-002 added. VH-002 re-runs against clarified rules with
  concrete acceptance steps in §5.

## 11. Wrap-up Checklist

- [x] Integration tasks complete (allowlist, symlinks, session loading)
- [ ] VH verification deferred — record evidence on first real dispatch
- [x] IMPR-029 created for follow-up
