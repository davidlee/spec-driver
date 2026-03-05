---
id: IP-043.PHASE-02
slug: 043-guidance-and-memory
name: IP-043 Phase 02 - Guidance and memory
created: '2026-03-05'
updated: '2026-03-05'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-043.PHASE-02
plan: IP-043
delta: DE-043
objective: >-
  Create discoverable lifecycle guidance for agents, correct memory drift,
  and update the status-enums memory to reference DE-043.
entrance_criteria:
  - Phase 1 complete (code fix committed)
exit_criteria:
  - mem.guide.spec-driver.requirement-lifecycle exists and answers corner cases
  - mem.concept.spec-driver.verification corrected (passed → verified)
  - mem.fact.spec-driver.status-enums updated to reference DE-043
  - All memories retrievable via relevant scope queries
verification:
  tests: []
  evidence:
    - VA-043-001
tasks:
  - id: '2.1'
    description: Create mem.guide.spec-driver.requirement-lifecycle
  - id: '2.2'
    description: Fix mem.concept.spec-driver.verification drift
  - id: '2.3'
    description: Update mem.fact.spec-driver.status-enums
  - id: '2.4'
    description: Verify discoverability via scope queries
risks:
  - description: Guidance memory becomes stale as lifecycle evolves
    mitigation: Link to canonical code and specs as provenance
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-043.PHASE-02
```

# Phase 2 – Guidance and memory

## 1. Objective

Create authoritative, agent-discoverable lifecycle guidance answering common
requirement lifecycle corner cases. Correct existing memory drift. Update
cross-references.

## 2. Links & References

- **Delta**: [DE-043](../DE-043.md)
- **Design Revision**: [DR-043 §7 DEC-043-03](../DR-043.md) – guidance as memory record
- **Specs**: PROD-009.FR-001 (explicit lifecycle statuses with clear semantics)
- **Memories to update**:
  - `mem.concept.spec-driver.verification` — `passed` → `verified` drift
  - `mem.fact.spec-driver.status-enums` — add DE-043 reference
- **Memory to create**:
  - `mem.guide.spec-driver.requirement-lifecycle` — lifecycle corner cases

## 3. Entrance Criteria

- [x] Phase 1 complete (62cfcd5)

## 4. Exit Criteria / Done When

- [x] `mem.concept.spec-driver.requirement-lifecycle` exists and covers:
  1. Three status vocabularies — what they are, where they apply
  2. Changing an established requirement — flow through spec revisions
  3. Backlog → spec transit — when and how requirements are formalised
  4. Lifecycle transition points — capture → deliver → observe cycle
- [x] `mem.concept.spec-driver.verification` corrected
- [x] `mem.fact.spec-driver.status-enums` updated
- [x] All memories retrievable via `spec-driver list memories` scope queries

## 5. Verification

- VA-043-001: agent review confirming lifecycle guidance is discoverable and
  answers the four corner cases from DE-043 §3
- `uv run spec-driver list memories -c "requirement lifecycle status"` returns
  the new guide

## 6. Assumptions & STOP Conditions

- **Assumption**: memory records are the primary discovery mechanism agents use
- **STOP when**: guidance scope starts expanding into areas that need ADR-level
  governance decisions

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Create `mem.guide.spec-driver.requirement-lifecycle` | | Updated existing `mem.concept.*` — `guide` type not supported; added all 4 corner cases |
| [x] | 2.2 | Fix `mem.concept.spec-driver.verification` drift | [P] | `passed` → `verified`, `in_progress` → `in-progress`, added `blocked` |
| [x] | 2.3 | Update `mem.fact.spec-driver.status-enums` | [P] | Added DE-043 validation note to caveat section |
| [x] | 2.4 | Verify discoverability via scope queries | | Tag + path queries succeed; `-c` requires CLI commands not keywords |

### Task Details

- **2.1 – Create lifecycle guidance memory**
  - **Approach**: `uv run spec-driver create memory` with type `guide`, then
    populate body with the four corner cases from DR-043 §7 DEC-043-03.
    Include provenance links to PROD-008, PROD-009, lifecycle.py, verification.py,
    and changes/lifecycle.py.
  - **Scope tags**: `requirement`, `lifecycle`, `status`, `coverage`, `spec-driver`
  - **Scope paths**: the three lifecycle.py/verification.py files
  - **Content must answer**:
    1. Three status vocabularies table
    2. "I want to change an established requirement" → spec revision flow
    3. "A requirement starts in backlog" → delta-driven spec update
    4. "When are transitions expected?" → capture/deliver/observe from PROD-008

- **2.2 – Fix verification concept memory**
  - **File**: `memory/mem.concept.spec-driver.verification.md`
  - **Change**: `planned → in_progress → passed | failed` →
    `planned → in-progress → verified | failed | blocked`
  - Also fix `in_progress` to `in-progress` (hyphenated, per canonical set)

- **2.3 – Update status-enums memory**
  - **File**: `memory/mem.fact.spec-driver.status-enums.md`
  - **Change**: Update "Important Caveat" section to note DE-043 addressed the
    coverage validation gap; the broader shared validator is still future work

- **2.4 – Verify discoverability**
  - Run scope queries to confirm the new guide surfaces correctly
  - Test: `spec-driver list memories -c "requirement lifecycle"`
  - Test: `spec-driver list memories --match-tag requirement --match-tag lifecycle`
  - Test: `spec-driver list memories -p supekku/scripts/lib/requirements/lifecycle.py`

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Guidance becomes stale | Provenance links to canonical code | Open |

## 9. Decisions & Outcomes

- **`guide` type not available**: The `create memory` command only supports types:
  concept, fact, pattern, signpost, system, thread. Used existing `concept` type
  memory (`mem.concept.spec-driver.requirement-lifecycle`) which was already created
  today. Updated in-place with all four corner cases rather than creating a duplicate.
- **`-c` scope query semantics**: The `-c` flag matches against `scope.commands`
  (actual CLI commands), not keyword tokens. The phase sheet test
  `-c "requirement lifecycle"` is a scope mismatch — correct queries use
  `--match-tag` or `-p` for this content.

## 10. Findings / Research Notes

- The existing `mem.concept.spec-driver.requirement-lifecycle` was created during
  Phase 1 work but only covered 2 of 4 corner cases. Extended rather than replaced.
- PROD-008 §2 capture/deliver/observe cycle and PROD-009 §4 evidence overlay
  semantics added as provenance sources.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] VA-043-001 evidence captured (IP-043 coverage block updated)
- [x] IP-043 progress tracking updated
- [x] Delta ready for closure
