---
id: IP-086.PHASE-01
slug: "086-memory_verification_primitive_sha_stamped_attestation_for_staleness_tracking-phase-01"
name: "IP-086 Phase 01: Core primitives"
created: "2026-03-09"
updated: "2026-03-09"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-086.PHASE-01
plan: IP-086
delta: DE-086
objective: >-
  Build the foundation: git SHA utility, schema addition, model update,
  frontmatter writer extension, and creation path changes. All with tests.
entrance_criteria:
  - DR-086 reviewed and all design decisions closed
  - IP-086 accepted
exit_criteria:
  - core/git.py exists with get_head_sha, short_sha, SHA_HEX_PATTERN — tested
  - memory schema includes verified_sha (optional) and confidence (required, default medium) — tested
  - MemoryRecord parses and emits verified_sha — tested
  - update_frontmatter_fields works with FieldUpdateResult — tested
  - build_memory_frontmatter stamps verified date + confidence, not verified_sha — tested
  - existing frontmatter_writer tests still pass
  - ruff + pylint clean on all touched files
verification:
  tests:
    - VT-memory-verified-sha (creation path)
    - VT-frontmatter-writer
    - VT-confidence-required
  evidence: []
tasks:
  - id: "1.1"
    description: Create core/git.py
  - id: "1.2"
    description: Add verified_sha to memory schema
  - id: "1.3"
    description: Make confidence required in memory schema
  - id: "1.4"
    description: Update MemoryRecord model
  - id: "1.5"
    description: Extend frontmatter writer
  - id: "1.6"
    description: Update memory creation path
