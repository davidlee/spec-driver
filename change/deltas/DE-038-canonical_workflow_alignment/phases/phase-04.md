---
id: IP-038.PHASE-04
slug: 038-canonical_workflow_alignment-phase-04
name: IP-038 Phase 04
created: '2026-03-03'
updated: '2026-03-03'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-038.PHASE-04
plan: IP-038
delta: DE-038
objective: >-
  Execute memory retrieval-precision pass so workflow-critical command/path
  queries surface operational records ahead of broad conceptual records.
entrance_criteria:
  - Phase 03 skill review outcomes are captured or ready for carry-forward.
  - Memory target set from phase 02 is available with current wording/provenance.
  - Baseline noisy query examples are recorded for comparison.
exit_criteria:
  - Target memories include sensible scope metadata (`scope.commands`/`scope.paths`) where needed.
  - Baseline and after-state query outputs show improved surfacing of operational memories.
  - Notes capture any residual retrieval noise and follow-up recommendations.
verification:
  tests:
    - VA retrieval precision readback against baseline command/path queries.
  evidence:
    - Diffs for memory files updated with scope metadata.
    - Before/after query snapshots recorded in phase notes.
tasks:
  - id: P4.1
    title: Baseline query capture for retrieval noise.
    status: todo
  - id: P4.2
    title: Patch scope metadata on workflow-critical memory set.
    status: todo
  - id: P4.3
    title: Re-run query set and validate improved ranking.
    status: todo
  - id: P4.4
    title: Finalize notes and handoff.
    status: todo
risks:
  - Over-scoping may hide useful conceptual records from discovery.
  - Inconsistent scope conventions across memories may create new retrieval bias.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-038.PHASE-04
```

# Phase 04 - Retrieval Precision Pass

## 1. Objective
Reduce memory retrieval noise by tuning scope metadata so command/path-context
queries prioritize actionable workflow records without removing conceptual context.

## 2. Links & References
- **Delta**: DE-038
- **Design Revision Sections**:
  - [DR-038.md](../DR-038.md) - retrieval precision pass intent
  - [workflow-research.md](../workflow-research.md) - command/runtime sources for query contexts
- **Support Docs**:
  - [IP-038.md](../IP-038.md)
  - [notes.md](../notes.md)
  - `/home/david/dev/spec-driver/.agents/skills/maintaining-memory/SKILL.md`

## 3. Entrance Criteria
- [ ] Phase 03 outcomes reviewed for skill-level wording dependencies
- [ ] Baseline noisy query set captured
- [ ] Candidate memory set selected for scope tuning

## 4. Exit Criteria / Done When
- [ ] Scope metadata updated on target memories
- [ ] Baseline vs after query set shows improved operational surfacing
- [ ] Residual risks documented for future maintenance

## 5. Verification
- Verification type: VA (retrieval quality and ranking coherence)
- Tooling/commands:
  - `uv run spec-driver list memories -c "uv run spec-driver complete delta" --match-tag spec-driver --limit 12 --format tsv`
  - `uv run spec-driver list memories -c "uv run spec-driver create delta" --match-tag spec-driver --limit 12 --format tsv`
  - `uv run spec-driver list memories -p supekku/scripts/complete_delta.py -p supekku/scripts/lib/changes/coverage_check.py --match-tag spec-driver --limit 12 --format tsv`
- Evidence to capture:
  - before/after query outputs
  - memory diffs showing scope updates
  - notes summary for unresolved ranking noise

## 6. Assumptions & STOP Conditions
- Assumptions:
  - Scope tuning is metadata-only and does not alter command/runtime behavior.
  - Current memory wording/provenance from phase 02 remains valid during this pass.
- STOP when:
  - scope tuning would require broad reclassification of memory types/statuses.
  - retrieval behavior cannot be improved without changing ranking algorithm (out of scope for DE-038).

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 4.1 | Capture baseline query outputs and identify noisy top results | [ ] | Use command/path contexts from phase-02 findings |
| [ ] | 4.2 | Apply scope metadata updates to target memories | [ ] | Prioritize `delta-completion`, `coverage-gate`, `status-enums`, and related sequencing memories |
| [ ] | 4.3 | Re-run query set and compare ordering | [ ] | Confirm operational memories rank above broad conceptual records in relevant contexts |
| [ ] | 4.4 | Finalize notes and update handoff guidance | [ ] | Record residual noise and follow-up recommendations |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Operational memories still not surfacing first | Increase scope specificity (`scope.commands` + `scope.paths`) and re-check query set | Open |
| Concept memories become undiscoverable | Keep tags/provenance unchanged; tune scope only for command/path contexts | Open |

## 9. Decisions & Outcomes
- `2026-03-03` - Phase added to explicitly address retrieval-precision risk surfaced in phase 02 notes.

## 10. Findings / Research Notes
- To be populated during execution with before/after query evidence and scope rationale.

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
