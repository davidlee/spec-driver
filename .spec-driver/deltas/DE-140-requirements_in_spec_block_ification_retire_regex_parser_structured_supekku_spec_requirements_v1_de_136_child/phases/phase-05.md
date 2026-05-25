---
id: IP-140-P05
slug: "140-requirements_in_spec_block_ification_retire_regex_parser_structured_supekku_spec_requirements_v1_de_136_child-phase-05"
name: "IP-140 Phase 05 — Strict Flip & Integration"
created: "2026-05-25"
updated: "2026-05-25"
status: in-progress
kind: phase
plan: IP-140
delta: DE-140
---

# Phase 05 — Strict Flip & Integration

## 1. Objective

Wire strict-mode enforcement for spec requirements: parser stops regex fallback when strict, validator errors on missing blocks, operational guard blocks the flip until all specs are migrated. E2E verification across the full pipeline.

## 2. Links & References

- **Delta**: DE-140
- **Design Revision**: DR-140 §7 (Validation & Strict Flip)
- **Specs**: PROD-004.FR-001, PROD-004.FR-002
- **Key Decisions**:
  - DEC-140-04: Strict flip via schema_version bump (DE-139 pattern)
  - DEC-140-13: Strict flip operationally gated — all specs must have blocks before bump
  - DEC-140-03: Block-first, regex fallback, never both
- **Exemplars**: DE-139 strict-flip pattern in `workflow.toml`

## 3. Entrance Criteria

- [x] P01 complete — block infrastructure
- [x] P02 complete — reading pipeline (block-first parser)
- [x] P03 complete — validation wiring + strict content checks
- [x] P04 complete — migration module + CLI

## 4. Exit Criteria / Done When

- [x] `records_from_spec()` accepts `strict: bool` kwarg
- [x] When strict: no block → zero records (no regex fallback)
- [x] When strict: extraction failure → error log, zero records (no regex fallback)
- [x] When non-strict: extraction failure → regex fallback (existing behavior preserved)
- [x] Validator: missing block → error when `self.strict`
- [x] Operational guard: `check_requirements_migration_complete()` returns unmigrated spec IDs
- [x] Admin CLI command: `strict-flip-requirements` — runs guard, writes config if clean
- [x] All 7 VTs passing (VT-140-017, -018, -021, -023, -024, -029)
- [ ] VH-140-001 and VH-140-002 attestable
- [x] `just lint` clean on modified files
- [x] `just pylint-files` clean on modified files
- [x] Full regression green

## 5. Verification

| VT/VH | Description |
|-------|-------------|
| VT-140-017 | Strict mode — missing block → error |
| VT-140-018 | Strict mode — empty description/acceptance_criteria → error |
| VT-140-021 | Post-flip — no block → zero records, no regex fallback |
| VT-140-023 | Pre-flip extraction failure → regex fallback |
| VT-140-024 | Post-flip extraction failure → error, no fallback |
| VT-140-029 | Strict flip blocked when unmigrated spec/prod files remain |
| VH-140-001 | Interactive migration on real corpus |
| VH-140-002 | Strict flip enforcement across corpus |

Commands: `just test`, `just lint`, `just pylint-files <modified files>`

## 6. Assumptions & STOP Conditions

- Validator missing-block check gated on existing `self.strict` — consistent with P03 strict content checks
- Parser `strict` param not auto-wired to config — callers pass explicitly; the "flip" is connecting config to registry
- Admin command writes `[validation.strict_requirements] enabled = true` to workflow.toml — separate from per-kind `[validation.strict]` (which filters to artifact kinds only)
- STOP if: per-kind strict map (`get_strict_map`) needs fundamental redesign to accommodate feature-level toggles
- STOP if: registry.sync() config threading reveals circular dependencies

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 5.1 | Parser: add `strict` kwarg to `records_from_spec()` + `_try_extract_block()` | | Core behavior change |
| [x] | 5.2 | Validator: missing-block error when `self.strict` | [P] | After 5.1 |
| [x] | 5.3 | Operational guard: `check_requirements_migration_complete()` | [P] | Pure function |
| [x] | 5.4 | Admin CLI: `strict-flip-requirements` command | | After 5.3 |
| [x] | 5.5 | Tests: VT-140-017, -018, -021, -023, -024, -029 | | 8 parser + 7 validator |
| [x] | 5.6 | Lint pass on all modified files | | Ruff clean, pylint established only |

### Task Details

- **5.1 — Parser strict-mode wiring**
  - **Files**: `supekku/scripts/lib/requirements/parser.py` (MODIFY)
  - **Logic**:
    1. Add `strict: bool = False` keyword-only param to `records_from_spec()`
    2. Pass `strict` to `_try_extract_block()`
    3. `_try_extract_block()` when strict + ValueError: log error (not warning), return None
    4. `records_from_spec()` when strict + no block: return early (no regex fallback)
    5. Pre-flip (strict=False): existing behavior preserved exactly

- **5.2 — Validator missing-block error**
  - **Files**: `supekku/scripts/lib/validation/validator.py` (MODIFY)
  - **Logic**: In `_validate_spec_requirements_blocks()`, change `if block is None: continue` to emit error when `self.strict`

- **5.3 — Operational guard**
  - **Files**: `supekku/scripts/lib/validation/migration_guard.py` (CREATE) or in `validation/validator.py`
  - **Logic**: `check_requirements_migration_complete(workspace) -> list[str]` — iterate all specs, check each has `spec.requirements` block, return list of unmigrated spec IDs

- **5.4 — Admin CLI command**
  - **Files**: `spec_driver/presentation/cli/admin/strict_flip_requirements.py` (CREATE), `supekku/cli/admin.py` (MODIFY)
  - **Logic**: Run guard → if unmigrated specs exist, print list and refuse → if clean, confirm and write config

- **5.5 — Tests**
  - **Files**: `supekku/scripts/lib/requirements/parser_strict_test.py` (CREATE), `supekku/scripts/lib/validation/validator_spec_requirements_test.py` (MODIFY)
  - **VTs covered**: VT-140-017, -018, -021, -023, -024, -029

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Strict enforcement breaks unmigrated specs at runtime | Parser strict not auto-wired to config — explicit opt-in only | design |
| Operational guard misses edge cases (empty specs, nested dirs) | Guard uses same `workspace.specs.all_specs()` as validator | design |
| Registry needs config to pass strict — circular deps | Registry already has repo_root; config load is one call | design |

## 9. Decisions & Outcomes

- Parser `strict` param not auto-wired to config — explicit opt-in only. The "flip" is connecting config → registry → parser after migration completes.
- Validator missing-block error gated on `self.strict` (same as P03 content checks) — no separate feature toggle for this diagnostic.
- Operational guard lives in `validator.py` as a pure function — reusable by both CLI and programmatic callers.
- Separate config section `[validation.strict_requirements]` instead of adding to `get_strict_map()` — the strict map filters to registered artifact kinds, and `spec_requirements` is not a kind.
- VT-140-018 counted as covered by P03's existing strict content tests — no duplication needed.

## 10. Findings / Research Notes

- `get_strict_map()` filters to registered artifact kinds — `spec_requirements` would be dropped. Need separate config path for requirements-specific strict toggle.
- `validate workspace` receives `strict` from CLI `--strict` flag, not from config. Per-kind `[validation.strict]` only applies to `validate file`.
- P03's strict content checks (trimmed-empty/blank) already fire under `self.strict` — only for specs WITH blocks, so no migration-ordering issue.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes in notes.md
