---
id: IP-132-P01
slug: "132-sub_agent_orchestration_skill_for_parallel_implementation-phase-01"
name: P01 — Worker foundation
created: "2026-04-16"
updated: "2026-04-16"
status: completed
kind: phase
plan: IP-132
delta: DE-132
---

# Phase 01 — Worker foundation

## 1. Objective

Create the static context layer: the dispatch-worker agent definition and
tourist skill that give sub-agents spec-driver fluency without ceremony.

## 2. Links & References

- **Delta**: DE-132
- **Design Revision Sections**: DR-132 §3.6 (Sub-Agent Context Architecture)
- **Specs**: PROD-011
- **Key decisions**: DEC-132-06 (tourist skill), DEC-132-09 (agent definition)

## 3. Entrance Criteria

- [x] DR-132 approved with context architecture design
- [x] Platform mechanics confirmed (subagent docs reviewed)

## 4. Exit Criteria / Done When

- [x] `.claude/agents/dispatch-worker.md` exists with valid frontmatter
- [x] `.spec-driver/skills/sub-driver/SKILL.md` exists, follows conventions
- [x] Injected skill token budget verified (~3k for all 4 skills)
- [ ] Agent definition loads without errors (deferred to P03 integration)

## 5. Verification

- VA-001 (partial): Review agent + skill files against project conventions
- Token count: estimate via character count / 4 heuristic
- Agent load: check via `claude agents` or `/agents` command

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `skills:` frontmatter in agent definitions works as documented
  - Existing skills (retrieving-memory, capturing-memory, notes) can be
    loaded by subagents without modification
- STOP when:
  - `skills:` injection doesn't work as expected (needs investigation)
  - Token budget significantly over ~8k (need to trim tourist skill)

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
|--------|-----|-------------|-------|
| [x] | 1.1 | Write dispatch-worker agent definition | `.claude/agents/dispatch-worker.md` |
| [x] | 1.2 | Write sub-driver tourist skill | `.spec-driver/skills/sub-driver/SKILL.md` |
| [x] | 1.3 | Verify token budget | ~3k total (well under 6.5k target) |

### Task Details

- **1.1 Write dispatch-worker agent definition**
  - **Files**: `.claude/agents/dispatch-worker.md`
  - **Design**: DR-132 §3.6.5 — frontmatter (name, description, tools,
    model, permissionMode, skills) + body (task-generic system prompt,
    completion protocol)
  - **Key content**: Body describes how to work (small coherent units,
    lint/test before reporting, structured return summary). Does NOT
    contain task-specific context — that comes from orchestrator prompt.

- **1.2 Write sub-driver tourist skill**
  - **Files**: `.spec-driver/skills/sub-driver/SKILL.md`
  - **Design**: DR-132 §3.6.4 — must contain:
    - Pointer to `.spec-driver/agents/exec.md` for invocation convention
    - Mini glossary: VT (verification test), VA (verification by agent),
      VH (verification by human), FR-xxx (functional req), NF-xxx
      (non-functional req), DE/DR/IP/phase identifiers
    - Phase sheet task status update commands
    - Governance boundary recognition (flag, don't resolve)
    - What NOT to do (no deltas, revisions, audits, ceremony skills)
  - **Budget**: ~2k tokens target

- **1.3 Verify token budget**
  - Estimate combined token count of sub-driver skill +
    retrieving-memory + capturing-memory + notes
  - Target: ~6.5k total. Warn if >8k.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| sub-driver skill too large | Trim to essentials; glossary and exec.md pointer are compact | open |
| skills: injection untested in this project | Test in P03; if broken, fall back to inline prompt | open |

## 9. Decisions & Outcomes

- 2026-04-16 — Token budget came in at ~3k (vs 6.5k estimate). The earlier
  estimate double-counted: skills are smaller than expected, and the chars/4
  heuristic is conservative for structured markdown.

## 10. Findings / Research Notes

- Agent definition body is ~676 tokens. Completion protocol template in the
  body adds structure but is worth the cost for consistent return summaries.
- sub-driver skill is compact at ~600 tokens. The glossary + commands +
  boundaries format works well. The `exec.md` pointer avoids duplicating
  invocation convention.
- capturing-memory is the largest injected skill at ~1.25k tokens. Most of
  that is confidence calibration and scope metadata guidance — useful for
  workers since they may discover genuine gotchas.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied (agent load deferred to P03 — file-level criteria met)
- [x] Verification evidence stored (token budget in §9)
- [x] Hand-off notes to P02 (in delta notes.md)
