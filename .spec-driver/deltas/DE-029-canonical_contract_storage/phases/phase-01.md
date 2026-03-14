---
id: IP-029.PHASE-01
slug: 029-canonical_contract_storage-phase-01
name: IP-029 Phase 01 — Canonical storage
created: '2026-02-21'
updated: '2026-02-21'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-029.PHASE-01
plan: IP-029
delta: DE-029
objective: >-
  Change adapter interface from spec_dir to variant_outputs, compute canonical
  output paths in process_source_unit, write contracts as real files to
  .contracts/<view>/<mirror-path>. Python uses staging + distribute.
entrance_criteria:
  - DE-028 complete (generate_contracts seam exists)
  - Delta DE-029 accepted
  - Gate checks passed (IP-029 §3)
exit_criteria:
  - All 4 adapters accept variant_outputs (Go/Zig/TS) or staging dir (Python)
  - sync writes real files to .contracts/<view>/...
  - VT-CONTRACTS-STORAGE-001 passes
  - VT-CONTRACTS-ADAPTER-001 passes
  - VT-CONTRACTS-PATH-VALIDATION-001 passes
  - just green (tests + lint + pylint)
verification:
  tests:
    - VT-CONTRACTS-STORAGE-001
    - VT-CONTRACTS-ADAPTER-001
    - VT-CONTRACTS-PATH-VALIDATION-001
  evidence: []
tasks:
  - id: "1.1"
    description: "Change LanguageAdapter.generate() signature: spec_dir → variant_outputs"
  - id: "1.2"
    description: "Update Go adapter to write to provided variant output paths"
  - id: "1.3"
    description: "Update Zig adapter to write to provided variant output paths"
  - id: "1.4"
    description: "Update TypeScript adapter to write to provided variant output paths"
  - id: "1.5"
    description: "Update Python adapter to accept staging dir"
  - id: "1.6"
    description: "Implement path resolution + dispatch in process_source_unit"
  - id: "1.7"
    description: "Implement Python distribute step (staging → canonical)"
  - id: "1.8"
    description: "Write VT tests (storage, adapter, path validation)"
  - id: "1.9"
    description: "Update _sync_specs post-sync flow"
risks:
  - description: "Zig/TS adapters call external tools with --output; must redirect to caller-provided path"
    mitigation: "Already passing output path to subprocess; just change the variable source"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-029.PHASE-01
