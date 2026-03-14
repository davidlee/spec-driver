---
id: IP-055.PHASE-11
slug: "055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-11"
name: IP-055 Phase 11
created: "2026-03-08"
updated: "2026-03-08"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-11
plan: IP-055
delta: DE-055
objective: >-
  Make `.spec-driver` commit guidance configurable while defaulting to
  frequent, small workflow-artifact commits and a clean repo.
entrance_criteria:
- DE-055 remains in-progress and commit policy is still an open workflow question.
- Current doctrine and execution/handoff skills have been reviewed for commit guidance gaps.
exit_criteria:
- Repo doctrine records the local default for `.spec-driver` commit behavior.
- Relevant packaged skills direct agents to follow doctrine and avoid mixed uncommitted piles by default.
- Generated skill copies are resynced and verification evidence is recorded.
verification:
  tests:
  - uv run spec-driver skills sync
  - uv run pytest supekku/scripts/lib/skills/sync_test.py supekku/scripts/lib/install_test.py supekku/cli/skills_test.py
  evidence:
  - 2026-03-08: `uv run spec-driver skills sync` passed; `.spec-driver/skills` refreshed and both agent targets reported all skill symlinks `ok`.
  - 2026-03-08: `uv run pytest supekku/scripts/lib/skills/sync_test.py supekku/scripts/lib/install_test.py supekku/cli/skills_test.py` passed (148 tests).
  - 2026-03-08: `mem.pattern.git.spec-driver-commit-cleanliness` surfaced under `.spec-driver/hooks/doctrine.md` plus `git commit` query.
tasks:
- id: '11.1'
  title: Record repo-local default in doctrine hook
  status: completed
  notes: local doctrine now prefers frequent, small `.spec-driver` commits with a clean-repo bias, whether they land with code or separately.
- id: '11.2'
  title: Update packaged skills to respect doctrine and keep workflow artefacts from accumulating
  status: completed
  notes: execute-phase, notes, close-change, and continuation updated.
- id: '11.3'
  title: Resync installed skills and verify propagation
  status: completed
  notes: sync, targeted tests, and memory-surface sanity check all passed on 2026-03-08.
risks:
- risk: Package skills may become too prescriptive for repos with different commit habits.
  mitigation: keep the policy source in doctrine; package skills point to doctrine and only state a soft default.
- risk: Agents may still avoid committing during active work and push the problem into handoff.
  mitigation: mention commit-state explicitly in notes and continuation guidance.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-11
