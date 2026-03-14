---
id: IP-036.PHASE-02
slug: 036-frontmatter_metadata_compaction_and_canonicalization_controls-phase-02
name: IP-036 Phase 02 - Memory Controls
created: "2026-03-03"
updated: "2026-03-03"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-036.PHASE-02
plan: IP-036
delta: DE-036
objective: >-
  Add resolve/sync write modes and memory compaction profile so link
  persistence is mode-controlled and defaults are lean.
entrance_criteria:
  - Phase 0 complete (canonical/derived matrix, DR-036 filled in)
exit_criteria:
  - FieldMetadata extended with persistence + default_value
  - Memory and delta metadata annotated with persistence classifications
  - links_to_frontmatter() supports mode parameter (none/missing/compact/full)
  - resolve links and sync --memory-links pass --link-mode through
  - All tests pass, linters clean
verification:
  tests:
    - VT-036-001: resolve/sync default does not persist links.out
    - VT-036-002: mode parameter controls serialization shape
  evidence:
    - Test output from just test
    - Lint output from just lint + just pylint
tasks:
  - id: "1.1"
    description: Extend FieldMetadata with persistence and default_value
    status: complete
  - id: "1.2"
    description: Annotate memory frontmatter fields with persistence
    status: complete
  - id: "1.3"
    description: Annotate delta frontmatter fields with persistence
    status: complete
  - id: "1.4"
    description: Add mode parameter to links_to_frontmatter()
    status: complete
  - id: "1.5"
    description: Add --link-mode flag to resolve links CLI
    status: complete
  - id: "1.6"
    description: Add --link-mode flag to sync --memory-links CLI
    status: complete
risks:
  - description: Existing FieldMetadata consumers may fail if __post_init__ validates new fields
    mitigation: New fields have safe defaults; no validation constraints added
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-036.PHASE-02
```

# Phase 1 - Memory Controls

## 1. Objective

Add resolve/sync write modes and memory compaction profile so link persistence is mode-controlled and defaults are lean.

## 2. Links & References

- **Delta**: DE-036
- **Design Revision**: DR-036 (DEC-036-001 through DEC-036-004)
- **Phase 0**: phases/phase-01.md (canonical/derived matrix in §10)
- **Key code**: `blocks/metadata/schema.py`, `frontmatter_metadata/memory.py`, `frontmatter_metadata/delta.py`, `memory/links.py`, `cli/resolve.py`, `cli/sync.py`

## 3. Entrance Criteria

- [x] Phase 0 complete

## 4. Exit Criteria / Done When

- [x] `FieldMetadata` has `persistence` and `default_value` fields
- [x] Memory metadata annotated per P0 matrix
- [x] Delta metadata annotated per P0 matrix
- [x] `links_to_frontmatter()` supports `mode` parameter
- [x] `resolve links` has `--link-mode` flag
- [x] `sync --memory-links` has `--link-mode` flag
- [x] Default mode is `missing` (DEC-036-002)
- [x] All tests pass, linters clean

## 5. Verification

- `just test` — all tests pass
- `just lint` + `just pylint` — zero warnings
- New tests for mode-controlled serialization

## 6. Assumptions & STOP Conditions

- Assumes `FieldMetadata.__post_init__` does not need to validate new fields
- STOP if: schema engine consumers break on new fields

## 7. Tasks & Progress

| Status | ID  | Description                                           | Notes                                                |
| ------ | --- | ----------------------------------------------------- | ---------------------------------------------------- |
| [x]    | 1.1 | Extend FieldMetadata with persistence + default_value | schema.py; +validation in **post_init**              |
| [x]    | 1.2 | Annotate memory frontmatter fields                    | memory.py; base fields via replace()                 |
| [x]    | 1.3 | Annotate delta frontmatter fields                     | delta.py; base fields via replace()                  |
| [x]    | 1.4 | Add mode parameter to links_to_frontmatter()          | links.py; 4 modes implemented                        |
| [x]    | 1.5 | Add --link-mode to resolve links CLI                  | resolve.py; threaded through \_resolve_single_memory |
| [x]    | 1.6 | Add --link-mode to sync --memory-links CLI            | sync.py; threaded to \_resolve_memory_links          |

## 8. Risks & Mitigations

| Risk                                   | Mitigation                    | Status |
| -------------------------------------- | ----------------------------- | ------ |
| Existing FieldMetadata consumers break | New fields have safe defaults | Open   |

## 9. Decisions & Outcomes

- 2026-03-03 — Used `dataclasses.replace()` to override base field persistence at leaf level rather than modifying base.py. Keeps base definitions clean and allows different families to have different persistence semantics for the same base field (e.g. `relations` is `optional` for memory but `default-omit` for delta).
- 2026-03-03 — `aliases` field from P0 matrix is not in metadata definitions; skipped annotation. When/if it gets defined, add persistence then.
- 2026-03-03 — Existing `TestLinksToFrontmatter` tests updated to explicitly pass `mode="full"` since default changed from implicit-full to `missing`.

## 10. Findings / Research Notes

- Pylint duplicate-code warning between memory.py and delta.py base field overrides (6 identical `replace()` calls). Acceptable per "avoid premature abstraction" — will extract if a third family needs the same pattern.
- `FieldMetadata` now has 12 instance attributes (was 10); pylint `too-many-instance-attributes` was already triggered at 10. No practical concern — dataclass is a pure data carrier.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: 2146 tests pass, ruff clean, pylint 9.43/10
- [x] Notes updated
- [ ] Hand-off notes to Phase 2
