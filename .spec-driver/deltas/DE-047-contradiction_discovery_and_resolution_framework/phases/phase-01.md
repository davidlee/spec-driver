---
id: IP-047.PHASE-01
slug: 047-agent-survey-and-ledger-population
name: Agent survey and ledger population
created: "2026-03-05"
updated: "2026-03-05"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-047.PHASE-01
plan: IP-047
delta: DE-047
objective: >-
  Systematically survey the PROD spec corpus and governance docs to populate
  drift ledger DL-047 with all contradictions, stale claims, missing decisions,
  and ambiguous intent.
entrance_criteria:
  - DR-047 reviewed and approved
  - Corpus inventory confirmed (DR-047 §4)
  - DL schema understood (IMPR-007)
exit_criteria:
  - DL-047 exists with entries covering all corpus docs
  - Every document in corpus inventory appears as a source in at least one entry
  - All entries at minimum triaged status (severity, topic, owner assigned)
verification:
  tests: []
  evidence:
    - VA-047-001
tasks:
  - id: 1.1
    description: Create drift ledger file
  - id: 1.2
    description: Read and extract claims from all PROD specs
  - id: 1.3
    description: Read and extract claims from governance docs
  - id: 1.4
    description: Cross-reference and populate ledger entries
  - id: 1.5
    description: Triage all entries (severity, topic, owner)
  - id: 1.6
    description: Verify corpus coverage
