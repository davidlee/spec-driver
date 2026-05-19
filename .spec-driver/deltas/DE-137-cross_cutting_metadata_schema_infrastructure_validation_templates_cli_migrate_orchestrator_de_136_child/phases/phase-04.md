---
id: IP-137-P04
slug: "137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child-phase-04"
name: IP-137 Phase 04 - Migrate framework + workflow.toml schema + import-linter contract
created: "2026-05-19"
updated: "2026-05-19"
status: draft
kind: phase
plan: IP-137
delta: DE-137
---

# IP-137-P04 — Migrate framework + `workflow.toml` schema + import-linter contract

## 1. Objective

Land the migration subsystem and the per-kind strict-mode plumbing
that DE-138..142 (sibling per-artefact deltas) will consume:

- `spec_driver/migrations/_protocol.py` — `MigrationStep` Protocol,
  `BaseMigrationStep`, `StepPreview`, `StepResult` (frozen-forever
  per DEC-137-26).
- `spec_driver/migrations/_helpers.py` — `split_frontmatter`,
  `atomic_write`, `replace_in_frontmatter_block` (frozen-forever
  bytes-level helpers, F-20).
- `spec_driver/migrations/_folder.py` — `MIGRATION_FOLDER_PATTERN`,
  `parse_migration_folder(name) -> ParsedFolder | None` (F-13).
- `spec_driver/presentation/cli/admin/migrate.py` — orchestrator
  (discovery, kind-filter, dispatch, lockfile, watermark advance,
  per-run log). Wired into the user-facing `admin` Typer group via
  `supekku/cli/admin.py` (mirroring P03's pattern for the `validate`
  group).
- `DEFAULT_CONFIG` (`supekku/scripts/lib/core/config.py`) gains
  `[migrations]`, `[validation.strict]`, `[schema_version]` sections.
- Install-time fresh-vs-upgrade trigger (DEC-137-18, F-5): presence
  of `.spec-driver/` decides whether `workflow.toml` ships with
  strict-on per kind plus install message.
- Loader → `MetadataValidator` per-kind strict dispatch (F-48):
  registry caches a `dict[str, bool]` strict map; per-artefact
  loaders pass `strict=strict_map.get(kind, False),
  accept_tolerated=True`.
- `workflow.toml` unknown-kind warning (F-47): config load emits
  `workflow.toml [validation.strict]: unknown kind 'foo'; ignored`
  for unregistered kinds.
- `pyproject.toml` `import-linter` `Migrations isolation` contract
  (F-2, §5.6 verbatim diff): `spec_driver.migrations` forbidden
  from importing `spec_driver.{core,models,domain,orchestration,
  presentation}` or `supekku`. Requires
  `include_external_packages = true`.

DE-137 ships **zero migrations**. `admin migrate --check` runs cleanly
against an empty step inventory. Fixture-only migration step (for
VT-CC-019, 020, 021, 023, 029, 031) lives under
`tests/fixtures/de_137/migrations/` — NOT under
`spec_driver/migrations/` (kept out of the production discovery walk).

## 2. Links & References

- **Delta**: DE-137
- **Design Revision Sections**:
  - DR-137 §5.6 (Deliverable 7 + 8 — `admin migrate` orchestrator +
    `workflow.toml`):
    - "`_protocol.py` — frozen forever (F-4 singular kind)"
    - "Two-layer dispatch (F-33)"
    - "Multi-kind steps are forbidden (DEC-137-16, F-4)"
    - "Kind validation at discovery (F-26)"
    - "Plan/phase/task shared-schema dispatch (F-27)"
    - "Migration folder structure (F-13 valid Python module name)"
    - "Shared `_helpers.py` (F-20)"
    - "Frozen-forever ≠ bug-frozen (F-35)"
    - "`admin migrate` orchestrator"
    - "`workflow.toml` schema additions"
    - "Loader → MetadataValidator dispatch (F-48)"
    - "Config validation at load (F-47)"
    - "Pre-DE-137 artefacts"
    - "Import-linter contract for migration isolation (F-2)"
  - DR-137 §7 — DEC-137-11 (POL-003 migrations boundary), DEC-137-13
    (per-kind strict-flip), DEC-137-16 (singular kind), DEC-137-18
    (install fresh-vs-upgrade trigger), DEC-137-22 (lockfile
    semantics), DEC-137-26 (frozen-forever Protocol+BaseMigrationStep).
  - DR-137 §9.3 — operational notes (forward-only migrations, Windows
    lockfile deferral, mid-walk recovery).
  - DR-137 §10 — DR-136 supersedes (per-kind integer table ⇒
    last_applied watermark; supekku/scripts/lib/migrations/ ⇒
    spec_driver/migrations/; MigrationStep base class ⇒ Protocol).
  - DR-137 §11 — VT-CC-018, 019, 020, 021, 022, 023, 028, 029, 031, 033.
- **Specs / PRODs**: PROD-004 (FR-001), SPEC-114 (blocks/metadata),
  SPEC-125 (validation), SPEC-116 (frontmatter_metadata).
- **Support Docs**:
  - `spec_driver/presentation/cli/constants.py` — already ships
    `MIGRATION_FOLDER_PATTERN`, `MIGRATION_LOG_PATH`,
    `MIGRATION_LOCK_PATH` (P03 task 3.2 hand-off). P04 imports.
  - `supekku/cli/admin.py` — existing admin Typer group (carries
    `regenerate-templates`); P04 adds `migrate` registration here.
  - `supekku/scripts/lib/core/config.py` — `DEFAULT_CONFIG` extended
    in P04 with `[migrations]`, `[validation.strict]`,
    `[schema_version]` sections.
  - `supekku/cli/install.py` (or equivalent) — fresh-vs-upgrade
    trigger lives here (F-5, DEC-137-18).
  - `supekku/scripts/lib/blocks/metadata/validator.py` —
    `MetadataValidator.validate(data, *, strict, accept_tolerated)`
    surface from P01 consumed by loader dispatch.
  - `pyproject.toml` — existing `[tool.importlinter]` block with
    Architectural Layers contract; P04 adds Migrations isolation
    sibling contract.
  - `packaging.version.Version` — sort-key dependency for
    `_folder.py`; transitive via setuptools, confirm direct usage at
    task 4.3.

## 3. Entrance Criteria

- [x] IP-137-P03 complete and committed
  (5217 pytest pass, ruff clean, pylint 9.69 baseline; commit
  `c91746d0`).
