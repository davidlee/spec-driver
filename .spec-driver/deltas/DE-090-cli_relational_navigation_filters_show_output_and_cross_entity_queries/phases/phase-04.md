---
id: IP-090.PHASE-04
slug: 090-cli_relational_navigation_filters_show_output_and_cross_entity_queries-phase-04
name: IP-090 Phase 04 — P3 domain collectors
created: '2026-03-14'
updated: '2026-03-14'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-090.PHASE-04
plan: IP-090
delta: DE-090
objective: >-
  Dedicated domain-field collectors for Decision, Governance, Requirement,
  and BacklogItem models; dispatcher chaining into collect_references();
  update P1-8 backlog --related-to to use matches_related_to().
entrance_criteria:
  - Phase 03 (P2 show enrichment) complete
  - DR-090 §P3-1 through §P3-3 approved
exit_criteria:
  - All 4 collectors + dispatcher implemented in relations/query.py
  - "domain_field" added to REFERENCE_SOURCES in core/relation_types.py
  - "backlog_field" added to REFERENCE_SOURCES in core/relation_types.py
  - P1-8 backlog --related-to uses matches_related_to()
  - VT-090-P3-1 through VT-090-P3-8 passing
  - just passes (tests + ruff + pylint clean)
verification:
  tests:
    - VT-090-P3-1
    - VT-090-P3-2
    - VT-090-P3-3
    - VT-090-P3-4
    - VT-090-P3-5
    - VT-090-P3-6
    - VT-090-P3-7
    - VT-090-P3-8
  evidence: []
tasks:
  - id: "4.1"
    description: "Add domain_field and backlog_field to REFERENCE_SOURCES"
  - id: "4.2"
    description: "_collect_from_decision_fields() — 11 list fields"
  - id: "4.3"
    description: "_collect_from_governance_fields() — Policy/Standard 8 fields"
  - id: "4.4"
    description: "_collect_from_requirement_fields() — 4 list + 1 scalar"
  - id: "4.5"
    description: "_collect_from_backlog_fields() — frontmatter dict fields"
  - id: "4.6"
    description: "_collect_from_domain_fields() dispatcher"
  - id: "4.7"
    description: "Wire dispatcher into collect_references()"
  - id: "4.8"
    description: "Update P1-8 backlog --related-to to use matches_related_to()"
  - id: "4.9"
    description: "Tests for all collectors + integration"
risks:
  - description: "coverage_evidence entries may be dicts not strings"
    mitigation: "Check RequirementRecord field type; handle both"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-090.PHASE-04
```

# Phase 04 — P3 Domain Collectors

## 1. Objective

Add dedicated domain-field collectors so `collect_references()` sees references
stored in named model fields (DecisionRecord.specs, RequirementRecord.implemented_by,
etc.) — not just `.relations`/`.applies_to`/`.context_inputs`/`.informed_by`.
This unblocks P4 (--referenced-by) and P5 (--related).

## 2. Links & References
- **Delta**: DE-090
- **Design Revision Sections**: DR-090 §P3-1, §P3-2, §P3-3
- **Specs / PRODs**: PROD-010.FR-005
- **Key files**: `relations/query.py`, `core/relation_types.py`, `cli/list.py`

## 3. Entrance Criteria
- [x] Phase 03 complete (commit 55148fe)
- [x] DR-090 §P3 designed with concrete code examples

## 4. Exit Criteria / Done When
- [x] 4 collectors + dispatcher in `relations/query.py`
- [x] `REFERENCE_SOURCES` updated with `domain_field`, `backlog_field`
- [x] `collect_references()` chains `_collect_from_domain_fields()`
- [x] `list backlog --related-to` uses `matches_related_to()` (replaces raw frontmatter)
- [x] VT-090-P3-1 through P3-8 all passing
- [x] `just` clean (3935 tests pass, ruff clean)

## 5. Verification
- `just test` — full suite
- `just lint` — ruff clean
- `just pylint-files supekku/scripts/lib/relations/query.py supekku/scripts/lib/core/relation_types.py supekku/cli/list.py`

## 6. Assumptions & STOP Conditions
- Assumptions: All domain models use `list[str]` for reference fields (verified)
- Assumptions: `coverage_evidence` on RequirementRecord is `list[str]` (verified)
- STOP when: A model field turns out to be a nested structure needing special parsing

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 4.1 | Add domain_field, backlog_field to REFERENCE_SOURCES | [ ] | relation_types.py |
| [x] | 4.2 | _collect_from_decision_fields() | [x] | 11 list fields |
| [x] | 4.3 | _collect_from_governance_fields() | [x] | 9 fields (includes policies) |
| [x] | 4.4 | _collect_from_requirement_fields() | [x] | 4 list + scalar primary_spec |
| [x] | 4.5 | _collect_from_backlog_fields() | [x] | + frontmatter relations |
| [x] | 4.6 | _collect_from_domain_fields() dispatcher | [ ] | chains 4.2–4.5 |
| [x] | 4.7 | Wire into collect_references() | [ ] | depends on 4.6 |
| [x] | 4.8 | Update backlog --related-to | [ ] | matches_related_to() |
| [x] | 4.9 | Tests (VT-090-P3-1 through P3-8) | [ ] | 87 tests, TDD |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| coverage_evidence may contain dicts | Verified: list[str] on RequirementRecord | resolved |
| Semantic overlap between domain_field and backlog_field sources | Distinct provenance by design (DR-090 §P3-1 vs §P3-2) | resolved |

## 9. Decisions & Outcomes
- 2026-03-14 — Following DR-090 with minor adaptations: getattr-based collectors, `source="domain_field"` for typed models, `source="backlog_field"` for BacklogItem frontmatter dict.
- 2026-03-14 — `supersedes`/`superseded_by` detail values overlap with RELATION_TYPES. Semantic separation enforced by `source` field, not detail uniqueness. Test updated.
- 2026-03-14 — Extracted `_collect_from_list_fields()` helper to DRY the 3 typed model collectors.
- 2026-03-14 — Added frontmatter `relations` handling to backlog collector since BacklogItem.relations is not a dataclass field.

## 10. Findings / Research Notes
- DecisionRecord: 11 fields confirmed (specs, deltas, requirements, revisions, audits, policies, standards, related_decisions, related_policies, supersedes, superseded_by)
- PolicyRecord: 8 fields (specs, requirements, deltas, standards, related_policies, related_standards, supersedes, superseded_by)
- StandardRecord: 8 fields (specs, requirements, deltas, policies, related_policies, related_standards, supersedes, superseded_by)
- RequirementRecord: 4 list fields (specs, implemented_by, verified_by, coverage_evidence) + scalar primary_spec
- BacklogItem.frontmatter is dict[str, Any]; keys: linked_deltas, related_requirements

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored (3935 tests, ruff clean)
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase: P5 — P4 reverse reference filtering
