---
id: IP-115-P02
slug: "115-core_utility_extraction_parse_date_sequential_ids_title_extraction_atomic_write_block_patterns-phase-02"
name: IP-115 Phase 02 — Sequential ID consolidation
created: "2026-04-10"
updated: "2026-04-10"
status: draft
kind: phase
plan: IP-115
delta: DE-115
---

# Phase 02 — Sequential ID consolidation

## 1. Objective

Consolidate 8 sequential ID generation functions into a single `next_sequential_id(names, prefix, separator)` in `core/ids.py`. Update all call sites. Delete all originals.

## 2. Links & References

- **Delta**: DE-115
- **Design Revision**: DR-115 §7 (Design Decisions — `next_sequential_id` signature)
- **Specs**: SPEC-117, SPEC-126, SPEC-127
- **Governance**: POL-001, ADR-009

## 3. Entrance Criteria

- [ ] P01 complete — all simple extractions done
- [ ] `just check` passes

## 4. Exit Criteria / Done When

- [ ] `grep -rn 'def next_sequential_id' supekku/` returns exactly 1 result (in `core/ids.py`)
- [ ] `grep -rn 'def.*next.*identifier\|def.*generate_next.*id\|def.*next_ledger_id\|def next_id' supekku/` returns 0 results (all originals removed or delegating)
- [ ] `just check` passes clean

## 5. Verification

- Unit tests for `core/ids.py`: empty collection, single entry, multiple entries, prefix with dash separator, prefix with no separator, non-matching entries ignored
- Existing creation and registry tests green throughout
- `just lint` zero warnings on touched files

## 6. Assumptions & STOP Conditions

- Assumptions: all 8 variants implement the same logical algorithm (scan → regex-extract → max+1 → format). Confirmed by code review during DR-115.
- STOP when: `specs/creation.py:determine_next_identifier`'s looser regex (no prefix check) causes a test to break when tightened — investigate before proceeding.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | ----------- | --------- | ----- |
| [ ] | 2.1 | Create `core/ids.py` with `next_sequential_id` | | canonical implementation |
| [ ] | 2.2 | Write `core/ids_test.py` | | TDD: red then green |
| [ ] | 2.3 | Update directory-scan callers | [P] | `_next_identifier`, `determine_next_identifier`, `_next_ledger_id` |
| [ ] | 2.4 | Update registry-scan callers | [P] | `generate_next_adr_id`, `generate_next_policy_id`, `generate_next_standard_id` |
| [ ] | 2.5 | Update entries-based caller | [P] | `backlog/registry.py:next_identifier` |
| [ ] | 2.6 | Update cards caller | [P] | `CardRegistry.next_id` |
| [ ] | 2.7 | Delete all original functions | | after all callers verified |

### Task Details

- **2.1 Create `core/ids.py`**
  - **Approach**: `def next_sequential_id(names: Iterable[str], prefix: str, separator: str = "-") -> str:` — compile `rf"{re.escape(prefix)}{re.escape(separator)}(\d+)"`, scan names for max, return `f"{prefix}{separator}{max+1:03d}"`.
  - **Files**: `core/ids.py`

- **2.2 Write `core/ids_test.py`**
  - **Testing**: Empty input → `{prefix}-001`. Single match → next. Multiple → highest+1. Non-matching entries ignored. No separator variant (`separator=""`). Prefix with special chars (edge case for `re.escape`).

- **2.3 Update directory-scan callers**
  - `changes/_creation_utils.py:_next_identifier(base_dir, prefix)` → `next_sequential_id([e.name for e in base_dir.iterdir()], prefix)` (guard `base_dir.exists()` at call site)
  - `specs/creation.py:determine_next_identifier(base_dir, prefix)` → same pattern (note: filter to `is_dir()` entries, tighten regex by adding prefix)
  - `drift/creation.py:_next_ledger_id(drift_dir)` → `next_sequential_id([p.name for p in drift_dir.iterdir()], "DL")`

- **2.4 Update registry-scan callers**
  - `decisions/creation.py:generate_next_adr_id(registry)` → `next_sequential_id(registry.collect(), "ADR")`
  - `policies/creation.py:generate_next_policy_id(registry)` → `next_sequential_id(registry.collect(), "POL")`
  - `standards/creation.py:generate_next_standard_id(registry)` → `next_sequential_id(registry.collect(), "STD")`

- **2.5 Update entries-based caller**
  - `backlog/registry.py:next_identifier(entries, prefix)` → `next_sequential_id([e.name for e in entries], prefix)`

- **2.6 Update cards caller**
  - `cards/registry.py:CardRegistry.next_id` → `next_sequential_id([c.id for c in self.all_cards()], "T", separator="")`

- **2.7 Delete originals**
  - After all callers verified green: delete the 8 original functions. Run `just check` final gate.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| `specs/creation.py` looser regex breaks when tightened | Run spec creation tests after update; investigate if failures | open |
| `backlog/registry.py` accepts `[-_]` separator in input but shared function uses `-` | Shared regex uses `re.escape(separator)` which handles `-`; backlog currently outputs `-` only; `-_` input tolerance is a nicety — document if dropped | open |

## 9. Decisions & Outcomes

- 2026-04-10 — Canonical signature: `next_sequential_id(names: Iterable[str], prefix: str, separator: str = "-") -> str`. Callers convert their collection to names. `separator=""` handles cards.

## 10. Findings / Research Notes

- See DR-115 §8 for resolved open questions about `backlog/registry.py` and `CardRegistry.next_id` algorithm analysis.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes (if any)