- [x] `MetadataValidator(metadata).validate(data, *, strict,
  accept_tolerated)` surface from P01 stable.
- [x] `spec_driver/presentation/cli/constants.py` ships
  `MIGRATION_FOLDER_PATTERN`, `MIGRATION_LOG_PATH`,
  `MIGRATION_LOCK_PATH` (P03 task 3.2).
- [x] `validate` Typer group lives at
  `spec_driver/presentation/cli/validate/` (P03 reference pattern
  for `admin` group wiring).
- [ ] Local toolchain green at start: `just check` clean on the
  post-P03 commit.
- [ ] Pre-flight grep audit captured: every `MetadataValidator(...)`
  construction site in the codebase tagged "loader path" (F-48
  dispatch site) or "ad-hoc" (not part of dispatch); every
  `dump_markdown_file` and config-reader path inspected for strict
  toggle consumption opportunities.

## 4. Exit Criteria / Done When

- [ ] `spec_driver/migrations/__init__.py` exists (empty package
  marker).
- [ ] `spec_driver/migrations/_protocol.py` ships per DR-137 §5.6
  verbatim (~40 LOC):
  - `MigrationStep` Protocol with `applies_to_kind: str` (singular),
    `description: str`, `applies_to(path)`, `preview(path)`,
    `apply(path)` methods.
  - `BaseMigrationStep` concrete base with default
    `applies_to(...) -> True`.
  - `StepPreview` (touched, skipped, drift) and `StepResult`
    (touched, skipped, drift_entries) frozen dataclasses.
- [ ] `spec_driver/migrations/_helpers.py` ships per DR-137 §5.6
  verbatim:
  - `split_frontmatter(text) -> (yaml_block, body)` bytes-only.
  - `atomic_write(path, content)` via sibling tempfile + os.replace,
    preserves existing mode.
  - `replace_in_frontmatter_block(fm_text, key, new_value)`
    whitespace-/comment-preserving scalar rewrite.
- [ ] `spec_driver/migrations/_folder.py` ships:
  - `MIGRATION_FOLDER_PATTERN` re-exported from
    `presentation/cli/constants.py` (single source).
  - `ParsedFolder` frozen dataclass (`version`, `ordinal`, `slug`,
    `name`).
  - `parse_migration_folder(name) -> ParsedFolder | None`.
- [ ] `spec_driver/presentation/cli/admin/__init__.py` ships
  (presentation-layer admin Typer group, distinct from existing
  `supekku/cli/admin.py` user-facing group).
- [ ] `spec_driver/presentation/cli/admin/migrate.py` ships the
  orchestrator per DR-137 §5.6:
  - Subcommands: `--check`, `--list`, `<kind>`, `<kind> --dry-run`,
    `<kind> --strict`, `all`.
  - Lockfile acquisition at `MIGRATION_LOCK_PATH` (PID file); stale
    fresh detection (POSIX) with diagnostic message naming held PID.
  - Discovery walks `spec_driver/migrations/` directory; non-parsing
    folder names skipped silently.
  - Kind validation at discovery: each step's `applies_to_kind`
    checked against registered kinds; mismatch ⇒ fail-fast before
    any dispatch (VT-CC-031).
  - Per-step pass: preview ⇒ apply ⇒ tolerant-mode revalidate ⇒
    write per-run log to `MIGRATION_LOG_PATH` formatted dir ⇒
    advance `[migrations] last_applied` atomically.
  - Mid-walk error: `last_applied` NOT advanced; per-file atomicity
    via `atomic_write`.
- [ ] `supekku/cli/admin.py` registers `migrate` subcommand pointing
  at `spec_driver/presentation/cli/admin/migrate.py::app`.
- [ ] `supekku/scripts/lib/core/config.py::DEFAULT_CONFIG` extended
  with `[migrations] last_applied`, `[validation.strict]` (empty by
  default), `[schema_version]` (empty by default).
- [ ] Install path (`supekku/cli/install.py` or equivalent) detects
  `.spec-driver/` presence (DEC-137-18, F-5):
  - Absent ⇒ generate `workflow.toml` with `[validation.strict]
    delta=true / spec=true / audit=true / revision=true / plan=true`
    plus the verbatim install message from DR-137 §5.6.
  - Present ⇒ preserve all existing keys; do NOT auto-insert strict
    toggles for absent keys.
- [ ] Config load surfaces unknown-kind warning for
  `[validation.strict]` keys not in the registered-kinds set
  (VT-CC-033).
- [ ] Loader → `MetadataValidator` per-kind dispatch (F-48):
  - Registry reads `workflow.toml` once, caches `dict[str, bool]`.
  - Every per-artefact loader call constructs `MetadataValidator`
    and invokes `.validate(data, strict=strict_map.get(kind, False),
    accept_tolerated=True)`.
  - `validate workspace` and `validate file` CLI surfaces consume
    the same per-kind toggle; `--strict` flag continues to force
    True for in-scope kinds.
- [ ] `pyproject.toml` gains the second import-linter contract
  (§5.6 verbatim diff):
  - `include_external_packages = true` at top of
    `[tool.importlinter]` block.
  - `[[tool.importlinter.contracts]] name = "Migrations isolation"
    type = "forbidden" source_modules = ["spec_driver.migrations"]
    forbidden_modules = ["spec_driver.core", "spec_driver.models",
    "spec_driver.domain", "spec_driver.orchestration",
    "spec_driver.presentation", "supekku"]`.
- [ ] `lint-imports` reports `Migrations isolation KEPT` on the
  clean post-P04 tree; `Architectural Layers` contract unchanged.
- [ ] VT coverage green: VT-CC-018, 019, 020, 021, 022, 023, 028,
  029, 031, 033.
- [ ] `just check` clean (test + ruff + format + pylint ratchet);
  `lint-imports` clean.
- [ ] `spec-driver admin migrate --check` runs cleanly against this
  repo (no steps registered ⇒ exit 0 + empty list).

## 5. Verification