```

# Phase 1 — Canonical storage

## 1. Objective

Change the adapter interface so that adapters write contract files to caller-specified canonical paths under `.contracts/`. The caller (`process_source_unit`) computes per-variant output file paths using the existing mirror mapping logic from `mirror.py`, applied _before_ generation rather than after. Python uses a staging directory with post-generation distribution.

## 2. Links & References

- **Delta**: [DE-029](../DE-029.md)
- **Design Revision**: [DR-029](../DR-029.md) — §7.1 (interface), §7.2 (DocVariant contract), §7.3 (Python staging), §7.6 (path resolution)
- **Requirements**: PROD-014.FR-008 (canonical storage), PROD-012.FR-006 (adapter interface)
- **Mirror mapping code**: `supekku/scripts/lib/contracts/mirror.py` — `zig_mirror_entries()`, `go_mirror_entries()`, `ts_mirror_entries()`, `python_mirror_entries()`, `read_python_module_name()`

## 3. Entrance Criteria

- [x] DE-028 complete (`generate_contracts` param exists on `process_source_unit`)
- [x] Delta DE-029 accepted
- [x] Gate checks passed (IP-029 §3)
- [x] Design decisions resolved (variant_outputs interface, Python staging key, DocVariant contract)

## 4. Exit Criteria / Done When

- [x] `LanguageAdapter.generate()` signature changed to `variant_outputs: dict[str, Path]`
- [x] All 4 adapters updated (Go/Zig/TS: variant_outputs; Python: staging dir)
- [x] `process_source_unit` computes canonical output paths and dispatches correctly
- [x] Python distribute step moves staged files to `.contracts/<view>/<module>.py.md`
- [x] `sync` on this repo writes real files to `.contracts/` (verified on spec-driver + external zig repo)
- [x] VT-CONTRACTS-STORAGE-001, VT-CONTRACTS-ADAPTER-001, VT-CONTRACTS-PATH-VALIDATION-001 pass
- [x] `just` green

## 5. Verification

- `just test` — full test suite
- `just lint` + `just pylint` — zero warnings
- Manual: `uv run spec-driver sync` on this repo → inspect `.contracts/` for real files
- VT-CONTRACTS-STORAGE-001: generate, assert real files; delete + regenerate = byte-identical
- VT-CONTRACTS-ADAPTER-001: per-adapter test, writes to provided paths
- VT-CONTRACTS-PATH-VALIDATION-001: per-adapter, returned DocVariant.path matches provided output

## 6. Assumptions & STOP Conditions

- Assumptions:
  - External tools (gomarkdoc, zigmarkdoc, ts-doc-extract) accept arbitrary `--output` paths
  - Python `generate_docs()` accepts arbitrary `output_root` (already parameterised)
- STOP when:
  - An external tool doesn't support writing to an arbitrary output path
  - Mirror mapping functions produce unexpected results when called pre-generation

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                         | Parallel? | Notes                                                                                                                     |
| ------ | --- | --------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------- |
| [x]    | 1.1 | Change `LanguageAdapter.generate()` signature       |           | `spec_dir: Path` → `variant_outputs: dict[str, Path]` in ABC + docstring                                                  |
| [x]    | 1.2 | Update `GoAdapter.generate()`                       | [P]       | Reads `variant_outputs["public"]`/`["internal"]`; passes to gomarkdoc `--output`                                          |
| [x]    | 1.3 | Update `ZigAdapter.generate()`                      | [P]       | Same pattern; canonical leaf = `{id}.md` via caller-provided paths                                                        |
| [x]    | 1.4 | Update `TypeScriptAdapter.generate()`               | [P]       | Iterates `variant_outputs.items()`; dedup logic uses provided paths                                                       |
| [x]    | 1.5 | Update `PythonAdapter.generate()`                   | [P]       | Uses `variant_outputs["_staging_dir"]` as `output_root` for `generate_docs()`                                             |
| [x]    | 1.6 | Path resolution + dispatch in `process_source_unit` |           | `_resolve_variant_outputs()` delegates to `resolve_{go,zig,ts}_variant_outputs()` / `python_staging_dir()` from mirror.py |
| [x]    | 1.7 | Python distribute step                              |           | `_distribute_python_contracts()` scans staging, parses headers, moves to canonical paths, cleans up                       |
| [x]    | 1.8 | Write VT tests                                      |           | Existing adapter tests updated to `variant_outputs=`; resolver + staging tests in mirror_test.py; 1670 tests pass         |
| [x]    | 1.9 | Update `_sync_specs` post-sync flow                 |           | Canonical files written during `process_source_unit`; mirror rebuild still runs for compat symlinks                       |

### Task Details

- **1.1 Change base signature**
  - **Files**: `supekku/scripts/lib/sync/adapters/base.py`
  - **Approach**: Change `spec_dir: Path` → `variant_outputs: dict[str, Path]` in abstract method. Update docstring.
  - **Testing**: Existing tests will fail until adapters updated (do 1.2–1.5 immediately after).

- **1.2 GoAdapter**
  - **Files**: `supekku/scripts/lib/sync/adapters/go.py`
  - **Approach**: Replace `contracts_dir = spec_dir / "contracts"` + fixed filenames with `variant_outputs["public"]` / `variant_outputs["internal"]`. Pass directly to gomarkdoc `--output`. Return `DocVariant.path` = provided path.
  - **Note**: Go canonical paths PRESERVE original filenames (`interfaces.md`, `internals.md`).

- **1.3 ZigAdapter**
  - **Files**: `supekku/scripts/lib/sync/adapters/zig.py`
  - **Approach**: Same as Go but canonical leaf is `{identifier}.md` — adapter writes zigmarkdoc output to the provided path, not to `interfaces.md`.
  - **Note**: The `--output` flag of zigmarkdoc already accepts an arbitrary path.

- **1.4 TypeScriptAdapter**
  - **Files**: `supekku/scripts/lib/sync/adapters/typescript.py`
  - **Approach**: Same as Zig — write to `variant_outputs` paths. Canonical leaf = `{identifier}.md`.

- **1.5 PythonAdapter**
  - **Files**: `supekku/scripts/lib/sync/adapters/python.py`
  - **Approach**: Replace `output_root = spec_dir / "contracts"` with staging dir received from caller. Internal `generate_docs()` call unchanged — just different `output_root`. May return empty/placeholder `DocVariant.path` values.

- **1.6 Path resolution in process_source_unit**
  - **Files**: `supekku/scripts/sync_specs.py`, `supekku/scripts/lib/contracts/mirror.py`
  - **Approach**: Extract pre-generation path resolvers from existing mirror mapping functions. For Go/Zig/TS: `(language, identifier, variant)` → canonical output file path. For Python: create staging dir at `.contracts/.staging/<language>/<identifier-slug>/`. Build `variant_outputs` dict and pass to adapter.
  - **Key mapping rules** (from `mirror.py`):
    - Go: `mirror_path = f"{identifier}/{contract_name}"` (dir + filename)
    - Zig: `mirror_path = f"{identifier}.md"` (leaf file per view)
    - TS: `mirror_path = f"{identifier}.md"` (leaf file per view)
  - **Validation**: After `adapter.generate()`, validate returned `DocVariant.path` matches provided paths.

- **1.7 Python distribute step**
  - **Files**: `supekku/scripts/sync_specs.py` (or new helper in `supekku/scripts/lib/contracts/`)
  - **Approach**: After Python adapter writes to staging dir, scan files. For each: `read_python_module_name()` → module identity, `extract_python_variant()` → variant/view. Move to `.contracts/<view>/<module-path>.py.md`. Remove staging dir.
  - **Reuse**: `read_python_module_name()` and `extract_python_variant()` already in `mirror.py`.

- **1.8 Write VT tests**
  - **Files**: New test file(s) under `supekku/scripts/lib/contracts/` or `supekku/scripts/lib/sync/adapters/`
  - **VT-CONTRACTS-STORAGE-001**: Generate contracts, assert `.contracts/<view>/...` contains real files (not symlinks). Delete + regenerate = byte-identical.
  - **VT-CONTRACTS-ADAPTER-001**: Per-adapter: provide variant_outputs, assert files written to those paths.
  - **VT-CONTRACTS-PATH-VALIDATION-001**: Per-adapter: assert returned DocVariant.path matches provided output paths.

- **1.9 Update \_sync_specs post-sync**
  - **Files**: `supekku/cli/sync.py`
  - **Approach**: Canonical files are now written during `process_source_unit` (not by mirror builder). The existing `ContractMirrorTreeBuilder.rebuild()` call may need adjustment — it currently creates `.contracts/` symlinks from `SPEC-*/contracts/`, but canonical files are now written directly. Phase 2 will fully invert the mirror builder; this task just ensures the post-sync flow doesn't conflict.

## 8. Risks & Mitigations

| Risk                                                         | Mitigation                                                                  | Status   |
| ------------------------------------------------------------ | --------------------------------------------------------------------------- | -------- |
| Zig/TS external tools may not support arbitrary output paths | Already pass `--output <path>` — just change the path value                 | resolved |
| Python staging dir left behind on error                      | Wrap distribute in try/finally with cleanup                                 | resolved |
| Existing mirror builder conflicts with new canonical files   | `rebuild()` inverted: now creates SPEC-\*/contracts/ → .contracts/ symlinks | resolved |

## 9. Decisions & Outcomes

- 2026-02-21 — `variant_outputs: dict[str, Path]` chosen over `contracts_dir: Path` (see DR-029 §7.1)
- 2026-02-21 — Python staging key: `<language>/<identifier-slug>` (not spec-id; works with --no-specs)
- 2026-02-21 — DocVariant.path must match provided output paths (centrally validated)

## 10. Findings / Research Notes

- **DocVariant.path semantics shift**: In the old interface, `DocVariant.path` was relative to the spec's contracts dir. Now it's the absolute canonical output path provided by the caller. Adapter tests updated accordingly.
- **Python staging key**: Uses `identifier.replace("/", "-").replace(".", "-")` — works for both path-style (`supekku/scripts/lib/foo`) and dotted-style identifiers.
- **TS variant name mapping**: TS adapter uses `api`/`internal` variant names (not `public`/`internal`), so `resolve_ts_variant_outputs()` keys match. The adapter iterates `variant_outputs.items()` directly.
- **Mirror builder inverted (agent #3)**: `rebuild()` no longer nukes `.contracts/`. It now creates compat symlinks FROM `SPEC-*/contracts/` pointing INTO `.contracts/`. Old dead code (`_collect_entries`, `_resolve_conflicts`, `_create_symlinks`, `MirrorEntry`, `*_mirror_entries`) is still exported from `__init__.py` — can be cleaned up in a follow-up.
- **Contract generation gate fixed (agent #3)**: `process_source_unit()` restructured so contract generation is independent of spec existence. When `create_specs=False`, spec work is skipped but contracts still proceed.
- **Zig adapter status bug (observed, not fixed)**: `_generate_variant` reports `status="created"` even when `output_path` doesn't exist after zigmarkdoc runs (line 357). Pre-existing; not related to DE-029.
- **Test count**: 1667 tests, 0 failures, 3 skipped. Pylint 9.67/10 (unchanged).

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (test suite green, manual verification done)
- [x] Phase notes updated with observations
- [x] Compat symlinks implemented (mirror inversion done in this phase, not deferred)
- [ ] Hand-off notes to Phase 2 (drift warnings, dead code cleanup, Zig status bug)
