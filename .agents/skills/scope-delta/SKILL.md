---
name: scope-delta
description: Scope intentional change as a delta. Define applies-to specs/requirements, risks, and closure targets before implementation.
---
You are converting intent into a concrete change bundle.

Inputs:
- Target requirements/specs, or a backlog item.
- Policy/doctrine constraints (including any revision-first gate).

Process:
1. Read:
   - `.spec-driver/agents/workflow.md`
   - `.spec-driver/agents/policy.md`
   - `.spec-driver/doctrine.md`
2. If revision-first is required and missing, stop and run `/shape-revision`.
3. Create delta:
   - From scratch:
     - `uv run spec-driver create delta "<title>" --spec SPEC-XXX --requirement SPEC-XXX.FR-001`
   - From backlog item:
     - `uv run spec-driver create delta --from-backlog ISSUE-XXX`
4. Ensure delivery bundle is present and usable:
   - `DE-XXX.md`
   - `DR-XXX.md` (if non-trivial change)
   - `IP-XXX.md`
   - At least one phase sheet (create via `/plan-phases`)
5. Update `DE-XXX.md` to make scope explicit:
   - `applies_to` specs/requirements
   - Context inputs and risks
   - Verification/closure intent
6. If design is non-trivial, run `/draft-design-revision`.
7. Run `/plan-phases` to create/refine phase sheets before implementation.

Outcomes:
- A delta exists with clear scope and traceability targets.
- Next step (design/planning/implementation) is explicit.
