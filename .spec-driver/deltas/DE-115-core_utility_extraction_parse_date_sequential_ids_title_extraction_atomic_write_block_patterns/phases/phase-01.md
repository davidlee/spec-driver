---
id: IP-115-P01
slug: "115-core_utility_extraction_parse_date_sequential_ids_title_extraction_atomic_write_block_patterns-phase-01"
name: "IP-115 Phase 01 — Utility extractions"
created: "2026-04-10"
updated: "2026-04-10"
status: draft
kind: phase
plan: IP-115
delta: DE-115
---

# Phase 01 — Utility extractions

## 1. Objective

Extract 6 duplicated utilities into canonical homes. Each extraction: create/extend target module, write tests, replace all call sites, delete originals.

## 2. Links & References

- **Delta**: DE-115
- **Design Revision**: DR-115 §3 (Architecture Intent), §4 (Code Impact Summary)
- **Specs**: SPEC-117, SPEC-126, SPEC-127
- **Governance**: POL-001 (reuse), POL-002 (no magic strings)

## 3. Entrance Criteria

- [x] DE-114 completed
- [x] DR-115 written with resolved open questions
- [ ] `just check` passes on current main

## 4. Exit Criteria / Done When

- [ ] `grep -rn 'def parse_date' supekku/` returns exactly 1 result (in `core/dates.py`)
- [ ] `grep -rn 'def create_title_slug' supekku/` returns 0 results
- [ ] `grep -rn 'def _matches_pattern' supekku/` returns 0 results
- [ ] No inline atomic-write patterns (fd/mkstemp/replace) outside `core/io.py`
- [ ] No inline `re.compile(r"```(?:yaml|yml)` in `blocks/` modules
- [ ] No inline H1-extraction blocks in `decisions/registry.py`, `policies/registry.py`, `standards/registry.py`
- [ ] `just check` passes clean

## 5. Verification

- Unit tests for `core/dates.py`, `core/io.py`, `core/filters.py` (new `matches_pattern`)
- Unit tests for `blocks/yaml_utils.py` (new `make_block_pattern`)
- Unit tests for `core/spec_utils.py` (new `extract_h1_title`)
- Existing test suite green throughout (regression guard)
- `just lint` zero warnings on touched files

## 6. Assumptions & STOP Conditions

- Assumptions: all copies are functionally identical (verified by diff during review)
- STOP when: a copy has a subtle behavioural difference that existing tests rely on

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | ----------- | --------- | ----- |
| [ ] | 1.1 | Extract `parse_date` to `core/dates.py` | [P] | 3 identical instance methods → 1 module function |
| [ ] | 1.2 | Delete `create_title_slug` wrappers | [P] | 3 one-liner passthroughs to `slugify()` — callers import `slugify` directly |
| [ ] | 1.3 | Extract `matches_pattern` to `core/filters.py` | [P] | 2 identical private functions → 1 public function |
| [ ] | 1.4 | Promote `atomic_write` to `core/io.py` | [P] | 1 named + 2 inlined → 1 canonical function; callers delegate |
| [ ] | 1.5 | Add `make_block_pattern` to `blocks/yaml_utils.py` | [P] | 6 identical `re.compile(...)` → 1 factory function |
| [ ] | 1.6 | Add `extract_h1_title` to `core/spec_utils.py` | [P] | 3 inline H1-extraction blocks → 1 function |

### Task Details

- **1.1 Extract `parse_date`**
  - **Files**: Create `core/dates.py` + `core/dates_test.py`. Update `decisions/registry.py`, `policies/registry.py`, `standards/registry.py` — remove instance method, import shared function.
  - **Approach**: Lift the method body verbatim. Convert `self.parse_date(x)` calls to `parse_date(x)`. Remove `self` parameter.
  - **Testing**: Test None, date object, datetime object, ISO string, invalid string. Existing registry tests cover regression.

- **1.2 Delete `create_title_slug`**
  - **Files**: `decisions/creation.py`, `policies/creation.py`, `standards/creation.py` — delete function, update imports at call sites to use `slugify()` directly.
  - **Approach**: Find all callers of `create_title_slug`, replace with `slugify()`. Delete the wrappers.
  - **Testing**: Existing creation tests cover regression. No new tests needed (no new function).

- **1.3 Extract `matches_pattern`**
  - **Files**: Extend `core/filters.py` + `core/filters_test.py`. Update `cli/artifacts.py`, `cli/find.py` — delete private copies, import from `core.filters`.
  - **Approach**: Lift function verbatim, make public (drop leading `_`).
  - **Testing**: Test exact match, glob match, case-insensitive match, no-match.

- **1.4 Promote `atomic_write`**
  - **Files**: Create `core/io.py` + `core/io_test.py`. Update `workflow/review_io.py` (delegate), `workflow/state_io.py` (replace inline), `workflow/handoff_io.py` (replace inline).
  - **Approach**: Promote `review_io._atomic_write` to `core.io.atomic_write` (public). In `state_io` and `handoff_io`, replace the fd/mkstemp/replace block with `atomic_write(path, content)` after the validation/serialization step.
  - **Testing**: Test normal write, parent dir creation, cleanup on error. Existing workflow tests cover regression.

- **1.5 Add `make_block_pattern`**
  - **Files**: Extend `blocks/yaml_utils.py` + create/extend test. Update `blocks/delta.py`, `blocks/relationships.py`, `blocks/verification.py`, `blocks/plan.py` — replace inline `re.compile(...)` with `make_block_pattern(MARKER)`.
  - **Approach**: `def make_block_pattern(marker: str) -> re.Pattern:` returning `re.compile(r"```(?:yaml|yml)\s+" + re.escape(marker) + r"\n(.*?)```", re.DOTALL)`. Each module replaces its `_*_PATTERN = re.compile(...)` with `_*_PATTERN = make_block_pattern(MARKER)`.
  - **Testing**: Test that returned pattern matches a sample fenced block. Existing block parsing tests cover regression.

- **1.6 Add `extract_h1_title`**
  - **Files**: Extend `core/spec_utils.py` + `core/spec_utils_test.py`. Update `decisions/registry.py`, `policies/registry.py`, `standards/registry.py` — replace inline H1 search loop with `extract_h1_title(content, prefix)`.
  - **Approach**: `def extract_h1_title(content: str, prefix: str = "") -> str:` — scans lines for `# {prefix}` (or any `#` if no prefix), returns the H1 text. Falls back to empty string.
  - **Testing**: Test with prefix match, no prefix, no H1 found, multiple headings.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Copies diverge subtly | Diff each pair before extracting; run full test suite after each extraction | open |
| `state_io`/`handoff_io` atomic-write has validation-coupled logic | Confirmed: validation is separate from the write; only the fd/mkstemp/replace block is extracted | resolved |

## 9. Decisions & Outcomes

- 2026-04-10 — Collapsed P01+P02 into single phase. All 6 extractions are independent mechanical operations with small blast radius; no need for separate phases.

## 10. Findings / Research Notes

- `delta.py` and `relationships.py` both define `RELATIONSHIPS_MARKER` but with different string values (`supekku:delta.relationships@v1` vs `supekku:spec.relationships@v1`). Each module's `make_block_pattern` call uses its own constant — no collision.
- `state_io.py` and `handoff_io.py` validated as having identical atomic-write pattern to `review_io._atomic_write` (fd/mkstemp/replace with cleanup on failure).

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to P02 (if any)
