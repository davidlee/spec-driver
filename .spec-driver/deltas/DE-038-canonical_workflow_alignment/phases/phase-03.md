---
id: IP-038.PHASE-03
slug: 038-canonical_workflow_alignment-phase-03
name: IP-038 Phase 03
created: '2026-03-03'
updated: '2026-03-03'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-038.PHASE-03
plan: IP-038
delta: DE-038
objective: >-
  Execute skill-review pass to align workflow-facing skills/templates with the
  DE-038 canonical sequence and strict-mode contract.
entrance_criteria:
  - Phase 02 memory review outcomes are captured or ready for carry-forward.
  - Skill review target set in IP-038 is confirmed.
  - DE/DR/research contract wording is stable.
exit_criteria:
  - Workflow-facing skills/templates reviewed for sequencing/enforcement claims.
  - Skill guidance no longer conflicts with delta-first default or advisory ceremony runtime.
  - Notes capture residual follow-ups and handoff outcomes.
verification:
  tests:
    - VA skill-guidance review against DE-038/DR-038/workflow-research contract.
  evidence:
    - Diffs for skill/template files touched in this phase.
    - Notes entry summarizing reviewed skills and unresolved gaps.
tasks:
  - id: P3.1
    title: Inventory workflow-facing skills/templates and baseline their claims.
    status: done
  - id: P3.2
    title: Patch sequencing and enforcement language to match DE-038 contract.
    status: done
  - id: P3.3
    title: Readback for consistency with memory set and docs.
    status: done
  - id: P3.4
    title: Finalize notes + recommend any follow-up deltas for remaining drift.
    status: done
risks:
  - Skill guidance may implicitly preserve stale revision-first/default narratives.
  - Template text may diverge from skill text after partial updates.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-038.PHASE-03
```

# Phase 03 - Skill Review Pass

## 1. Objective

Review and align workflow-facing skill guidance so agent behavior matches the frozen DE-038 contract (delta-first default, strict-mode hard-fail baseline, advisory ceremony runtime).

## 2. Links & References

- **Delta**: DE-038
- **Design Revision Sections**:
  - [DR-038.md](../DR-038.md) - strict-mode and memory/skill alignment intent
  - [workflow-research.md](../workflow-research.md) - runtime/code-truth and policy wording
- **Specs / PRODs**:
  - N/A (documentation/skills alignment phase)
- **Support Docs**:
  - [DE-038.md](../DE-038.md)
  - [notes.md](../notes.md)
  - `/home/david/dev/spec-driver/.agents/skills/`
  - `/home/david/dev/spec-driver/supekku/templates/agents/workflow.md`

## 3. Entrance Criteria

- [x] Contract wording in DE/DR/research is stable
- [x] Skill review target set listed in IP-038
- [x] Skill/template files loaded and baselined for drift

## 4. Exit Criteria / Done When

- [x] Skill/template workflow guidance is aligned with canonical model
- [x] No reviewed skill implies ceremony runtime enforcement today
- [x] Handoff notes include any remaining follow-up scope

## 5. Verification

- Verification type: VA (skill guidance coherence audit)
- Tooling/commands:
  - `rg -n` and `nl -ba` over `.agents/skills/**`, `supekku/skills/**`, and agent templates
  - targeted readback against `DE-038.md`, `DR-038.md`, and `workflow-research.md`
- Evidence to capture:
  - skill/template diffs with rationale
  - notes summary of unchanged vs modified skill assets
  - list of deferred skill-level gaps (if any)

## 6. Assumptions & STOP Conditions

- Assumptions:
  - Skill updates remain documentation-only and should not introduce new runtime behavior.
  - Strict-mode policy decisions are already fixed in earlier phases.
- STOP when:
  - a skill change would require broad policy reinterpretation not covered by DE-038.
  - template/skill conflicts cannot be resolved without changing DE/DR/research contract text.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                   | Parallel? | Notes                                                                                |
| ------ | --- | ------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------ |
| [x]    | 3.1 | Inventory workflow-facing skills/templates and baseline drift | [ ]       | Drift was mostly omission: workflow docs lacked explicit canonical/advisory wording  |
| [x]    | 3.2 | Patch core skill guidance to canonical model                  | [ ]       | Updated workflow template/runtime docs and implement skill source guidance           |
| [x]    | 3.3 | Cross-check skill output against reviewed memories            | [ ]       | Readback confirms no ceremony-as-runtime-enforcement claim remains in reviewed files |
| [x]    | 3.4 | Final notes and handoff                                       | [ ]       | Notes updated; next activity points to retrieval precision phase                     |

### Task Details

- **3.1 Description**
  - **Design / Approach**: enumerate workflow-impacting skills/templates and tag each claim as aligned/stale/ambiguous.
  - **Files / Components**: `.agents/skills/**`, `supekku/skills/**`, `supekku/templates/agents/**`.
  - **Testing**: source-truth cross-check against DE/DR/research.
  - **Observations & AI Notes**: to be populated during execution.
  - **Commits / References**: uncommitted work in DE-038 bundle.

- **3.2 Description**
  - **Design / Approach**: patch only claim-bearing lines; preserve non-workflow behavior.
  - **Files / Components**: workflow and completion related skills/templates identified in 3.1.
  - **Testing**: readback for consistency with strict-mode and ceremony posture text.
  - **Observations & AI Notes**: to be populated during execution.
  - **Commits / References**: uncommitted work in DE-038 bundle.

- **3.3 Description**
  - **Design / Approach**: compare skill language against updated memory set and docs.
  - **Files / Components**: touched skill/template files + memory targets in IP-038.
  - **Testing**: grep for stale phrases (`revision-first default`, ceremony as enforcement, archive closure language).
  - **Observations & AI Notes**: to be populated during execution.
  - **Commits / References**: uncommitted work in DE-038 bundle.

- **3.4 Description**
  - **Design / Approach**: summarize outcomes and unresolved gaps in notes.
  - **Files / Components**: `notes.md`, optionally `gaps-to-adoption.md` if new gaps emerge.
  - **Testing**: final checklist pass.
  - **Observations & AI Notes**: to be populated during execution.
  - **Commits / References**: uncommitted work in DE-038 bundle.

_(Repeat detail blocks per task as needed)_

## 8. Risks & Mitigations

| Risk                                    | Mitigation                                            | Status |
| --------------------------------------- | ----------------------------------------------------- | ------ |
| Skill text and agent templates diverge  | Update paired sources in same pass and run readback   | Open   |
| Over-editing skills beyond DE-038 scope | Constrain edits to sequencing/enforcement claims only | Open   |
| Residual drift remains hidden           | Capture deferred items explicitly in notes/gaps       | Open   |

## 9. Decisions & Outcomes

- `2026-03-03` - Phase scaffolded; execution checklist prefilled for skill-review pass.

## 10. Findings / Research Notes

- Baseline inventory covered:
  - `.agents/skills/*` and `supekku/skills/*` skill pairs
  - `.spec-driver/agents/workflow.md`
  - `supekku/templates/agents/workflow.md`
- Drift findings:
  - Workflow docs/templates did not explicitly state delta-first canonical sequencing.
  - Workflow docs/templates did not explicitly clarify ceremony as advisory guidance vs runtime enforcement.
  - Implement skill guidance lacked explicit canonical-sequence and completion-gate reminders.
- Files updated in this phase:
  - `supekku/templates/agents/workflow.md`
  - `.spec-driver/agents/workflow.md`
  - `supekku/skills/implement/SKILL.md`
- Source-of-truth note:
  - Skill edits were applied to `supekku/skills/*/SKILL.md` sources to avoid overwrite by skill sync.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase (if any)
