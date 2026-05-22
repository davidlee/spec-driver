---
id: IP-139-P02
slug: "139-spec_metadata_propagation-phase-02"
name: IP-139 Phase 02 — List enrichment + packages removal
created: "2026-05-22"
updated: "2026-05-22"
status: in-progress
kind: phase
plan: IP-139
delta: DE-139
---

# Phase 2 — List enrichment + packages removal

## 1. Objective

Remove deprecated `packages` property chain (model → index → formatters → CLI) and enrich `list specs` output with Category, C4 glyph, and Sources columns. Tags become opt-in via `--tags`.

## 2. Links & References

- **Delta**: DE-139
- **Design Revision Sections**: DR-139 §7 (list enrichment, C4 glyphs, column defs), §8.1 (packages removal chain)
- **Requirements**: PROD-004.FR-003 (discoverability)
- **Precedent**: DE-138 DEC-138-09 (tags opt-in pattern)
- **Decisions**: DEC-139-05 (packages cut), DEC-139-09 (enriched columns + tags opt-in)

## 3. Entrance Criteria

- [x] P01 complete (block schemas, FM removals, taxonomy strict)
- [x] DR-139 §7 + §8.1 reviewed

## 4. Exit Criteria / Done When

- [x] `Spec.packages` property removed from models.py
- [x] `packages` serialization removed from `to_dict()`
- [x] By-package index builder removed from index.py
- [x] `format_package_list`, `_format_packages`, `include_packages` param removed from spec_formatters.py
- [x] `PACKAGES_COLUMN` removed from column_defs.py
- [x] `--packages`, `--package`, `--package-path` flags removed from CLI
- [x] `SPEC_COLUMNS` replaced with enriched set: ID, Name, Status, Category, C4, Sources
- [x] Tags opt-in via `--tags` flag
- [x] VT-DE139-LIST-001 passing (19 tests)
- [x] `just test` passing (5066); `just lint` clean

## 5. Verification

- VT-DE139-LIST-001: enriched list columns (Category, C4 glyph, Sources) — 19 tests passing
- Regression: existing spec list tests pass after packages removal
- `just test` — 5066 passed (5058 baseline + 19 new - 11 removed package tests)
- `just lint` — clean

## 6. Assumptions & STOP Conditions

- Assumptions: no external consumers of `Spec.packages` (internal project; confirmed in DEC-139-05)
- Assumptions: DE-138 tags opt-in pattern is settled precedent
- STOP when: if packages removal breaks >5 unexpected test sites (indicates undocumented consumers)

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID | Description | Parallel? | Notes |
|---|---|---|---|---|
| [x] | 2.1 | Remove `packages` property from models.py | [ ] | Also removed find_by_package from registry |
| [x] | 2.2 | Remove by-package index builder from index.py | [ ] | Removed package_dir, packages field from SpecIndexEntry |
| [x] | 2.3 | Remove packages formatting from spec_formatters.py | [ ] | format_package_list, _format_packages, include_packages all removed |
| [x] | 2.4 | Remove PACKAGES_COLUMN from column_defs.py | [ ] | |
| [x] | 2.5 | Remove --packages/--package/--package-path/--for-path from CLI | [ ] | --for-path was package-only; also removed get_tech_specs_dir import |
| [x] | 2.6 | Fix tests broken by packages removal | [ ] | 7 failures fixed; 11 package tests deleted |
| [x] | 2.7 | Add C4_GLYPHS mapping | [x] | In column_defs.py; S/N/C/D/I |
| [x] | 2.8 | Add Category, C4, Sources column defs to column_defs.py | [x] | SPEC_COLUMNS + SPEC_TAGS_COLUMN |
| [x] | 2.9 | Add enriched column renderers in spec_formatters.py | [ ] | format_c4_glyph, format_sources_cell |
| [x] | 2.10 | Tags opt-in: add --tags flag, remove tags from default columns | [ ] | show_tags param wired through |
| [x] | 2.11 | Wire enriched columns in CLI list/specs.py | [ ] | --tags flag, show_tags= kwarg |
| [x] | 2.12 | Write VT-DE139-LIST-001 tests | [ ] | 19 tests: C4 glyphs, sources cell, enriched table |
| [x] | 2.13 | Verify all tests pass | [ ] | 5066 passed |
| [x] | 2.14 | Lint clean | [ ] | `just lint` clean |

### Task Details

- **2.1 Remove packages property (models.py)**
  - **Files**: `supekku/scripts/lib/specs/models.py:25-30` (property), `:118-119` (to_dict)
  - **Approach**: Delete `packages` property and its serialization in `to_dict()`. Any callers will surface as test failures in 2.6.