- **Unit tests** (added or extended):
  - `tests/spec_driver/migrations/folder_test.py` — VT-CC-028
    (parser: canonical `v0_10_0_001_delta_blocks` parses to
    `(Version("0.10.0"), 1, "delta_blocks")`; non-matching names
    `_protocol.py`, `__pycache__`, `0.10.0_001_x`, `v0.10.0_001_x`
    return `None`).
  - `tests/spec_driver/migrations/helpers_test.py` — coverage of
    `split_frontmatter` (with/without leading `---`),
    `atomic_write` (mode preservation, sibling tempfile path,
    replace semantics), `replace_in_frontmatter_block`
    (whitespace/comment preservation around rewritten scalar).
  - `tests/spec_driver/presentation/cli/admin/migrate_test.py` —
    VT-CC-018 (`--check` lists pending), VT-CC-019 (idempotency
    over mixed pre/post fixture corpus), VT-CC-020 (atomicity:
    interrupted step leaves watermark unchanged), VT-CC-023
    (mid-walk recovery: file N raise → files 1..N-1 in post-state,
    file N unchanged, files N+1..M unchanged, re-run reaches all
    M), VT-CC-031 (kind validation at discovery: fixture step with
    `applies_to_kind='speec'` fails fast).
  - `tests/spec_driver/presentation/cli/admin/lockfile_test.py` —
    VT-CC-029 (POSIX: pre-existing lockfile with running PID ⇒
    non-zero exit + diagnostic naming PID; lockfile not deleted by
    aborting process; staleness branch via known-dead PID;
    Windows: `@pytest.mark.skipif(sys.platform == 'win32', ...)`).
  - `tests/supekku/cli/install_strict_defaults_test.py` —
    VT-CC-022 (fixture without `.spec-driver/` ⇒ post-install
    `workflow.toml` carries strict-on per kind + install message
    on stdout/stderr; fixture with `.spec-driver/` and no
    `[validation.strict]` section ⇒ post-install workflow.toml
    unchanged for those keys).
  - `tests/supekku/scripts/lib/core/config_unknown_kind_test.py`
    (or equivalent location) — VT-CC-033 (workflow.toml
    `[validation.strict] foo = true` for unknown kind ⇒ warning at
    load: `workflow.toml [validation.strict]: unknown kind 'foo';
    ignored`; valid kinds unaffected; no auto-correct).
  - `tests/spec_driver/migrations/importlinter_test.py` — VT-CC-021
    (runs `lint-imports` via subprocess against a fixture branch
    with a deliberate `from spec_driver.core import X` in a
    fixture migration step; asserts non-zero exit + presence of
    the expected violation message;
    `Migrations isolation BROKEN` line matches DR-137 §5.6
    prototype output).
- **Fixtures**:
  - `tests/fixtures/de_137/migrations/v0_10_0_001_fake/` — minimal
    valid migration step (used by VT-CC-019, 020, 023; per
    DR-137 §11 fixture intent).
  - `tests/fixtures/de_137/migrations/v0_10_0_002_bad_kind/` —
    step with `applies_to_kind = 'speec'` (VT-CC-031).
  - `tests/fixtures/de_137/migrations/v0_10_0_003_violates_isolation/`
    — step that imports `spec_driver.core` (VT-CC-021).
  - `tests/fixtures/de_137/install_fresh/` — workspace skeleton
    without `.spec-driver/` (VT-CC-022 fresh branch).
  - `tests/fixtures/de_137/install_existing/` — workspace skeleton
    with `.spec-driver/` (VT-CC-022 upgrade branch).
  - `tests/fixtures/de_137/workflow_unknown_kind/` — workflow.toml
    with `[validation.strict] foo = true` (VT-CC-033).
- **Tooling / commands**:
  - `just test` — full suite, including the new modules under
    `tests/spec_driver/migrations/` and
    `tests/spec_driver/presentation/cli/admin/`.
  - `just lint` — ruff zero warnings on touched files.
  - `just pylint-files <touched paths>` — no regression on
    touched files; address pre-existing warnings per CLAUDE.md.
  - `uv run lint-imports` — both contracts (`Architectural Layers`,
    `Migrations isolation`) `KEPT`.
  - `just check` — phase gate.
  - `spec-driver admin migrate --check` — smoke against this
    repo's empty migration inventory.
- **Evidence to capture** (in `notes.md`):
  - VT IDs + pass status table (one row per VT-CC-018/019/020/
    021/022/023/028/029/031/033).
  - `lint-imports` output showing both contracts `KEPT`.
  - `MetadataValidator` construction-site audit (pre-flight task
    4.1) before/after F-48 dispatch wire-up.
  - `spec-driver admin migrate --check` output on empty inventory.
  - `workflow.toml` diffs for fresh vs upgrade install branches.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `presentation/cli/constants.py` migration entries
    (`MIGRATION_FOLDER_PATTERN`, `MIGRATION_LOG_PATH`,
    `MIGRATION_LOCK_PATH`) ship verbatim per DR-137 §5.4 / §5.6.
    `_folder.py` re-exports the pattern; orchestrator imports the
    path templates directly.
  - `packaging.version.Version` is reachable transitively
    (setuptools / pip chain); if absent, declare it explicitly in
    `pyproject.toml` `[project] dependencies`.
  - The user-facing `admin` Typer group at `supekku/cli/admin.py`
    is the registration site for `migrate` (mirrors how
    `regenerate-templates` already plugs in there). The actual
    orchestrator module lives at
    `spec_driver/presentation/cli/admin/migrate.py` (DR-137 §5.6
    path) — same split pattern P03 used for `validate`.
  - `MetadataValidator(metadata).validate(data, *, strict,
    accept_tolerated)` signature is stable from P01. Per-kind
    dispatch passes `strict=strict_map.get(kind, False),
    accept_tolerated=True` unless `--strict` overrides.
  - Loader entry points for F-48 dispatch are limited to a small,
    enumerable set (registry construction, per-artefact load,
    `validate workspace`, `validate file`). Task 4.1 confirms the
    set; if the set sprawls to >10 sites, surface for `/consult`.
  - Install path (fresh-vs-upgrade trigger) lives in a single
    function reachable from `spec-driver install`. If install
    spans multiple modules with no single entry point, factor a
    helper per DEC-137-18 verbatim text.
  - Lockfile lives at `.spec-driver/run/migrations/.lock`; per-run
    log at `.spec-driver/run/migrations/<timestamp>-<step>.md`.
    These paths come from `presentation/cli/constants.py` (P03
    shipped them).
  - `import-linter` 2.11 `ForbiddenContract` accepts
    `source_modules`, `forbidden_modules`, and
    `include_external_packages` per DR-137 §5.6 prototype.