risks:
  - description: Import cycle between core/git.py and schema
    mitigation: git.py has no internal dependencies; schema imports constant only
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-086.PHASE-01
```

# Phase 01 — Core Primitives

## 1. Objective

Build all foundational modules and changes needed before CLI or staleness work. Each task is independently testable. Tasks 1.1–1.4 can be parallelised; 1.5 and 1.6 depend on 1.1.

## 2. Links & References

- **Delta**: [DE-086](../DE-086.md)
- **Design Revision**: [DR-086](../DR-086.md) §5.1–§5.5
- **Specs**: SPEC-132 (memory), SPEC-116 (frontmatter metadata)

## 3. Entrance Criteria

- [x] DR-086 reviewed, all decisions closed
- [x] IP-086 accepted

## 4. Exit Criteria / Done When

- [ ] `core/git.py` exists with `get_head_sha()`, `short_sha()`, `SHA_HEX_PATTERN` — unit tested
- [ ] Memory schema has `verified_sha` (optional string, `SHA_HEX_PATTERN`) and `confidence` (required enum, default `medium`)
- [ ] `MemoryRecord` parses `verified_sha` from frontmatter and emits it in `to_dict`
- [ ] `update_frontmatter_fields()` works: replaces existing fields, inserts missing fields, returns `FieldUpdateResult` with `updated`/`inserted` sets
- [ ] `build_memory_frontmatter()` stamps `verified` date and `confidence` but NOT `verified_sha`
- [ ] `MemoryCreationOptions` has `confidence: str = "medium"` field
- [ ] All existing `frontmatter_writer` tests still pass
- [ ] `just lint` clean on all touched files
- [ ] `just pylint-files` clean on all touched files

## 5. Verification

- Run: `just test` (full suite)
- Run: `just lint` (ruff)
- Run: `just pylint-files supekku/scripts/lib/core/git.py supekku/scripts/lib/core/frontmatter_writer.py supekku/scripts/lib/core/frontmatter_metadata/memory.py supekku/scripts/lib/memory/models.py supekku/scripts/lib/memory/creation.py`

## 6. Assumptions & STOP Conditions

- Assumes `SHA_HEX_PATTERN` can be imported from `core/git.py` into `frontmatter_metadata/memory.py` without import cycle
- STOP if existing frontmatter writer tests break (investigate before continuing)
- STOP if schema change causes existing memory loading to fail

## 7. Tasks & Progress

| Status | ID  | Description                          | Parallel? | Notes                                |
| ------ | --- | ------------------------------------ | --------- | ------------------------------------ |
| [x]    | 1.1 | Create `core/git.py`                 | [P]       | DR §5.1 — 23 tests                   |
| [x]    | 1.2 | Add `verified_sha` to memory schema  | [P]       | DR §5.2                              |
| [x]    | 1.3 | Make `confidence` required in schema | [P]       | DR §5.2 — updated test helper        |
| [x]    | 1.4 | Update `MemoryRecord` model          | [P]       | DR §5.3 — 4 new tests                |
| [x]    | 1.5 | Extend frontmatter writer            | [P]       | DR §5.5 — 13 new tests, pylint 10/10 |
| [x]    | 1.6 | Update memory creation path          | —         | DR §5.4 — 6 new tests                |

### Task Details

- **1.1 Create `core/git.py`**
  - **Files**: `supekku/scripts/lib/core/git.py` (new), `supekku/scripts/lib/core/git_test.py` (new)
  - **Design**: DR §5.1 — `get_head_sha(root) -> str | None`, `short_sha(sha, length=8) -> str`, `SHA_HEX_PATTERN` constant
  - **Testing**: Mock `subprocess.run` for success (returns SHA), failure (returncode != 0), `FileNotFoundError`, `TimeoutExpired`. Test `short_sha` truncation. Test pattern matches valid/invalid SHAs.

- **1.2 Add `verified_sha` to memory schema**
  - **Files**: `supekku/scripts/lib/core/frontmatter_metadata/memory.py`
  - **Design**: DR §5.2 — `FieldMetadata(type="string", required=False, pattern=SHA_HEX_PATTERN, persistence="optional")`
  - **Testing**: Existing schema tests should cover; add test that `verified_sha` is in MEMORY_FRONTMATTER_METADATA.fields

- **1.3 Make `confidence` required in schema**
  - **Files**: `supekku/scripts/lib/core/frontmatter_metadata/memory.py`
  - **Design**: DR §5.2 — `required=True`, add `default_value="medium"`, update description with calibration note
  - **Testing**: Verify schema reflects required=True. Verify existing memories without confidence still load (model handles None).

- **1.4 Update `MemoryRecord` model**
  - **Files**: `supekku/scripts/lib/memory/models.py`, `supekku/scripts/lib/memory/models_test.py` (or existing test file)
  - **Design**: DR §5.3 — add `verified_sha: str | None = None`, wire into `from_frontmatter` and `to_dict`
  - **Testing**: Parse frontmatter with/without `verified_sha`. Verify `to_dict` includes it when present, omits when None.

- **1.5 Extend frontmatter writer**
  - **Files**: `supekku/scripts/lib/core/frontmatter_writer.py`, `supekku/scripts/lib/core/frontmatter_writer_test.py`
  - **Design**: DR §5.5 — `FieldUpdateResult` dataclass, `update_frontmatter_fields(path, updates) -> FieldUpdateResult`
  - **Testing**: Replace existing field; insert missing field; replace + insert in one call; verify return sets distinguish updated vs inserted; verify insertion order matches dict order; verify file content preserved outside frontmatter.

- **1.6 Update memory creation path**
  - **Files**: `supekku/scripts/lib/memory/creation.py`, `supekku/scripts/lib/memory/creation_test.py`
  - **Design**: DR §5.4 — stamp `verified: today` and `confidence: options.confidence or "medium"` but NOT `verified_sha`. Add `confidence: str = "medium"` to `MemoryCreationOptions`.
  - **Testing**: Verify created frontmatter has `verified` date, has `confidence`, does NOT have `verified_sha`. Verify confidence defaults to medium.

## 8. Risks & Mitigations

| Risk                                               | Mitigation                                                      | Status   |
| -------------------------------------------------- | --------------------------------------------------------------- | -------- |
| Import cycle `core/git.py` ↔ schema               | `git.py` has zero internal deps; schema imports one constant    | Low risk |
| Confidence required breaks existing memory loading | Model default is None; schema required applies to creation only | Low risk |

## 9. Decisions & Outcomes

- All design decisions closed in DR-086 prior to phase start.
- 2026-03-09: Refactored `update_frontmatter_fields` to reduce McCabe complexity from 12 to acceptable level by extracting `_replace_fields`, `_try_replace_line`, `_insert_missing_fields` helpers. Pylint 10/10.
- 2026-03-09: Updated `_minimal_memory()` test helper in memory_test.py to include required `confidence` field.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: 3742 passed, 0 failed; ruff clean; pylint 10/10 on writer
- [ ] Hand-off to Phase 02
