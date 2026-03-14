---
id: IP-027.PHASE-01
slug: "027-contract_mirror_tree_index-phase-01"
name: IP-027 Phase 01 - Core builder and path mapping
created: "2026-02-20"
updated: "2026-02-20"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-027.PHASE-01
plan: IP-027
delta: DE-027
objective: >-
  Implement ContractMirrorTreeBuilder with per-language path mapping functions
  (Python + Zig tested, Go/TS architectural). Unit and integration tests passing,
  linters clean.
entrance_criteria:
  - Delta and design revision drafted (DE-027, DR-027)
  - Reference implementation understood (SpecIndexBuilder)
  - Contract naming conventions confirmed from filesystem
exit_criteria:
  - ContractMirrorTreeBuilder produces correct .contracts/ tree for Python contracts
  - Per-language path mapping functions implemented and tested
  - Zig mapping implemented (testable via fixtures)
  - Go/TS mappers implemented architecturally with fixture tests
  - Unit + integration tests pass (just test)
  - Linters clean (just lint, just pylint)
verification:
  tests:
    - VT-CONTRACT-MIRROR-001
    - VT-CONTRACT-MIRROR-002
  evidence: []
tasks:
  - id: "1.1"
    description: Create contracts package with per-language path mapping functions
    status: pending
  - id: "1.2"
    description: Implement ContractMirrorTreeBuilder core
    status: pending
  - id: "1.3"
    description: Unit tests for path mapping (all languages)
    status: pending
  - id: "1.4"
    description: Integration tests for tree building (Python contracts)
    status: pending
  - id: "1.5"
    description: Lint and final checks
    status: pending
risks:
  - description: Python contract header format may vary
    mitigation: Confirmed from real files; header is always "# dotted.module.name"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-027.PHASE-01
```

# Phase 1 - Core builder and path mapping

## 1. Objective

Implement `ContractMirrorTreeBuilder` with per-language path mapping and full test coverage.
The builder reads `registry_v2.json` + scans `SPEC-*/contracts/` directories, then creates
a `.contracts/<view>/<source-path>.md` symlink tree.

## 2. Links & References

- **Delta**: [DE-027](../DE-027.md)
- **Design Revision**: [DR-027](../DR-027.md) — sections 7.1–7.8
- **Specs**: PROD-014 (FR-001 through FR-007, NF-001, NF-002)
- **Reference Implementation**: `supekku/scripts/lib/specs/index.py` (SpecIndexBuilder)
- **Registry**: `specify/tech/registry_v2.json`

## 3. Entrance Criteria

- [x] DE-027 and DR-027 drafted with clear design decisions
- [x] SpecIndexBuilder pattern understood
- [x] Contract naming conventions confirmed from real filesystem

## 4. Exit Criteria / Done When

- [ ] `ContractMirrorTreeBuilder.rebuild()` produces correct `.contracts/` tree
- [ ] Python path mapping: header-based module identity → mirror path
- [ ] Zig path mapping: file-based identifier → mirror path (including `"."` → `__root__/`)
- [ ] Go/TS path mapping: architectural implementation with fixture tests
- [ ] Missing variant handling: skip + warn
- [ ] Conflict resolution: deterministic precedence + warning
- [ ] `just test` passes
- [ ] `just lint` and `just pylint` clean

## 5. Verification

- `just test` — all unit and integration tests
- `just lint` — ruff
- `just pylint` — pylint threshold
- VT-CONTRACT-MIRROR-001: `.contracts/` structure and variant roots
- VT-CONTRACT-MIRROR-002: Per-language path mapping, missing variants, conflicts

## 6. Assumptions & STOP Conditions

- Assumptions: All Python contracts begin with `# dotted.module.name` header
- STOP when: Contract header format varies from expected pattern

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                         | Parallel? | Notes                                        |
| ------ | --- | ----------------------------------- | --------- | -------------------------------------------- |
| [x]    | 1.1 | Per-language path mapping functions | [P]       | Pure functions, all 4 languages              |
| [x]    | 1.2 | ContractMirrorTreeBuilder core      |           | Rebuild, clean, conflict resolution, aliases |
| [x]    | 1.3 | Unit tests for path mapping         | [P]       | 29 unit tests                                |
| [x]    | 1.4 | Integration tests for tree building |           | 15 integration tests                         |
| [x]    | 1.5 | Lint and final checks               |           | ruff + pylint 10/10, 1646 tests pass         |

### Task Details

- **1.1 Per-language path mapping**
  - **Design**: Pure functions per DR-027 §7.2–7.3. Python reads first header line. Zig/Go/TS use filename lookup.
  - **Files**: `supekku/scripts/lib/contracts/mirror.py`
  - **Testing**: Unit tests in `supekku/scripts/lib/contracts/mirror_test.py`

- **1.2 ContractMirrorTreeBuilder**
  - **Design**: Follows SpecIndexBuilder pattern. Reads registry, scans contract dirs, computes mirror paths, creates symlinks.
  - **Files**: `supekku/scripts/lib/contracts/mirror.py`, `supekku/scripts/lib/contracts/__init__.py`

- **1.3 Unit tests for path mapping**
  - **Testing**: All languages, edge cases (root package, missing variants, conflicts)

- **1.4 Integration tests**
  - **Testing**: Temp directory with mock registry + contract files, assert `.contracts/` structure

- **1.5 Lint and final checks**
  - `just test`, `just lint`, `just pylint`

## 8. Risks & Mitigations

| Risk                          | Mitigation                                  | Status    |
| ----------------------------- | ------------------------------------------- | --------- |
| Python contract header varies | Confirmed consistent format from real files | mitigated |
| Deep symlink paths            | Use `os.path.relpath` per DR-027 §7.6       | mitigated |

## 9. Decisions & Outcomes

- 2026-02-20 — Python mapper deduplicates by SPEC ID to avoid redundant scanning when multiple identifiers map to the same SPEC.
- 2026-02-20 — `shutil.rmtree` for cleanup (simpler than selective symlink removal; `.contracts/` is entirely generated).
- 2026-02-20 — `MirrorEntry` and `ContractMirrorTreeBuilder` both get `pylint: disable=too-few-public-methods` (dataclass and single-responsibility builder).

## 10. Findings / Research Notes

- Updated `package_utils_test.py` to account for new `contracts` leaf package (19 -> 20).
- Python contract headers confirmed consistent: always `# dotted.module.name` as first line.
- `ruff` import sorting auto-fix needed on test file (expected).

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to phase 2 (complete)
