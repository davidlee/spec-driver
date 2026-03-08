---
id: IP-079.PHASE-04
slug: 079-implement_canonical_audit_reconciliation_contract-phase-04
name: Rewrite audit-change as canonical reconciliation runsheet
created: '2026-03-09'
updated: '2026-03-09'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-079.PHASE-04
plan: IP-079
delta: DE-079
objective: >-
  Rewrite the audit-change skill so it becomes the canonical runsheet for
  closure-grade audits: create or update the AUD artefact, disposition every
  finding, reconcile specs, sync/validate, then hand off to closure.
entrance_criteria:
  - Phase 3 validation work is complete.
  - DR-079 code impact for audit-change has been reviewed.
  - Current audit-change skill and skill-install surface have been reviewed.
exit_criteria:
  - supekku/skills/audit-change/SKILL.md requires AUD artefact creation or update for qualifying work.
  - The skill requires per-finding disposition and explicit reconciliation before closure handoff.
  - Generated .spec-driver skill copy is refreshed and matches the packaged skill.
  - AGENTS metadata still reflects the updated audit-change description.
  - just check passes and the phase work is committed.
verification:
  tests:
    - just check
  evidence:
    - generated .spec-driver skill copy matches packaged audit-change
    - AGENTS.md still exposes the updated audit-change description
tasks:
  - id: 4.1
    title: Rewrite packaged audit-change skill around the new reconciliation contract
    status: done
  - id: 4.2
    title: Refresh generated skill surfaces and verify AGENTS exposure
    status: done
  - id: 4.3
    title: Run just check, commit phase work, and reconcile DE-079 tracking docs
    status: done
risks:
  - description: Skill wording may drift from the now-shipped CLI/runtime contract if it paraphrases instead of using the actual artifact flow.
    mitigation: Anchor the skill to the real `create audit` command shape and DR-079 terms (mode, delta_ref, per-finding disposition).
  - description: Skill sync mechanism may have changed from earlier notes.
    mitigation: Verify the current refresh command in the local CLI before updating notes or AGENTS expectations.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-079.PHASE-04
```

# Phase 4 - Rewrite audit-change as canonical reconciliation runsheet

## 1. Objective
Rewrite `audit-change` so it is the canonical procedural runsheet for audit reconciliation under DE-079 rather than an advisory checklist.

## 2. Links & References
- **Delta**: DE-079
- **Design Revision Sections**:
  - `DR-079` section 3, architecture intent
  - `DR-079` section 4, code impact summary for `supekku/skills/audit-change/SKILL.md`
- **Specs / PRODs**:
  - `PROD-008`
  - `PROD-011`
  - `SPEC-116`
  - `SPEC-122`
  - `SPEC-125`
- **Support Docs**:
  - `supekku/skills/audit-change/SKILL.md`
  - `.spec-driver/skills/`
  - `.spec-driver/AGENTS.md`
  - `.spec-driver/deltas/DE-079-implement_canonical_audit_reconciliation_contract/notes.md`

## 3. Entrance Criteria
- [x] Phase 3 validation work is complete
- [x] DR-079 code impact for audit-change reviewed
- [x] Current skill and install surface reviewed

## 4. Exit Criteria / Done When
- [x] audit-change requires AUD artefact creation/update for qualifying work
- [x] audit-change requires per-finding disposition and reconciliation before closure handoff
- [x] generated skill copy refreshed and AGENTS exposure verified
- [x] just check passes and phase work is committed

## 5. Verification
- Run `just check`
- Verify `.spec-driver/skills/audit-change/SKILL.md` matches packaged skill
- Verify `.spec-driver/AGENTS.md` still exposes the updated audit-change description

## 6. Assumptions & STOP Conditions
- Assumptions:
  - the current sync/install surface can still refresh generated skill copies without bespoke file editing
  - phase 4 is skill/doc/runtime-surface work only; no schema/runtime code changes are expected
- STOP when:
  - the current CLI no longer has a supported path to refresh generated skills
  - the existing audit-change description in AGENTS is generated from a different source than the packaged skill metadata

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 4.1 | Rewrite packaged audit-change skill around the new reconciliation contract | [ ] | Preserved evidence/reconciliation flow while replacing advisory wording |
| [x] | 4.2 | Refresh generated skill surfaces and verify AGENTS exposure | [ ] | Current supported refresh flow was `uv run spec-driver install -y .` |
| [x] | 4.3 | Run just check, commit, and reconcile phase tracking | [ ] | Commit scoped to DE-079 phase-4 files plus generated skill surfaces |

### Task Details
- **4.1 Description**
  - **Design / Approach**: Rewrite the skill as a canonical runsheet: determine mode, create/update AUD artefact, disposition every finding, patch specs/revisions/follow-up work, run sync/validate, then hand off to close-change only when audit state supports it.
  - **Files / Components**:
    - `supekku/skills/audit-change/SKILL.md`
  - **Testing**: Manual review against DR-079 code impact and current `create audit` CLI.
  - **Observations & AI Notes**: The skill should describe closure-grade audit behavior, not restate the entire schema.
  - **Commits / References**: pending
- **4.2 Description**
  - **Design / Approach**: Refresh generated `.spec-driver/skills/` copy using the current supported workspace refresh flow, then verify AGENTS description remains correct.
  - **Files / Components**:
    - `.spec-driver/skills/audit-change/SKILL.md`
    - `.spec-driver/AGENTS.md`
  - **Testing**: Diff/manual verification only.
  - **Observations & AI Notes**: Notes from DE-055 suggest the historical sync command changed; verify current flow locally rather than assuming.
  - **Commits / References**: pending
- **4.3 Description**
  - **Design / Approach**: Run `just check`, then commit only phase-4-relevant files and update DE/IP/phase notes.
  - **Files / Components**:
    - `DE-079` bundle docs
    - packaged/generated audit-change skill
  - **Testing**: `just check`
  - **Observations & AI Notes**: Worktree is dirty outside DE-079; do not bundle unrelated user changes.
  - **Commits / References**: pending

*(Repeat detail blocks per task as needed)*

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |

## 9. Decisions & Outcomes
- `2026-03-09` - Phase 4 uses the real `create audit` CLI surface (`--mode`, `--delta`) as the skill anchor rather than inventing command shapes. Rationale: the runsheet should match the shipped workflow exactly.
- `2026-03-09` - Generated skill refresh used `uv run spec-driver install -y .` in this workspace. Rationale: the older dedicated skill-sync command is gone; phase notes should reflect the current supported flow.

## 10. Findings / Research Notes
- `spec-driver create audit --help` confirms the current supported options are `--mode`, `--delta`, `--spec`, `--prod`, and `--code-scope`.
- The current packaged audit-change skill is still advisory and explicitly conditional about standalone audit docs, which conflicts with DR-079 phase 4 intent.
- `uv run spec-driver install -y .` refreshed the generated `audit-change` skill and `AGENTS.md`, but warned about a stale allowlist entry for `audit-check`. That warning is workspace state, not part of the phase-4 rewrite.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase (if any)