```

# Phase 11 - Define configurable commit guidance for .spec-driver files

## 1. Objective

Make `.spec-driver` commit guidance configurable while defaulting to frequent,
small workflow-artifact commits and a clean repo.

## 2. Links & References

- **Delta**: DE-055
- **Design Revision Sections**:
  - `DR-055` commit-policy open question and customisation seam
- **Specs / PRODs**:
  - `PROD-002`
  - `PROD-011`
  - `SPEC-151`
- **Support Docs**:
  - `ADR-004`
  - `ADR-005`
  - `.spec-driver/hooks/doctrine.md`

## 3. Entrance Criteria

- [x] DE-055 remains `in-progress`
- [x] Current doctrine and skill surfaces reviewed for commit guidance gaps

## 4. Exit Criteria / Done When

- [x] Repo doctrine records the local default for `.spec-driver` commit behavior
- [x] Relevant packaged skills direct agents to follow doctrine and avoid mixed uncommitted piles by default
- [x] Generated skill copies are resynced and verification evidence is recorded

## 5. Verification

- `uv run spec-driver skills sync`
- `uv run pytest supekku/scripts/lib/skills/sync_test.py supekku/scripts/lib/install_test.py supekku/cli/skills_test.py`
- Evidence: sync output, targeted test pass, notes update

## 6. Assumptions & STOP Conditions

- Assumptions: doctrine hooks are the right per-repo customisation seam for commit policy, and package skills should remain generic.
- STOP when: the user wants a hard config/runtime enforcement mechanism instead of skill-layer guidance.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID   | Description                                                                  | Parallel? | Notes                                                     |
| ------ | ---- | ---------------------------------------------------------------------------- | --------- | --------------------------------------------------------- |
| [x]    | 11.1 | Record repo-local default in doctrine hook                                   | [ ]       | frequent, small `.spec-driver` commit preference recorded |
| [x]    | 11.2 | Update packaged skills to respect doctrine and avoid mixed uncommitted piles | [ ]       | execute-phase, notes, close-change, continuation updated  |
| [x]    | 11.3 | Resync installed skills and verify propagation                               | [ ]       | sync, targeted tests, and memory surface check passed     |

### Task Details

- **11.1 Description**
  - **Design / Approach**: put the repo-specific default in the user-owned doctrine hook so the behavior is configurable without forking packaged skills.
  - **Files / Components**: `.spec-driver/hooks/doctrine.md`
  - **Testing**: verify skill guidance references doctrine and syncs cleanly
  - **Observations & AI Notes**: this matches the existing generated-guidance plus hook-stub customisation model and lets the repo bias toward cleanliness over rigid commit bundling.
  - **Commits / References**: uncommitted work

- **11.2 Description**
  - **Design / Approach**: teach execution and handoff skills to follow doctrine, prefer small `.spec-driver` commits, and call out pending commit state explicitly without insisting on a separate workflow-only commit.
  - **Files / Components**: `supekku/skills/execute-phase/SKILL.md`, `supekku/skills/notes/SKILL.md`, `supekku/skills/close-change/SKILL.md`, `supekku/skills/continuation/SKILL.md`
  - **Testing**: verify via skill sync and generated copies
  - **Observations & AI Notes**: the package layer should say where the policy lives and what the soft default is, not own repo-specific commit wording.
  - **Commits / References**: uncommitted work

- **11.3 Description**
  - **Design / Approach**: resync installed skill projections and run targeted sync/install/CLI skill tests.
  - **Files / Components**: `.spec-driver/skills/**`, `.spec-driver/AGENTS.md`, sync/install test surfaces
  - **Testing**: `uv run spec-driver skills sync`; targeted pytest invocation
  - **Observations & AI Notes**: sync refreshed the checked-in skill projections cleanly; targeted tests and commit-policy memory retrieval stayed green after shifting from split-first to cleanliness-first guidance.
  - **Commits / References**: uncommitted work

_(Repeat detail blocks per task as needed)_

## 8. Risks & Mitigations

| Risk                                                                  | Mitigation                                                               | Status     |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------ | ---------- |
| Packaged skills overfit this repo's commit habit                      | Keep the hard rule in doctrine and only a soft default in package skills | Mitigated  |
| Agents still leave `.spec-driver` changes uncommitted through handoff | Make pending commit state explicit in notes and continuation             | Monitoring |

## 9. Decisions & Outcomes

- `2026-03-08` - Put `.spec-driver` commit policy in the doctrine hook and make skills defer to doctrine. Rationale: this keeps the behavior configurable per repo while letting this repo prefer frequent, small workflow-artifact commits and a clean tree.
- `2026-03-08` - Refined the default from "workflow-only commit first" to "keep the worktree clean; commit `.spec-driver` changes either with code or separately, whichever comes first." Rationale: cleanliness and short conventional commits matter more than enforcing a rigid split.

## 10. Findings / Research Notes

- DE-055 already identified commit policy as an unresolved workflow question.
- There was no existing memory or skill guidance telling agents to prefer prompt `.spec-driver` commits over waiting for perfect relatedness.
- The current repo customisation model already points to `.spec-driver/hooks/doctrine.md` as the right place for local policy.
- Created `mem.pattern.git.spec-driver-commit-cleanliness` so the local commit convention is retrievable without re-reading doctrine or DE-055 notes.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
