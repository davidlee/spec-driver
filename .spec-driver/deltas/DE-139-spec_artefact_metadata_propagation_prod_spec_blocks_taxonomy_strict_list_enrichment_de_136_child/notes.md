# Notes for DE-139

## P02 — List enrichment + packages removal (2026-05-22)

### Done

- **Packages removal chain**: Spec.packages property, find_by_package, SpecIndexEntry.packages field, package_dir in index builder, format_package_list, _format_packages, include_packages param, PACKAGES_COLUMN, --packages/--package/--package-path/--for-path CLI flags + all filter logic.
- **Enriched columns**: SPEC_COLUMNS now [ID, Name, Status, Category, C4, Sources]. C4_GLYPHS mapping in column_defs.py. format_c4_glyph + format_sources_cell pure formatters. Tags opt-in via `--tags` flag (DEC-139-09).
- **Spec.sources property** added to model (was missing — only accessed from raw FM in index.py).
- **VT-DE139-LIST-001**: 19 tests (C4 glyphs, sources cell, enriched table, tags opt-in).
- 5066 tests passing, lint clean.

### Surprises / Adaptations

- `--for-path` flag help text confirmed package-only ("Filter specs whose packages include PATH") — safe removal.
- `find_by_package` on registry had no production callers, only tests — clean removal.
- `SpecIndexEntry.packages` field removed; dataclass had it as required positional, so test fixtures needed updating.
- Mock objects in test helpers needed `spec.sources = []` added — Mock auto-creates attrs but iterating a Mock attr raises TypeError.
- Two separate regression test sites in column_defs_test.py asserted old SPEC_COLUMNS labels.
- `replace_all` on `spec.packages = []` → `spec.ext_id = ""` created one duplicate in a mock that already had ext_id. Fixed manually.

### Commit

`87ddd401` — `.spec-driver` artefacts committed with code per doctrine.

### Verification

`just test` (5066 passed) + `just lint` (clean) run after final changes.

### Follow-up

- P03 next: migration step, sweep, template updates.
- `format_spec_list_json` still doesn't emit category/c4_level/sources in JSON output — may want to enrich in P03 or follow-up.

