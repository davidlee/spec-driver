---
id: IP-083.PHASE-01
slug: 083-strengthen_audit_to_spec_reconciliation_and_spec_revision_authorship_skills-phase-01
name: "IP-083 Phase 01 — Apply authorship skill changes"
created: '2026-03-09'
updated: '2026-03-10'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-083.PHASE-01
plan: IP-083
delta: DE-083
objective: >-
  Update the affected skills and direct governance surfaces so the settled
  audit-to-spec authorship path is executable without reopening design.
entrance_criteria:
  - DR-083 resolves the dedicated-skill question and the branch criteria
  - DE-079 boundary is accepted: no schema or gating changes in this phase
  - Direct revision targets are identified as PROD-011 and SPEC-151
exit_criteria:
  - audit-change teaches existing-spec patch -> revision -> revision-led new spec
  - shape-revision teaches post-audit triage, doctrine pass, and section-by-section authorship
  - PROD-011 reflects the canonical audit-to-spec reconciliation path and concession posture
  - SPEC-151 states the strengthened skills subsystem responsibilities
  - Need for PROD-001 or PROD-002 edits is resolved and any required edits are applied
  - Installed skill copies and delta docs are reconciled after the packaged changes
verification:
  tests:
    - uv run spec-driver install -y .
    - uv run spec-driver show delta DE-083
  evidence:
    - Updated packaged and installed skill wording for audit-change and shape-revision
    - Revised PROD-011 and SPEC-151 text aligned with DR-083
    - Notes capturing whether PROD-001 and PROD-002 required direct changes
tasks:
  - id: "1.1"
    title: Update audit-change with explicit authorship ordering
    status: todo
  - id: "1.2"
    title: Upgrade shape-revision into the post-audit authorship loop
    status: todo
  - id: "1.3"
    title: Reassess spec-driver wording for the revision-led create-spec branch
    status: todo
  - id: "1.4"
    title: Revise PROD-011 for canonical audit-to-spec reconciliation
    status: todo
  - id: "1.5"
    title: Replace the SPEC-151 stub boundary with explicit responsibilities
    status: todo
  - id: "1.6"
    title: Patch PROD-001 or PROD-002 only if implementation proves a direct wording gap
    status: todo
  - id: "1.7"
    title: Sync installed skills and reconcile DE/IP/notes
    status: todo
