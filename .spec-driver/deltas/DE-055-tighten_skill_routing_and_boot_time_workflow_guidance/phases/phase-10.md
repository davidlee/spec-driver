---
id: IP-055.PHASE-10
slug: 055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-10
name: IP-055 Phase 10
created: '2026-03-08'
updated: '2026-03-08'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-10
plan: IP-055
delta: DE-055
objective: >-
  Make scoped memory retrieval before subsystem work and memory capture during
  phase or delta wrap-up explicit in the execution skills.
entrance_criteria:
- DE-055 remains in-progress and governs the routing/workflow guidance changes.
- Existing memory and execution skills have been reviewed for current gaps.
exit_criteria:
- Relevant skill sources require scoped retrieval before touching a subsystem.
- Wrap-up skills require explicit review for durable memory capture candidates.
- Generated skill copies are resynced and verification evidence is recorded.
verification:
  tests:
  - uv run spec-driver skills sync
  - uv run pytest supekku/scripts/lib/skills/sync_test.py supekku/scripts/lib/install_test.py supekku/cli/skills_test.py
  evidence:
  - 2026-03-08: `uv run spec-driver skills sync` passed; `.spec-driver/skills` refreshed and both agent targets reported all skill symlinks `ok`.
  - 2026-03-08: `uv run pytest supekku/scripts/lib/skills/sync_test.py supekku/scripts/lib/install_test.py supekku/cli/skills_test.py` passed (148 tests).
tasks:
- id: '10.1'
  title: Update retrieval and execution skills for scoped memory lookup
  status: completed
  notes: retrieving-memory, execute-phase, and implement now make file-scoped pre-work memory queries explicit.
- id: '10.2'
  title: Update wrap-up skills for memory capture
  status: completed
  notes: notes, capturing-memory, and close-change now require checking for durable memory candidates during wrap-up.
- id: '10.3'
  title: Resync installed skills and verify propagation
  status: completed
  notes: `uv run spec-driver skills sync` and targeted pytest both passed on 2026-03-08.
risks:
- risk: Guidance-only changes may drift if generated skill copies are not resynced.
  mitigation: Run skill sync immediately after editing and verify copied output.
- risk: Memory-capture prompts may become noisy if they ask for memory creation on every small unit.
  mitigation: Keep wording focused on durable facts, patterns, and gotchas that save future rediscovery.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-10
```

# Phase 10 - Improve memory retrieval and capture workflow guidance

## 1. Objective

Make scoped memory retrieval before subsystem work and memory capture during
phase or delta wrap-up explicit in the execution skills.

## 2. Links & References

- **Delta**: DE-055
- **Design Revision Sections**:
  - `DR-055` routing boundary and guidance-layer decisions
- **Specs / PRODs**:
  - `PROD-002`
  - `PROD-011`
  - `SPEC-151`
- **Support Docs**:
  - `ADR-004`
  - `ADR-005`
  - `PROB-004`
  - `mem.pattern.spec-driver.core-loop`

## 3. Entrance Criteria

- [x] DE-055 remains `in-progress`
- [x] Existing memory and execution skills reviewed for current gaps

## 4. Exit Criteria / Done When

- [x] Relevant skill sources require scoped retrieval before touching a subsystem
- [x] Wrap-up skills require explicit review for durable memory capture candidates
- [x] Generated skill copies are resynced and verification evidence is recorded

## 5. Verification

- `uv run spec-driver skills sync`
- `uv run pytest supekku/scripts/lib/skills/sync_test.py supekku/scripts/lib/install_test.py supekku/cli/skills_test.py`
- Evidence: sync output, targeted test pass, notes update

## 6. Assumptions & STOP Conditions

- Assumptions: the right place for this behavior is the canonical skill layer, not a new runtime hook in this phase.
- STOP when: implementation reveals the skill-only approach conflicts with existing doctrine or needs schema/runtime changes.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID   | Description                                                    | Parallel? | Notes                                                   |
| ------ | ---- | -------------------------------------------------------------- | --------- | ------------------------------------------------------- |
| [x]    | 10.1 | Update retrieval and execution skills for scoped memory lookup | [ ]       | retrieving-memory, execute-phase, and implement updated |
| [x]    | 10.2 | Update wrap-up skills for memory capture                       | [ ]       | notes, capturing-memory, and close-change updated       |
| [x]    | 10.3 | Resync installed skills and verify propagation                 | [ ]       | sync and targeted tests passed                          |

### Task Details

- **10.1 Description**
  - **Design / Approach**: make scoped `spec-driver list memories -p ...` retrieval explicit before deep subsystem work so `scope.globs` memories surface through concrete file queries.
  - **Files / Components**: `supekku/skills/retrieving-memory/SKILL.md`, `supekku/skills/execute-phase/SKILL.md`, `supekku/skills/implement/SKILL.md`
  - **Testing**: verify via skill sync and generated copies
  - **Observations & AI Notes**: execute-path guidance was the right leverage point; no new routing skill needed for this behavior.
  - **Commits / References**: uncommitted work

- **10.2 Description**
  - **Design / Approach**: make phase and delta wrap-up explicitly review for durable facts, patterns, and gotchas that deserve memory capture or maintenance.
  - **Files / Components**: `supekku/skills/notes/SKILL.md`, `supekku/skills/capturing-memory/SKILL.md`, `supekku/skills/close-change/SKILL.md`
  - **Testing**: verify via skill sync and generated copies
  - **Observations & AI Notes**: keeping the prompt in wrap-up skills preserves ADR-005's skill-owned procedural guidance layer.
  - **Commits / References**: uncommitted work

- **10.3 Description**
  - **Design / Approach**: resync installed skill projections and run targeted sync/install/CLI skill tests.
  - **Files / Components**: `.spec-driver/skills/**`, `.spec-driver/AGENTS.md`, sync/install test surfaces
  - **Testing**: `uv run spec-driver skills sync`; targeted pytest invocation
  - **Observations & AI Notes**: sync refreshed the checked-in skill projections cleanly; targeted test coverage stayed green.
  - **Commits / References**: uncommitted work

_(Repeat detail blocks per task as needed)_

## 8. Risks & Mitigations

| Risk                                                          | Mitigation                                              | Status     |
| ------------------------------------------------------------- | ------------------------------------------------------- | ---------- |
| Guidance change does not propagate to checked-in skill copies | Run skill sync before closing the phase                 | Mitigated  |
| Wrap-up prompt becomes too noisy                              | Keep wording focused on durable, reusable guidance only | Monitoring |

## 9. Decisions & Outcomes

- `2026-03-08` - Land this as a skill-layer improvement inside DE-055 rather than a runtime hook or new subsystem. Rationale: the user asked for a skills-based solution, and ADR-005 says skills own procedural guidance.

## 10. Findings / Research Notes

- Existing execution skills did not require scoped memory lookup before touching a subsystem.
- Existing wrap-up skills did not explicitly require checking for durable memory candidates before phase or delta close-out.
- `PROB-004` remains relevant prior art for a later runtime-hook solution, but this phase intentionally stays in the skill layer.
- Created `mem.pattern.skills.memory-retrieval-and-wrapup` so the new workflow is retrievable without re-reading DE-055 notes.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
