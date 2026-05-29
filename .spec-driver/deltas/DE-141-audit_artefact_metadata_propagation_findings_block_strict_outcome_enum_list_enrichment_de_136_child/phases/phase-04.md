---
id: IP-141-P04
slug: "141-audit_artefact_metadata_propagation-phase-04"
name: "IP-141 Phase 04 — Migration + sweep + strict flip"
created: "2026-05-29"
updated: "2026-05-29"
status: completed
kind: phase
plan: IP-141
delta: DE-141
---

# Phase 4 — Migration + sweep + strict flip

## 1. Objective

Create migration step `v0_10_0_004_audit_findings` to move findings from FM to block. Sweep corpus. Cut `findings` from `AUDIT_FRONTMATTER_METADATA`. Flip `[validation.strict].audit = true` in `workflow.toml`. Update audit template.

## 2. Links & References

- **Delta**: DE-141
- **Design Revision**: DR-141 §6 (migration), §3.3 (FM cut), §6.3 (strict flip)
- **Specs / PRODs**: PROD-004.FR-001, PROD-004.FR-002
- **Precedent**: `spec_driver/migrations/v0_10_0_003_prod_blocks/`

## 3. Entrance Criteria

- [ ] P01, P02, P03 all completed
- [ ] `load_audit_findings()` + strict validation operational

## 4. Exit Criteria / Done When

- [ ] Migration step `v0_10_0_004_audit_findings/` created following DE-138 precedent
- [ ] Migration handles: FM→block, idempotence, FM+block coexistence, universal FM cuts, drift entries for invalid outcomes
- [ ] `findings` cut from `AUDIT_FRONTMATTER_METADATA`
- [ ] Corpus migrated: all audit files have findings block, no FM findings key
- [ ] Audit template updated with block instead of FM
- [ ] `[validation.strict].audit = true` in `workflow.toml`
- [ ] VT-141-MIGRATE-001..005 and VA-141-CORPUS-001 passing
- [ ] All existing tests still pass
- [ ] Lint clean

## 5. Verification

- `uv run python -m pytest spec_driver/migrations/v0_10_0_004_audit_findings/ -x`
- `uv run spec-driver admin migrate --kind audit --dry-run`
- `uv run spec-driver validate workspace --kind audit --strict`
- `uv run python -m pytest supekku -x -q`

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - DEC-138-12 constraint: migration imports only stdlib + helpers + yaml
  - AUD-012 `outcome: pass` produces drift entry (not auto-fix)
- **STOP when**:
  - Migration breaks existing audit loading → investigate before proceeding
  - More than 3 drift entries from invalid outcomes → review scope

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 4.1 | Create migration module `v0_10_0_004_audit_findings/` | [ ] | DEC-141-05 |
| [ ] | 4.2 | Write migration tests: VT-141-MIGRATE-001..005 | [ ] | After 4.1 |
| [ ] | 4.3 | Run migration: `admin migrate --kind audit` | [ ] | After tests pass |
| [ ] | 4.4 | Cut `findings` from `AUDIT_FRONTMATTER_METADATA` | [ ] | After migration |
| [ ] | 4.5 | Update `supekku/templates/audit.md` | [P] | Block template |
| [ ] | 4.6 | Flip `[validation.strict].audit = true` | [ ] | After corpus clean |
| [ ] | 4.7 | VA-141-CORPUS-001: `validate workspace --kind audit` | [ ] | Post-flip |
| [ ] | 4.8 | Full test suite + lint pass | [ ] | Gate |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| AUD-012 invalid outcome blocks strict flip | Drift entry + manual disposition | open |
| FM cut breaks callers not yet migrated to loader | P03 migrates all callers first | design |

## 9. Decisions & Outcomes

_(populated during execution)_

## 10. Findings / Research Notes

_(populated during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria (§4) satisfied
- [ ] Verification evidence stored
- [ ] DE-141 ready for closure
