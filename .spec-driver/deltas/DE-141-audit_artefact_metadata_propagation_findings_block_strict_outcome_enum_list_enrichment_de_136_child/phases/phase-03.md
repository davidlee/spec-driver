---
id: IP-141-P03
slug: "141-audit_artefact_metadata_propagation-phase-03"
name: "IP-141 Phase 03 — Strict enforcement"
created: "2026-05-29"
updated: "2026-05-29"
status: completed
kind: phase
plan: IP-141
delta: DE-141
---

# Phase 3 — Strict enforcement

## 1. Objective

Switch validator callers from `fm.get("findings")` to `load_audit_findings()`. Gate existing audit disposition/collision checks on `self.strict`. Add new strict-only checks: undisposed findings on completed audits, `closure_override` rationale/escalation, duplicate finding IDs.

## 2. Links & References

- **Delta**: DE-141
- **Design Revision**: DR-141 §4 (strict enforcement table)
- **Specs / PRODs**: PROD-004.FR-002

## 3. Entrance Criteria

- [x] P01 completed — `load_audit_findings()` available

## 4. Exit Criteria / Done When

- [ ] `_validate_audit_disposition()` reads findings via `load_audit_findings()`
- [ ] `_check_finding_id_collisions()` reads findings via `load_audit_findings()`
- [ ] `collect_gating_findings()` reads findings via `load_audit_findings()`
- [ ] Invalid outcome enum → error under strict, warn under non-strict
- [ ] Completed audit + undisposed finding → error under strict
- [ ] `closure_override` without rationale → error under strict
- [ ] `closure_override.effect` escalation → error under strict
- [ ] Duplicate finding IDs → error under strict
- [ ] VT-141-STRICT-001 through -005 passing
- [ ] All existing tests still pass
- [ ] Lint clean

## 5. Verification

- `uv run python -m pytest supekku/scripts/lib/validation/validator_test.py -x -k audit`
- `uv run python -m pytest supekku -x -q`
- `uv run ruff check supekku`

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `self.strict` attribute available in WorkspaceValidator
  - Existing audit validation at :506, :608 in validator.py is the complete set
- **STOP when**:
  - Additional FM callers found beyond the three identified → inventory before proceeding

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.1 | Switch `_validate_audit_disposition()` to `load_audit_findings()` + strict gating | [ ] | DR-141 §4 |
| [ ] | 3.2 | Switch `_check_finding_id_collisions()` to `load_audit_findings()` + strict gating | [ ] | DR-141 §4 |
| [ ] | 3.3 | Switch `collect_gating_findings()` to `load_audit_findings()` | [ ] | DEC-141-06 |
| [ ] | 3.4 | Add undisposed-finding check (completed audit) | [ ] | New check |
| [ ] | 3.5 | Add closure_override rationale + escalation checks | [ ] | New check |
| [ ] | 3.6 | Write tests: VT-141-STRICT-001..005 | [ ] | After 3.1–3.5 |
| [ ] | 3.7 | Full test suite + lint pass | [ ] | Gate |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Existing tests depend on FM-based findings reading | Dual-path loader preserves FM fallback | open |

## 9. Decisions & Outcomes

_(populated during execution)_

## 10. Findings / Research Notes

_(populated during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria (§4) satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes for P04
