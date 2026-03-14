---
id: IP-090.PHASE-03
slug: 090-cli_relational_navigation_filters_show_output_and_cross_entity_queries-phase-03
name: 'IP-090 Phase 03: P2 show enrichment'
created: '2026-03-13'
updated: '2026-03-13'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-090.PHASE-03
plan: IP-090
delta: DE-090
objective: >-
  Enrich show spec/delta with reverse lookup counts, add --requirements flag
  on show spec, ensure backlog JSON consistency, and backfill audit relations.
entrance_criteria:
  - P02 complete (P1 filter flags shipped)
  - DR-090 P2 design approved
exit_criteria:
  - show spec displays reverse lookup counts (deltas, revisions, audits)
  - show spec --requirements expands full requirements list
  - show delta displays linked audits and revisions
  - Backlog list/show JSON includes linked_deltas and related_requirements with [] defaults
  - 8 existing audits backfilled with relations entries
  - VT-090-P2-* all passing
  - just passes (tests + ruff + pylint)
verification:
  tests:
    - VT-090-P2-1
    - VT-090-P2-2
    - VT-090-P2-3
    - VT-090-P2-4
  evidence: []
tasks:
  - id: "3.0"
    description: "Backfill 8 existing audits with relations entries (prerequisite)"
  - id: "3.1"
    description: "show spec reverse lookup counts"
  - id: "3.2"
    description: "show spec --requirements flag"
  - id: "3.3"
    description: "show delta reverse lookups (linked audits + revisions)"
  - id: "3.4"
    description: "Backlog JSON consistency (list vs show defaults)"
risks:
  - description: "Audit backfill touches 8 files outside code"
    mitigation: "Purely additive frontmatter change; no code coupling"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-090.PHASE-03
