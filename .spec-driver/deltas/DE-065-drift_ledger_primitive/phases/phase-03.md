---
id: IP-065.PHASE-03
slug: 065-drift_ledger_primitive-phase-03
name: Migration and close
created: "2026-03-08"
updated: "2026-03-08"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-065.PHASE-03
plan: IP-065
delta: DE-065
objective: >-
  Migrate pilot DL-047 from repo-root drift/ to .spec-driver/drift/,
  converting entries from list-item format to fenced YAML blocks.
  Verify end-to-end CLI (create/list/show), then close delta DE-065.
entrance_criteria:
  - Phase 2 complete (formatters & CLI working)
  - Pilot DL-047 exists at drift/DL-047-spec-corpus-reconciliation.md
exit_criteria:
  - DL-047 migrated to .spec-driver/drift/ with fenced YAML entries
  - Parser roundtrips all 21 entries correctly
  - list drift shows DL-047
  - show drift DL-047 renders detail view
  - Old drift/ directory removed
  - just check green
  - Delta DE-065 completed
verification:
  tests:
    - VT-065-migration-roundtrip
  evidence:
    - VA-065-cli-e2e
tasks:
  - id: "3.1"
    description: convert DL-047 entries from list-item to fenced YAML format
  - id: "3.2"
    description: move DL-047 to .spec-driver/drift/ and remove old drift/ dir
  - id: "3.3"
    description: end-to-end CLI verification (list/show/create)
  - id: "3.4"
    description: delta closure (spec-driver complete delta DE-065)
risks:
  - description: pilot entry format has edge cases not covered by parser
    mitigation: verify parser roundtrip on each entry after conversion
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-065.PHASE-03
```

# Phase 3 — Migration and close

## 1. Objective

Migrate the pilot drift ledger DL-047 from `drift/` to `.spec-driver/drift/`,
converting all 21 entries from the old list-item format to fenced YAML blocks
(DEC-065-02). Verify end-to-end CLI operations, then close DE-065.

## 2. Links & References

- **Delta**: DE-065
- **Design Revision**: DR-065 §10 (creation template), DEC-065-02 (fenced YAML format)
- **Pilot file**: `drift/DL-047-spec-corpus-reconciliation.md`
- **Parser contract**: DR-065 DEC-065-03 edge case table

## 3. Entrance Criteria

- [x] Phase 2 complete (formatters & CLI working)
- [x] Pilot DL-047 exists at `drift/DL-047-spec-corpus-reconciliation.md`

## 4. Exit Criteria / Done When

- [x] DL-047 migrated to `.spec-driver/drift/DL-047-spec-corpus-reconciliation.md`
- [x] All 21 entries converted to fenced YAML block format
- [x] Parser roundtrips all entries (verified via `show drift DL-047`)
- [x] `list drift` shows DL-047
- [x] Old `drift/` directory removed
- [x] `just check` green (3285 pass, ruff clean, pylint 9.71)
- [x] `spec-driver complete delta DE-065` succeeds

## 5. Verification

- `uv run spec-driver list drift` — shows DL-047
- `uv run spec-driver show drift DL-047` — renders all entries
- `just check` — all tests, linters clean

## 6. Assumptions & STOP Conditions

- Assumptions:
  - Pilot entries can be mechanically converted (same fields, just different syntax)
  - No uncommitted changes in `drift/` directory
- STOP when:
  - Parser rejects converted entries (investigate format mismatch)
  - `complete delta` fails without `--force` (investigate coverage gaps)

## 7. Tasks & Progress

| Status | ID  | Description                                    | Parallel? | Notes                     |
| ------ | --- | ---------------------------------------------- | --------- | ------------------------- |
| [x]    | 3.1 | Convert DL-047 entries to fenced YAML format   | —         | 21 entries converted      |
| [x]    | 3.2 | Move to .spec-driver/drift/, remove old drift/ | —         | done                      |
| [x]    | 3.3 | End-to-end CLI verification                    | —         | list/show/parse all work  |
| [x]    | 3.4 | Delta closure                                  | —         | completed without --force |

### Task Details

- **3.1 Convert entries**
  - Read current DL-047 pilot format (list-item `- key: value`)
  - For each of 21 entries: wrap structured data in ````yaml` fence
  - Move `analysis:` field content outside fence as freeform markdown
  - Move `evidence:` list inside fence as YAML
  - Preserve frontmatter and corpus coverage table

- **3.2 Relocate file**
  - Move `drift/DL-047-spec-corpus-reconciliation.md` → `.spec-driver/drift/DL-047-spec-corpus-reconciliation.md`
  - Remove `drift/` directory (after confirming no other files)
  - Verify git status clean

- **3.3 E2E verification**
  - `uv run spec-driver list drift` — DL-047 appears with correct metadata
  - `uv run spec-driver show drift DL-047` — all entries render
  - `uv run spec-driver create drift "test-ledger"` — verify creation works
  - `just check` — all tests pass, linters clean

- **3.4 Delta closure**
  - `uv run spec-driver complete delta DE-065`
  - If force needed: document reason, create follow-up

## 8. Risks & Mitigations

| Risk                                            | Mitigation                                             | Status |
| ----------------------------------------------- | ------------------------------------------------------ | ------ |
| Pilot entries have fields parser doesn't expect | Parser is permissive — extra fields go to `extra` dict | open   |
| 21 entries is tedious to convert manually       | Systematic conversion, verify each                     | open   |

## 9. Decisions & Outcomes

- 2026-03-08: Manual conversion chosen over programmatic — single file, one-time operation
- 2026-03-08: `analysis` field content moved outside YAML fence as freeform markdown per DEC-065-02
- 2026-03-08: `evidence` field kept inside YAML fence as list of strings

## 10. Findings / Research Notes

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (3285 tests, linters clean)
- [x] Phase sheet updated with outcomes
- [x] Notes updated with final handover
