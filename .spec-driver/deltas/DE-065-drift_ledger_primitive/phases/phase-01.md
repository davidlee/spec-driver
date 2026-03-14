---
id: IP-065.PHASE-01
slug: 065-drift_ledger_primitive-phase-01
name: Domain layer — models, parser, registry
created: "2026-03-08"
updated: "2026-03-08"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-065.PHASE-01
plan: IP-065
delta: DE-065
objective: >-
  Build the drift ledger domain layer: models (DriftLedger, DriftEntry,
  Source, Claim, DiscoveredBy), lifecycle constants, fenced-YAML parser,
  and read-only registry. All with tests, both linters clean.
entrance_criteria:
  - DR-065 accepted
  - paths.py extension point identified
exit_criteria:
  - models construct correctly with typed substructures
  - parser handles all edge cases in DR-065 contract table
  - registry discovers, finds, and filters ledger files
  - VT-065-models, VT-065-parser, VT-065-registry passing
  - ruff and pylint clean on all new files
verification:
  tests:
    - VT-065-models
    - VT-065-parser
    - VT-065-registry
  evidence: []
tasks:
  - id: "1.1"
    description: add DRIFT_SUBDIR and get_drift_dir() to paths.py
  - id: "1.2"
    description: implement models (DriftLedger, DriftEntry, Source, Claim, DiscoveredBy, lifecycle constants)
  - id: "1.3"
    description: implement parser (heading split, YAML block extraction, entry construction)
  - id: "1.4"
    description: implement DriftLedgerRegistry (discover, find, iter)
  - id: "1.5"
    description: write tests for all of the above