```

# Phase 03 — P2 Show Enrichment

## 1. Objective

Enrich `show spec` and `show delta` with reverse lookup information — what other artifacts reference this entity. Add `--requirements` expansion flag on `show spec`. Ensure backlog JSON output is consistent between `list` and `show` commands. Backfill existing audits with proper `relations` entries linking them to their deltas.

## 2. Links & References

- **Delta**: DE-090
- **Design Revision Sections**: DR-090 §P2-1 (show spec enrichment), §P2-2 (show delta reverse lookups), §P2-3 (backlog JSON consistency)
- **Specs / PRODs**: PROD-010.FR-005
- **Key files**:
  - `supekku/cli/show.py` — show_spec, show_delta orchestration
  - `supekku/scripts/lib/formatters/spec_formatters.py` — format_spec_details + helpers
  - `supekku/scripts/lib/formatters/change_formatters.py` — format_delta_details + helpers
  - `supekku/scripts/lib/formatters/relation_formatters.py` — format_refs_count, format_refs_tsv (extend here)
  - `supekku/scripts/lib/relations/query.py` — find_related_to()
  - `supekku/scripts/lib/backlog/models.py` — BacklogItem (no to_dict yet)

## 3. Entrance Criteria

- [x] P02 complete (P1 filter flags shipped, commit 22d00a8)
- [x] DR-090 P2 design approved

## 4. Exit Criteria / Done When

- [ ] `show spec` displays "Related:" section with reverse lookup counts (deltas, revisions, audits referencing this spec)
- [ ] `show spec --requirements` expands full requirements list (FR/NF labels + titles) instead of count
- [ ] `show spec --json` includes `reverse_lookup_counts` when computed
- [ ] `show delta` displays "Audit:" and "Revision:" lines for linked artifacts
- [ ] `show delta --json` includes `linked_audits` and `linked_revisions` arrays
- [ ] `list backlog --json` includes `linked_deltas` and `related_requirements` with `[]` defaults
- [ ] `show issue --json` includes these fields with `[]` defaults when absent
- [ ] 8 existing audits backfilled with `relations: [{type: documents, target: DE-xxx}]`
- [ ] VT-090-P2-1 through VT-090-P2-4 passing
- [ ] `just` passes

## 5. Verification

- **Unit tests**: spec_formatters_test.py, change_formatters_test.py, show_test.py, relation_formatters_test.py
- **Commands**: `just test`, `just lint`, `just pylint-report`, `just`
- **Manual smoke**: `uv run spec-driver show spec PROD-010`, `uv run spec-driver show delta DE-090`

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `find_related_to()` returns artifacts referencing a target ID across all relation slots — confirmed
  - `ChangeRegistry(root, kind=...)` can be instantiated per-kind (delta/revision/audit) — confirmed
  - `format_spec_details()` already has `_format_spec_relations()` and `_format_requirements_summary()` from P0 — extend, don't rebuild
- STOP when:
  - `find_related_to()` doesn't pick up audit→delta references (would indicate audit frontmatter issue, not code issue)
  - BacklogItem serialisation requires schema changes beyond additive defaults

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                | Parallel? | Notes                                  |
| ------ | --- | ------------------------------------------ | --------- | -------------------------------------- |
| [x]    | 3.0 | Audit backfill — add relations to 6 audits | [ ]       | AUD-003–008; AUD-001/002 have no delta |
| [x]    | 3.1 | show spec reverse lookup counts            | [ ]       |                                        |
| [x]    | 3.2 | show spec --requirements flag              | [x]       |                                        |
| [x]    | 3.3 | show delta reverse lookups                 | [x]       |                                        |
| [x]    | 3.4 | Backlog JSON consistency                   | [x]       |                                        |

### Task Details

- **3.0 Audit backfill**
  - **Design / Approach**: Add `relations: [{type: documents, target: DE-xxx}]` to 8 existing audit frontmatter files. Identify audits via `uv run spec-driver list audits`, cross-reference each audit's name/body to determine which delta it covers.
  - **Files / Components**: `.spec-driver/audits/AUD-*/AUD-*.md` (8 files)
  - **Testing**: After backfill, `uv run spec-driver show delta DE-081` (or similar) should show the linked audit when 3.3 is implemented. Validate with `uv run spec-driver list audits --delta DE-081`.
  - **Notes**: Forward reference (audit → delta), consistent with ADR-002. DEC-090-07: use `type: documents`.

- **3.1 show spec reverse lookup counts**
  - **Design / Approach**: In `show.py:show_spec()`, load `ChangeRegistry` per kind (delta, revision, audit), call `find_related_to()` for each, count results. Pass counts to a new `_format_reverse_lookup_counts(delta_count, revision_count, audit_count)` formatter in `spec_formatters.py`. Add "Related:" section to `format_spec_details()`. For JSON: add `reverse_lookup_counts` dict when caller provides counts.
  - **Files / Components**: `show.py`, `spec_formatters.py`, `spec_formatters_test.py`, `show_test.py`
  - **Testing**: VT-090-P2-1 — test formatter with various count combinations (all zero, some populated, all populated). Test show_spec integration with mock registries.
  - **Notes**: CLI-layer composition — no registry coupling in formatters (DEC-090-06, DEC-090-08).

- **3.2 show spec --requirements flag**
  - **Design / Approach**: Add `--requirements` flag to `show_spec()`. When set, `_format_requirements_summary()` is replaced by a full requirements listing showing FR/NF labels + titles. Load `RequirementsRegistry`, filter by spec ID, format as list. New helper `_format_requirements_list(requirements)` in `spec_formatters.py`. JSON: include full requirements array when `--requirements` is passed.
  - **Files / Components**: `show.py`, `spec_formatters.py`, `spec_formatters_test.py`
  - **Testing**: VT-090-P2-2 — test expanded list formatting; test that default still shows count summary.
  - **Notes**: DEC-090-02: progressive disclosure. Count by default, list on flag.

- **3.3 show delta reverse lookups**
  - **Design / Approach**: In `show.py:show_delta()`, load `ChangeRegistry` for audits and revisions, call `find_related_to(all_audits, delta_id)` and same for revisions. Pass results to new `_format_reverse_lookups(audits, revisions)` in `change_formatters.py`. Insert section after relations. JSON: add `linked_audits` and `linked_revisions` as `[{id, name}]` arrays.
  - **Files / Components**: `show.py`, `change_formatters.py`, `change_formatters_test.py`, `show_test.py`
  - **Testing**: VT-090-P2-3 — test formatter with 0, 1, N audits/revisions. Integration test with mock registries.
  - **Notes**: Depends on 3.0 (audit backfill) for real-world validation. Test infra uses mocks regardless.

- **3.4 Backlog JSON consistency**
  - **Design / Approach**: Add `to_dict()` to `BacklogItem` that always includes `linked_deltas: []` and `related_requirements: []` (reading from frontmatter with defaults). Update `list backlog --json` to use `to_dict()`. Update `show issue --json` to use same serialisation.
  - **Files / Components**: `backlog/models.py`, `cli/list.py`, `cli/show.py`, `backlog/models_test.py` (or similar)
  - **Testing**: VT-090-P2-4 — test to_dict with and without frontmatter fields; test list vs show JSON parity.
  - **Notes**: DEC-090-14: additive contract change, documented explicitly.

## 8. Risks & Mitigations

| Risk                                                                      | Mitigation                                                                                                                                                                              | Status   |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Audit backfill requires identifying correct delta per audit               | Audit names typically include delta ID; can verify via body content                                                                                                                     | Open     |
| `find_related_to()` won't see audit→delta links until P3 collectors exist | It will — audits have `.relations` (frontmatter relations), which `_collect_from_relations()` already handles. P3 collectors are for domain-specific fields, not frontmatter relations. | Resolved |
| show_spec loading 3 registries adds latency                               | Bounded: current corpus ~150 artifacts total; no benchmark threshold claimed                                                                                                            | Accepted |

## 9. Decisions & Outcomes

_(Record decisions made during implementation)_

## 10. Findings / Research Notes

- `format_spec_details()` already has slots for relations and requirements summary (P0 work) — extend, don't restructure
- `relation_formatters.py` already exists — good home for `_format_reverse_lookup_counts()`
- `BacklogItem` has no `to_dict()` — needs adding
- `find_related_to()` searches `.relations`, `.applies_to`, `.context_inputs`, `.informed_by` — audit→delta via `.relations` is already covered

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