- **STOP** when:
  - F-48 dispatch site audit reveals a code path that constructs
    `MetadataValidator` with no kind in scope (e.g. cross-kind
    validation) — `/consult` for default behaviour (tolerant or
    inherit from caller).
  - `import-linter` 2.11 contract syntax does NOT match the DR-137
    §5.6 prototype (e.g. field name drift across patch versions) —
    `/consult`; fall back to the layers-equivalent that pyproject
    pin tolerates.
  - `BaseMigrationStep.applies_to` default-True behaviour conflicts
    with the orchestrator's "step decides if file needs work"
    discipline (DR-137 §5.6 two-layer dispatch) — diagnose; either
    the Protocol contract needs adjustment via `/consult` or the
    orchestrator wraps the default with a sentinel check.
  - Lockfile semantics on the CI/sandbox runner differ from POSIX
    (no `/proc`, no `os.kill(pid, 0)`) — defer Windows hardening
    per DR-137 §9.3; VT-CC-029 has the skip marker. STOP only if
    POSIX behaviour itself misbehaves.
  - Mid-walk recovery (VT-CC-023) shows non-atomic file state
    after a simulated raise (e.g. partial bytes written) —
    diagnose `atomic_write`; this IS a regression against the
    `_helpers.py` frozen-forever contract.
  - `[migrations] last_applied` advances on a partial sweep — this
    is a contract violation (DEC-137-22 atomicity); STOP and fix
    before any other task proceeds.
  - The fresh-vs-upgrade install trigger detects the wrong branch
    (e.g. ships strict-on against an upgrading user) — STOP;
    DEC-137-18 verbatim says `.spec-driver/` presence is the
    trigger, not `workflow.toml` presence.
  - `just check` surfaces a pylint regression on a file this phase
    did not touch — confirm out-of-scope per CLAUDE.md; do NOT
    silence the warning.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID   | Description | Parallel? | Notes |
| ------ | ---- | --- | --- | --- |
| [x] | 4.1  | Pre-flight `MetadataValidator(...)` construction-site grep audit + loader/install entry-point reconnaissance | [ ] | Authoritative F-48 dispatch list |
| [x] | 4.2  | Ship `spec_driver/migrations/_protocol.py` (Protocol + BaseMigrationStep + StepPreview/StepResult) | [P] | Frozen-forever; ~40 LOC |
| [x] | 4.3  | Ship `spec_driver/migrations/_helpers.py` (split_frontmatter, atomic_write, replace_in_frontmatter_block) | [P] | Frozen-forever; bytes-only |
| [x] | 4.4  | Ship `spec_driver/migrations/_folder.py` (ParsedFolder + parse_migration_folder) + VT-CC-028 | [P] | Imports MIGRATION_FOLDER_PATTERN from constants.py |
| [x] | 4.5  | Extend `supekku/scripts/lib/core/config.py::DEFAULT_CONFIG` with `[migrations]`, `[validation.strict]`, `[schema_version]` sections + VT-CC-033 unknown-kind warning | [P] | Independent of orchestrator |
| [x] | 4.6  | Install-time fresh-vs-upgrade trigger in `supekku/cli/install.py` + VT-CC-022 | [P] | Depends on 4.5 |
| [ ] | 4.7  | Ship `spec_driver/presentation/cli/admin/__init__.py` + `migrate.py` orchestrator (discovery + dispatch + kind-filter + log + watermark advance) | [ ] | Depends on 4.2/4.3/4.4 |
| [ ] | 4.8  | Wire `admin migrate` into `supekku/cli/admin.py` user-facing group | [ ] | Depends on 4.7 |
| [ ] | 4.9  | Lockfile acquisition + PID-liveness diagnostic in orchestrator + VT-CC-029 | [ ] | Depends on 4.7; POSIX-only test branch |
| [ ] | 4.10 | Kind validation at discovery (fail-fast on unknown applies_to_kind) + VT-CC-031 | [ ] | Depends on 4.7 |
| [ ] | 4.11 | Per-step idempotency + atomicity (watermark advance only on full pass) + VT-CC-018/019/020/023 | [ ] | Depends on 4.7 |
| [ ] | 4.12 | Loader → MetadataValidator per-kind strict dispatch (F-48); wire registry strict-map cache + propagate through `validate workspace` / `validate file` | [ ] | Depends on 4.1/4.5 |
| [ ] | 4.13 | `pyproject.toml` import-linter `Migrations isolation` contract (verbatim diff per DR-137 §5.6) + VT-CC-021 fixture step + subprocess test | [P] | Independent of orchestrator wire-up |
| [ ] | 4.14 | `spec-driver admin migrate --check` smoke against this repo's empty inventory; confirm clean exit | [ ] | Phase smoke; depends on 4.7–4.12 |
| [ ] | 4.15 | `just check` + `lint-imports`; reconcile lint + pylint ratchet | [ ] | Phase gate |
| [ ] | 4.16 | Update `notes.md` + IP-137 progress + commit phase wrap-up | [ ] | `docs(DE-137): IP-137-P04 wrap-up` |

### Task Details

- **4.1 Pre-flight construction-site audit**
  - **Design / Approach**:
    `rg -n 'MetadataValidator\(' --type py` plus
    `rg -n 'def validate' supekku/scripts/lib/blocks/metadata/` and
    `rg -n '\.validate\(' supekku/scripts/lib/` to enumerate every
    site where a metadata validation is constructed/invoked. Tag
    each as `loader` (per-artefact load path; receives the strict
    toggle), `cli` (validate workspace/file; receives `--strict`
    override), or `ad-hoc` (one-off, default tolerant). Capture
    the full list in `notes.md` as the authoritative F-48 dispatch
    inventory. Same pass also identifies the `supekku install`
    entry point (single function vs spread).
  - **Files / Components**: read-only.
  - **Testing**: n/a.
  - **Observations & AI Notes**: this protects against the
    "strict toggle inert" risk (IP §7). DE-137 ships the dispatch
    plumbing; DE-138..142 activate per-kind strictness via
    `admin migrate <kind> --strict`. A missed dispatch site means
    those future flips are silently inert.
  - **Commits / References**: rolled into `chore(DE-137): IP-137-P04
    pre-flight audit` or absorbed by 4.2.

