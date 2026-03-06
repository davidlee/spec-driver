---
id: IP-021.PHASE-01
slug: 021-kanban-card-support-phase-01
name: IP-021 Phase 01
created: '2026-02-03'
updated: '2026-02-03'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-021.PHASE-01
plan: IP-021
delta: DE-021
objective: >-
  Confirm architectural patterns, lock CLI behaviors, and resolve open design questions
entrance_criteria:
  - Delta DE-021 exists with clear scope
  - IMPR-003 reviewed and understood
exit_criteria:
  - Design decisions documented
  - CLI command signatures locked
  - Template requirements identified
  - Ready to implement domain + CLI
verification:
  tests: []
  evidence:
    - Design review completed
    - Open questions resolved or documented
tasks:
  - Review existing domain patterns (decisions, backlog)
  - Confirm CLI thin orchestration pattern
  - Identify template.md requirements
  - Answer open design questions
risks:
  - Missing kanban/template.md will block card creation
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-021.PHASE-01
```

# Phase 1 - Design Lock

## 1. Objective
Confirm patterns + lock CLI behaviors before implementation. Review design docs (DE-021, DR-021, IP-021), validate against existing codebase patterns, and resolve open questions.

## 2. Links & References
- **Delta**: DE-021 - Card support (kanban board)
- **Design Revision**: DR-021 - Architecture + code impacts
- **Implementation Plan**: IP-021 - 3-phase execution
- **Backlog Driver**: IMPR-003 - kanban support
- **Decision Context**: ADR-001 - use spec-driver to build spec-driver
- **Prior Art**: deck_of_dwarf/kanban Justfile:new-card
- **Similar Domains**: supekku/scripts/lib/decisions/, supekku/scripts/lib/backlog/

## 3. Entrance Criteria
- [x] Delta DE-021 exists with clear scope
- [x] IMPR-003 reviewed and understood
- [x] DR-021 details code impacts
- [x] IP-021 outlines phases and verification

## 4. Exit Criteria / Done When
- [x] Existing domain patterns reviewed (decisions, backlog)
- [x] CLI thin orchestration pattern confirmed
- [x] Open design questions resolved or explicitly deferred
- [x] Template.md requirements identified
- [x] Test strategy confirmed (VT-021-001..006, VH-021-001)
- [ ] Phase 2 sheet created with detailed tasks

## 5. Verification
- Design consistency: cards/ follows same structure as decisions/, backlog/
- CLI consistency: create/list/show/find follow thin orchestration pattern
- Template safety: only H1 + Created line rewritten

## 6. Assumptions & STOP Conditions
- Assumptions:
  - Existing CLI patterns (create, list, show) are well-established
  - Formatters follow pure function pattern
  - Registry sync patterns are proven
- STOP when:
  - User input needed on open design questions
  - Template.md location/creation strategy unclear

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Review existing domain patterns | [ ] | Reviewed decisions/, backlog/ |
| [x] | 1.2 | Review CLI patterns | [ ] | Reviewed create.py, list.py, show.py |
| [x] | 1.3 | Review formatter patterns | [ ] | Reviewed decision_formatters.py |
| [x] | 1.4 | Identify template requirements | [ ] | No kanban/template.md exists |
| [x] | 1.5 | Resolve open design questions | [ ] | User input received |
| [x] | 1.6 | Create Phase 2 sheet | [ ] | Phase 2 created with detailed tasks |

### Task Details
- **1.1 Review existing domain patterns**
  - **Design / Approach**: Examined decisions/ and backlog/ packages
  - **Files / Components**:
    - supekku/scripts/lib/decisions/registry.py:1 (DecisionRegistry)
    - supekku/scripts/lib/backlog/registry.py:1 (discovery, sync, create)
  - **Observations**: Consistent pattern: models.py + registry.py + registry_test.py

- **1.2 Review CLI patterns**
  - **Design / Approach**: Examined create.py, list.py, show.py structure
  - **Files / Components**:
    - supekku/cli/create.py:1 (thin command orchestration)
    - supekku/cli/list.py:1 (filters + formatters)
    - supekku/cli/show.py:1 (detail display)
  - **Observations**: Commands delegate to registries + formatters; CLI stays thin

- **1.3 Review formatter patterns**
  - **Design / Approach**: Examined decision_formatters.py structure
  - **Files / Components**: supekku/scripts/lib/formatters/decision_formatters.py:1
  - **Observations**: Pure functions for table/json/tsv output; no business logic

- **1.4 Identify template requirements**
  - **Findings**: No kanban/template.md exists; needs creation
  - **Options**:
    1. Create kanban/template.md as part of Phase 2
    2. Have spec-driver install create it
    3. Use inline default if missing
  - **Recommendation**: Create minimal template in Phase 2, defer install integration

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| No kanban/template.md exists | Create minimal template in Phase 2 | identified |
| Over-engineering on v1 | Defer optional features (lane flag, depends/related parsing) | planned |
| Ambiguous card locations | Default scope kanban/**, --anywhere flag explicit | designed |

## 9. Decisions & Outcomes
- `2026-02-03` - Confirmed thin CLI + pure formatter pattern from existing domains
- `2026-02-03` - Identified template.md missing; will create in Phase 2
- `2026-02-03` - **DECISION**: Defer Depends/Related parsing to future delta (keep v1 minimal)
- `2026-02-03` - **DECISION**: Add --lane flag to `create card` (backlog/doing/done, default backlog)
- `2026-02-03` - **DECISION**: Auto-create kanban/template.md on first card creation if missing (not during install)

## 10. Findings / Research Notes
- Existing domains (decisions, backlog) follow consistent structure
- No `find` command group exists yet - will create new supekku/cli/find.py
- Templates exist in supekku/templates/ but no kanban template
- CLI uses Typer app structure with command groups

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Open questions answered (defer dependencies, add --lane, auto-create template)
- [x] Phase 2 sheet created with detailed TDD tasks
- [x] Hand-off notes to Phase 2

**Hand-off to Phase 2**:
- Design locked: defer Depends/Related parsing, add --lane flag, auto-create template
- VT artifacts identified: VT-021-001 through VT-021-006
- Patterns confirmed: follow decisions/backlog structure, thin CLI, pure formatters
- Template strategy: auto-create kanban/template.md on first card creation if missing
- Ready to implement following TDD approach
