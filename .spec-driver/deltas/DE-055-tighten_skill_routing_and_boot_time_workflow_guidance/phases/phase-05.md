---
id: IP-055.PHASE-05
slug: 055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-05
name: IP-055 Phase 05
created: "2026-03-07"
updated: "2026-03-07"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-05
plan: IP-055
delta: DE-055
objective: >-
  Add a delta-specific execution documentation skill so `/notes` can remain
  generic while DE/IP/phase/DR reconciliation becomes explicit during
  implementation.
entrance_criteria:
  - Need confirmed for separating generic notes capture from delta-specific structured doc maintenance.
  - execute-phase already requires `/notes` during implementation.
exit_criteria:
  - A new delta-specific execution documentation skill exists with a narrow contract.
  - execute-phase references the new skill alongside `/notes`.
  - Installed skills and AGENTS output reflect the addition after sync.
  - DE-055 artefacts record the split and rationale.
verification:
  tests:
    - uv run spec-driver skills sync
  evidence:
    - Installed update-delta-docs skill matches the packaged source.
    - Installed execute-phase skill references update-delta-docs.
tasks:
  - id: 5.1
    title: Add update-delta-docs skill with a narrow delta-execution contract
    status: done
  - id: 5.2
    title: Wire execute-phase to use update-delta-docs alongside notes
    status: done
  - id: 5.3
    title: Sync installed skills and record the split in DE-055 artefacts
    status: done
risks:
  - description: The new skill could overlap too much with notes and become confusing
    mitigation: Keep notes generic and make update-delta-docs explicitly about structured DE/IP/phase/DR reconciliation
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-05
```

# Phase 5 - Add delta-specific execution documentation skill

## 1. Objective

Introduce a delta-specific skill for structured execution-document maintenance
without overloading `/notes`.

## 2. Links & References

- **Delta**: DE-055
- **Design Revision Sections**:
  - Problem & Constraints
  - Design Decisions & Trade-offs
  - Open Questions
- **Specs / PRODs**:
  - `PROD-002`
  - `PROD-011`
  - `SPEC-151`
- **Support Docs**:
  - `supekku/skills/notes/SKILL.md`
  - `supekku/skills/execute-phase/SKILL.md`
  - `supekku/skills/update-delta-docs/SKILL.md`
  - `.spec-driver/skills.allowlist`

## 3. Entrance Criteria

- [x] Need confirmed for a delta-specific structured-doc skill
- [x] Existing notes skill remains intentionally generic over card types

## 4. Exit Criteria / Done When

- [x] update-delta-docs skill exists with an explicit narrow scope
- [x] execute-phase references update-delta-docs alongside notes
- [x] Installed skills reflect the new skill and DE-055 artefacts capture the split

## 5. Verification

- Tests to run: none beyond sync/propagation for this skill-text change
- Tooling/commands:
  - `uv run spec-driver skills sync`
  - `sed -n '1,200p' .spec-driver/skills/update-delta-docs/SKILL.md`
  - `sed -n '1,120p' .spec-driver/skills/execute-phase/SKILL.md`
- Evidence to capture:
  - synced installed skill wording
  - execute-phase reference to update-delta-docs
  - notes entry summarising the split

## 6. Assumptions & STOP Conditions

- Assumptions:
  - The new skill should remain delta-specific and not absorb generic card journaling.
- STOP when:
  - the split would require redesigning audit/close-out semantics instead of execution-time doc maintenance.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                        | Parallel? | Notes                                                                                  |
| ------ | --- | ------------------------------------------------------------------ | --------- | -------------------------------------------------------------------------------------- |
| [x]    | 5.1 | Add update-delta-docs skill with a narrow delta-execution contract | [ ]       | New skill stays focused on structured DE/IP/phase/DR maintenance                       |
| [x]    | 5.2 | Wire execute-phase to use update-delta-docs alongside notes        | [ ]       | execute-phase now calls both generic notes and structured-doc reconciliation           |
| [x]    | 5.3 | Sync installed skills and record the split in DE-055 artefacts     | [ ]       | Sync succeeded after escalation because `.agents/skills` writes are sandbox-restricted |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |

## 9. Decisions & Outcomes

- `2026-03-07` - Keep `/notes` generic and add `update-delta-docs` for structured delta execution docs. Rationale: card journaling and DE/IP/phase/DR reconciliation are different responsibilities.

## 10. Findings / Research Notes

- notes is still appropriately generic over card types.
- execute-phase needed a second explicit doc-maintenance step for delta workflows.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