- **4.2 `_protocol.py`**
  - **Design / Approach**: NEW
    `spec_driver/migrations/_protocol.py` per DR-137 §5.6 verbatim:
    `MigrationStep` Protocol (`applies_to_kind: str`,
    `description: str`, `applies_to(path)`, `preview(path) ->
    StepPreview`, `apply(path) -> StepResult`); `BaseMigrationStep`
    concrete base (`applies_to_kind: str = ""`, `description: str =
    ""`, `applies_to(...) -> True`); `StepPreview(touched, skipped,
    drift)` and `StepResult(touched, skipped, drift_entries=[])`
    frozen dataclasses. ~40 LOC including docstring citing
    DEC-137-26 frozen-forever discipline.
  - **Files / Components**: NEW
    `spec_driver/migrations/__init__.py` (empty),
    `spec_driver/migrations/_protocol.py`; NEW
    `tests/spec_driver/migrations/protocol_test.py` (smoke:
    instantiate `BaseMigrationStep` subclass, assert Protocol
    structural typing passes).
  - **Testing**: smoke unit; Protocol structural check via mypy/
    runtime isinstance probe; dataclass frozen invariant.
  - **Observations & AI Notes**: keep this file minimal and pure.
    Module docstring quotes DEC-137-26 verbatim. Future migrations
    snapshot against this API forever; signature changes are
    framework v2 breaks.
  - **Commits / References**: `feat(DE-137): migration step
    protocol + base class (IP-137-P04 task 4.2)`.

- **4.3 `_helpers.py`**
  - **Design / Approach**: NEW
    `spec_driver/migrations/_helpers.py` per DR-137 §5.6 §"Shared
    `_helpers.py`": three bytes-level helpers:
    - `split_frontmatter(text: str) -> tuple[str, str]` — returns
      `(yaml_block, body)` or `('', text)` if no leading `---`.
    - `atomic_write(path: Path, content: str) -> None` — write via
      sibling tempfile + `os.replace`, preserves file mode on
      overwrite.
    - `replace_in_frontmatter_block(fm_text: str, key: str,
      new_value: str) -> str` — rewrite a single top-level scalar
      key's value preserving surrounding whitespace/comments.
    Module docstring quotes F-20 + F-35 verbatim (frozen-forever
    behaviour/signature, bug fixes allowed).
  - **Files / Components**: NEW
    `spec_driver/migrations/_helpers.py`; NEW
    `tests/spec_driver/migrations/helpers_test.py`.
  - **Testing**: round-trip via temp files: write known content +
    rewrite + reread; `atomic_write` mode preservation
    (`os.stat` before/after); `split_frontmatter` with/without
    `---` delimiter; `replace_in_frontmatter_block` preserves
    `# comment` trailing the scalar.
  - **Observations & AI Notes**: bytes-only — no `yaml.safe_load`
    in this module. DR-137 §5.6 calls out the schema-version
    isolation rationale. Future helpers go inline in their
    migration step, not here.
  - **Commits / References**: `feat(DE-137): migration helpers
    (IP-137-P04 task 4.3)`.

- **4.4 `_folder.py` + VT-CC-028**
  - **Design / Approach**: NEW
    `spec_driver/migrations/_folder.py`. Import
    `MIGRATION_FOLDER_PATTERN` from
    `spec_driver.presentation.cli.constants` (single source of
    truth, P03 already shipped it). Define `ParsedFolder` frozen
    dataclass (`version: packaging.version.Version`, `ordinal:
    int`, `slug: str`, `name: str`). `parse_migration_folder(name:
    str) -> ParsedFolder | None`: regex match on the pattern;
    returns `None` for non-matching names so the orchestrator can
    skip silently (`_protocol.py`, `__pycache__`, etc.).
  - **Files / Components**: NEW
    `spec_driver/migrations/_folder.py`; NEW
    `tests/spec_driver/migrations/folder_test.py`.
  - **Testing**: VT-CC-028 — canonical name
    `v0_10_0_001_delta_blocks` parses to
    `(Version("0.10.0"), 1, "delta_blocks")`; non-matching names
    (`_protocol.py`, `__pycache__`, `0.10.0_001_x`,
    `v0.10.0_001_x`) return `None`. Sort key
    `(version, ordinal)` total-order check across a small fixture
    set.
  - **Observations & AI Notes**: confirm `packaging` is on the
    direct deps list during this task. If transitively-only, add
    to `pyproject.toml` `[project] dependencies`.
  - **Commits / References**: `feat(DE-137): migration folder
    parser (IP-137-P04 task 4.4)`.

- **4.5 `DEFAULT_CONFIG` schema additions + VT-CC-033**
  - **Design / Approach**: In
    `supekku/scripts/lib/core/config.py::DEFAULT_CONFIG`, add:
    ```python
    "migrations": {"last_applied": None},
    "validation": {"strict": {}},
    "schema_version": {},
    ```
    At config load, after merge, walk `[validation.strict]` keys
    against `registered_kinds()` (or the equivalent registry
    surface). For each key not in the set, emit
    `workflow.toml [validation.strict]: unknown kind '<key>';
    ignored` via the existing config-warning channel (likely
    `warnings.warn` or a Rich console depending on entry point).
    Do NOT drop the key from the in-memory config — leave it so
    the user sees their typo on next run.
  - **Files / Components**:
    `supekku/scripts/lib/core/config.py`; NEW
    `tests/supekku/scripts/lib/core/config_unknown_kind_test.py`
    (or extend existing config_test.py).
  - **Testing**: VT-CC-033 — fixture workflow.toml with
    `[validation.strict] foo = true` ⇒ warning at load; valid
    kinds (delta, spec, audit, revision, plan) unaffected; no
    auto-correct (key remains in the in-memory config).
  - **Observations & AI Notes**: warning channel — check how
    `supekku.scripts.lib.core.config` currently surfaces warnings;
    reuse the existing pattern. If no channel exists, default to
    `warnings.warn(...)` (capture via `pytest.warns`).
  - **Commits / References**: `feat(DE-137): workflow.toml schema
    + unknown-kind warning (IP-137-P04 task 4.5)`.

- **4.6 Fresh-vs-upgrade install trigger + VT-CC-022**
  - **Design / Approach**: In the install path
    (`supekku/cli/install.py` or wherever workflow.toml is first
    materialised), detect `.spec-driver/` workspace directory
    presence per DEC-137-18:
    - Absent ⇒ generate workflow.toml with
      `[validation.strict] delta=true / spec=true / audit=true /
      revision=true / plan=true` plus emit (Rich console or
      stdout) the verbatim install message:
      ```
      Fresh workspace detected. Strict per-kind validation enabled by default.
      To opt out of strict mode for a kind: edit workflow.toml [validation.strict] <kind> = false
      ```
    - Present ⇒ preserve all existing keys; do NOT auto-insert
      strict toggles for absent keys.
    The trigger is workspace-directory presence, NOT workflow.toml
    presence (a user might delete workflow.toml without intending
    a strict-mode reclassification).
  - **Files / Components**: `supekku/cli/install.py` (or
    equivalent); NEW
    `tests/supekku/cli/install_strict_defaults_test.py`.
  - **Testing**: VT-CC-022 fresh branch — fixture without
    `.spec-driver/`; CliRunner `spec-driver install`; assert
    post-install workflow.toml has strict-on per kind + install
    message captured. Upgrade branch — fixture with
    `.spec-driver/` and no `[validation.strict]` section; assert
    post-install workflow.toml unchanged for those keys.
  - **Observations & AI Notes**: locate the install entry point
    early in this task; if install is spread across multiple
    functions, factor a `_resolve_strict_defaults(repo_root)`
    helper that returns the dict to merge.
  - **Commits / References**: `feat(DE-137): install fresh-vs-upgrade
    strict defaults (IP-137-P04 task 4.6)`.

