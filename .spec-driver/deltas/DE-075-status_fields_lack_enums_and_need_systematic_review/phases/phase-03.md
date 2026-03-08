---
id: IP-075.PHASE-03
slug: 075-status_fields_lack_enums_and_need_systematic_review-phase-03
name: 'IP-075 Phase 03: docs, guidance, and close-out'
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-075.PHASE-03
plan: IP-075
delta: DE-075
objective: >-
  Update memories, skills, and agent guidance to reflect new status enums
  and unified backlog lifecycle. Update ISSUE-009. Close delta.
entrance_criteria:
  - Phase 2 complete — theme aligned, migration done, CI green
exit_criteria:
  - Status enum memory updated or created
  - Skills/guidance referencing old backlog statuses updated
  - ISSUE-009 updated with resolution status
  - Delta close-out criteria met
verification:
  tests: []
  evidence: []
tasks:
  - id: '3.1'
    description: Update mem.fact.spec-driver.status-enums with all enum values
  - id: '3.2'
    description: Update skills/guidance referencing old backlog status values
  - id: '3.3'
    description: Update ISSUE-009 — mark enum/migration acceptance criteria done
  - id: '3.4'
    description: Update glossary.md if status terminology changed
  - id: '3.5'
    description: Audit and close delta
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-075.PHASE-03
```

# Phase 3 — Docs, guidance, and close-out

## 1. Objective

Ensure all downstream documentation, memories, skills, and agent guidance reflect the new status enums and unified backlog lifecycle. Update ISSUE-009 and close DE-075.

## 2. Links & References

- **Delta**: DE-075
- **Memory**: `mem.fact.spec-driver.status-enums`
- **Issue**: ISSUE-009
- **Glossary**: `.spec-driver/agents/glossary.md`

## 3. Entrance Criteria

- [ ] Phase 2 complete — theme aligned, backlog migrated, CI green

## 4. Exit Criteria / Done When

- [ ] `mem.fact.spec-driver.status-enums` updated with all new enums
- [ ] Any skills/guidance referencing old per-kind backlog statuses updated
- [ ] ISSUE-009 acceptance criteria updated (enum definitions done, migration done, theme aligned)
- [ ] Glossary updated if terminology changed
- [ ] `just check` passes
- [ ] Delta close-out: `/close-change DE-075`

## 5. Verification

- Review memory content against actual code constants
- Grep skills/guidance for old status values (`captured`, `idea`, `suspected`, `investigating`, `planned`, `mitigated`, `done`, `implemented`, `verified`, `live`, `obsolete`)
- `just check` — final gate

## 6. Assumptions & STOP Conditions

- Assumes no other deltas have introduced new status references since phase 2
- STOP if: close-change gates fail — investigate and resolve

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|---|---|---|---|---|
| [ ] | 3.1 | Update status-enums memory | [P] | All enum values |
| [ ] | 3.2 | Update skills/guidance for old backlog statuses | [P] | Grep for legacy values |
| [ ] | 3.3 | Update ISSUE-009 acceptance criteria | [P] | |
| [ ] | 3.4 | Update glossary if needed | [P] | |
| [ ] | 3.5 | Close delta | [ ] | Depends on 3.1–3.4 |
