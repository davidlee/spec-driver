---
id: IP-047.PHASE-02
slug: 047-human-resolution-adr-and-re-creation
name: Human resolution — ADR and RE creation
created: '2026-03-06'
updated: '2026-03-06'
status: in_progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-047.PHASE-02
plan: IP-047
delta: DE-047
objective: >-
  Adjudicate all DL-047 entries with human decisions, then codify as ADRs and
  spec revisions. Every blocking/significant entry gets a resolution_ref.
entrance_criteria:
  - DL-047 populated with all entries triaged (Phase 1 complete)
exit_criteria:
  - All 20 DL-047 entries at adjudicated or dismissed status
  - ADRs drafted for contracts and lifecycle topics
  - REs drafted for affected PROD specs
  - Every blocking/significant entry has resolution_ref populated
  - Backlog items created for deferred work (.006, .010, .019, .020)
verification:
  tests: []
  evidence:
    - VH-047-001
tasks:
  - id: 2.1
    description: Adjudicate all triaged DL entries with human decisions
  - id: 2.2
    description: Draft contracts ADR (role, canonical location, navigation)
  - id: 2.3
    description: Draft lifecycle ADR (normative vs observed truth)
  - id: 2.4
    description: Draft RE on PROD-002 (phase-01 auto-creation reversal)
  - id: 2.5
    description: Draft RE on PROD-003 (backlinks model — runtime computed)
  - id: 2.6
    description: Draft RE on PROD-012 (flows aligned to contracts ADR)
  - id: 2.7
    description: Draft RE on PROD-008/009 (lifecycle semantics per ADR)
  - id: 2.8
    description: Draft RE on PROD-016 (installer config semantics clarity)
  - id: 2.9
    description: Patch ADR-003 + CLAUDE.md (remove c4_level "interaction")
  - id: 2.10
    description: Patch doctrine.md/workflow.md/glossary.md for clarity (.008)
  - id: 2.11
    description: Create backlog items for deferred work
  - id: 2.12
    description: Populate resolution_ref on all blocking/significant DL entries
