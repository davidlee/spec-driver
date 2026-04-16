---
id: IP-132-P02
slug: "132-sub_agent_orchestration_skill_for_parallel_implementation-phase-02"
name: P02 — Orchestrator skill
created: "2026-04-16"
updated: "2026-04-16"
status: in-progress
kind: phase
plan: IP-132
delta: DE-132
---

# Phase 02 — Orchestrator skill

## 1. Objective

Write the `/dispatch` skill — the dynamic coordination layer that reads an
IP, analyses parallelism, batches tasks, constructs sub-agent prompts,
dispatches workers, collects results, reviews, and merges.

## 2. Links & References

- **Delta**: DE-132
- **Design Revision Sections**: DR-132 §3.1–3.7 (full orchestration model)
- **Specs**: PROD-011
- **Key decisions**: DEC-132-01 (batching), DEC-132-02 (worktree), DEC-132-03
  (peer), DEC-132-05 (adaptive review), DEC-132-07 (non-interactive),
  DEC-132-08 (auto-merge)
- **P01 output**: dispatch-worker agent + sub-driver skill

## 3. Entrance Criteria

- [x] P01 complete — worker foundation exists
- [x] DR-132 covers all orchestration sections

## 4. Exit Criteria / Done When

- [ ] `.spec-driver/skills/dispatch/SKILL.md` exists, follows conventions
- [ ] Skill covers all DR-132 §3.1–3.7 orchestration flow
- [ ] Prompt construction template references dispatch-worker capabilities

## 5. Verification

- VA-001 (partial): Review skill against project SKILL.md conventions
- Manual read-through: does the orchestration flow cover all DR sections?

## 6. Assumptions & STOP Conditions

- Assumptions:
  - A single SKILL.md file can contain the full orchestration logic
  - The orchestrator runs in the main agent context with full tool access
- STOP when:
  - Skill exceeds ~400 lines (may need structural rethink)
  - Design ambiguity surfaces that DR-132 doesn't address

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
|--------|-----|-------------|-------|
| [ ] | 2.1 | Write dispatch SKILL.md | Full orchestration flow |

### Task Details

- **2.1 Write dispatch SKILL.md**
  - **Files**: `.spec-driver/skills/dispatch/SKILL.md`
  - **Design**: DR-132 §3.1–3.7. The skill must implement:
    1. **Entry** (§3.1): Read IP, DR, phase sheets for the given delta
    2. **Analysis** (§3.2–3.3): Build dependency graph, identify parallelism,
       estimate token costs, pack into batches
    3. **Model routing** (§3.4): Assign sonnet/opus per batch based on
       complexity signals
    4. **Dispatch plan**: Present to user for approval before executing
    5. **Context assembly** (§3.6.2): For each batch, construct prompt with
       policy digest (from CLAUDE.md + doctrine.md), design context (DR
       excerpts), pre-fetched memories, task scope + file scope
    6. **Execution** (§3.5): Spawn dispatch-worker agents via Agent tool
       with appropriate isolation and model parameters
    7. **Collection**: Gather structured summaries from completed workers
    8. **Review** (§3.7): Batch review at phase boundary; tighter if
       warranted. Aggregate AC evidence.
    9. **Merge** (DEC-132-08): Auto-merge worktree branches on green,
       escalate conflicts
    10. **Reporting**: Surface results, blockers, governance concerns to user.
        Update notes.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Skill too long for single file | Focus on structure/flow, not edge cases | open |
| Prompt construction template hard to maintain | Keep it readable with clear sections | open |

## 9. Decisions & Outcomes

_(populated during execution)_

## 10. Findings / Research Notes

_(populated during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to P03
