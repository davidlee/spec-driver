---
id: IP-085.PHASE-02
slug: 085-surface_relation_and_backlog_metadata_in_cli_and_skills-phase-02
name: "CLI flags and relation formatters"
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-085.PHASE-02
plan: IP-085
delta: DE-085
objective: >-
  Add --related-to, --relation, --refs CLI flags to list deltas and list specs.
  Create relation formatters. Enhance create delta --from-backlog to populate
  context_inputs and relations. Regression-safe on --implements and --informed-by.
entrance_criteria:
  - Phase 1 complete (query module, constants, Spec.relations)
exit_criteria:
  - relation_formatters.py created with format_refs_count and format_refs_tsv
  - list deltas supports --related-to, --relation, --refs flags
  - list specs supports --related-to, --relation, --refs flags
  - --relation TYPE:TARGET parsing with colon split and warning on unknown type
  - create delta --from-backlog populates context_inputs and relations
  - VT-085-002 through VT-085-005 and VT-085-007 passing
  - VT-085-003 and VT-085-004 regression tests green
  - just check green
verification:
  tests:
    - VT-085-002
    - VT-085-003
    - VT-085-004
    - VT-085-005
    - VT-085-007
  evidence: []
tasks:
  - id: T01
    summary: Create relation_formatters.py with format_refs_count and format_refs_tsv
  - id: T02
    summary: Add --related-to, --relation, --refs flags to list deltas
  - id: T03
    summary: Add --related-to, --relation, --refs flags to list specs
  - id: T04
    summary: Enhance create delta --from-backlog to populate context_inputs and relations
  - id: T05
    summary: Write formatter tests (VT-085-005)
  - id: T06
    summary: Write CLI integration tests (VT-085-002)
  - id: T07
    summary: Write --from-backlog tests (VT-085-007)
  - id: T08
    summary: Verify regression (VT-085-003, VT-085-004)
  - id: T09
    summary: Lint and full check
