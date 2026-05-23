---
id: IP-140-P04
slug: "140-requirements_in_spec_block_ification_retire_regex_parser_structured_supekku_spec_requirements_v1_de_136_child-phase-04"
name: "IP-140 Phase 04 — Migration"
created: "2026-05-23"
updated: "2026-05-23"
status: in-progress
kind: phase
plan: IP-140
delta: DE-140
---

# Phase 04 — Migration

## 1. Objective

Implement interactive per-spec migration from prose-format requirements (`- **FR-001**: Title`) to structured `supekku:spec.requirements@v1` YAML blocks. Migration is standalone (not batch-orchestrated), per-spec, atomic, and writes drift ledger entries for unparseable or placeholder content.

## 2. Links & References

- **Delta**: DE-140
- **Design Revision**: DR-140 §6 (Migration)
- **Specs**: PROD-004.FR-001
- **Key Decisions**:
  - DEC-140-05: Interactive migration in migration folder
  - DEC-140-11: Migration atomic per-spec
  - DEC-140-12: Post-write validation mandatory
  - DEC-138-12: Migration isolation (stdlib + helpers + protocol + pyyaml only)
- **Exemplars**: `spec_driver/migrations/v0_10_0_003_prod_blocks/migration.py`

## 3. Entrance Criteria

- [x] P01 complete — block infrastructure (extract, render, validate)
- [x] DR-140 §6 reviewed
- [x] Existing migration step patterns studied

## 4. Exit Criteria / Done When

- [ ] Migration module in `spec_driver/migrations/spec_requirements/` with frozen-local constants
- [ ] DEC-138-12 isolation verified (zero supekku imports in migration module)
- [ ] `spec-driver admin migrate-requirements <SPEC-ID>` CLI command wired
- [ ] `--dry-run` mode shows proposed block without writes or prompts
- [ ] Guard: refuses if spec already has a `spec.requirements` block
- [ ] Parsed requirements rendered as valid `supekku:spec.requirements@v1` block
- [ ] Block inserted after frontmatter, before first heading
- [ ] Post-write validation catches malformed output, atomic revert on failure
- [ ] Drift ledger entries written for unparseable requirements and placeholders
- [ ] All 5 VAs passing (VA-140-001 through VA-140-005)
- [ ] `just lint` clean on modified files
- [ ] `just pylint-files` clean on modified files

## 5. Verification

| VA | Description |
|----|-------------|
| VA-140-001 | Migration dry-run produces valid proposed block |
| VA-140-002 | Migration post-write validation catches malformed output |
| VA-140-003 | Migration atomic per-spec — skip aborts entire spec |
| VA-140-004 | Migration refuses if block already present |
| VA-140-005 | Migration drift entries persist as DL-* ledger files |

Commands: `just test`, `just lint`, `just pylint-files spec_driver/migrations/spec_requirements/migration.py spec_driver/presentation/cli/admin/migrate_requirements.py`

## 6. Assumptions & STOP Conditions

- Assumes folder name `spec_requirements/` (no version prefix) is acceptable since this is NOT a batch-orchestrated step — the orchestrator's `_discover_steps()` skips it
- Assumes `_helpers.atomic_write()` provides sufficient atomicity for revert semantics
- Assumes regex pattern `_REQUIREMENT_LINE` from `parser.py` is the pattern to freeze locally
- STOP if: interactive flow requires terminal capabilities beyond basic input()
- STOP if: DEC-138-12 isolation conflicts with needed functionality
- STOP if: drift ledger path/format conflicts with existing drift entries

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 4.1 | Create migration module with frozen-local constants + transform | | Core logic |
| [ ] | 4.2 | Implement guard (block-already-present detection) | [P] | After 4.1 |
| [ ] | 4.3 | Implement dry-run mode (preview proposed block) | [P] | After 4.1 |
| [ ] | 4.4 | Implement write mode with post-write validation + revert | | After 4.1 |
| [ ] | 4.5 | Implement drift ledger entry creation | [P] | After 4.1 |
| [ ] | 4.6 | Wire CLI command `admin migrate-requirements` | | After 4.1–4.5 |
| [ ] | 4.7 | Write tests covering all 5 VAs | | After 4.1–4.6 |
| [ ] | 4.8 | Lint pass on all modified files | | After 4.7 |

### Task Details

- **4.1 — Migration module: frozen-local constants + transform**
  - **Files**: `spec_driver/migrations/spec_requirements/__init__.py` (CREATE), `spec_driver/migrations/spec_requirements/migration.py` (CREATE)
  - **Design**: DR-140 §6, DEC-138-12
  - **Logic**:
    1. Frozen-local copies: `_REQUIREMENT_LINE` regex, `_REQUIREMENTS_MARKER`, schema/version constants, lifecycle enum values, kind canonical values + alias map
    2. `_parse_requirements(body: str) -> list[dict]`: extract requirement entries from prose body using frozen regex
    3. `_render_block(spec_id: str, requirements: list[dict]) -> str`: render `supekku:spec.requirements@v1` block YAML
    4. `_insert_block(text: str, block: str) -> str`: insert block after frontmatter, before first heading
  - **Isolation**: Only `import yaml`, `from spec_driver.migrations._helpers import ...`

- **4.2 — Guard: block-already-present**
  - **Logic**: Check if body already contains `supekku:spec.requirements@v1` marker → refuse with message
  - **VA**: VA-140-004

- **4.3 — Dry-run mode**
  - **Logic**: Parse → render → display proposed block. No writes, no prompts.
  - **VA**: VA-140-001

- **4.4 — Write mode with post-write validation + revert**
  - **Logic**: Parse → render → insert → `atomic_write()` → re-read and verify marker present and YAML parseable. On validation failure: revert (rewrite original).
  - **VA**: VA-140-002, VA-140-003

- **4.5 — Drift ledger entries**
  - **Files**: Drift entries written to `.spec-driver/drift/DL-NNN.md`
  - **Logic**: For each: unparseable requirement-like line → `DRIFT_REQUIREMENT_UNPARSEABLE`; empty description → `DRIFT_DESCRIPTION_PLACEHOLDER`; empty acceptance_criteria → `DRIFT_ACCEPTANCE_PLACEHOLDER`
  - **VA**: VA-140-005

- **4.6 — CLI command wiring**
  - **Files**: `spec_driver/presentation/cli/admin/migrate_requirements.py` (CREATE), `spec_driver/presentation/cli/admin/__init__.py` (MODIFY)
  - **Logic**: Wire `migrate-requirements` as admin subcommand. CLI handles: repo root resolution, spec file lookup, interactive prompts (deferred — non-interactive first pass). Calls migration module for core logic.

- **4.7 — Tests**
  - **Files**: `spec_driver/migrations/spec_requirements/migration_test.py` (CREATE)
  - **Logic**: Test transform, guard, dry-run, write+validate, drift. Cover all 5 VAs.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Frozen regex drifts from runtime parser | Lockstep test comparing frozen vs `parser._REQUIREMENT_LINE` pattern string | |
| Interactive prompts not testable | Non-interactive core; interactive layer thin and tested via mock stdin | |
| Drift ledger ID collision | Sequential allocation from max existing DL-NNN | |

## 9. Decisions & Outcomes

- Folder named `spec_requirements/` (no version prefix) — not a batch step, orchestrator skips it silently.
- Interactive flow deferred to thin CLI layer (task 4.6). Migration module is pure transform + I/O.
- Non-interactive first: get transform/dry-run/write working, add interactive review after core works.

## 10. Findings / Research Notes

_(populated during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes in notes.md
