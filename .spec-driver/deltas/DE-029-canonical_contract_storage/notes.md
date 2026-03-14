# DE-029 Implementation Brief (read this first)

This file is the “cold start” handoff for implementing DE-029 without reading a giant chat log.
Treat it as the minimum context required to begin work safely.

## Goal (what changes)

- `.contracts/**` becomes the canonical contract corpus (real files, derived/deterministic).
- `specify/tech/SPEC-*/contracts/**` becomes compatibility-only (symlinks pointing _into_ `.contracts/**`).
- Adapters stop hardcoding `spec_dir / "contracts"`; the caller decides destination.

Authoritative docs:

- Delta: `change/deltas/DE-029-canonical_contract_storage/DE-029.md`
- Design: `change/deltas/DE-029-canonical_contract_storage/DR-029.md`
- Plan: `change/deltas/DE-029-canonical_contract_storage/IP-029.md`

## Locked decisions (do not re-open)

- **Python multiplicity**: stage+distribute (do not push mirror mapping into adapters).
- **`DocVariant.path` semantics**: relative to `contracts_dir`, centrally validated (Python may be scan-based).
- **Compat**: invert mirror — `SPEC-*/contracts/*` symlinks → `.contracts/**`; warn when replacing a non-symlink file.
- **Fresh repo story**: spec-independent discovery is _not_ in this delta (deferred to DE-030).

## Seam / invariants

- `process_source_unit()` is the only caller of `adapter.generate()` (single change point).
- `sync` must keep respecting `--contracts/--no-contracts` and `--specs/--no-specs` independently (DE-028).
- `.contracts/**` is safe to delete and regenerate; determinism is a hard requirement.

## Pre-read (10 minutes, in order)

Product & decisions:

- `specify/product/PROD-014/PROD-014.md` (FR-008/011/012)
- `change/revisions/RE-015-contracts_canonical_storage_sync_less_generation/RE-015.md`
- `specify/decisions/ADR-003-separate_unit_and_assembly_specs.md`

Sync semantics (don’t regress flags):

- `specify/product/PROD-012/PROD-012.md` (FR-006 now points to `.contracts/**`; VH-906 note)
- `change/revisions/RE-016-sync_defaults_contracts_first_opt_in_spec_creation/RE-016.md`
- `supekku/cli/sync.py` (Typer flags: `--specs/--no-specs`, `--contracts/--no-contracts`)

Core code touchpoints:

- `supekku/scripts/sync_specs.py` (`MultiLanguageSpecManager.process_source_unit`)
- `supekku/scripts/lib/sync/adapters/base.py` + all 4 adapters’ `generate()`
- `supekku/scripts/lib/contracts/mirror.py` (reuse mapping + Python module-name parsing)

## Checklist (implementation)

- Update adapter interface: `generate(..., contracts_dir=Path, ...)` and enforce `DocVariant.path` relativity.
- Canonical outputs:
  - Go/Zig/TS: pre-resolve canonical paths and write directly into `.contracts/**`.
  - Python: stage into `.contracts/.staging/<key>/`, then distribute into `.contracts/**`, then clean staging.
- Compat symlinks:
  - Build/refresh `SPEC-*/contracts/**` symlinks pointing into `.contracts/**` for registered specs.
  - `unlink()` before symlinking; warn if replacing a non-symlink file.
- Drift warning:
  - Warn when `SPEC-*/contracts/` is non-empty (≥1 `.md`) but canonical generation yielded zero `.contracts/**` outputs for that spec/unit.

## Checklist (verification)

Run (or ensure CI runs):

- `just` (tests + lint + pylint)
- Specific: the VT suite referenced in `DR-029.md` (storage, compat, drift, adapter contract, path validation).

## Current status (2026-02-21, post phase-1 agent #3)

Phase 1 tasks 1.1–1.9 are complete. Two post-phase bugs fixed. `just` is green (1667 passed, pylint 9.67).

### What works

- Adapter interface changed: `spec_dir → variant_outputs` across all 4 adapters + base ABC
- Path resolvers extracted in `mirror.py`: `resolve_{go,zig,ts}_variant_outputs()`, `python_staging_dir()`
- `process_source_unit._resolve_variant_outputs()` dispatches correctly
- Python staging + distribute step implemented
- All existing adapter tests updated and passing
- Contract generation independent of spec existence (gate fix)
- Compat symlinks: `SPEC-*/contracts/` → `.contracts/` (mirror inversion)
- Verified on external Zig repo (deck_of_dwarf): 644 contracts generated, persisted, and surviving sync

### Bug fixes applied (agent #3)

**Bug 1: contracts gated on spec existence** (fixed)

`process_source_unit()` early-returned when `create_specs=False` and no spec existed, preventing contract generation even when `generate_contracts=True`. Restructured to decouple: spec work is guarded by `has_spec or create_specs`, contract generation runs independently. 4 new tests in `sync_specs_test.py`.

**Bug 2: `ContractMirrorTreeBuilder.rebuild()` nuked canonical `.contracts/`** (fixed)

The old `rebuild()` did `shutil.rmtree(.contracts/)` and recreated it as a derived symlink tree pointing INTO `SPEC-*/contracts/` — the inverse of DE-029’s model. Contracts were generated correctly but deleted at the end of every sync.

Rewrote `rebuild()` to create compat symlinks FROM `SPEC-*/contracts/<view>/<path>` pointing INTO `.contracts/<view>/<path>`. Added `_canonical_paths_for()` (uses existing resolvers) and `_scan_python_contracts()`. Canonical files are never modified by rebuild. Non-symlink files at compat locations are replaced with a warning. 13 mirror tree builder tests rewritten for the inverted model.

## Don’ts

- Don’t introduce new ad-hoc “planning” docs; keep durable decisions in `DE-029.md` / `DR-029.md` / `IP-029.md`.
- Don’t make `.contracts/**` a “best effort” cache; it is canonical derived storage.
- Don’t change spec discovery semantics here; DE-030 owns spec-independent generation/discovery.
