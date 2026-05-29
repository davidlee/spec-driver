---
id: IP-141-P02
slug: "141-audit_artefact_metadata_propagation-phase-02"
name: "IP-141 Phase 02 — List enrichment"
created: "2026-05-29"
updated: "2026-05-29"
status: completed
kind: phase
plan: IP-141
delta: DE-141
---

# Phase 2 — List enrichment

## 1. Objective

Enrich `list audits` with audit-specific columns (Mode, Delta, Findings, Disposed). Add `AuditFindingsSummary` domain computation, `AUDIT_COLUMNS`, `format_audit_list_row()`, relocate `_collect_audited_delta_ids` to domain layer.

## 2. Links & References

- **Delta**: DE-141
- **Design Revision**: DR-141 §5.0–§5.5 (columns, summary, formatter, CLI wiring)
- **Specs / PRODs**: PROD-004.FR-001
- **Decisions**: DEC-141-01 (summary in domain), DEC-141-02 (audited_delta_ids relocation), DEC-141-07 (mode/delta_ref on ChangeArtifact)

## 3. Entrance Criteria

- [x] P01 completed — block module + loader + ChangeArtifact extension deployed
- [x] `load_audit_findings()` available for summary computation

## 4. Exit Criteria / Done When

- [ ] `AuditFindingsSummary` dataclass in `audit_check.py` with `findings_cell()` and `disposed_cell()` methods
- [ ] `audit_findings_summary()` computes breakdown from block (preferred) or FM fallback
- [ ] `collect_audited_delta_ids()` relocated from `cli/list/deltas.py` to `audit_check.py`
- [ ] `AUDIT_COLUMNS` in `formatters/column_defs.py`
- [ ] `format_audit_list_row()` and `format_audit_list_table()` in `change_formatters.py`
- [ ] `list audits` CLI wired to use enriched formatter
- [ ] VT-141-LIST-001 through -006 passing
- [ ] All existing tests still pass
- [ ] Lint clean

## 5. Verification

- `uv run python -m pytest supekku/scripts/lib/changes/audit_check_summary_test.py -x`
- `uv run python -m pytest supekku/scripts/lib/formatters/ -x`
- `uv run python -m pytest supekku -x -q`
- `uv run ruff check supekku`

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `ChangeArtifact.mode` and `.delta_ref` populated from P01 work
  - `load_audit_findings()` dual-path loader available
  - Existing `format_change_list_table` pattern applicable for audit variant
- **STOP when**:
  - `list audits` CLI structure differs significantly from assumed → investigate

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 2.1 | Add `AuditFindingsSummary` + `audit_findings_summary()` to `audit_check.py` | [ ] | DEC-141-01 |
| [ ] | 2.2 | Relocate `_collect_audited_delta_ids` to `audit_check.py` | [P] | DEC-141-02 |
| [ ] | 2.3 | Add `AUDIT_COLUMNS` to `column_defs.py` | [P] | DR-141 §5.1 |
| [ ] | 2.4 | Add `format_audit_list_row()` + `format_audit_list_table()` to `change_formatters.py` | [ ] | DR-141 §5.4 |
| [ ] | 2.5 | Wire `list audits` CLI to use enriched formatter | [ ] | DR-141 §5.5 |
| [ ] | 2.6 | Write tests: VT-141-LIST-001..006 | [ ] | After 2.1–2.5 |
| [ ] | 2.7 | Full test suite + lint pass | [ ] | Gate |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| `list audits` CLI may have different wiring than expected | Read reviews.py before implementing | open |

## 9. Decisions & Outcomes

_(populated during execution)_

## 10. Findings / Research Notes

_(populated during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria (§4) satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes for P04
