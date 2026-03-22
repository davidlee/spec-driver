---
id: IP-109-P02
slug: "109-review_state_machine_formalisation-phase-02"
name: "I/O layer — accumulative rounds, schema v2, judgment_status"
created: "2026-03-22"
updated: "2026-03-22"
status: in-progress
kind: phase
plan: IP-109
delta: DE-109
---

# Phase 2 — I/O layer

## 1. Objective

Refactor `review_io.py` and `workflow_metadata.py` for accumulative rounds
(schema v2), v1 rejection, `judgment_status` in review-index, and finding
serialisation with status re-derivation.

## 2. Links & References

- **Delta**: DE-109
- **Design Revision Sections**: DR-109 §3.3 (judgment_status storage), §3.4 (status derivation enforcement), §3.5 (accumulative rounds), §3.6 (session metadata), §3.7 (in-place disposition)
- **Phase 1 output**: `workflow/review_state_machine.py` — enums, models, derive_finding_status()

## 3. Entrance Criteria

- [x] Phase 1 complete — all VTs passing, lint clean

## 4. Exit Criteria / Done When

- [x] `REVIEW_FINDINGS_METADATA` updated to v2 schema (rounds array)
- [x] `REVIEW_INDEX_METADATA` gains `judgment_status` field
- [x] `build_review_index()` accepts `judgment_status` parameter
- [x] `build_findings_round()` creates v2 round entries
- [x] `append_round()` preserves prior rounds, appends new
- [x] `read_findings()` raises `FindingsVersionError` on v1
- [x] `next_round_number()` works with v2 rounds array
- [x] Finding status re-derived on read via `derive_finding_status()`
- [x] VT-109-004: Accumulative rounds tests passing
- [x] VA-109-001: Schema v1 rejection test passing
- [x] Lint clean on all touched files

## 5. Verification

- `uv run python -m pytest supekku/scripts/lib/workflow/review_io_test.py -v`
- `uv run ruff check supekku/scripts/lib/workflow/review_io.py supekku/scripts/lib/blocks/workflow_metadata.py`
- `just pylint-files supekku/scripts/lib/workflow/review_io.py supekku/scripts/lib/blocks/workflow_metadata.py`

## 6. Tasks & Progress

| Status | ID | Description | Notes |
|--------|-----|-------------|-------|
| [x] | 2.1 | Add `judgment_status` field to `REVIEW_INDEX_METADATA` | DR-109 §3.3 |
| [x] | 2.2 | Update `build_review_index()` to accept `judgment_status` | |
| [x] | 2.3 | Update `REVIEW_FINDINGS_METADATA` to v2 (rounds array) | DR-109 §3.5. Disposition sub-schema added. |
| [x] | 2.4 | Add `FindingsVersionError`; `read_findings()` rejects v1 | DR-109 §3.5 |
| [x] | 2.5 | Implement `build_round_entry()` for v2 round entry | |
| [x] | 2.6 | Implement `append_round()` — accumulative write | |
| [x] | 2.7 | Update `next_round_number()` for v2 rounds array | |
| [x] | 2.8 | Finding status re-derivation on read | DR-109 §3.4. Also added `update_finding_disposition()` and `find_finding()`. |
| [x] | 2.9 | Update tests for v2 model | 44 review_io tests + 8 metadata tests + 21 CLI tests. |
| [x] | 2.10 | Lint clean | ruff clean. Also fixed 10 pre-existing test failures across 3 files. |
