---
id: IP-038.PHASE-01
slug: 038-canonical_workflow_alignment-phase-01
name: IP-038 Phase 01
created: '2026-03-03'
updated: '2026-03-03'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-038.PHASE-01
plan: IP-038
delta: DE-038
objective: >-
  Freeze the DE-038 documentation contract so strict-mode policy, coverage precedence,
  and code-truth wording are internally coherent before memory/skill updates.
entrance_criteria:
  - DE-038, DR-038, and workflow-research draft updates are present in the bundle.
  - Strict-mode baseline direction is agreed (hard-fail non-canonical paths).
  - Gaps document exists in the delta bundle.
exit_criteria:
  - DE-038, DR-038, and workflow-research align on strict_mode contract and terminology.
  - Recommended v1 coverage precedence and mixed-status warning posture are documented.
  - Remaining open questions are narrowed to follow-up feasibility/scope items.
verification:
  tests:
    - VA doc coherence pass against code truth sources listed in workflow-research.
  evidence:
    - Updated DE-038/DR-038/workflow-research with line-citable strict-mode contract language.
    - Updated gaps-to-adoption and notes records for this phase.
tasks:
  - id: P1.1
    title: Align strict_mode contract language across DE/DR/research.
    status: done
  - id: P1.2
    title: Add v1 coverage precedence and mixed-status warning policy.
    status: done
  - id: P1.3
    title: Create IP-038 phase sheet and prefill contract-freeze checklist.
    status: done
risks:
  - Policy language drifts between artifacts and reintroduces ambiguity.
  - Overstating runtime enforcement in documentation before implementation.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-038.PHASE-01
```

# Phase 01 - Contract Freeze

## 1. Objective

Freeze DE-038 policy/doc language so the strict-mode contract and follow-up implementation surface are clear before memory and skill review phases.

## 2. Links & References

- **Delta**: DE-038
- **Design Revision Sections**:
  - [DR-038.md](../DR-038.md) - strict-mode contract and enforcement touchpoints
  - [workflow-research.md](../workflow-research.md) - path matrix and policy detail
- **Specs / PRODs**:
  - N/A (documentation/design delta; no direct requirement implementation in this phase)
- **Support Docs**:
  - [DE-038.md](../DE-038.md)
  - [gaps-to-adoption.md](../gaps-to-adoption.md)
  - [notes.md](../notes.md)

## 3. Entrance Criteria

- [x] DE-038, DR-038, and workflow-research drafts exist in the bundle
- [x] Strict-mode baseline direction agreed: hard-fail non-canonical paths
- [x] Gaps document exists in the bundle

## 4. Exit Criteria / Done When

- [x] DE/DR/research are coherent on strict_mode contract wording
- [x] v1 coverage precedence + mixed-status warning policy is documented
- [x] Open questions reduced to feasibility/scope follow-ups only

## 5. Verification

- Verification type: VA (documentation/code-truth review)
- Tooling/commands:
  - `nl -ba` and `rg -n` spot checks across DE/DR/research and source-of-truth scripts
  - `uv run spec-driver create phase ...` scaffold command validation
- Evidence to capture:
  - line-cited updates in DE-038, DR-038, workflow-research
  - `gaps-to-adoption.md` presence and structured content
  - `notes.md` update for the phase work

## 6. Assumptions & STOP Conditions

- Assumptions:
  - This phase remains documentation-only and does not alter runtime code behavior.
  - Policy decisions captured here are inputs to a follow-up implementation delta.
- STOP when:
  - new policy ambiguity appears that would change strict-mode baseline semantics.
  - code-truth verification reveals a contradiction that requires design escalation.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                | Parallel? | Notes                                             |
| ------ | --- | ---------------------------------------------------------- | --------- | ------------------------------------------------- |
| [x]    | 1.1 | Align strict_mode contract language across DE/DR/research  | [ ]       | Hard-fail + no exception knobs captured           |
| [x]    | 1.2 | Add v1 coverage precedence and mixed-status warning policy | [ ]       | Conservative aggregation, warn-level drift checks |
| [x]    | 1.3 | Create `phase-01.md` and prefill contract-freeze checklist | [ ]       | Includes gate/exit/verification details           |

### Task Details

- **1.1 Description**
  - **Design / Approach**: Normalize all strict-mode references to one concrete `workflow.toml` key with explicit enabled/disabled behavior.
  - **Files / Components**: `DE-038.md`, `DR-038.md`, `workflow-research.md`
  - **Testing**: line-level readback to verify no conflicting phrasing remains.
  - **Observations & AI Notes**: ambiguity dropped after replacing "likely/should" with explicit hard-fail contract language.
  - **Commits / References**: uncommitted work in DE-038 bundle.

- **1.2 Description**
  - **Design / Approach**: Document conservative precedence contract for mixed coverage sources and validation severity.
  - **Files / Components**: `workflow-research.md`, `DR-038.md`, `DE-038.md`
  - **Testing**: cross-check policy wording against `requirements/registry.py` behavior model.
  - **Observations & AI Notes**: mixed `verified + planned -> in-progress` retained as deliberate conservative behavior.
  - **Commits / References**: uncommitted work in DE-038 bundle.

- **1.3 Description**
  - **Design / Approach**: scaffold phase sheet via CLI, then replace placeholders with concrete contract-freeze checklist items.
  - **Files / Components**: `IP-038.md`, `phases/phase-01.md`
  - **Testing**: verify phase ID and plan references are consistent.
  - **Observations & AI Notes**: scaffold appended duplicate phase ID in `IP-038` plan overview; cleaned manually.
  - **Commits / References**: uncommitted work in DE-038 bundle.

_(Repeat detail blocks per task as needed)_

## 8. Risks & Mitigations

| Risk                                            | Mitigation                                                             | Status    |
| ----------------------------------------------- | ---------------------------------------------------------------------- | --------- |
| Strict-mode wording drifts across documents     | Use line-cited readback against all three artifacts before phase close | Mitigated |
| Policy text overstates current runtime behavior | Keep explicit "documentation-only, no runtime branching yet" framing   | Mitigated |

## 9. Decisions & Outcomes

- `2026-03-03` - Baseline strict-mode contract frozen: hard-fail non-canonical paths, no exception knobs in this delta.
- `2026-03-03` - Recommended v1 coverage precedence frozen: mixed statuses resolve to `in-progress` with warning-level validation.

## 10. Findings / Research Notes

- Coverage remains primary close-out gate; other hard failures (invalid requirement IDs, missing parent spec, retired requirement) were kept explicit in contract docs.
- Plan coverage in default sync remains a follow-up scope question contingent on precedence+warning implementation.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase (if any)
