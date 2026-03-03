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

## New Agent Instructions

### Task
DE-036 — frontmatter metadata compaction and canonicalization controls.
Phase 0 (Baseline & Taxonomy) **complete**. Phase 1 (Memory Controls) **complete**. Next: **Phase 2 — Generalized Framework Pilot**.

### Required reading
- `change/deltas/DE-036-frontmatter_metadata_compaction_and_canonicalization_controls/DR-036.md` — design revision (4 binding design decisions)
- `change/deltas/DE-036-frontmatter_metadata_compaction_and_canonicalization_controls/IP-036.md` — implementation plan
- `change/deltas/DE-036-frontmatter_metadata_compaction_and_canonicalization_controls/phases/phase-01.md` — P0: canonical/derived matrices in §10, compaction semantics in §10.5
- `change/deltas/DE-036-frontmatter_metadata_compaction_and_canonicalization_controls/phases/phase-02.md` — P1: completed, decisions in §9
- `change/deltas/DE-036-frontmatter_metadata_compaction_and_canonicalization_controls/phases/phase-03.md` — **P2: active phase sheet**

### Related documents
- `specify/product/PROD-004/PROD-004.md` — FR-007 (metadata compaction capability)
- `change/revisions/RE-019-refresh_prod_004_frontmatter_metadata_validation_for_memory_and_compaction/RE-019.md` — completed revision

### Key files (what was changed in P1)
- `supekku/scripts/lib/blocks/metadata/schema.py` — `FieldMetadata` now has `persistence` + `default_value` with `__post_init__` validation
- `supekku/scripts/lib/core/frontmatter_metadata/memory.py` — all fields annotated; base overrides via `dataclasses.replace()`
- `supekku/scripts/lib/core/frontmatter_metadata/delta.py` — all fields annotated; `relations` is `default-omit`, `applies_to` is `default-omit`
- `supekku/scripts/lib/memory/links.py` — `links_to_frontmatter(result, mode="missing")` — 4 modes: none/missing/compact/full
- `supekku/cli/resolve.py` — `--link-mode` flag, threaded through `_resolve_single_memory` and `_resolve_memory_links`
- `supekku/cli/sync.py` — `--link-mode` flag for `--memory-links`

### Key files (P2 targets)
- New: compaction function (likely in `supekku/scripts/lib/core/` or `blocks/metadata/`)
- `supekku/scripts/lib/core/frontmatter_metadata/delta.py` — pilot target; fields already annotated
- `supekku/scripts/lib/blocks/metadata/schema.py` — `FieldMetadata` is the source of truth for persistence semantics

### Design decisions (binding)
- DEC-036-001: compact-by-default on sync commands only (not all write paths)
- DEC-036-002: link persistence default is `missing` only
- DEC-036-003: pilot non-memory family is delta frontmatter (Phase 2)
- DEC-036-004: `FieldMetadata.persistence` + `default_value` — already implemented

### Known pitfall for P2
- `applies_to` has `default_value={"specs": [], "requirements": []}` but real delta files may also have a `prod` key. Equality check must compare against the default, not structural subset — a file with `{specs: [], prod: [PROD-020], requirements: []}` must NOT be omitted.

### User instructions
- Consult before non-trivial design choices
- Agent guidance risk: monitor if compaction causes confusion during P2 pilot
- Quality: TDD, lint as you go (`just lint`, `just pylint`), run tests (`just test`), zero warnings

### Uncommitted work
All P0 + P1 work is uncommitted. Commit before starting P2.

### Loose ends
- IP-036 §8 open questions answered but IP file not updated to mark them resolved
- Pylint duplicate-code warning between memory.py and delta.py base overrides — extract shared helper if a third family needs the pattern
- `aliases` field in P0 matrix not in metadata definitions — annotate when defined