- **2.2 Remove by-package index builder (index.py)**
  - **Files**: `supekku/scripts/lib/specs/index.py:28` (package_dir init), `:33-96` (rebuild with package symlinks)
  - **Approach**: Remove `package_dir` attribute and package-related logic from `rebuild()`. Keep other index builders (category, c4_level) intact.

- **2.3 Remove packages formatting (spec_formatters.py)**
  - **Files**: `supekku/scripts/lib/formatters/spec_formatters.py:37-46` (format_package_list), `:166-174` (_format_packages), `:49-85` (include_packages param in format_spec_list_item), `:88-152` (include_packages in format_spec_list_table)
  - **Approach**: Delete format_package_list and _format_packages functions. Remove include_packages parameter from format_spec_list_item and format_spec_list_table. Update __all__ exports.

- **2.4 Remove PACKAGES_COLUMN (column_defs.py)**
  - **Files**: `supekku/scripts/lib/formatters/column_defs.py:138`
  - **Approach**: Delete PACKAGES_COLUMN definition. Will be replaced by enriched columns in 2.8.

- **2.5 Remove package CLI flags (list/specs.py)**
  - **Files**: `supekku/cli/list/specs.py:64-71` (--package, --package-path), `:161-167` (--packages output flag), `:214-242` (package filter logic), `:346-364` (format dispatch with packages param)
  - **Approach**: Remove all three CLI flags and their associated filter/format logic. Remove --for-path package resolution if only used for packages.

- **2.6 Fix tests broken by packages removal**
  - **Approach**: Run `just test`, identify failures from removed packages API. Update test fixtures and assertions. Tests that directly test packages functionality are deleted; tests that incidentally reference packages are updated.

- **2.7 Add C4_GLYPHS mapping**
  - **Files**: `supekku/scripts/lib/formatters/spec_formatters.py` or `column_defs.py`
  - **Approach**: Pure constant dict per DR-139 §7.2: `{"system": "S", "container": "N", "component": "C", "code": "D", "interaction": "I"}`

- **2.8 Add enriched column defs (column_defs.py)**
  - **Files**: `supekku/scripts/lib/formatters/column_defs.py`
  - **Approach**: Replace SPEC_COLUMNS with: ID, Name, Status, Category, C4, Sources. Add optional SPEC_TAGS_COLUMN for --tags.

- **2.9 Add enriched column renderers (spec_formatters.py)**
  - **Files**: `supekku/scripts/lib/formatters/spec_formatters.py`
  - **Approach**: Add renderers for Category (unit/assembly/—), C4 (glyph from C4_GLYPHS, — if missing), Sources (count × first-lang format, — if none). Integrate into format_spec_list_table.

- **2.10 Tags opt-in**
  - **Files**: `supekku/cli/list/specs.py`, `column_defs.py`
  - **Approach**: Add `--tags` flag (default False). When True, append tags column. Remove tags from default SPEC_COLUMNS. Matches DE-138 DEC-138-09 precedent.

- **2.11 Wire enriched columns in CLI**
  - **Files**: `supekku/cli/list/specs.py`
  - **Approach**: Update format dispatch to use enriched columns. Pass --tags through. Category/C4 already available as CLI filters; enrichment makes them visible by default.

- **2.12 Write VT-DE139-LIST-001 tests**
  - **Approach**: Test enriched table output: Category column shows unit/assembly/—; C4 column shows glyph; Sources column shows count×lang format. Test --tags opt-in. Test missing values show —.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|---|---|---|
| Packages removal breaks unexpected callers | Code survey confirmed 3 defs, 7 refs — all mapped in task chain | open |
| --for-path flag entangled with packages | Check if --for-path has non-package uses before removing | open |
| Sources column format edge cases | Test 0 sources (—), 1 source, multi-source, mixed languages | open |

## 9. Decisions & Outcomes

- DEC-139-05: packages cut (no external consumers)
- DEC-139-09: enriched columns (Category, C4, Sources); tags opt-in

## 10. Findings / Research Notes

Code survey (2026-05-22):
- `packages` property: models.py:25-30, to_dict:118-119
- by-package index: index.py:28,33-96
- format_package_list: spec_formatters.py:37-46
- _format_packages: spec_formatters.py:166-174
- include_packages: spec_formatters.py:49-85, 88-152
- PACKAGES_COLUMN: column_defs.py:138
- CLI flags: specs.py:64-71 (--package/--package-path), 161-167 (--packages), 214-242 (filter logic)
- Template: spec.md has NO packages field (already clean)