- **4.7 Orchestrator core**
  - **Design / Approach**: NEW
    `spec_driver/presentation/cli/admin/__init__.py` (Typer group
    skeleton inside the presentation layer — distinct from
    `supekku/cli/admin.py` user-facing group) and
    `spec_driver/presentation/cli/admin/migrate.py`:
    - Typer subcommand surface per DR-137 §5.6:
      `--check`, `--list`, `<kind>`, `<kind> --dry-run`,
      `<kind> --strict`, `all`.
    - Discovery: walk `spec_driver/migrations/` directory; call
      `parse_migration_folder` on each child; collect parsed
      entries; sort by `(version, ordinal)`.
    - Per step: read step module via `importlib.import_module`
      (e.g. `spec_driver.migrations.v0_10_0_001_x.migration`);
      assert top-level `step: MigrationStep` instance exists.
    - Dispatch loop: for each step after `[migrations]
      last_applied`:
      1. Kind-filter pass: read each candidate file's `kind:`
         frontmatter; skip if `!= step.applies_to_kind`.
      2. Call `step.applies_to(path)`; skip if False.
      3. `--dry-run` ⇒ call `step.preview(path)`; collect
         StepPreview; print summary; exit 0 without write.
      4. Otherwise call `step.apply(path)`; receive StepResult.
      5. Re-run current `MetadataValidator` in tolerant mode on
         touched files.
      6. Write per-run log to
         `.spec-driver/run/migrations/<timestamp>-<step>.md`
         (path from `MIGRATION_LOG_PATH`).
      7. Atomically advance `[migrations] last_applied` after the
         step's full pass completes (workflow.toml tempfile +
         rename).
    - `--strict` flag flips `[validation.strict] <kind> = true`
      after the kind's sweep completes cleanly.
  - **Files / Components**: NEW directory
    `spec_driver/presentation/cli/admin/`; NEW
    `spec_driver/presentation/cli/admin/__init__.py`,
    `migrate.py`.
  - **Testing**: smoke that `--check` runs cleanly on empty
    inventory; VT-CC-018 (lists pending against fixture inventory
    with one step). Idempotency / atomicity / mid-walk VTs land
    in task 4.11.
  - **Observations & AI Notes**: keep the orchestrator under ~200
    LOC by factoring helpers (`_discover_steps`, `_load_step`,
    `_advance_watermark`). The orchestrator imports
    `_protocol`/`_helpers`/`_folder` plus the metadata validator
    (presentation may import migrations and metadata —
    layers-allowed direction).
  - **Commits / References**: `feat(DE-137): admin migrate
    orchestrator (IP-137-P04 task 4.7)`.

- **4.8 `supekku/cli/admin.py` registration**
  - **Design / Approach**: In `supekku/cli/admin.py`:
    ```python
    from spec_driver.presentation.cli.admin import app as migrate_app
    app.add_typer(migrate_app, name="migrate", help="…")
    ```
    Mirrors the existing `regenerate-templates` wire-up. No
    behavioural change to other admin subcommands.
  - **Files / Components**: `supekku/cli/admin.py`.
  - **Testing**: CliRunner smoke that `spec-driver admin migrate
    --help` resolves; existing `admin regenerate-templates`
    surface unchanged.
  - **Observations & AI Notes**: P03 pattern for `validate`
    group wiring is the precedent. If `spec_driver.presentation.cli.admin`
    exposes `app` (Typer instance) directly, this is one import +
    one `add_typer` call.
  - **Commits / References**: bundles with 4.7.

- **4.9 Lockfile + VT-CC-029**
  - **Design / Approach**: In `admin/migrate.py`, before any
    discovery walk, acquire `MIGRATION_LOCK_PATH`
    (`.spec-driver/run/migrations/.lock`). Lock content:
    `<pid>\n<iso_timestamp>\n<uuid>\n` (per DR-137 §9.3 / DEC-137-22).
    If lock file already exists:
    - POSIX: parse PID; check via `os.kill(pid, 0)`; if alive ⇒
      exit non-zero with `migrate: concurrent invocation
      detected (lock held by PID <n>); aborting`; if dead (stale)
      ⇒ overwrite the lock and proceed with an info message.
    - Windows: skip liveness probe; conservatively treat lock as
      held; exit non-zero.
    Release on exit (success or failure) via try/finally + atexit
    safety net.
  - **Files / Components**:
    `spec_driver/presentation/cli/admin/migrate.py`; NEW
    `tests/spec_driver/presentation/cli/admin/lockfile_test.py`.
  - **Testing**: VT-CC-029 POSIX path — fixture creates lockfile
    with this process's PID; invoke orchestrator; assert non-zero
    exit + diagnostic message naming PID + timestamp + uuid;
    lockfile NOT deleted by the aborting process. Staleness branch
    — fixture writes a known-dead PID (e.g. very large); invoke
    orchestrator; assert proceed-and-overwrite path with info
    message. Windows path —
    `@pytest.mark.skipif(sys.platform == 'win32', ...)`.
  - **Observations & AI Notes**: `os.kill(pid, 0)` is the POSIX
    idiom; ESRCH ⇒ dead, EPERM ⇒ alive (different user). Treat
    EPERM as alive for safety. Lock content includes
    timestamp+uuid so concurrent-write races are diagnosable.
  - **Commits / References**: bundles with 4.7 or separate
    `feat(DE-137): migrate lockfile (IP-137-P04 task 4.9)`.

