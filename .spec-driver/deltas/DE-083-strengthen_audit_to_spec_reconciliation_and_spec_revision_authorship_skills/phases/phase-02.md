---
id: IP-083.PHASE-02
slug: 083-strengthen_audit_to_spec_reconciliation_and_spec_revision_authorship_skills-phase-02
name: "IP-083 Phase 02 — Verify audit-to-spec examples and reconcile docs"
created: '2026-03-10'
updated: '2026-03-10'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-083.PHASE-02
plan: IP-083
delta: DE-083
objective: >-
  Prove the Phase 1 authorship path with worked examples covering all three
  branches (existing-spec patch, revision, revision-led new spec), execute the
  planned verification artefacts, and reconcile DE/DR/IP/notes for closure.
entrance_criteria:
  - Phase 1 complete with skill and governance surfaces updated
  - VA-083-001/002/003 still planned (not yet executed)
  - DR-083 design decisions remain current
exit_criteria:
  - VA-083-001 executed — decision path review confirms branch criteria are explicit and doctrine-aligned
  - VA-083-002 executed — authorship-skill gap review confirms no remaining gaps requiring immediate work
  - VA-083-003 executed — worked examples for all three branches are documented and teachable
  - DE/DR/IP/notes are reconciled and ready for closure handoff
  - DR-083 status updated to accepted (or issues raised if design drift found)
verification:
  tests:
    - uv run spec-driver show delta DE-083
    - just check
  evidence:
    - VA-083-001 decision path review documented in this phase sheet
    - VA-083-002 skill gap review documented in this phase sheet
    - VA-083-003 worked examples documented in this phase sheet
    - IP-083 verification coverage entries updated to reflect execution
tasks:
  - id: "2.1"
    title: "Execute VA-083-001: decision path review"
    status: done
  - id: "2.2"
    title: "Execute VA-083-002: authorship-skill gap review"
    status: done
  - id: "2.3"
    title: "Execute VA-083-003: worked-example walkthroughs"
    status: done
  - id: "2.4"
    title: "Reconcile DE/DR/IP/notes and update verification coverage"
    status: done
  - id: "2.5"
    title: "Update DR-083 status and hand off to closure"
    status: done
risks:
  - description: Worked examples reveal a gap that requires reopening Phase 1 skill changes
    mitigation: Treat minor wording fixes as Phase 2 scope; major gaps trigger STOP condition
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-083.PHASE-02
```

# Phase 2 — Verify audit-to-spec examples and reconcile docs

## 1. Objective
Prove the Phase 1 authorship path with worked examples covering all three
branches, execute the three planned verification artefacts (VA-083-001/002/003),
and reconcile delta documentation for closure handoff.

## 2. Links & References
- **Delta**: DE-083
- **Design Revision**: DR-083 (§4 Branch Criteria, §6 Verification Alignment)
- **Specs / PRODs**: PROD-011, SPEC-151
- **Support Docs**:
  - `supekku/skills/audit-change/SKILL.md` (Phase 1 output)
  - `supekku/skills/shape-revision/SKILL.md` (Phase 1 output)
  - `supekku/skills/spec-driver/SKILL.md` (Phase 1 output)
  - Phase 1 sheet: `phases/phase-01.md`

## 3. Entrance Criteria
- [x] Phase 1 complete with all exit criteria satisfied
- [x] VA-083-001/002/003 still at `planned` status
- [x] DR-083 design decisions remain current (no design drift from Phase 1)

## 4. Exit Criteria / Done When
- [x] VA-083-001: decision path review confirms branch criteria are explicit and doctrine-aligned
- [x] VA-083-002: authorship-skill gap review confirms no remaining gaps requiring immediate work
- [x] VA-083-003: worked examples for all three branches documented and teachable
- [x] DE/DR/IP/notes reconciled and ready for closure handoff
- [x] DR-083 status updated to `accepted`

## 5. Verification
- Commands:
  - `uv run spec-driver show delta DE-083`
  - `just check`
- Evidence to capture:
  - Decision path review (VA-083-001) in §10
  - Skill gap review (VA-083-002) in §10
  - Worked examples (VA-083-003) in §10
  - IP-083 verification coverage entries updated to `verified`

## 6. Assumptions & STOP Conditions
- Assumptions:
  - Phase 1 skill wording is substantially correct; Phase 2 fixes are limited to minor wording
  - The three VA artefacts can be executed as document reviews, not runtime tests
- STOP when:
  - A worked example reveals a design gap that cannot be resolved by minor wording fix
  - DR-083 design decisions are contradicted by the worked examples
  - A new skill surface appears necessary to express the authorship path

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Execute VA-083-001: decision path review | [P] | PASS — branch criteria explicit and doctrine-aligned across all 5 surfaces |
| [x] | 2.2 | Execute VA-083-002: authorship-skill gap review | [P] | PASS — no remaining gaps; audit→revision→spec-driver chain is coherent |
| [x] | 2.3 | Execute VA-083-003: worked-example walkthroughs | [ ] | PASS — 3 examples covering spec_patch, revision, revision-led new spec |
| [x] | 2.4 | Reconcile DE/DR/IP/notes and update verification coverage | [ ] | IP-083 and SPEC-151 verification entries updated to verified |
| [x] | 2.5 | Update DR-083 status and hand off to closure | [ ] | DR-083 accepted; ready for audit/closure |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Worked examples reveal a gap requiring Phase 1 rework | Minor wording fixes are Phase 2 scope; major gaps trigger STOP | active |
| Verification becomes rubber-stamping | Use concrete audit scenarios, not abstract summaries | active |

## 9. Decisions & Outcomes

## 10. Findings / Research Notes

### VA-083-001: Decision path review — PASS

Branch criteria from DR-083 §4 are present and correctly ordered across all five
touched surfaces (audit-change, shape-revision, spec-driver, PROD-011, SPEC-151).

Doctrine alignment:
- ADR-004 (audit→reconcile→close): all surfaces follow spec_patch→revision→revision-led new spec
- ADR-005 (skills=procedures): audit-change and shape-revision are procedural runsheets
- ADR-008 (explicit reconciliation): all branches require explicit disposition
- ADR-003 (no competing truths): new spec nested under revision, not a peer disposition

### VA-083-002: Authorship-skill gap review — PASS

No remaining gaps requiring immediate work:
- audit-change: explicit branch ordering, rationalization counters, reconciliation before closure
- shape-revision: doctrine pass, triage before creation, section-by-section authorship, new-spec inside revision
- spec-driver: narrow CLI routing with explicit authorship tip
- Cross-skill coherence: audit-change→shape-revision→spec-driver forms a clean chain with no authority overlap

### VA-083-003: Worked-example walkthroughs — PASS

Three concrete scenarios exercised:

**Example 1 — Existing spec patch**: Audit finds SPEC-140.FR-002 says "returns a list" but
implementation returns a generator. Disposition: `spec_patch`. Patch the spec wording directly.
Not revision because no authority moved.

**Example 2 — Revision**: Audit finds validation logic moved from SPEC-120 to SPEC-135 after
refactor. Disposition: `revision`. Create RE-045 with source/destination, capture requirement
movement, update both specs. Not spec_patch because authority moved between specs.

**Example 3 — Revision-led new spec**: Audit finds three assembly specs partially describe a
cross-cutting observability subsystem with overlap. Disposition: `revision`. Revision proves no
existing spec can own it cleanly → `spec-driver create spec` creates SPEC-160 → old specs updated
to remove overlap and link. Not a peer disposition because the new-spec decision lives inside the
revision analysis.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored (§10)
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off to audit/closure
