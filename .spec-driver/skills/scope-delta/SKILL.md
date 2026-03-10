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
   - `.spec-driver/hooks/doctrine.md`
2. If revision-first is required and missing, stop and run `/shape-revision`.
3. Create delta:
   - From scratch:
     - `uv run spec-driver create delta "<title>" --spec SPEC-XXX --requirement SPEC-XXX.FR-001`
   - From backlog item:
     - `uv run spec-driver create delta --from-backlog ISSUE-XXX`
     - `--from-backlog` auto-populates `context_inputs` and `relations` from the source item.
   - When creating a delta motivated by a backlog item (even without `--from-backlog`), ensure:
     - `context_inputs` includes `type: issue` (or appropriate type) with the backlog item ID
     - `relations` includes `type: relates_to` (or more specific type) with the backlog item ID as target
     - `applies_to.requirements` includes any requirement IDs from the backlog item
4. Ensure delivery bundle is present and usable:
   - `DE-XXX.md`
   - `DR-XXX.md` (if non-trivial change)
   - `IP-XXX.md`
5. Update `DE-XXX.md` to make scope explicit:
   - `applies_to` specs/requirements
   - Context inputs and risks
   - Verification/closure intent
6. You MUST run `/draft-design-revision` before `/plan-phases` unless **explicitly instructed** by the user to skip a DR.
7. Do not treat IP or phase creation as a substitute for missing design. `/plan-phases` comes after DR work, not instead of it.
8. Run `/plan-phases` to create/refine phase sheets before implementation.

Outcomes:
- A delta exists with clear scope and traceability targets.
- A DR has been fleshed out with a robust design, and `DE-XXX` is consistent with it.
- Next step (design/planning/implementation) is explicit.