- **4.10 Kind validation at discovery + VT-CC-031**
  - **Design / Approach**: After discovery and before any
    dispatch (including `--check`), iterate the loaded steps and
    validate each step's `applies_to_kind` against
    `registered_kinds()`. On mismatch, emit verbatim message from
    DR-137 §5.6:
    ```
    admin migrate: migration step <folder_name> declares
    applies_to_kind='<bad>' which is not a registered kind.
    Registered kinds: <sorted list>.
    ```
    Exit non-zero. No step runs.
  - **Files / Components**:
    `spec_driver/presentation/cli/admin/migrate.py`.
  - **Testing**: VT-CC-031 — fixture step at
    `tests/fixtures/de_137/migrations/v0_10_0_002_bad_kind/` with
    `applies_to_kind = 'speec'`; invoke
    `spec-driver admin migrate --check` against the fixture
    workspace; assert non-zero exit + verbatim message.
  - **Observations & AI Notes**: `registered_kinds()` source —
    `FRONTMATTER_METADATA_REGISTRY` keys, optionally extended
    with any kinds that ship without metadata (improvement,
    guidance — see P02 dev note about fallback). Confirm during
    implementation.
  - **Commits / References**: bundles with 4.7.

- **4.11 Idempotency + atomicity + VT-CC-018/019/020/023**
  - **Design / Approach**: Wire the four sibling VTs:
    - VT-CC-018: `--check` against fixture inventory with one
      registered fake step (workspace `last_applied = ""`)
      lists the step as pending; with `last_applied = step.name`
      lists nothing.
    - VT-CC-019: mixed pre/post corpus — fixture workspace
      contains both pre-state and post-state artefact files
      under the kind; running the step is idempotent (second run
      no-op, final state uniform).
    - VT-CC-020: simulated interruption — wrap `step.apply` to
      raise after writing N files; assert `last_applied` watermark
      NOT advanced.
    - VT-CC-023: same fixture as VT-CC-020 but tests recovery —
      re-run step (raise removed); assert files 1..N-1 in
      post-state (already migrated), file N rolled back via
      atomic_write (or re-migrated cleanly), files N+1..M in
      post-state after re-run; final state matches "fully
      applied".
    Fixture step implementation lives at
    `tests/fixtures/de_137/migrations/v0_10_0_001_fake/`.
  - **Files / Components**:
    `tests/spec_driver/presentation/cli/admin/migrate_test.py`;
    `tests/fixtures/de_137/migrations/v0_10_0_001_fake/`.
  - **Testing**: four VTs above.
  - **Observations & AI Notes**: per-step idempotency is the
    step's responsibility — `apply()` returns a no-op
    StepResult on already-applied files. Orchestrator does NOT
    re-check post-state across runs. The fake fixture step's
    `apply` checks frontmatter for the marker block and skips if
    present; this models the canonical pattern.
  - **Commits / References**: `test(DE-137): migrate idempotency
    + atomicity + recovery (IP-137-P04 task 4.11)`.

- **4.12 F-48 loader dispatch**
  - **Design / Approach**: Per task 4.1's audit, wire the
    per-kind strict map through every identified loader site:
    1. Registry (or Workspace) ctor reads `workflow.toml` once
       via the existing config-loader and caches a
       `dict[str, bool]` `strict_map` derived from
       `[validation.strict]`. Unknown keys already warned by 4.5.
    2. Each per-artefact loader call that constructs
       `MetadataValidator(metadata)` and invokes `.validate(data,
       ...)` passes
       `strict=strict_map.get(kind, False), accept_tolerated=True`.
    3. `validate workspace` already accepts `--strict` /
       `--no-tolerated-aliases` overrides (P03 contract); confirm
       those overrides take precedence over the cached strict map.
    4. `validate file` (P03) inherits the same propagation path.
    Document the wired sites in `notes.md`.
  - **Files / Components**: per audit — likely
    `spec_driver/domain/registries/` or `supekku/scripts/lib/`
    Workspace ctor; per-artefact loader bodies; potentially
    `spec_driver/presentation/cli/validate/workspace.py` and
    `validate/file.py`.
  - **Testing**: integration smoke — fixture workflow.toml with
    `[validation.strict] delta = true`; load a fixture corpus
    where a delta artefact carries a tolerated alias; assert
    error surfaces (strict promoted) instead of warning. Reverse
    fixture confirms tolerant default.
  - **Observations & AI Notes**: this is the "strict toggle
    inert" risk site. The audit (4.1) is the protection. If a
    new loader site appears between 4.1 and 4.12, re-audit.
  - **Commits / References**: `feat(DE-137): loader per-kind
    strict dispatch (IP-137-P04 task 4.12)`.

- **4.13 Import-linter contract + VT-CC-021**
  - **Design / Approach**: `pyproject.toml` diff per DR-137 §5.6
    verbatim:
    ```diff
     [tool.importlinter]
     root_package = "spec_driver"
    +include_external_packages = true

     [[tool.importlinter.contracts]]
     name = "Architectural Layers"
     ...

    +[[tool.importlinter.contracts]]
    +name = "Migrations isolation"
    +type = "forbidden"
    +source_modules = ["spec_driver.migrations"]
    +forbidden_modules = [
    +  "spec_driver.core",
    +  "spec_driver.models",
    +  "spec_driver.domain",
    +  "spec_driver.orchestration",
    +  "spec_driver.presentation",
    +  "supekku",
    +]
    ```
    VT-CC-021: fixture step at
    `tests/fixtures/de_137/migrations/v0_10_0_003_violates_isolation/`
    with `from spec_driver.core import ...`. Test invokes
    `lint-imports` via `subprocess.run` against a temporary
    pyproject pointing the source_modules at the fixture
    directory (or copies the fixture step into a tempdir mirror
    of `spec_driver/migrations/` and runs lint-imports there).
    Asserts non-zero exit + presence of `Migrations isolation
    BROKEN` and the violating edge line. Clean variant (no
    fixture step under migrations/) asserts `Migrations
    isolation KEPT`.
  - **Files / Components**: `pyproject.toml`; NEW
    `tests/spec_driver/migrations/importlinter_test.py`;
    fixture under
    `tests/fixtures/de_137/migrations/v0_10_0_003_violates_isolation/`.
  - **Testing**: VT-CC-021 (subprocess invocation of `lint-imports`).
  - **Observations & AI Notes**: subprocess test is slow; mark
    `@pytest.mark.slow` if a marker exists, else accept the
    cost. Alternative: invoke the import-linter Python API
    directly — confirm against the 2.11 surface during 4.13.
  - **Commits / References**: `feat(DE-137): import-linter
    migrations isolation contract (IP-137-P04 task 4.13)`.

