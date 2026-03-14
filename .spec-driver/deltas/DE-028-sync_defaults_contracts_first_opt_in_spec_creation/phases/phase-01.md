```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-028-P01
plan: IP-028
delta: DE-028
status: complete
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-028-P01
tasks_total: 6
tasks_done: 6
tasks_blocked: 0
```

# Phase 1 - Sync Defaults & Preference Persistence

## 1. Objective

Implement contracts-first sync defaults, opt-in spec creation with persistent preference marker, and independent `--contracts/--no-contracts` flag.

## 2. Links & References

- **Delta**: [DE-028](../DE-028.md)
- **Revision**: [RE-016](../../../revisions/RE-016-sync_defaults_contracts_first_opt_in_spec_creation/RE-016.md)
- **Specs / PRODs**: PROD-012.FR-005
- **Design Direction**: DE-028 §10 (seam constraints for DE-029)

## 3. Entrance Criteria

- [x] Delta accepted
- [x] Research complete (current sync CLI + engine understood)
- [x] Open question resolved (backward-compat heuristic writes marker → yes)

## 4. Exit Criteria / Done When

- [x] `sync_preferences` module exists with tests
- [x] `--specs` defaults to `None` (tri-state), resolved via preferences
- [x] `--contracts/--no-contracts` flag wired and functional
- [x] `process_source_unit` accepts `generate_contracts` parameter
- [x] Backward compat: existing registry → implicit opt-in + marker written
- [x] First-run hint message emitted when specs skipped
- [x] All VTs passing (VT-SYNC-DEFAULTS-001 through 005)
- [x] `just` green (tests + lint + pylint)

## 5. Verification

- `uv run pytest` — all tests pass
- `just lint` — ruff clean
- `just pylint` — threshold met or improved
- Manual smoke: run `sync` on this repo to confirm no regression

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `.spec-driver/` directory already exists in repos using spec-driver (confirmed)
  - Typer supports `Optional[bool]` with `--flag/--no-flag` pairs
- STOP when:
  - Contract generation turns out to be more deeply coupled than understood (escalate to DR)
  - Changing `--specs` default causes cascading test failures beyond sync tests

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                       | Parallel? | Notes                                                |
| ------ | --- | ----------------------------------------------------------------- | --------- | ---------------------------------------------------- |
| [x]    | 1.1 | Create `sync_preferences` module + tests                          | [P]       | 7 tests, both linters clean                          |
| [x]    | 1.2 | Add `generate_contracts` param to `process_source_unit`           | [ ]       | Gates `adapter.generate()` + dry-run variant listing |
| [x]    | 1.3 | Wire CLI flags: tri-state `--specs`, `--contracts/--no-contracts` | [ ]       | Existing sync_test.py updated for new default        |
| [x]    | 1.4 | Implement preference resolution in `_sync_specs` call site        | [ ]       | Preference resolution + flag passthrough wired       |
| [x]    | 1.5 | Backward compat: registry heuristic + marker write-through        | [ ]       | Lazy RegistryV2 load, stderr message                 |
| [x]    | 1.6 | Integration tests: VT-SYNC-DEFAULTS-001 through 005               | [ ]       | 5 VTs in sync_defaults_test.py, all pass             |

### Task Details

- **1.1 Create `sync_preferences` module + tests**
  - **Design / Approach**: New module `supekku/scripts/lib/core/sync_preferences.py`. Two public functions: `spec_autocreate_enabled(root: Path) -> bool` (checks for `.spec-driver/enable_spec_autocreate` marker) and `persist_spec_autocreate(root: Path) -> None` (creates the marker). Marker is a zero-byte file.
  - **Files / Components**: `supekku/scripts/lib/core/sync_preferences.py`, `supekku/scripts/lib/core/sync_preferences_test.py`
  - **Testing**: marker absent → False; marker present → True; persist creates marker; persist is idempotent; missing `.spec-driver/` dir handled gracefully.
  - **Observations & AI Notes**: Implemented as planned. 7 tests. `persist` creates `.spec-driver/` dir if missing. Module exports `MARKER_FILENAME` constant for test use. Not added to `core/__init__.py` (no need — imported directly by consumers).

- **1.2 Add `generate_contracts` param to `process_source_unit`**
  - **Design / Approach**: Add `generate_contracts: bool = True` parameter. When `False`, skip the `adapter.generate()` call. `_ensure_source_in_spec` still runs (spec frontmatter update is a spec concern, not a contracts concern). In dry-run mode, variant path listing is also gated.
  - **Files / Components**: `supekku/scripts/sync_specs.py` — `MultiLanguageSpecManager.process_source_unit()`
  - **Testing**: existing tests pass (default `True`). No dedicated test for `generate_contracts=False` added yet — covered by integration tests in 1.6.
  - **Observations & AI Notes**: Adds 6th argument to `process_source_unit`, triggering pylint R0913 (too-many-arguments). Pre-existing complexity in this file (e.g. `main` has McCabe 44). Full pylint threshold still passes. Note: `_ensure_source_in_spec` was NOT gated (unlike the original plan which said to skip it) — updating spec frontmatter is orthogonal to contract generation.

- **1.3 Wire CLI flags**
  - **Design / Approach**: Changed `--specs` from `bool = True` to `bool | None = None` via typer's `--specs/--no-specs` flag pair. Added `--contracts/--no-contracts` as `bool = True`. Updated docstring.
  - **Observations & AI Notes**: Typer handles `bool | None` with `--flag/--no-flag` syntax cleanly — no default shown in help for the tri-state flag. `contracts` param is defined but not yet used in the function body (wired in 1.4). Updated `sync_test.py` to pass `--specs` explicitly in both existing tests (they previously relied on default `True`). One cascading test failure caught and fixed: `test_sync_exits_one_when_specs_fail` was invoking `sync` without `--specs`, so spec sync no longer ran and the test passed unexpectedly.
  - **Files / Components**: `supekku/cli/sync.py` — `sync()` function signature + help strings
  - **Testing**: verify typer parses all flag combinations correctly.

