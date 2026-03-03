---
name: shape-revision
description: Shape a spec revision when requirements/responsibilities move. Use this before delta scoping when policy/doctrine requires revision-first flow.
---
You are establishing the spec-change intent before implementation work.

Inputs:
- A change request that moves/rewrites requirements or responsibilities.
- Candidate source/destination specs and requirement IDs.

Process:
1. Read:
   - `.spec-driver/agents/workflow.md`
   - `.spec-driver/agents/policy.md`
   - `.spec-driver/doctrine.md`
2. Decide if revision is required:
   - If policy/doctrine says revision-first, create/update a revision.
   - If the change is implementation-only with no spec movement, stop and use `/scope-delta`.
3. Create a revision:
   - `uv run spec-driver create revision "<summary>" --source SPEC-XXX --destination SPEC-YYY --requirement SPEC-XXX.FR-001`
4. Update the generated `RE-XXX.md`:
   - New/changed requirements (when applicable)
   - Requirement moves and rationale
   - Lifecycle notes for affected requirements
   - Links to related specs/deltas if known
5. If policy implications appear, stop and `/consult`.

Outcomes:
- A revision exists and captures spec-change intent unambiguously.
- Downstream delta/design work can proceed with clear authority.