- **4.14 `admin migrate --check` repo smoke**
  - **Design / Approach**: Run
    `uv run spec-driver admin migrate --check` against this repo
    (zero registered steps). Assert exit 0 + empty
    "pending: <none>" output. If the orchestrator's discovery
    walk surfaces a stray non-parsing folder under
    `spec_driver/migrations/` (e.g. `__pycache__`), confirm it's
    silently skipped per `_folder.parse_migration_folder ⇒ None`
    semantics.
  - **Files / Components**: orchestrator entry point.
  - **Testing**: manual smoke captured in `notes.md`.
  - **Observations & AI Notes**: this is the integration smoke
    that catches "discovery walks the wrong directory" or
    "lockfile path misformatted" classes of bug before the phase
    closes.
  - **Commits / References**: rolled into 4.16 wrap-up.

- **4.15 Acceptance gate**
  - **Design / Approach**: `just check` (test + ruff + format +
    pylint ratchet) + `uv run lint-imports` (both contracts
    `KEPT`). Address every failure. For pylint, regression on
    touched files blocks per CLAUDE.md; out-of-scope regressions
    left as-is. New CLI / migrations modules are this phase's
    responsibility for lint.
  - **Files / Components**: as needed.
  - **Testing**: this is the gate.
  - **Observations & AI Notes**: pylint score should hold at ≥
    baseline 9.69. `lint-imports` is a NEW gate this phase
    introduces — confirm it's wired into `just check` (or run it
    separately and document).
  - **Commits / References**: cleanups separate from feature
    commits where practical.

- **4.16 Phase wrap-up**
  - **Design / Approach**: Update `notes.md` with:
    - VT pass table (VT-CC-018/019/020/021/022/023/028/029/031/033).
    - F-48 dispatch site audit (before/after grep).
    - `lint-imports` output showing both contracts `KEPT`.
    - `admin migrate --check` smoke output.
    - workflow.toml diffs for fresh vs upgrade install branches.
    - Hand-off note for IP-137-P05 (skill gates use the now-shipped
      `validate file` / `validate workspace` surface; verbatim
      insert points enumerated in DR-137 §5.5).
    Check IP-137 §9 progress box for P04. Commit phase as
    `docs(DE-137): IP-137-P04 wrap-up`.
  - **Files / Components**: `notes.md`, `IP-137.md`,
    `phases/phase-04.md`.
  - **Testing**: n/a (paperwork).
  - **Observations & AI Notes**: phase-05 sheet is NOT scaffolded
    here. `/plan-phases` runs at P04 close.
  - **Commits / References**: final phase commit.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| F-48 dispatch audit misses a loader site; per-kind strict toggle inert at that path | Task 4.1 captures the audit; task 4.12 wires every identified site; re-audit if new sites appear between 4.1 and 4.12 | open |
| `import-linter` 2.11 syntax drift (e.g. field name change in a patch release) breaks the verbatim DR-137 §5.6 diff | DR-137 prototyped against 2.11; pyproject pins `import-linter>=2.11` already. If contract fails to parse, `/consult` before relaxing the pin | open |
| `packaging.version.Version` not a direct dep (transitive only); breaks if upstream removes it | Task 4.4 confirms; add to `[project] dependencies` explicitly if needed | open |
| Lockfile semantics misbehave on sandbox/CI runner (e.g. no `/proc`); VT-CC-029 false-positives | POSIX path uses `os.kill(pid, 0)` which works across Linux/macOS; Windows path skipped per DR-137 §9.3 | open |
| `BaseMigrationStep.applies_to ⇒ True` default conflicts with step author intent (step actually wants per-file discrimination) | DR-137 §5.6 makes the default behaviour explicit; step author overrides on subclass. Docstring on `BaseMigrationStep` calls this out | open |
| Mid-walk `last_applied` advance on partial sweep ⇒ permanent state corruption | DEC-137-22 atomicity discipline; watermark advance happens only after step's full pass; VT-CC-020/023 cover; STOP condition triggers if violated | open |
| Fresh-vs-upgrade trigger detects the wrong branch (e.g. ships strict-on against upgrading user) | DEC-137-18 verbatim: `.spec-driver/` workspace directory presence is the trigger; VT-CC-022 covers both branches | open |
| Subprocess VT-CC-021 is slow / flaky in CI | Mark `@pytest.mark.slow` if available; alternative: invoke import-linter Python API directly | open |
| `admin migrate <kind> --strict` flag race vs concurrent edits to workflow.toml | Lockfile already serialises concurrent migrate invocations; user direct edits to workflow.toml during a migrate run are out of scope (documented contract) | open |
| F-48 wiring touches the registry surface and risks breakage of unrelated registry consumers | Task 4.12 wires through the existing `MetadataValidator.validate(...)` signature; no changes to the validator itself; per-kind dispatch is additive | open |

## 9. Decisions & Outcomes

- `2026-05-19` — P04 sheet drafted at IP-137-P03 close. Inherits
  DR-137 v3.1 decisions: DEC-137-11 (POL-003 migrations boundary),
  DEC-137-13 (per-kind strict-flip), DEC-137-16 (singular kind,
  multi-kind forbidden), DEC-137-18 (install fresh-vs-upgrade
  trigger by `.spec-driver/` presence), DEC-137-22 (lockfile +
  atomicity semantics), DEC-137-26 (Protocol + BaseMigrationStep
  frozen-forever). F-2 / F-4 / F-5 / F-13 / F-20 / F-21 / F-26 /
  F-27 / F-33 / F-34 / F-35 / F-36 / F-47 / F-48 in scope. No new
  decisions yet; the phase rides on DR-137 §5.6 verbatim.

## 10. Findings / Research Notes

- Task 4.1 F-48 audit captured here.
- `packaging.version.Version` direct-dep status confirmed at task 4.4.
- Install entry-point single-function vs spread confirmed at task 4.6.
- Discovery walk dry-run output captured at task 4.14.

## 11. Wrap-up Checklist

- [ ] Exit criteria (all bullets in §4) satisfied.
- [ ] Verification evidence stored in `notes.md` (VT pass table;
  F-48 audit before/after; lint-imports output; admin migrate
  --check smoke; install workflow.toml diffs).
- [ ] IP-137 §9 progress box for P04 checked.
- [ ] Hand-off note in `notes.md` summarising any new constraints
  for IP-137-P05 (skill gates: verbatim text + anchor markers per
  DR-137 §5.5 — `validate file` / `validate workspace` surfaces
  already shipped by P03).