risks:
  - id: R1
    description: list.py is already large — adding flags may push past 150-line function limits
    mitigation: Keep filter logic in query module; CLI just calls find_related_to/find_by_relation
  - id: R2
    description: --relation TYPE:TARGET colon parsing edge cases
    mitigation: Split on first colon only; test empty type/target/no-colon
  - id: R3
    description: Formatter R4 residual — pass list[ReferenceHit] not artifact
    mitigation: Formatters receive pre-collected hits per DR-085 R4
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-085.PHASE-02
```

# Phase 2 — CLI flags and relation formatters

## 1. Objective

Add CLI-visible relation discovery: `--related-to`, `--relation`, `--refs` flags on `list deltas` and `list specs`. Create pure relation formatters. Enhance `create delta --from-backlog` to auto-populate `context_inputs` and `relations`. All existing filter semantics (`--implements`, `--informed-by`) unchanged.

## 2. Links & References
- **Delta**: [DE-085](../DE-085.md)
- **Design Revision**: [DR-085](../DR-085.md) §5.4 (registry), §5.5 (CLI flags), §5.6 (column rendering), §5.7 (`--from-backlog`)
- **Specs**: PROD-010 (CLI UX), PROD-002 (Delta Creation)
- **Phase 1 outputs**: `relations/query.py`, `core/relation_types.py`, `Spec.relations`

## 3. Entrance Criteria
- [x] Phase 1 complete — query module, constants, Spec.relations all working

## 4. Exit Criteria / Done When
- [x] `formatters/relation_formatters.py` created with `format_refs_count()` and `format_refs_tsv()`
- [x] `list deltas` supports `--related-to ID`, `--relation TYPE:TARGET`, `--refs`
- [x] `list specs` supports `--related-to ID`, `--relation TYPE:TARGET`, `--refs`
- [x] `--relation` parses on first colon; unknown type emits stderr warning
- [x] `create delta --from-backlog` populates `context_inputs` and `relations`
- [x] VT-085-002 passing (CLI integration tests)
- [x] VT-085-003 regression green (--implements unchanged)
- [x] VT-085-004 regression green (--informed-by unchanged)
- [x] VT-085-005 passing (formatter tests)
- [x] VT-085-007 passing (--from-backlog enhancement)
- [x] `just check` green

## 5. Verification
- `just test` — VT-085-002 through VT-085-005, VT-085-007
- `just lint` — zero warnings on new and modified files
- `just pylint-files` on all touched files
- `just check` — full suite

## 6. Assumptions & STOP Conditions
- **Assumption**: `format_list_table` in `table_utils.py` supports optional columns via the existing `show_external` pattern (conditional column insertion).
- **Assumption**: `ChangeArtifact` already has `.relations`, `.applies_to`, `.context_inputs` attributes accessible to `collect_references()`.
- **STOP if**: `list.py` function complexity exceeds maintainable limits — consider extracting a `_apply_relation_filters()` helper.

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | T01 | Create `formatters/relation_formatters.py` | [P] | Done — 2 pure functions, 10 tests |
| [x] | T02 | Add `--related-to`, `--relation`, `--refs` to `list deltas` | | Done |
| [x] | T03 | Add `--related-to`, `--relation`, `--refs` to `list specs` | | Done |
| [x] | T04 | Enhance `create delta --from-backlog` | [P] | Done — context_inputs + relations auto-populated |
| [x] | T05 | Formatter tests (VT-085-005) | [P] | Done — 10 tests |
| [x] | T06 | CLI integration tests (VT-085-002) | | Done — 11 tests (7 delta, 4 spec) |
| [x] | T07 | `--from-backlog` tests (VT-085-007) | [P] | Done — 2 tests in creation_test.py |
| [x] | T08 | Regression verification (VT-085-003, VT-085-004) | | 3697 pass, 0 fail |
| [x] | T09 | Lint + full check | | `just check` green, new files pylint 10/10 |

### Task Details

- **T01 — `formatters/relation_formatters.py`**
  - **Files**: `supekku/scripts/lib/formatters/relation_formatters.py` (new), `supekku/scripts/lib/formatters/__init__.py` (update exports)
  - **Design**: DR-085 §5.6, R4. Pure formatting functions receiving `list[ReferenceHit]`, not artifacts.
  - **Functions**:
    - `format_refs_count(refs: list[ReferenceHit]) -> str` — e.g. `"3 refs"` or `""`
    - `format_refs_tsv(refs: list[ReferenceHit]) -> str` — e.g. `"relation.implements:PROD-010,context_input.issue:IMPR-006"`
  - **Testing**: VT-085-005 — empty list, single ref, multiple refs, various source/detail combos

- **T02 — `list deltas` flags**
  - **Files**: `supekku/cli/list.py` (modify delta list command)
  - **Design**: DR-085 §5.5.
  - **Approach**:
    - Add `--related-to` option → call `find_related_to(artifacts, target_id)` from query module
    - Add `--relation` option → parse `TYPE:TARGET` on first colon, call `find_by_relation()`; warn on unknown type
    - Add `--refs` flag → conditional column in `format_change_list_table` (count in table, pairs in TSV)
    - Filter order: `--related-to`/`--relation` pre-filter, then existing status/text filters
  - **Key**: `--implements` semantics preserved exactly (DEC-085-002)
  - **Column**: Update `change_formatters.py` to accept `show_refs` parameter, add refs column via `collect_references()` + `format_refs_count()`/`format_refs_tsv()`

- **T03 — `list specs` flags**
  - **Files**: `supekku/cli/list.py` (modify spec list command)
  - **Design**: DR-085 §5.5. Same flags as T02 but on specs.
  - **Approach**: Same pattern as T02. Specs have `.relations` (from P01) and `.informed_by` — both searched by `collect_references()`.
  - **Column**: Update `spec_formatters.py` to accept `show_refs`, add refs column.
  - **Key**: `--informed-by` semantics preserved exactly (DEC-085-002/004)

- **T04 — `create delta --from-backlog` enhancement**
  - **Files**: `supekku/cli/create.py` (modify `--from-backlog` branch)
  - **Design**: DR-085 §5.7.
  - **Approach**: When `--from-backlog ITEM-ID` is used, add:
    - `context_inputs = [{"type": "issue", "id": item.id}]`
    - `relations = [{"type": "relates_to", "target": item.id}]`
  - **Key**: Check what `create_delta()` accepts — may need to pass these through or write them post-creation.

- **T05 — Formatter tests (VT-085-005)**
  - **Files**: `supekku/scripts/lib/formatters/relation_formatters_test.py` (new)
  - Edge cases: empty refs, single ref, multiple refs with different sources, special characters in target IDs

- **T06 — CLI integration tests (VT-085-002)**
  - **Files**: `supekku/cli/list_test.py` (extend)
  - Test `--related-to`, `--relation TYPE:TARGET`, `--refs` flag for both deltas and specs
  - Edge cases: no colon in `--relation` (error), empty type, unknown type (warning), composing with `--status`

- **T07 — `--from-backlog` tests (VT-085-007)**
  - **Files**: `supekku/cli/create_test.py` (extend)
  - Verify context_inputs and relations populated after `--from-backlog`

- **T08 — Regression (VT-085-003, VT-085-004)**
  - Run existing `--implements` and `--informed-by` tests, confirm pass unchanged

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| R1: list.py function size | Keep filter logic in query module; CLI just delegates | Open |
| R2: --relation colon parsing | Split on first colon; explicit edge case tests | Open |
| R3: Formatter purity (R4) | Formatters take list[ReferenceHit], not artifact | Open |

## 9. Decisions & Outcomes
- 2026-03-09: Moved relation_formatters imports to top-level (no circular dependency exists); ruff PLC0415 forbids lazy imports.
- 2026-03-09: `_parse_relation_filter()` helper in list.py — splits on first colon, uses `typer.BadParameter` for invalid format, warns on unknown type to stderr.
- 2026-03-09: `create_delta()` extended with `context_inputs` and `relations` params; defaults to `[]` in frontmatter so all new deltas have consistent schema.
- 2026-03-09: Relation filters applied after the main filter loop in list_deltas (post-dict-to-list conversion), before sorting. In list_specs they're applied after --informed-by, before status filters.

## 10. Findings / Research Notes

### Pre-phase research

- `list deltas` filter pattern at `list.py:356-511`: uses `parse_multi_value_filter`, `registry.find_by_implements()`, list comprehension chains
- `list specs` at `list.py:68-353`: similar pattern, includes `--informed-by` via `registry.find_by_informed_by()`
- `format_change_list_table` uses conditional column insertion via `show_external` bool — same pattern for `show_refs`
- `format_list_table` in `table_utils.py` dispatches table/TSV/JSON via prepare_row/prepare_tsv_row/to_json
- `create delta --from-backlog` at `create.py:153-199`: extracts title + requirements; no context_inputs/relations yet
- `create_delta()` signature needs investigation — may need `context_inputs` and `relations` parameters added

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Notes updated with findings
- [x] Hand-off notes to Phase 3 — skill update + verification + coverage update only; no code changes
