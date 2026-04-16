---
id: IP-132-P02
slug: "132-sub_agent_orchestration_skill_for_parallel_implementation-phase-02"
name: P02 — Orchestrator skill
created: "2026-04-16"
updated: "2026-04-16"
status: completed
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

- [x] `.spec-driver/skills/dispatch/SKILL.md` exists, follows conventions
- [x] Skill covers all DR-132 §3.1–3.7 orchestration flow
- [x] Prompt construction template references dispatch-worker capabilities

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
| [x] | 2.1 | Write dispatch SKILL.md | 302 lines, covers DR §3.1–3.7 |

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

- 2026-04-16 — Skill came in at 302 lines (under 400-line threshold).
  Structured as 10 numbered sections matching the orchestration flow.
  Policy digest in §5.1 uses concrete `just` commands from this project's
  CLAUDE.md but the pattern is generic enough for other projects.

## 10. Findings / Research Notes

- The prompt construction template (§5) is the most complex section. It
  requires the orchestrator to read and distil multiple source files. This
  is inherent to the design — the orchestrator bears the context assembly
  burden so workers don't have to.
- The merge section (§9) is deliberately conservative: attempt merge, run
  checks, escalate on failure. No automatic conflict resolution.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (DR coverage check in notes)
- [x] Hand-off notes to P03 (in delta notes.md)
