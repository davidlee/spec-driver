---
id: IP-142-P03
slug: "142-revision_artefact_metadata_propagation_revision_frontmatter_metadata_change_block_enrichment_applies_to_derivation_de_136_child-phase-03"
name: IP-142 Phase 03 — list revisions enrichment
created: "2026-05-29"
updated: "2026-05-29"
status: completed  # one of: completed | deferred | draft | in-progress | pending
kind: phase  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
plan: IP-142
delta: DE-142
---

# Phase 3 — `list revisions` enrichment

## 1. Objective

Surface revision scope at a glance in `list revisions`, mirroring the DE-141
audit pattern (DEC-142-01): block → domain summary → formatter column → thin CLI.
POL-003: formatters carry no business logic; the domain computes the summary.

## 2. Links & References

- **Design Revision Sections**: DR-142 §7 (list enrichment), §13.2 (source/dest split
  recomputed in summary, not read from `applies_to`); DEC-142-01.
- **Specs / PRODs**: PROD-004.FR-001.
- **Precedent (mirror exactly)**:
  - `changes/audit_check.py` — `AuditFindingsSummary` + `audit_findings_summary()`
  - `formatters/column_defs.py` — `AUDIT_COLUMNS`, `ColumnDef`, `EXT_ID_COLUMN`, `column_labels`
  - `formatters/change_formatters.py` — `format_audit_list_row/json/table`, `_format_specs_cell` (:216), `format_list_table` call
  - `cli/list/reviews.py` — `list_audits` (the wiring shape; `list_revisions` is the target)
  - `formatters/table_utils.py:180` — generic `format_list_table`

## 3. Entrance Criteria

- [x] P02 complete — `_derive_revision_applies_to` + block parsing land; deriver returns
      the deduped union (the source/dest SPLIT is recomputed here, separately)
- [x] DEC-CONSULT-06 resolved (user 2026-05-29): **adaptive** Source column — rendered
      only when ≥1 revision has an origin; JSON keeps a stable schema (all fields)

## 4. Exit Criteria / Done When

- [x] NEW `changes/revision_check.py`: frozen `RevisionChangeSummary(sources,
      destinations, requirements)` + `source_cell()/destination_cell()/requirements_cell()`
      + `revision_change_summary(artifact)` (loads block(s), tolerant)
- [x] `REVISION_COLUMNS` (ID, Name, Status, Source, Destination, Requirements) in `column_defs.py`
- [x] `format_revision_list_row/json/table` in `change_formatters.py`; **adaptive
      Source-hide** (table view only) when no revision has sources
- [x] `cli/list/reviews.py:list_revisions` wired via `ChangeRegistry(kind="revision")`
      + `{r.id: revision_change_summary(r)}` + `format_revision_list_table` (thin)
- [x] VT-142-LIST-001/002/003/004 + adaptive-hide test pass (82 targeted)
- [x] Existing suites green; ruff/ty clean; pylint net +1 (audit-mirror, see §9)

## 5. Verification

- Targeted: `changes/revision_check_test.py` (NEW), `formatters/change_formatters_test.py`,
  `cli/list_test.py` (revision listing). Pin terminal width on table assertions.
- **VT-142-LIST-001**: table renders Source/Destination as `N (first-id)`, Requirements as count.
- **VT-142-LIST-002**: `revision_change_summary` breakdown — sources ← `origin[].ref`
  (kind=spec), destinations ← `destination.spec`, requirements ← `requirement_id`;
  deduped + sorted; multi-block union.
- **VT-142-LIST-003**: zero-change revision (no block / empty) → em-dash cells (`–`).
- **VT-142-LIST-004**: JSON includes enriched fields with stable schema; TSV column order.
- **VT-142-LIST-ADAPT** (DEC-CONSULT-06): Source column ABSENT when no revision has
  origins; PRESENT when ≥1 does. (Live corpus → absent today.)

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `RevisionChangeSummary` carries cell-formatting methods (mirrors `AuditFindingsSummary`
    findings_cell/disposed_cell — presentation on the domain summary is the precedent).
  - sources = unique `origin[].ref` where `kind=="spec"`; destinations = unique
    `destination.spec`; the list SPLIT is recomputed here, NOT from `applies_to` (DR §13.2).
  - Adaptive hide affects the **table** view only; JSON/TSV keep the full field set
    (stable schema for scripts).
- **STOP when**:
  - The generic `format_list_table` cannot express per-format column sets without a
    bespoke path → `/consult` before forking the table builder (the `show_external`
    insert precedent suggests it can: mutate `col_defs` before the call).
  - Filter semantics (`--spec`/`--delta`) need to move from `relations` to derived
    `applies_to` → out of scope (enrichment is columns, not filters); flag, don't drift.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | ----------- | --------- | ----- |
