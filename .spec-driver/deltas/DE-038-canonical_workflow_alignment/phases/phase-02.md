---
id: IP-038.PHASE-02
slug: 038-canonical_workflow_alignment-phase-02
name: IP-038 Phase 02
created: '2026-03-03'
updated: '2026-03-03'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-038.PHASE-02
plan: IP-038
delta: DE-038
objective: >-
  Execute memory review pass to align workflow-critical memory records with
  DE-038 strict-mode and coverage-policy contract.
entrance_criteria:
  - Phase 01 contract-freeze outcomes are documented in DE/DR/research.
  - Memory target list is confirmed in IP-038.
  - Gaps document and notes are available for evidence references.
exit_criteria:
  - Target memory records are updated or explicitly confirmed already aligned.
  - Memory claims are traceable to code/docs with cited sources.
  - No reviewed memory implies ceremony runtime enforcement or non-canonical sequencing as default.
verification:
  tests:
    - VA memory review against source-of-truth scripts/docs listed in workflow-research.
  evidence:
    - Diffs for reviewed memory files with line-level source references.
    - Notes entry summarizing findings, updates, and residual risks.
tasks:
  - id: P2.1
    title: Baseline-read memory targets and capture claim drift.
    status: done
  - id: P2.2
    title: Patch core-loop, revision, and delta-completion memories.
    status: done
  - id: P2.3
    title: Patch posture/ceremony memories and add new fact memories if missing.
    status: done
  - id: P2.4
    title: Coherence readback + notes update + handoff to phase 03.
    status: done
risks:
  - Memory provenance may still reference stale docs unless explicitly updated.
  - Over-correction could hide valid town-planner concession pathways.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-038.PHASE-02
