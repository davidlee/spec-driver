---
id: IP-026.PHASE-01
slug: 026-use_zigmarkdoc_for_zig_documentation_generation-phase-01
name: IP-026 Phase 01
created: "2026-02-16"
updated: "2026-02-16"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-026.PHASE-01
plan: IP-026
delta: DE-026
objective: >-
  Replace manual Zig doc parser with zigmarkdoc subprocess calls
entrance_criteria:
  - Design revision approved
  - Open questions resolved
  - zigmarkdoc tool available at ~/.local/bin/zigmarkdoc
exit_criteria:
  - Code refactored to use zigmarkdoc
  - Obsolete methods removed
  - Basic functionality working (contracts generate)
  - Code passes lint
verification:
  tests:
    - Manual verification: uv run spec-driver sync --language zig
  evidence:
    - Generated contracts using zigmarkdoc
tasks:
  - id: "1.1"
    description: Add zigmarkdoc availability check and error class
  - id: "1.2"
    description: Update describe() to return both public and all variants
  - id: "1.3"
    description: Refactor generate() to call zigmarkdoc subprocess
  - id: "1.4"
    description: Remove obsolete manual parser methods
  - id: "1.5"
    description: Lint and manual test
risks:
  - risk: zigmarkdoc output format incompatible with expected structure
    mitigation: Follow GoAdapter pattern closely
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-026.PHASE-01
```

# Phase 1 - Core Implementation

## 1. Objective

Replace manual Zig documentation parser with zigmarkdoc subprocess calls, following GoAdapter pattern.

## 2. Links & References

- **Delta**: DE-026
- **Design Revision**: DR-026, sections 4 (Code Impact) and 7 (Design Decisions)
- **Specs / PRODs**: SPEC-124 (Sync command)
- **Reference Implementation**: supekku/scripts/lib/sync/adapters/go.py:176-400

## 3. Entrance Criteria

- [x] Design revision approved
- [x] Open questions resolved
- [x] zigmarkdoc tool available at ~/.local/bin/zigmarkdoc

## 4. Exit Criteria / Done When

- [x] Code refactored to use zigmarkdoc subprocess
- [x] Obsolete manual parser methods removed
- [x] Both public and all variants generated
- [x] `just lint` passes clean
- [ ] Manual test: `uv run spec-driver sync --language zig` succeeds (deferred to Phase 2 - needs test fixtures)

## 5. Verification

- Manual test: `uv run spec-driver sync --language zig`
- Verify contracts generated at correct paths
- Check contract content quality vs old parser
- Evidence: Generated contract files

## 6. Assumptions & STOP Conditions

- Assumptions:
  - zigmarkdoc installed and working at ~/.local/bin/zigmarkdoc
  - GoAdapter pattern applies cleanly to Zig
- STOP when: zigmarkdoc behavior differs significantly from expected

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                       | Parallel? | Notes                                                                  |
| ------ | --- | ------------------------------------------------- | --------- | ---------------------------------------------------------------------- |
| [x]    | 1.1 | Add zigmarkdoc availability check and error class | [ ]       | ✓ Added is_zigmarkdoc_available() and ZigmarkdocNotAvailableError      |
| [x]    | 1.2 | Update describe() to return both variants         | [ ]       | ✓ Updated to return public (interfaces.md) and internal (internals.md) |
| [x]    | 1.3 | Refactor generate() to call zigmarkdoc            | [ ]       | ✓ Replaced manual parser with subprocess calls                         |
| [x]    | 1.4 | Remove obsolete manual parser methods             | [ ]       | ✓ Removed \_generate_zig_docs, \_parse_zig_file, \_extract_declaration |
| [x]    | 1.5 | Lint and manual test                              | [ ]       | ✓ Ruff clean, pylint 9.75/10 (better than GoAdapter 9.70/10)           |

### Task Details

- **1.1 Add zigmarkdoc availability check and error class**
  - **Design / Approach**: Add `is_zigmarkdoc_available()` using `which()`, add `ZigmarkdocNotAvailableError` exception
  - **Files / Components**: supekku/scripts/lib/sync/adapters/zig.py:23-40
  - **Testing**: Manual verification
  - **Observations & AI Notes**: Followed GoAdapter pattern exactly. Error message includes installation URL.
  - **Commits / References**: 2026-02-16

- **1.2 Update describe() to return both variants**
  - **Design / Approach**: Modify variants list to include both "public" (interfaces.md) and "internal" (internals.md)
  - **Files / Components**: supekku/scripts/lib/sync/adapters/zig.py:178-226
  - **Testing**: Verify frontmatter structure
  - **Observations & AI Notes**: Changed from single "zig/public.md" to dual "interfaces.md" and "internals.md" matching GoAdapter
  - **Commits / References**: 2026-02-16

- **1.3 Refactor generate() to call zigmarkdoc**
  - **Design / Approach**: Replace manual parser calls with subprocess.run() to zigmarkdoc, support --check and --include-private flags
  - **Files / Components**: supekku/scripts/lib/sync/adapters/zig.py:228-415
  - **Testing**: Manual contract generation
  - **Observations & AI Notes**: Complete rewrite following GoAdapter pattern. Raises clear error if zigmarkdoc unavailable. Supports both check mode and normal generation.
  - **Commits / References**: 2026-02-16

- **1.4 Remove obsolete manual parser methods**
  - **Design / Approach**: Delete \_generate_zig_docs, \_parse_zig_file, \_extract_declaration
  - **Files / Components**: supekku/scripts/lib/sync/adapters/zig.py (removed ~100 lines)
  - **Testing**: Ensure no references remain
  - **Observations & AI Notes**: Clean removal - no other code referenced these methods.
  - **Commits / References**: 2026-02-16

- **1.5 Lint and manual test**
  - **Design / Approach**: Run just lint, run manual sync test
  - **Files / Components**: All modified files
  - **Testing**: just lint, uv run pylint
  - **Observations & AI Notes**: Ruff: clean. Pylint: 9.75/10 (better than GoAdapter's 9.70/10). Complexity warnings expected and match reference implementation.
  - **Commits / References**: 2026-02-16

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |

## 9. Decisions & Outcomes

- `2026-02-16` - Followed GoAdapter pattern exactly for consistency
- `2026-02-16` - Changed contract paths from `contracts/zig/{slug}-public.md` to `contracts/interfaces.md` and `contracts/internals.md`
- `2026-02-16` - Raise ZigmarkdocNotAvailableError instead of falling back (fail fast)

## 10. Findings / Research Notes

- GoAdapter at 9.70/10 pylint, ZigAdapter now at 9.75/10
- Complexity warnings (too-complex, too-many-branches, too-many-statements) are expected and match reference implementation
- Removed ~100 lines of manual parsing code
- No existing Zig test files found - will create in Phase 2
- No Zig source files in main repo for manual testing - will use test fixtures in Phase 2

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied (except manual test - deferred to Phase 2)
- [x] Verification evidence stored (lint results)
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase: Phase 2 needs to create comprehensive tests including mocked subprocess calls and integration tests with real Zig fixtures