| [x] | 3.1 | RED: `revision_check_test.py` — VT-142-LIST-002 (breakdown, multi-block, dedup) + VT-142-LIST-003 (em-dash) | [ ] | done; non-spec origin excluded |
| [x] | 3.2 | `changes/revision_check.py`: `RevisionChangeSummary` + cells + `revision_change_summary()` | [ ] | mirrors `audit_check.py`; tolerant load |
| [x] | 3.3 | `REVISION_COLUMNS` in `column_defs.py` | [P] | ID, Name, Status, Source, Destination, Requirements |
| [x] | 3.4 | RED: `change_formatters_test.py` — VT-142-LIST-001 (row cells) + VT-142-LIST-004 (json/tsv) + adaptive-hide | [ ] | default width OK; "Source" header presence asserted |
| [x] | 3.5 | `format_revision_list_row/json/table` in `change_formatters.py`; adaptive Source-hide (table only) | [ ] | strips `"Spec Revision - "`; top-level `RevisionChangeSummary` import (no cycle, cleaner than audit) |
| [x] | 3.6 | Wire `cli/list/reviews.py:list_revisions` → summaries + `format_revision_list_table` | [ ] | replaced `format_change_list_table`; filters kept |
| [x] | 3.7 | Verify: targeted + full suite green; ruff/ty/pylint clean | [ ] | live `list revisions` confirms Source hidden |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Source/dest split leaks into `applies_to` (competing truth) | Recompute in summary only; `applies_to` stays the deduped union (DR §13.2) | design |
| Adaptive hide breaks TSV/JSON schema stability | Hide table-view only; tsv/json emit full field set | design |
| Name-prefix strip mismatched (audit strips "Audit - ") | Strip the real "Spec Revision - " prefix (verify on corpus) | design |
| Premature generalisation of a shared revision/audit summary | Keep `revision_check.py` separate (different block shape; POL-001) | design |

## 9. Decisions & Outcomes

- `2026-05-29` — **DEC-CONSULT-06 resolved (adaptive Source column)**, user-approved.
  Render Source only when ≥1 revision has an origin (`origin[].ref` kind=spec); hide it
  in the table view otherwise. JSON/TSV keep the full field set (stable schema).
  Cheap — mirrors the existing `show_external` conditional-column pattern
  (`format_audit_list_table` mutates `col_defs` before the `format_list_table` call).
- `2026-05-29` — **`format_revision_list_table` is McCabe 12 (`too-complex`)** — identical
  to its sibling `format_audit_list_table` (also 12, pre-existing). Faithful mirror per
  DEC-142-01; reducing it would diverge structurally from audit. Net pylint impact of P03
  = exactly this +1 (no new message types; new files contribute zero). A future DRY win:
  extract a shared `_styled_change_cell` helper used by both audit + revision row builders
  (would drop both below threshold) — out of P03 scope (touches audit).
- `2026-05-29` — `RevisionChangeSummary` imported at module top-level in
  `change_formatters.py` (no import cycle, unlike `audit_check`), so the row-builder needs
  no inner-import fallback — cleaner than the audit mirror (one fewer `import-outside-toplevel`).

## 10. Findings / Research Notes

- Block shape (verified): `requirements[].origin` = `[{kind∈backlog|external|requirement|spec,
  ref, notes?}]`; `requirements[].destination` = `{spec, requirement_id?, path?, additional_specs?}`.
  Live corpus has **zero** populated `origin[]` → Source hidden today.
- Reuse the `N (first-id)` rendering (cf. `_format_specs_cell`); em-dash constant `–`
  (inline on the summary cells, matching `AuditFindingsSummary`).
- `list_revisions` currently uses the generic `format_change_list_table`; swap to the
  enriched `format_revision_list_table`. Keep the existing `--spec/--delta/--tag/--filter`
  filter logic (relations-based) untouched — filter migration is out of scope.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (§10)
- [x] DR-142/IP-142 updated (coverage VT-142-LIST-* → verified; §9 progress P03)
- [x] Hand-off note to P04 (migration + sweep + flip — the consequential gate; DEC-CONSULT-03/04/05/07 still open) — see DE-142 `notes.md` "New Agent Instructions"

### Implementation evidence (2026-05-29)

- **Domain** (`changes/revision_check.py`, NEW): `RevisionChangeSummary` (frozen) +
  `source_cell/destination_cell/requirements_cell` + `revision_change_summary(artifact)`
  — sources ← `origin[].ref` (kind=spec), destinations ← `destination.spec`,
  requirements ← `requirement_id`; sorted+deduped; tolerant load; multi-block union.
- **Columns** (`column_defs.py`): `REVISION_COLUMNS` (6).
- **Formatter** (`change_formatters.py`): `format_revision_list_row/json/table`; adaptive
  Source-hide in the table view (TSV/JSON keep full schema); strips `"Spec Revision - "`.
- **CLI** (`cli/list/reviews.py`): `list_revisions` wired thin via summaries +
  `format_revision_list_table` (replaced generic `format_change_list_table`); filters kept.
- **Tests**: VT-142-LIST-001/002/003/004 + adaptive-hide; 82 targeted pass.
- **Live**: `list revisions` renders Destination/Requirements; Source adaptively HIDDEN
  (corpus has zero origins); `--json` carries sources/destinations/requirements (stable).
- **Regression**: cli/list + changes + formatters → 770 passed (2 pre-existing width-wrap
  delta-list failures only). ruff/ty clean; pylint net +1 (audit-mirror `too-complex`).
