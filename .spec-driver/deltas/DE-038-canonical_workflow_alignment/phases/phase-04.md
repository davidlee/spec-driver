---
id: IP-038.PHASE-04
slug: "038-canonical_workflow_alignment-phase-04"
name: IP-038 Phase 04
created: "2026-03-03"
updated: "2026-03-03"
status: completed
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
    status: done
  - id: P4.2
    title: Patch scope metadata on workflow-critical memory set.
    status: done
  - id: P4.3
    title: Re-run query set and validate improved ranking.
    status: done
  - id: P4.4
    title: Finalize notes and handoff.
    status: done
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
  - `/home/david/dev/spec-driver/supekku/skills/maintaining-memory/SKILL.md`
  - `/home/david/dev/spec-driver/supekku/skills/retrieving-memory/SKILL.md`

## 3. Entrance Criteria

- [x] Phase 03 outcomes reviewed for skill-level wording dependencies
- [x] Baseline noisy query set captured
- [x] Candidate memory set selected for scope tuning

## 4. Exit Criteria / Done When

- [x] Scope metadata updated on target memories
- [x] Baseline vs after query set shows improved operational surfacing
- [x] Residual risks documented for future maintenance

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

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                   | Parallel? | Notes                                                                                                     |
| ------ | --- | ------------------------------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------- |
| [x]    | 4.1 | Capture baseline query outputs and identify noisy top results | [ ]       | All three baseline queries returned near-identical top ordering with broad conceptual records leading     |
| [x]    | 4.2 | Apply scope metadata updates to target memories               | [ ]       | Added/tuned `scope.commands`/`scope.paths` on all eight target memories                                   |
| [x]    | 4.3 | Re-run query set and compare ordering                         | [ ]       | `coverage-gate`/`status-enums` now lead close-out/path contexts; `core-loop` leads `create delta` context |
| [x]    | 4.4 | Finalize notes and update handoff guidance                    | [ ]       | Residual ranking noise captured below and propagated to notes                                             |

## 8. Risks & Mitigations

| Risk                                           | Mitigation                                                                           | Status              |
| ---------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------- |
| Operational memories still not surfacing first | Increase scope specificity (`scope.commands` + `scope.paths`) and re-check query set | Partially mitigated |
| Concept memories become undiscoverable         | Keep tags/provenance unchanged; tune scope only for command/path contexts            | Mitigated           |

## 9. Decisions & Outcomes

- `2026-03-03` - Phase added to explicitly address retrieval-precision risk surfaced in phase 02 notes.
- `2026-03-03` - Scope tuning completed on the phase target memory set using command/path anchors only; no runtime behavior changes.

## 10. Findings / Research Notes

- Baseline query outputs (top results before scope tuning):
  - `-c "uv run spec-driver complete delta"`: `philosophy` ranked #1; operational memories were interleaved lower.
  - `-c "uv run spec-driver create delta"`: `philosophy` ranked #1; `core-loop` did not lead.
  - `-p complete_delta.py -p coverage_check.py`: `philosophy` ranked #1; operational ordering was noisy.
- Scope updates applied to target set:
  - `mem.pattern.spec-driver.core-loop`
  - `mem.concept.spec-driver.revision`
  - `mem.pattern.spec-driver.delta-completion`
  - `mem.concept.spec-driver.posture`
  - `mem.signpost.spec-driver.ceremony`
  - `mem.concept.spec-driver.ceremony.settler`
  - `mem.fact.spec-driver.coverage-gate`
  - `mem.fact.spec-driver.status-enums`
- After-state query outputs (same command set, same limits):
  - `-c "uv run spec-driver complete delta"`: `coverage-gate` #1, `status-enums` #2, `delta-completion` #5.
  - `-c "uv run spec-driver create delta"`: `core-loop` #1.
  - `-p complete_delta.py -p coverage_check.py`: `coverage-gate` #1, `status-enums` #2, `delta-completion` #5.
- Residual ranking noise:
  - `mem.concept.spec-driver.philosophy` remains top-3 in close-out/path contexts due high base priority and no scope tuning in this phase target.
  - Follow-up (optional): evaluate adding explicit scope to non-target broad conceptual memories if stricter operational-first ranking is required.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase (if any)