risks:
  - description: Survey misses subtle contradictions in long PROD specs
    mitigation: Structured concept extraction; multiple passes if needed
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-047.PHASE-01
```

# Phase 1 — Agent survey and ledger population

## 1. Objective

Systematically read every document in the corpus inventory, extract key claims,
cross-reference them, and populate `drift/DL-047-spec-corpus-reconciliation.md`
with all identified drift.

## 2. Links & References

- **Delta**: [DE-047](../DE-047.md)
- **Design Revision**: [DR-047 §4–5](../DR-047.md) — corpus inventory + process
- **DL Schema**: [IMPR-007](../../../backlog/improvements/IMPR-007-drift_ledger_primitive/drift-ledger-schema-draft.md)
- **Corpus**: 16 PROD specs, 3 ADRs, 2 policies, CLAUDE.md, glossary, doctrine, workflow, INIT.md

## 3. Entrance Criteria

- [x] DR-047 defines corpus inventory with file paths
- [x] DL schema defined in IMPR-007
- [x] DR-047 reviewed/approved by owner

## 4. Exit Criteria / Done When

- [x] `drift/DL-047-spec-corpus-reconciliation.md` exists with ledger frontmatter
- [x] Every corpus document (DR-047 §4) appears as a source in at least one entry
- [x] All entries have: entry_type, claims, severity, topic, owner (triaged)
- [x] VA-047-001 gate satisfied

## 5. Verification

- **VA-047-001**: Confirm every file path in DR-047 §4 corpus inventory appears
  as a `ref` in at least one entry's `sources`. Count of entries recorded.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - Contradictions will cluster around 4–6 topic areas
  - Most PROD specs have some drift (given 15/16 are still draft)
  - The IMPR-007 schema is usable without tooling for ~20–40 entries
- **STOP when**:
  - A contradiction is found that fundamentally questions whether a PROD spec
    should exist (escalate to owner before continuing)
  - Entry count exceeds ~50 (reassess whether batching/tooling is needed)

## 7. Tasks & Progress

| Status | ID  | Description                          | Parallel? | Notes                                                     |
| ------ | --- | ------------------------------------ | --------- | --------------------------------------------------------- |
| [x]    | 1.1 | Create DL-047 ledger file            |           | drift/DL-047-spec-corpus-reconciliation.md                |
| [x]    | 1.2 | Extract claims from PROD specs       | [P]       | 3 parallel agents: PROD-001–008, PROD-009–016, governance |
| [x]    | 1.3 | Extract claims from governance docs  | [P]       | All 11 governance/framework docs covered                  |
| [x]    | 1.4 | Cross-reference and populate entries |           | 20 entries: 2 blocking, 11 significant, 7 cosmetic        |
| [x]    | 1.5 | Triage all entries                   |           | All entries at triaged status with severity, topic, owner |
| [x]    | 1.6 | Verify corpus coverage (VA-047-001)  |           | 27/27 docs surveyed; 19 with findings, 8 clean            |

### Task Details

- **1.1 Create DL-047 ledger file**
  - Create `drift/DL-047-spec-corpus-reconciliation.md`
  - Frontmatter: id, name, created, status, kind, delta_ref
  - Empty entries section ready for population

- **1.2 Extract claims from PROD specs**
  - For each of the 16 PROD specs, extract claims about:
    - Definitions of terms/concepts
    - Lifecycle rules and transitions
    - Responsibility boundaries
    - Process requirements
    - Assumptions and constraints
  - Focus on §1 (Intent), §3 (Responsibilities), §4 (Solution)
  - Record which spec makes each claim for cross-referencing

- **1.3 Extract claims from governance docs**
  - ADR-001, ADR-002, ADR-003: decisions and their implications
  - POL-001, POL-002: requirements and constraints
  - CLAUDE.md: stated conventions and architecture rules
  - Glossary: term definitions
  - Doctrine, workflow, INIT.md: process claims

- **1.4 Cross-reference and populate entries**
  - For each concept/term, compare all documents that mention it
  - Where they disagree, are ambiguous, or make incompatible assumptions:
    create a DL entry with sources and claims
  - Also capture: stale claims, missing decisions, ambiguous intent

- **1.5 Triage all entries**
  - Assign severity (blocking / significant / cosmetic)
  - Assign topic area
  - Set owner (david for all, initially)
  - Add initial evidence line with discovery date

- **1.6 Verify corpus coverage**
  - Check every file path in DR-047 §4 appears in at least one entry's sources
  - If a document has no drift: note it in the ledger as a coverage confirmation
    (not as an entry — just a note)

## 8. Risks & Mitigations

| Risk                                | Mitigation                                              | Status             |
| ----------------------------------- | ------------------------------------------------------- | ------------------ |
| Long PROD specs bury contradictions | Structured extraction by section; focus on §1, §3, §4   | mitigated          |
| Too many entries to manage manually | STOP condition at ~50; reassess tooling if hit          | clear (20 entries) |
| Agent misinterprets design intent   | Entries are flagged for human review, not auto-resolved | mitigated          |

## 9. Findings Summary

**20 entries** across 6 topic areas:

| Topic      | Blocking | Significant | Cosmetic | Total  |
| ---------- | -------- | ----------- | -------- | ------ |
| Workflow   | 2        | 1           | 1        | 4      |
| Contracts  | —        | 5           | 1        | 6      |
| Governance | —        | 3           | —        | 3      |
| Lifecycle  | —        | 2           | 1        | 3      |
| Taxonomy   | —        | —           | 1        | 1      |
| Other      | —        | —           | 3        | 3      |
| **Total**  | **2**    | **11**      | **7**    | **20** |

**Blocking entries** (must resolve before any PROD promotion):

- DL-047.001 + .011: Phase-01 auto-creation — PROD-011 reversed PROD-002
  but PROD-002 was never formally revised. Same underlying issue.

**Cluster observations**:

- **Contracts** (6 entries): densest topic. Canonical location, navigation
  structure, and storage model evolved PROD-005 → PROD-012 → PROD-014
  without back-propagating revisions.
- **Governance** (3 entries): PROD-003 pre-dates ADR-002; PROD-016 introduced
  workflow.toml without reconciling existing docs.
- **Lifecycle** (3 entries): single conceptual conflict — PROD-008's "spec is
  truth" vs PROD-009's "latest evidence is truth."

## 10. Hand-off to Phase 2

DL-047 is populated and triaged. Phase 2 is human resolution — review entries
grouped by topic, make design calls, codify as ADRs or spec revisions.

Suggested resolution order (blocking first, then by cluster density):

1. **Workflow blocking** (.001, .011) — single decision resolves both
2. **Contracts cluster** (.002, .003, .004, .012, .013) — likely one ADR
3. **Lifecycle cluster** (.009, .017, .018) — likely one ADR
4. **Governance cluster** (.005, .007, .008, .014, .015) — mix of ADR + RE
5. **Cosmetic** (.006, .010, .016, .019, .020) — editorial fixes