```

# Phase 02 - Memory Review Pass

## 1. Objective

Execute the memory review pass so workflow-critical memories consistently reflect the DE-038 contract (delta-first default, strict-mode baseline semantics, coverage gate reality, and advisory ceremony posture).

## 2. Links & References

- **Delta**: DE-038
- **Design Revision Sections**:
  - [DR-038.md](../DR-038.md) - memory change intent and strict-mode contract
  - [workflow-research.md](../workflow-research.md) - code-truth backing and policy detail
- **Specs / PRODs**:
  - N/A (documentation/memory alignment phase)
- **Support Docs**:
  - [DE-038.md](../DE-038.md)
  - [gaps-to-adoption.md](../gaps-to-adoption.md)
  - [notes.md](../notes.md)
  - `/home/david/dev/spec-driver/supekku/scripts/complete_delta.py`
  - `/home/david/dev/spec-driver/supekku/scripts/lib/changes/coverage_check.py`

## 3. Entrance Criteria

- [x] Phase 01 contract-freeze complete and documented
- [x] Memory review target set listed in IP-038
- [x] Memory files loaded for baseline read and drift capture

## 4. Exit Criteria / Done When

- [x] Target memories updated/confirmed aligned with DE-038 contract
- [x] Provenance and claim wording are code-truth aligned
- [x] No residual contradiction across core-loop/revision/delta-completion/posture/ceremony memory set

## 5. Verification

- Verification type: VA (memory consistency + source-truth audit)
- Tooling/commands:
  - `uv run spec-driver find memory "*spec-driver*"`
  - `uv run spec-driver show memory <id> --raw`
  - `rg -n` and `nl -ba` over source-of-truth code/docs
- Evidence to capture:
  - reviewed memory file diffs
  - cited code/doc references for major claims
  - notes entry with open risks and handoff guidance

## 6. Assumptions & STOP Conditions

- Assumptions:
  - Memory updates remain documentation-only and do not require runtime code changes.
  - Strict-mode baseline policy is already decided; this phase applies it consistently.
- STOP when:
  - a target memory claim conflicts with code-truth and cannot be resolved by wording correction.
  - a requested memory change would materially alter DE-038 scope.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                             | Parallel? | Notes                                                                                        |
| ------ | --- | ------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------- |
| [x]    | 2.1 | Baseline-read all target memories and log drift         | [ ]       | Captured revision-first default drift, ceremony enforcement drift, and missing fact memories |
| [x]    | 2.2 | Update core workflow memories                           | [ ]       | Updated `core-loop`, `revision`, `delta-completion` with code-backed framing                 |
| [x]    | 2.3 | Update posture/ceremony memories + create fact memories | [ ]       | Updated `posture`, `ceremony*`; added `coverage-gate` and `status-enums` facts               |
| [x]    | 2.4 | Run coherence readback and finalize memory notes        | [ ]       | Completed grep/readback checks and updated DE-038 notes                                      |

### Task Details

- **2.1 Description**
  - **Design / Approach**: inspect each target memory and classify statements as aligned, stale, or ambiguous.
  - **Files / Components**: memory files listed under IP-038 section 5.
  - **Testing**: source-check each non-trivial claim against code/docs.
  - **Observations & AI Notes**: record contradiction hotspots before patching.
  - **Commits / References**: uncommitted work in DE-038 bundle.

- **2.2 Description**
  - **Design / Approach**: apply minimal wording changes that enforce delta-first default and accurate completion semantics.
  - **Files / Components**: `mem.pattern.spec-driver.core-loop`, `mem.concept.spec-driver.revision`, `mem.pattern.spec-driver.delta-completion`.
  - **Testing**: re-read updated memory set end-to-end for sequencing coherence.
  - **Observations & AI Notes**: verify revision-first remains documented as concession path, not default.
  - **Commits / References**: uncommitted work in DE-038 bundle.

- **2.3 Description**
  - **Design / Approach**: align ceremony/posture guidance with advisory runtime reality and strict-mode future behavior.
  - **Files / Components**: `mem.concept.spec-driver.posture`, `mem.signpost.spec-driver.ceremony`, `mem.concept.spec-driver.ceremony.settler`, new fact memories if absent.
  - **Testing**: check for removed/updated stale status vocab and enforcement claims.
  - **Observations & AI Notes**: ensure no memory implies ceremony-based runtime gating today.
  - **Commits / References**: uncommitted work in DE-038 bundle.

- **2.4 Description**
  - **Design / Approach**: perform final coherence pass and capture outcomes in notes.
  - **Files / Components**: all touched memory files + `notes.md`.
  - **Testing**: quick grep for known stale terms (`implemented`, `live`, `archive`, "only hard gate") in reviewed memory set.
  - **Observations & AI Notes**: capture residual risks for phase 03.
  - **Commits / References**: uncommitted work in DE-038 bundle.

_(Repeat detail blocks per task as needed)_

## 8. Risks & Mitigations

| Risk                                                        | Mitigation                                                      | Status |
| ----------------------------------------------------------- | --------------------------------------------------------------- | ------ |
| Memory provenance remains tied to stale docs                | Add/refresh provenance entries with current code/doc references | Open   |
| Narrative over-correction suppresses valid concession paths | Keep explicit town-planner concession language where applicable | Open   |
| Memory set drifts internally after partial edits            | Perform full-set coherence readback before phase close          | Open   |

## 9. Decisions & Outcomes

- `2026-03-03` - Phase scaffolded; execution checklist prefilled with target memory set from IP-038.

## 10. Findings / Research Notes

- Drift captured against source-of-truth code:
  - `core-loop` incorrectly led with revision intent instead of delta-first scope.
  - `revision` framed as default entry step instead of post-audit reconciliation or town-planner concession path.
  - `delta-completion` lacked explicit parent-spec coverage gate semantics and env/flag bypass caveats.
  - `posture` and ceremony signpost wording implied ceremony-mode enforcement, which is not implemented in runtime branching.
  - No memory record existed for the close-out coverage sharp edge or canonical status enum set.
- Source references used for correction:
  - `supekku/scripts/complete_delta.py`
  - `supekku/scripts/lib/changes/coverage_check.py`
  - `supekku/scripts/lib/requirements/lifecycle.py`
  - `supekku/scripts/lib/requirements/registry.py`
  - `supekku/scripts/lib/changes/lifecycle.py`
  - `supekku/scripts/lib/blocks/verification.py`

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase (if any)