risks:
  - description: New-spec wording could drift into a peer audit disposition and conflict with DE-079
    mitigation: Keep the new-spec case nested under revision in every touched surface
  - description: Direct spec revisions could sprawl into collaborator surfaces without clear need
    mitigation: Treat PROD-001 and PROD-002 as opt-in edits gated by explicit wording gaps
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-083.PHASE-01
```

# Phase 1 - Apply authorship skill changes

## 1. Objective
Update the skills and direct governance surfaces identified by DR-083 so the
post-audit authorship path is concrete enough to execute without re-opening the
design questions.

## 2. Links & References
- **Delta**: DE-083
- **Design Revision Sections**:
  - Foundational Triage
  - Architecture Intent / Branch Criteria
  - Code Impact Summary
  - Readiness Outcome
- **Specs / PRODs**:
  - `PROD-011`
  - `SPEC-151`
  - `PROD-001` (collaborator surface; edit only if needed)
  - `PROD-002` (collaborator surface; edit only if needed)
- **Support Docs**:
  - `supekku/skills/audit-change/SKILL.md`
  - `supekku/skills/shape-revision/SKILL.md`
  - `supekku/skills/spec-driver/SKILL.md`
  - `.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/DR-055.md`
  - `.spec-driver/deltas/DE-079-implement_canonical_audit_reconciliation_contract/DR-079.md`

## 3. Entrance Criteria
- [x] DR-083 resolves the dedicated-skill question and branch criteria
- [x] Direct vs collaborator governance surfaces are identified
- [x] DE-079 ownership boundary is clear and excludes runtime/schema changes from this phase

## 4. Exit Criteria / Done When
- [x] `audit-change` teaches `spec_patch -> revision -> revision-led new spec`
- [x] `shape-revision` teaches post-audit triage, doctrine consultation, and section-by-section authorship
- [x] `PROD-011` reflects the canonical audit-to-spec reconciliation path
- [x] `SPEC-151` captures the strengthened skills subsystem responsibilities
- [x] Need for `PROD-001` or `PROD-002` edits is resolved, with any required edits applied
- [x] Packaged and installed skill copies are synchronized and DE/IP/notes reflect the work

## 5. Verification
- Tests to run:
  - `uv run spec-driver install -y .`
  - `uv run spec-driver show delta DE-083`
- Tooling/commands:
  - `sed -n '1,260p' supekku/skills/audit-change/SKILL.md`
  - `sed -n '1,260p' supekku/skills/shape-revision/SKILL.md`
  - `sed -n '1,260p' .spec-driver/product/PROD-011/PROD-011.md`
  - `sed -n '1,200p' .spec-driver/tech/SPEC-151/SPEC-151.md`
- Evidence to capture:
  - packaged and installed skill wording matches the DR-083 branch criteria
  - direct governance surfaces match the settled authorship boundary
  - notes record whether collaborator surfaces stayed untouched or required edits

## 6. Assumptions & STOP Conditions
- Assumptions:
  - `spec-driver create spec` remains sufficient for the rare revision-led new-spec branch
  - no new audit disposition kind is required beyond `spec_patch` and `revision`
- STOP when:
  - implementation reveals a need to change DE-079 audit schema, validation, or gate behaviour
  - a dedicated spec-authoring skill becomes necessary to express the design cleanly
  - required governance edits expand beyond `PROD-011`, `SPEC-151`, `PROD-001`, and `PROD-002`

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Update `audit-change` with explicit authorship ordering | [ ] | Closure-grade skill surface |
| [x] | 1.2 | Upgrade `shape-revision` into the post-audit authorship loop | [ ] | Reuse DR authoring patterns where justified |
| [x] | 1.3 | Reassess `spec-driver` wording for revision-led `create spec` | [P] | Existing command path was sufficient; only doctrinal wording was added |
| [x] | 1.4 | Revise `PROD-011` for canonical audit-to-spec reconciliation | [ ] | Direct governance target |
| [x] | 1.5 | Replace the `SPEC-151` stub boundary with explicit responsibilities | [ ] | Direct technical target |
| [x] | 1.6 | Patch `PROD-001` or `PROD-002` only if needed | [P] | No direct wording gap found, so both stayed untouched |
| [x] | 1.7 | Sync installed skills and reconcile DE/IP/notes | [ ] | `uv run spec-driver install -y .` is the current install/sync path |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| New-spec wording drifts into a peer audit disposition | keep every touched surface aligned with `revision -> optional new spec` | active |
| Collaborator-surface edits sprawl | require an explicit wording gap before touching `PROD-001` or `PROD-002` | active |
| Packaged and installed skill copies diverge | run `uv run spec-driver install -y .` before phase close-out | active |

## 9. Decisions & Outcomes
- `2026-03-09` - Phase planning starts at execution, not retrospective design capture. Rationale: DR-083 already settled the design questions before the first phase sheet was created.
- `2026-03-10` - `uv run spec-driver install -y .` replaced the stale `uv run spec-driver skills sync` note as the real packaged-skill install path in this repo.

## 10. Findings / Research Notes
- DR-083 settled the branch order as existing-spec patch -> revision -> revision-led new spec.
- Direct revision targets are `PROD-011` and `SPEC-151`; `PROD-001` and `PROD-002` are collaborator surfaces to justify before touching.
- `PROD-001` and `PROD-002` did not require edits once the branch order was made explicit in `audit-change`, `shape-revision`, `spec-driver`, and `PROD-011`.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase (if any)