risks:
  - description: ADR drafting cascades into scope creep
    mitigation: ADRs record decisions already made; keep minimal
  - description: RE volume is high (5+ specs)
    mitigation: REs can be lightweight — frontmatter + summary of change
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-047.PHASE-02
```

# Phase 2 — Human resolution, ADR and RE creation

## 1. Objective

Codify all adjudication decisions from DL-047 as formal artifacts (ADRs, REs,
backlog items) and link them back to the ledger as resolution references.

## 2. Links & References

- **Delta**: [DE-047](../DE-047.md)
- **Drift Ledger**: `drift/DL-047-spec-corpus-reconciliation.md`
- **Phase 1**: [phase-01.md](./phase-01.md) — survey and ledger population
- **Verification**: VH-047-001 (human resolves all blocking/significant)

## 3. Entrance Criteria

- [x] DL-047 populated with 20 entries, all triaged
- [x] Phase 1 complete (VA-047-001 satisfied)

## 4. Exit Criteria / Done When

- [x] All 20 entries adjudicated or dismissed
- [ ] Contracts ADR drafted
- [ ] Lifecycle ADR drafted
- [ ] REs drafted for PROD-002, PROD-003, PROD-008/009, PROD-012, PROD-016
- [ ] ADR-003 + CLAUDE.md patched (c4_level "interaction" removed)
- [ ] Doctrine/workflow/glossary patched for clarity
- [ ] Backlog items created for .006, .010, .019, .020
- [ ] All blocking/significant entries have resolution_ref

## 5. Verification

- **VH-047-001**: Human has reviewed and adjudicated every blocking/significant
  entry. Each resolved entry has resolution_ref and affected_artifacts populated.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - ADRs record decisions already made during adjudication — drafting is codification, not design
  - REs are lightweight: frontmatter + summary of what changes in the spec
  - Actual spec text edits happen in Phase 3
- **STOP when**:
  - An ADR draft reveals the decision isn't as clear as thought (escalate)
  - RE scope expands beyond the adjudicated change (split or defer)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Adjudicate all triaged DL entries | | 11 entries resolved in human review session |
| [ ] | 2.2 | Draft contracts ADR | | Covers .003, .004, .013: role, location, navigation |
| [ ] | 2.3 | Draft lifecycle ADR | | Covers .009, .017, .018: normative vs observed truth |
| [ ] | 2.3a | Draft core loop ADR | | Covers .021: canonical workflow + permutations. Blocking. |
| [ ] | 2.4 | Draft RE on PROD-002 | | Covers .001, .011: phase-01 auto-creation reversal |
| [ ] | 2.5 | Draft RE on PROD-003 | | Covers .005, .015: backlinks → runtime computed |
| [ ] | 2.6 | Draft RE on PROD-012 | [P] | Covers .002, .012: flows aligned to contracts ADR |
| [ ] | 2.7 | Draft RE on PROD-008/009 | [P] | Covers .009, .017, .018: lifecycle per ADR |
| [ ] | 2.8 | Draft RE on PROD-016 | [P] | Covers .014: installer config semantics |
| [ ] | 2.9 | Patch ADR-003 + CLAUDE.md | [P] | Covers .016: remove "interaction" c4_level |
| [ ] | 2.10 | Patch doctrine/workflow/glossary | [P] | Covers .008: default posture clarity |
| [ ] | 2.11 | Create backlog items | [P] | .006 (INIT.md), .010 (marker→toml), .019 (glossary merge), .020 (VCS) |
| [ ] | 2.12 | Populate resolution_ref on DL entries | | After artifacts exist |

### Task Details

- **2.1 Adjudicate all triaged DL entries**
  - Completed in interactive session with owner
  - 11 entries moved from triaged → adjudicated
  - Decisions recorded in DL-047 evidence blocks

- **2.2 Contracts ADR**
  - Unifies .003 (canonical location), .004 (mirror vs symlink), .013 (navigation)
  - Key decisions: contracts are derived/deterministic; .contracts/ is canonical;
    navigation structure TBD but single ADR covers role + location + navigation
  - Blocked on: nothing — decisions already made

- **2.3 Lifecycle ADR**
  - Unifies .009 (authority model), .017 (registry role), .018 (baseline statuses)
  - Key decisions: specs own normative truth; evidence overlays own observed truth;
    registry is derived; drift resolved explicitly; define "asserted" and "legacy_verified"

- **2.3a Core loop ADR**
  - Covers .021: the most important gap in the corpus
  - Canonically defines the core loop and its permutations:
    delta-first (default), revision-first (concession), eager-spec-edit (status TBD), pioneer minimal
  - Defines when each applies, what triggers the choice, what's optional vs mandatory
  - Should become the single source agents read first for workflow understanding
  - May later warrant its own PROD spec

- **2.4–2.8 Spec Revisions**
  - Each RE is lightweight: document what changes and why
  - Actual text edits to specs happen in Phase 3
  - REs for PROD-012, PROD-008/009, PROD-016 depend on their respective ADRs (2.2, 2.3)

- **2.9 Patch ADR-003 + CLAUDE.md**
  - Remove "interaction" from c4_level enum
  - Direct edit, no RE needed (ADR-003 is the source)

- **2.10 Patch doctrine/workflow/glossary**
  - Clarify polymorphic "card" concept in glossary
  - Clarify doctrine vs workflow relationship (config-dependent, not contradictory)
  - Clarify kanban = low-ceremony gateway

- **2.11 Backlog items**
  - ISSUE for .006: remove INIT.md from installer
  - ISSUE for .010: migrate spec auto-create to workflow.toml
  - ISSUE for .019: consolidate glossaries
  - ISSUE for .020: VCS abstraction scope (link to PROD-011 FR-008)

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| ADR drafting cascades into design work | ADRs codify decisions already made; keep minimal | clear |
| RE volume is high (5+ specs) | REs are lightweight — frontmatter + change summary | clear |
| Dependency chain: REs wait on ADRs | Draft ADRs first (2.2, 2.3), then parallel REs | planned |

## 9. Decisions & Outcomes

- 2026-03-06 — All 11 triaged entries adjudicated in interactive session:
  - .005/.015: ADR-002 wins; PROD-003 RE for runtime-computed backlinks
  - .009/.017/.018: one lifecycle ADR; specs = normative, evidence = observed
  - .008: config-dependent; "card" is polymorphic; patch docs for clarity
  - .014: doctrine.md user-owned, workflow.md generated; RE on PROD-016
  - .016: remove "interaction" c4_level; backlog UX spec concept
  - .010: workflow.toml canonical; small delta to migrate
  - .019: .contracts/ correct; consolidate glossaries later
  - .020: VCS gap acknowledged; backlog only