risks:
  - description: parser edge cases not covered by contract table
    mitigation: add tests as discovered, update DR-065 contract table
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-065.PHASE-01
```

# Phase 1 — Domain layer

## 1. Objective

Build the drift ledger domain package (`supekku/scripts/lib/drift/`) with
models, lifecycle constants, fenced-YAML parser, and read-only registry.
All test-driven, both linters clean.

## 2. Links & References

- **Delta**: DE-065
- **Design Revision**: DR-065 sections 5 (decisions), 6 (DE-063 integration), 7 (model design)
- **Parser contract**: DR-065 DEC-065-03 edge case table
- **Pattern reference**: `supekku/scripts/lib/backlog/` (registry/models pattern)

## 3. Entrance Criteria

- [x] DR-065 accepted
- [x] paths.py extension point identified (line 33, `DRIFT_SUBDIR`)

## 4. Exit Criteria / Done When

- [ ] `supekku/scripts/lib/drift/` package exists with `__init__.py`, `models.py`, `parser.py`, `registry.py`
- [ ] Models construct correctly: DriftLedger, DriftEntry, Source, Claim, DiscoveredBy
- [ ] Lifecycle constants defined and validation works (permissive, with warnings)
- [ ] Parser handles all 5 edge cases from DR-065 contract table
- [ ] Parser extracts freeform body content (DEC-065-08)
- [ ] Parser respects fence/heading precedence (DEC-065-03)
- [ ] Registry discovers `.spec-driver/drift/DL-*.md` files
- [ ] Registry find/iter/collect work correctly
- [ ] All tests pass (`just test`)
- [ ] Both linters clean (`just lint`, `just pylint-files` on new files)

## 5. Verification

- `just test` — all unit tests
- `just lint` — ruff
- `just pylint-files supekku/scripts/lib/drift/*.py` — pylint on new files

## 6. Assumptions & STOP Conditions

- Assumptions:
  - No existing `supekku/scripts/lib/drift/` directory
  - `paths.py` follows the established pattern for adding new subdirs
  - Backlog `models.py` is a valid structural reference for lifecycle constants
- STOP when:
  - Parser edge cases reveal format ambiguities not covered by DR-065
  - `paths.py` pattern has changed in ways not anticipated

## 7. Tasks & Progress

| Status | ID  | Description                                                                                 | Parallel? | Notes                             |
| ------ | --- | ------------------------------------------------------------------------------------------- | --------- | --------------------------------- |
| [x]    | 1.1 | paths.py: add `DRIFT_SUBDIR` + `get_drift_dir()`                                            | —         | done                              |
| [x]    | 1.2 | models: `Source`, `Claim`, `DiscoveredBy`, `DriftEntry`, `DriftLedger`, lifecycle constants | [P]       | 26 tests                          |
| [x]    | 1.3 | parser: `parse_ledger_body()` — heading split, YAML extraction, entry construction          | [P]       | 24 tests, all contract edge cases |
| [x]    | 1.4 | registry: `DriftLedgerRegistry` — discover, find, iter                                      | —         | 15 tests                          |
| [x]    | 1.5 | tests: VT-065-models, VT-065-parser, VT-065-registry                                        | —         | 65 total, all passing             |

### Task Details

- **1.1 paths.py**
  - Add `DRIFT_SUBDIR = "drift"` to constants
  - Add to `_CONFIG_KEY_TO_CONSTANT`: `"drift": "DRIFT_SUBDIR"`
  - Add `get_drift_dir(repo_root=None) -> Path`
  - Add to `__all__`
  - Lint after change

- **1.2 models**
  - Create `supekku/scripts/lib/drift/__init__.py`
  - Create `supekku/scripts/lib/drift/models.py`
  - Frozen dataclasses: `Source(kind, ref, note)`, `Claim(kind, text, label)`, `DiscoveredBy(kind, ref)`
  - `DriftEntry`: 15 fields per DR-065 §7, typed substructures
  - `DriftLedger`: id, name, status, path, created, updated, delta_ref, body, frontmatter, entries
  - Lifecycle constants: `LEDGER_STATUSES`, `ENTRY_STATUSES`, `ENTRY_TYPES`, `SEVERITIES`, `ASSESSMENTS`, `RESOLUTION_PATHS`
  - `is_valid_entry_status()` — permissive validation with warnings (backlog pattern)

- **1.3 parser**
  - Create `supekku/scripts/lib/drift/parser.py`
  - `parse_ledger_body(body: str) -> tuple[str, list[DriftEntry]]`
  - Step 1: split on `### ` headings (fence-aware — fences before headings)
  - Step 2: extract ID + title from heading
  - Step 3: find fenced YAML block, `yaml.safe_load()`
  - Step 4: construct typed substructures (Source, Claim, DiscoveredBy) from YAML dicts
  - Step 5: capture remaining markdown as `analysis`
  - Edge cases per contract table:
    - malformed YAML → warning, `extra: {"_parse_error": msg}`
    - missing required nested keys → warning, skip record
    - duplicate entry IDs → warning, preserve both
    - no YAML block → warning, heading-only entry
    - multiple YAML blocks → first parsed, rest is analysis

- **1.4 registry**
  - Create `supekku/scripts/lib/drift/registry.py`
  - `DriftLedgerRegistry(root=None)` — lazy or eager discovery
  - `collect() -> dict[str, DriftLedger]`
  - `find(ledger_id) -> DriftLedger | None`
  - `iter(status=None) -> Iterator[DriftLedger]`
  - Discover `DL-*.md` files in `get_drift_dir()`
  - Parse frontmatter via existing `load_markdown_file()`
  - Parse body via `parse_ledger_body()`

## 8. Risks & Mitigations

| Risk                                                   | Mitigation                                                                          | Status |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------- | ------ |
| Fence-aware heading split is trickier than expected    | Simple state machine: track fence open/close, only split on headings outside fences | open   |
| `load_markdown_file()` may not suit ledger frontmatter | Verify compatibility before building registry                                       | open   |

## 9. Decisions & Outcomes

- 2026-03-08: `_split_sections` returns `tuple[str, list[tuple[str, str]]]` instead of mixed union list — cleaner type contract
- 2026-03-08: `broad-exception-caught` in registry narrowed to `(OSError, ValueError, KeyError)`
- 2026-03-08: `too-many-instance-attributes` for DriftEntry (17) and DriftLedger (10) accepted — inherent to domain
- 2026-03-08: Fixed pre-existing PROB-001 test reference (deleted item)
- 2026-03-08: Updated package_utils_test.py KNOWN_LEAF_PACKAGES with new `drift` package

## 10. Findings / Research Notes

- `load_markdown_file()` from `core/spec_utils.py` works well for ledger frontmatter parsing — returns `(dict, str)` tuple
- Fence-aware heading split is a simple state machine — `in_fence` boolean toggle on ```lines, only split on`### ` when not in fence
- Parser pylint score: 9.93/10 (only inherent too-many-instance-attributes)

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (65 tests passing, linters clean)
- [x] Phase sheet updated with outcomes
- [ ] Hand-off notes to phase 2
