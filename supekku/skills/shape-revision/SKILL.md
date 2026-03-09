---
name: shape-revision
description: Shape a spec revision when requirements/responsibilities move. Use this before delta scoping when policy/doctrine requires revision-first flow, or when audit reconciliation shows authority must move.
---
You are establishing the spec-change intent before implementation work.

Inputs:
- A change request that moves/rewrites requirements or responsibilities.
- Candidate source/destination specs and requirement IDs.
- Owning audit, delta, or DR context when this is post-audit reconciliation work.

Process:
1. Read:
   - `.spec-driver/agents/workflow.md`
   - `.spec-driver/agents/policy.md`
   - `.spec-driver/hooks/doctrine.md`
2. Run a doctrine pass before deciding the artifact path:
   - use `ADR-004` to keep revision work inside `audit -> revision -> spec reconcile -> close`
   - use `ADR-005` to keep concepts in memories and procedures in skills
   - use `ADR-008` to treat observed evidence as a trigger for explicit reconciliation, not silent overwrite
   - use `ADR-003` when the change may create a new spec boundary, so you avoid overlapping or competing truths
3. Decide whether the finding really needs a revision:
   - if the current spec is still the right authority surface and the change is only a local wording, coverage, example, or constraint update, stop and patch the existing spec instead
   - if responsibility, requirement ownership, lineage, or spec topology changes, create or update a revision
   - if the change is implementation-only with no spec movement, stop and use `/scope-delta`
4. Close the authorship branch before creating anything new:
   - identify the current authority surface
   - identify the destination authority surface if it must change
   - name the exact reason a patch is insufficient
   - if you cannot explain why the truth must move, you probably do not need a revision yet
5. Create or update the revision:
   - `uv run spec-driver create revision "<summary>" --source SPEC-XXX --destination SPEC-YYY --requirement SPEC-XXX.FR-001`
   - if the revision already exists, update it instead of creating a parallel artefact
6. Author the revision section by section rather than as loose notes:
   - scope and owning context
   - source and destination specs
   - requirement or responsibility movement
   - rationale for the move
   - lifecycle notes and downstream spec updates
   - related deltas, audits, or DRs when known
7. Handle the rare new-spec case inside the revision flow:
   - only justify a new spec when no existing spec can own the reconciled truth cleanly without overlap, competing truths, or topology distortion
   - record that rationale in the revision first
   - then reuse the normal `uv run spec-driver create spec ...` path rather than inventing a separate spec-authoring workflow
   - update the old and new spec links so authority is explicit
8. Keep the revision concrete and section-scoped:
   - prefer explicit source/destination IDs over prose like "move this somewhere better"
   - name affected requirements when known
   - capture why the new boundary is cleaner, not just that it exists
9. If policy implications, unresolved ownership conflicts, or unclear spec boundaries appear, stop and `/consult`.

Outcomes:
- Existing specs are patched directly when revision is unnecessary.
- A revision exists when authority or lineage really changed, and it captures that spec-change intent unambiguously.
- New spec creation, when justified, stays nested under revision rather than becoming a competing workflow.
- Downstream delta/design work can proceed with clear authority.
