# Notes for DE-036

## 2026-03-03 — Phase 0 complete

### Done

- RE-019 applied: PROD-004 refreshed with current kind counts (15 unique / 17 entries), memory coverage, FR-007 (metadata compaction), CI-anchored test count phrasing
- Phase 0 sheet created and completed with baseline metrics and canonical/derived matrices for memory + delta frontmatter
- DR-036 filled in with 4 design decisions:
  - DEC-036-001: compact-by-default on sync only
  - DEC-036-002: link persistence default is missing-only
  - DEC-036-003: pilot family is delta frontmatter
  - DEC-036-004: extend FieldMetadata with `persistence` + `default_value`
- All open design questions from IP-036 §8 answered

### Key findings

- Memory link inflation: 22% avg, 62% worst-case (9-link files)
- No files currently have `links:` frontmatter — inflation is latent
- `links.out` is the only truly derived field in memory frontmatter
- Delta frontmatter has 3 clear default-omit candidates: `aliases: []`, `relations: []`, `applies_to: {specs: [], requirements: []}`

### Surprises

- `accepted` is not a valid delta status (valid: draft, pending, in-progress, deferred, complete, completed). Used `in-progress`.
- FR-001 kind list in PROD-004 was already inconsistent with appendix table (missing policy, standard, risk). Fixed.

### Next

- Phase 1: extend FieldMetadata, annotate memory metadata, implement link persistence modes
- Uncommitted work across: PROD-004, RE-019, DE-036, DR-036, phase-01

---

## 2026-03-03 — Phase 1 complete

### Done

- `FieldMetadata` extended with `persistence` (validated: canonical/derived/optional/default-omit) and `default_value`
- Memory and delta frontmatter fields annotated per P0 canonical/derived matrix
- Base fields overridden at leaf level via `dataclasses.replace()` — memory and delta can diverge (e.g. `relations`: optional vs default-omit)
- `links_to_frontmatter()` gains `mode` parameter: none/missing/compact/full (default: missing per DEC-036-002)
- `--link-mode` flag added to `resolve links` and `sync --memory-links`
- Existing tests updated to pass `mode="full"` where they tested full-output behavior
- 18 new tests across 3 files; 2146 total pass, ruff clean, pylint 9.43

### Adaptations

- `aliases` field appears in P0 matrix but is not in metadata definitions — skipped. Annotate when/if defined.
- Base field overrides create pylint duplicate-code warning between memory.py and delta.py (6 identical `replace()` calls). Acceptable per "avoid premature abstraction" — extract shared helper if a third family needs same pattern.

### Rough edges

- `FieldMetadata` now has 12 instance attributes (pylint `too-many-instance-attributes`). Cosmetic — it's a pure data carrier.
- IP-036 §8 open questions still not marked resolved in the IP file itself (carried from P0).

### Verification

- `just test`: 2146 passed, 3 skipped
- `just lint` (ruff): clean
- `just pylint`: 9.43/10 (up from 9.06)
- Uncommitted work

### Next

- Phase 2: generalized compaction framework + delta pilot
- Phase 1 sheet at `phases/phase-02.md` (complete)

---

## 2026-03-03 — Phase 2 complete

### Done

- `compact_frontmatter(data, metadata, mode)` implemented in `core/frontmatter_metadata/compaction.py`
- Pure function: iterates data dict, applies persistence rules per field metadata
- 17 unit tests (generic compaction logic) + 8 delta round-trip tests = 25 new tests
- Exported via `core/frontmatter_metadata/__init__.py`
- Delta corpus measurement: 37/37 files reducible, 7.1% avg, 26% max reduction
- 2176 tests pass, ruff clean, pylint 9.61

### Task 2.3 resolved

- Added `spec-driver compact delta` CLI command (`supekku/cli/compact.py`, 8be91c4)
- Thin CLI (87 lines): `compact delta [DE-XXX] [--dry-run] [--root PATH]`
- 7 CLI tests, pylint 10/10
- 2183 tests total, ruff clean, pylint 9.61
- Recommendation for P3: add a `compact` CLI command that applies `compact_frontmatter()` to artifact files by kind

### Design choices

- **Placement**: `core/frontmatter_metadata/compaction.py` — near metadata definitions, not in `blocks/metadata/` (compaction is a frontmatter write concern, not a schema concern)
- **Unknown fields**: pass through unchanged (forward compatibility)
- **Mode API**: `"compact"` (default) and `"full"` — matches link mode pattern from P1

### Verification

- `just test`: 2176 passed, 3 skipped
- `just lint` (ruff): clean
- `just pylint`: 9.61/10

---

## 2026-03-03 — Docs + memory alignment follow-up (frontmatter compaction)

### Done

- Updated `supekku/about/frontmatter-schema.md`:
  - corrected `relations` note (`relations` may be omitted when empty; parsers should treat absence as `[]`)
  - added concise compaction reference section (persistence levels, write-side/read-side contract, unknown-field passthrough, compact CLI entry points)
- Updated `supekku/about/processes.md`:
  - added `Frontmatter Compaction` workflow section with:
    - `uv run spec-driver compact delta`
    - `uv run spec-driver compact delta DE-XXX`
    - `uv run spec-driver compact delta --dry-run`
- Created memory:
  - `mem.pattern.spec-driver.frontmatter-compaction`
  - captures `compact_frontmatter()` semantics, persistence classes, CLI/implementation locations, write-side/read-side contract, DEC-036-001/003, scope globs, and provenance (`DR-036`, `phase-01.md §10.5`).

### Verification

- No runtime behavior changes.
- `just`, `just test`, `just lint`, and `just pylint` not run for this follow-up (docs/memory-only updates).

---

## New Agent Instructions

### Task

DE-036 — frontmatter metadata compaction and canonicalization controls.
Implementation **complete** (P0–P2) with docs/memory alignment follow-up applied.

### Remaining work

1. `uv run spec-driver complete delta DE-036`
2. If needed, run final VA/VH confirmation pass over DE-036 bundle before close-out.

### Loose ends (non-blocking)

- Pylint duplicate-code warning between memory.py and delta.py base overrides — extract shared helper if a third family needs the pattern
- `aliases` field in P0 matrix not in metadata definitions — annotate when defined