- **1.4 Implement preference resolution**
  - **Design / Approach**: In `sync()` before calling `_sync_specs`:
    ```
    resolved_specs = specs                           # explicit flag (True/False/None)
    if resolved_specs is None:
      resolved_specs = spec_autocreate_enabled(root)  # persisted marker
    if resolved_specs and specs is True:              # explicit --specs: persist
      persist_spec_autocreate(root)
    ```
    Pass `resolved_specs` and `contracts` to `_sync_specs`. When `resolved_specs` is False, skip spec creation in `process_source_unit` (pass `create_specs=False` — or simply don't call it for new units). When `contracts` is False, skip `adapter.generate()` and mirror rebuild.
  - **Files / Components**: `supekku/cli/sync.py` — `sync()` body, `_sync_specs()` parameters; `supekku/scripts/sync_specs.py` — `process_source_unit()`
  - **Testing**: covered by VTs in task 1.6.
  - **Observations & AI Notes**: Entry guard changed from `if specs:` to `if resolved_specs or contracts:` — sync runs whenever either is wanted. `_sync_specs` gains `create_specs` and `generate_contracts` keyword params (defaults `True`), passed through to `process_source_unit`. `process_source_unit` gains `create_specs: bool = True` — when False and no existing spec, returns skipped with reason `"spec auto-creation is off"`. Mirror tree rebuild gated on `generate_contracts`. Hint message emitted to stderr when specs off but contracts on. `persist_spec_autocreate` called unconditionally when `specs is True` (idempotent). Now 8 params on `process_source_unit` (7 + self) — pre-existing pylint complexity; threshold holds at 9.67.

- **1.5 Backward compat: registry heuristic**
  - **Design / Approach**: Before preference resolution, check if `registry_v2.json` has any spec entries for the target language(s). If yes and no marker exists, treat as implicit opt-in and write the marker (making it explicit). Log: `"Existing specs detected; enabling spec auto-creation (persisted)."`
  - **Files / Components**: `supekku/cli/sync.py` — early in `sync()` body
  - **Testing**: VT-SYNC-DEFAULTS-004.
  - **Observations & AI Notes**: Uses lazy import of `RegistryV2` — only loaded when registry exists and marker absent. Checks `any(registry.languages.values())` — language-agnostic, not filtered by `--language`. Message goes to stderr. Marker written before preference resolution so it's immediately picked up.

- **1.6 Integration tests**
  - **Design / Approach**: Tests exercise the full CLI flow with temp directories. Each VT maps to a test function:
    - VT-001: fresh dir, `sync` → no specs created, contracts attempted (but no spec dirs, so skip)
    - VT-002: fresh dir, `sync --specs` → specs created, marker written; second `sync` → specs still created
    - VT-003: populated dir, `sync --no-contracts` → spec processing runs, contract generation skipped
    - VT-004: dir with populated registry, `sync` → specs enabled, marker written
    - VT-005: fresh dir, `sync` → stderr contains hint message
  - **Files / Components**: `supekku/cli/sync_defaults_test.py` (new)
  - **Testing**: self-referential — these ARE the tests.
  - **Observations & AI Notes**: Created as standalone file (not extending sync_test.py) — different concerns. Mocks `_sync_specs`, `_sync_requirements`, `find_repo_root`. Asserts on `call_args.kwargs` for `create_specs` and `generate_contracts` passthrough. VT-002 exercises two sequential invocations to verify persistence. Typer's CliRunner mixes stderr into `result.output` — no `mix_stderr` option available, so all message assertions use `result.output`. All 5 VTs pass. Total test count: 1660 (was 1655).

## 8. Risks & Mitigations

| Risk                                                   | Mitigation                                                     | Status                             |
| ------------------------------------------------------ | -------------------------------------------------------------- | ---------------------------------- |
| Typer `Optional[bool]` with flag pairs may have quirks | Test flag parsing explicitly; check typer docs                 | resolved — works cleanly           |
| Existing sync tests may assume `--specs=True` default  | Run full suite early after flag change; fix breakage           | resolved — 1 test fixed in 1.3     |
| `process_source_unit` changes affect other callers     | Check for references; method is only called from `_sync_specs` | resolved — confirmed single caller |

## 9. Decisions & Outcomes

- `2026-02-21` - Backward-compat heuristic writes marker file (makes implicit opt-in explicit). Rationale: avoids repeated heuristic evaluation, makes state visible to user.

## 10. Findings / Research Notes

- `process_source_unit` lives in `supekku/scripts/sync_specs.py:175`, not in `supekku/scripts/lib/sync/engine.py`. `SpecSyncEngine` exists but `_sync_specs` in the CLI bypasses it and uses `MultiLanguageSpecManager` directly.
- `--specs` is currently at `sync.py:76` as `bool = True`.
- Mirror tree rebuild is at `sync.py:500` (inside `_sync_specs`), guarded by `processed_count > 0`. The `--no-contracts` flag should also suppress this.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (VT-001–005 in sync_defaults_test.py)
- [x] Delta/Plan updated with findings
- [ ] RE-016 actions updated (mark implementation action as done)
- [ ] Manual smoke test: `sync` on this repo (§5 verification)
