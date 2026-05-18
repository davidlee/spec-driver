---
id: IP-137-P03
slug: "137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child-phase-03"
name: IP-137 Phase 03 - validate Typer group + schema enums CLI + ripple
created: "2026-05-18"
updated: "2026-05-18"
status: completed
kind: phase
plan: IP-137
delta: DE-137
---

# IP-137-P03 — `validate` Typer group + `schema enums` CLI + ripple

## 1. Objective

Promote the validation surface from P02's hyphenated stopgap to the
DR-137 §5.4 design:

- `spec_driver/presentation/cli/constants.py` — POL-002 CLI vocabulary
  module (subcommand names, flag literals, paths, regex patterns).
- New `validate` Typer group at
  `spec_driver/presentation/cli/validate/__init__.py` replacing
  `supekku/cli/workspace.py:validate`. Bare `spec-driver validate` ⇒
  Typer-default help, exit 2.
- Three subcommands as named peers:
  - `validate workspace` (current behaviour, renamed; gains
    `--kind <kind>` per F-8).
  - `validate file <path>` (NEW; single-file authoring-time validation;
    dotted-path diagnostic shape per DEC-137-21).
  - `validate templates` (moved from P02's
    `spec-driver validate-templates` into the group).
- New `spec_driver/presentation/cli/schema/enums.py` —
  `spec-driver schema enums [kind[.field]]` Rich-table CLI reading
  `FRONTMATTER_METADATA_REGISTRY` (POL-001 single source of truth).
- Uniform exit-code contract across `validate` subcommands (F-46):
  `0` clean, `1` errors surfaced, `2` usage.
- `--fix` on `validate workspace` consumes `fix_hint`/`fix_kind`
  emitted by the P01 validator (`rename_key` ⇒ key rewrite,
  `rewrite_value` ⇒ value rewrite). Uses
  `dump_markdown_file_update` so existing comment maps survive.
- Migrate ~8 live ripple sites (lifecycle.md, PROD-010.md, SPEC-110.md,
  Justfile recipes, audit-change/close-change SKILL.md references)
  from bare `validate` to explicit subcommand form.
- ISSUE-054 regression: VT-CC-026 asserts `list deltas` on a
  malformed-YAML fixture emits a single-line human error, no Rich
  traceback.

No skill insertions (P05). No migration framework (P04). No
artefact-data sweeps (DE-138..142).

## 2. Links & References

- **Delta**: DE-137
- **Design Revision Sections**:
  - DR-137 §5.3 (Deliverable X — `schema enums` CLI)
  - DR-137 §5.4 (Deliverable 4 + 5.4a — `validate file` + `validate workspace --kind`):
    - "`validate` Typer group (DEC-137-17)"
    - "Exit-code contract (uniform across validate subcommands; F-46)"
    - "`validate file` path handling (F-41)"
    - "CLI migration ripple (F-11 / F-12)"
    - "CLI vocabulary constants (F-16, POL-002)"
    - "`--kind <kind>` semantics (F-8)"
    - "`validate file <path>` output format" (DEC-137-21)
    - "ISSUE-054 re-verification (F-10)"
  - DR-137 §11 — VT-CC-014, 015, 016, 017, 025, 026, 032 + VA-CC-001
  - DR-137 §7 — DEC-137-17 (bare validate ⇒ help), DEC-137-20
    (did-you-mean cutoff 0.6), DEC-137-21 (dotted-path diagnostic
    format)
- **Specs / PRODs**: PROD-004 (FR-002, FR-003, FR-006), SPEC-114
  (blocks/metadata), SPEC-116 (frontmatter_metadata), SPEC-125
  (validation), SPEC-134 (CLI surfaces touched)
- **Support Docs**:
  - `supekku/cli/main.py:124-132` — current `validate` +
    `validate-templates` top-level wiring
  - `supekku/cli/workspace.py:65-130` — current
    `workspace.validate` (target of removal/wrap)
  - `supekku/cli/validate.py` — current `templates_cmd` (target of
    move into group)
  - `supekku/cli/schema.py` — existing schema library module (called
    by `show.py` / `list/`). DR-137 §5.3 places `schema enums` under a
    top-level `schema` Typer group (NEW); confirm during task 3.5.
  - `supekku/scripts/lib/blocks/metadata/validator.py` — P01
    `MetadataValidator.validate(...)` with `fix_hint`/`fix_kind`
  - `supekku/scripts/lib/core/frontmatter_metadata/` —
    `FRONTMATTER_METADATA_REGISTRY` consumed by `schema enums`
  - `spec_driver/orchestration/templates.py::validate_templates` —
    reused by group's `templates` subcommand
  - `supekku/scripts/lib/core/spec_utils.py::dump_markdown_file_update`
    — reused by `--fix` rewrite path
  - P02 hand-off (`notes.md`): comment-extraction MVP is single-line
    scalars; multi-line values lose trailing comment on `--fix`
    rewrite

## 3. Entrance Criteria

- [x] IP-137-P02 complete and committed (5080 pytest pass, ruff clean,
  pylint 9.69 baseline)
- [x] `MetadataValidator(metadata).validate(data, *, strict,
  accept_tolerated)` exposes `fix_hint`/`fix_kind` per P01 contract
- [x] `dump_markdown_file_create(..., kind=)` /
  `dump_markdown_file_update(...)` available; legacy entrypoint removed
- [x] `spec-driver validate-templates` hyphenated stopgap shipped in
  P02 (target of in-place move into group)
- [x] `FRONTMATTER_METADATA_REGISTRY` is the canonical source of
  enum-values + aliases + tolerated_aliases (post-P01 split)
- [ ] Local toolchain green at start: `just check` clean on the
  post-P02 commit
- [ ] Pre-flight grep audit captured: every live `spec-driver validate`
  reference in the repo (docs, skills, Justfile, tests) tagged
  ripple/non-ripple

## 4. Exit Criteria / Done When

- [ ] `spec_driver/presentation/cli/constants.py` shipped with the DR-137
  §5.4 vocabulary (subcommand names, flag literals,
  `MIGRATION_FOLDER_PATTERN`, `MIGRATION_LOG_PATH`,
  `MIGRATION_LOCK_PATH`). P04 imports the migration entries; P03 wires
  the validate/schema subset.
- [ ] `spec_driver/presentation/cli/validate/__init__.py` ships a Typer
  group with `no_args_is_help=True` (bare ⇒ help, exit 2 per Typer
  default) — no `invoke_without_command=True` and no
  default-dispatch callback (DEC-137-17).
- [ ] `validate workspace` subcommand absorbs the current behaviour of
  `supekku/cli/workspace.py:validate` with the existing flag surface
  PLUS `--kind <kind>` (F-8 sweep procedure).
- [ ] `validate file <path>` subcommand ships per §5.4 path handling
  (markdown-with-kind, markdown-with-inferred-kind via
  `<delta>/phases/phase-0N.md` style, markdown-without-frontmatter
  ⇒ exit 0 no-op message, non-readable ⇒ exit 2, binary ⇒ exit 2)
  with the dotted-path diagnostic format (DEC-137-21).
- [ ] `validate templates` subcommand reuses `templates_cmd` from
  P02's `supekku/cli/validate.py` (moved/wrapped into the group).
- [ ] `supekku/cli/main.py` registration:
  - `validate-templates` top-level command removed.
  - `validate` top-level command removed.
  - New `validate` Typer group added via
    `app.add_typer(validate.app, name="validate", help=...)`.
- [ ] `supekku/cli/workspace.py:validate` removed (function +
  registration); `workspace.install` / `workspace.doctor` remain.
- [ ] `validate workspace --fix` consumes `fix_hint`/`fix_kind` from
  P01 validator; key-rename (`rename_key`) and value-rewrite
  (`rewrite_value`) both use `dump_markdown_file_update` to preserve
  comments.
- [ ] `spec_driver/presentation/cli/schema/enums.py` ships
  `spec-driver schema enums [kind[.field]]` Rich-table CLI reading
  `FRONTMATTER_METADATA_REGISTRY`; emits canonical + permanent aliases
  + tolerated aliases per §5.3 output shape.
- [ ] `supekku/cli/main.py` registers a top-level `schema` Typer group
  carrying `enums` (and re-exporting / accommodating the existing
  `show schema` / `list schema` surface — confirm placement during
  task 3.5).
- [ ] Uniform exit-code contract verified: `validate workspace`,
  `validate file`, `validate templates` each return `0`/`1`/`2` per
  F-46 (VT-CC-032).
- [ ] Live ripple migrated:
  - `supekku/about/lifecycle.md:118` —
    `validate --sync` ⇒ `validate workspace --sync`.
  - `.spec-driver/product/PROD-010/PROD-010.md:1022` —
    `validate --strict` ⇒ `validate workspace --strict`.
  - `.spec-driver/tech/SPEC-110/SPEC-110.md:439` — same.
  - `Justfile:39-40` — `validate:` recipe ⇒ `uv run spec-driver
    validate workspace`.
  - `Justfile:42-43` — `validate-templates:` recipe ⇒
    `uv run spec-driver validate templates`.
  - `supekku/skills/audit-change/SKILL.md:64` and
    `supekku/skills/close-change/SKILL.md:36` — existing
    `validate` references migrated to `validate workspace`. (P05's
    verbatim skill inserts are separate from this ripple.)
- [ ] `grep -rn 'spec-driver validate\b\|spec-driver validate$'` shows
  zero remaining bare-form callers in live files (frozen
  history/audit files allowed).
- [ ] VT coverage green: VT-CC-014, VT-CC-015, VT-CC-016, VT-CC-017,
  VT-CC-025, VT-CC-026, VT-CC-032 + VA-CC-001.
- [ ] `just check` clean (test + ruff + format + pylint ratchet).
- [ ] `just validate-templates` (renamed recipe) clean.
- [ ] `just validate` (renamed recipe) clean against this repo.

## 5. Verification

- **Unit tests** (added or extended):
  - `tests/spec_driver/presentation/cli/constants_test.py` — sanity
    coverage that vocabulary constants exist and match DR-137 §5.4
    spelling (regression guard against magic-string reintroduction).
  - `tests/spec_driver/presentation/cli/validate/workspace_test.py` —
    VT-CC-014 (`validate workspace --strict --fix` idempotent: second
    invocation on a corpus with a single field-name alias ⇒ first run
    rewrites, exit 0; second run ⇒ no diff, exit 0), VT-CC-017
    (`--kind delta` filters scope; non-delta diagnostics suppressed),
    VT-CC-025 (sweep procedure: post-migration corpus where every
    delta is clean, other kinds carry unmigrated warnings ⇒
    `validate workspace --kind delta --strict` exits 0).
  - `tests/spec_driver/presentation/cli/validate/file_test.py` —
    VT-CC-016 (diagnostic shape per DEC-137-21: enum-violation ⇒
    `path: error: dotted.field.path: …` with "Allowed:" + "Did you
    mean:" hint; alias-warning ⇒
    `path: warning: dotted.field.path: 'alias' is a known alias for
    'canonical'` with fix advice; parse-error ⇒ `path:line:col:`).
    Path handling matrix: kind in frontmatter ⇒ dispatch; inferred
    kind from `<delta>/phases/phase-0N.md` location ⇒ dispatch; no
    frontmatter ⇒ exit 0; missing file ⇒ exit 2; binary ⇒ exit 2.
  - `tests/spec_driver/presentation/cli/validate/group_test.py` —
    VT-CC-032 (uniform exit-code contract: bare `validate` ⇒ exit 2;
    `validate workspace` clean ⇒ 0; with errors ⇒ 1; `validate file
    <missing>` ⇒ 2; `validate file <clean>` ⇒ 0; `validate file
    <error>` ⇒ 1; `validate templates` clean ⇒ 0; drift ⇒ 1).
  - `tests/spec_driver/presentation/cli/schema/enums_test.py` —
    VT-CC-015 (`spec-driver schema enums delta.status` emits canonical
    values + permanent aliases + tolerated aliases per §5.3 output
    shape; `spec-driver schema enums delta` emits all controlled-vocab
    fields; `spec-driver schema enums` lists every kind with
    controlled-vocab fields). VA-CC-001 (parametric smoke across
    every controlled-vocab field in `FRONTMATTER_METADATA_REGISTRY`
    Category A; structured as a parameterised pytest sweep —
    automated to satisfy the VA's "agent-generated" intent without
    requiring a manual report).
  - `tests/supekku/cli/list_deltas_yaml_error_test.py` (new fixture +
    test) — VT-CC-026 (ISSUE-054 regression: fixture workspace with a
    delta carrying malformed YAML in frontmatter; invoke
    `spec-driver list deltas` via CliRunner; assert exit non-zero,
    stdout/stderr matches `<path>:<line>:<col>: parse-error: …`
    pattern, regex-asserts absence of `Traceback (most recent call
    last):` and Rich panel-border characters `│└┘─`).
- **Tooling / commands**:
  - `just test` — full suite, including the 4 new test modules.
  - `just lint` — ruff zero warnings (the new CLI modules are touched
    files).
  - `just pylint-files <touched paths>` — no regression on touched
    files; address pre-existing warnings per CLAUDE.md.
  - `just validate` — renamed Justfile recipe runs `validate
    workspace`; clean on this repo (modulo pre-existing 8 audit-gate
    warnings).
  - `just validate-templates` — renamed Justfile recipe runs
    `validate templates`; clean.
  - `just check` — phase gate.
- **Evidence to capture** (in `notes.md`):
  - VT IDs + pass status table (one row per
    VT-CC-014/015/016/017/025/026/032 + VA-CC-001).
  - Pre-migration `spec-driver validate` callers audit (full grep
    output from task 3.1) + post-migration grep showing zero
    bare-form references in live files.
  - CliRunner invocation snippets for `validate workspace`,
    `validate file`, `validate templates`, `schema enums delta.status`
    demonstrating exit codes + output shape.
  - VT-CC-026 outcome — ISSUE-054 closes alongside DE-137, OR
    follow-up filed if regression assertion fails.
  - DEC-137-21 dotted-path format examples: one enum-violation, one
    alias-warning, one parse-error. Confirm in notes that the
    format matches DR-137 §5.4 verbatim.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - P01 validator's `fix_hint`/`fix_kind` semantics are stable:
    `fix_kind ∈ {rename_key, rewrite_value}`, `fix_hint` carries the
    canonical key/value. `--fix` dispatches on `fix_kind`. Any new
    `fix_kind` value (e.g. `rewrite_subfield`) is out of scope for
    P03 and would trigger a `/consult`.
  - `validate workspace --kind <kind>` sweep procedure (F-8) is
    feasible on the existing loader surface: a load-time kind filter
    plus a relation-traversal pass with subject-filtered warnings.
    If the loader cannot be cleanly split into "full-frontmatter
    load" vs "registry-minimal load" without significant refactor,
    P03 defers `--kind` to a follow-up and ships VT-CC-017/025 as
    SKIP with rationale recorded in notes.
  - The current `workspace.validate` flag surface (`--sync`,
    `--strict`, `--verbose`, `--fix`) maps 1:1 onto
    `validate workspace`. Adding `--kind` and
    `--no-tolerated-aliases` (per DR-137 §5.4) is additive.
  - The existing `schema` callable (`supekku/cli/schema.py`) is a
    library module exposed via `show schema` / `list schema`. P03
    introduces a top-level `schema` Typer **group** wired in
    `main.py`; the group carries `enums` as a new subcommand without
    disturbing the existing `show schema` / `list schema` surface.
    If a naming clash surfaces during 3.5, fall back to
    `spec-driver schema-enums` (hyphenated stopgap) and file the
    clash for follow-up.
  - P02's comment-extraction MVP (single-line scalars only) is
    acceptable for `--fix` rewrites in P03. Multi-line scalar values
    lose trailing comments on rewrite; document in notes as
    accepted trade-off.
  - `<delta>/phases/phase-0N.md` is the only file-location pattern
    that needs inference (no `kind:` in current phase frontmatter
    historically). Other location-based inferences are deferred.
  - VT-CC-026 fixture can be hand-authored in
    `tests/fixtures/de_137/issue_054/` without disturbing the
    existing fixture/loader contracts.
- **STOP** when:
  - `validate workspace --kind <kind>` requires a non-trivial loader
    refactor to enforce the load-time kind filter — `/consult` for
    scope decision (defer to follow-up vs accept refactor in scope).
  - `schema enums delta.status` output does NOT match DR-137 §5.3
    sample shape (e.g. registry walk misses a Category A field) —
    diagnose; either the registry-derived view is incomplete (P01
    regression) or the §5.3 shape needs adjustment via `/consult`.
  - Existing `show schema` / `list schema` callers break under the
    new top-level `schema` group — STOP and either re-route via the
    fallback (`schema-enums` hyphenated) or refactor the existing
    surface explicitly (out of scope; needs `/consult`).
  - VT-CC-026 fails (ISSUE-054 regression detected) — do NOT block
    P03 exit; file a follow-up issue and record the failure in
    notes. ISSUE-054 closure is decoupled from `validate file`
    landing (DR-137 §5.4 ISSUE-054 paragraph).
  - Comment-extraction loses comments on a representative `--fix`
    rewrite of a single-line scalar — this IS a regression; STOP and
    diagnose. Multi-line scalar comment loss is accepted; single-line
    loss is not.
  - Bare `spec-driver validate` exits 0 instead of 2 — Typer's
    `no_args_is_help=True` behaviour does not match VT-CC-032's
    contract; `/consult` for the right Typer pattern (e.g. explicit
    callback raising `typer.Exit(2)`).
  - `just check` surfaces a pylint regression on a file this phase
    did not touch — confirm out-of-scope per CLAUDE.md; do NOT
    silence.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID   | Description | Parallel? | Notes |
| ------ | ---- | --- | --- | --- |
| [ ] | 3.1  | Pre-flight grep audit of `spec-driver validate` callers (docs, skills, Justfile, tests) | [ ] | Authoritative ripple list |
| [ ] | 3.2  | Ship `spec_driver/presentation/cli/constants.py` (POL-002 vocabulary) + tests | [P] | Validate + schema subset; migration entries reserved for P04 |
| [ ] | 3.3  | Ship `validate` Typer group skeleton at `spec_driver/presentation/cli/validate/__init__.py` (no subcommands yet) | [ ] | Depends on 3.2 |
| [ ] | 3.4  | Wire `validate workspace` subcommand (port `workspace.validate` body; add `--kind`, `--no-tolerated-aliases`; uniform exit codes) + VT-CC-014/017/025 | [ ] | Depends on 3.3 |
| [ ] | 3.5  | Wire `validate file <path>` subcommand (path-handling matrix; dotted-path output) + VT-CC-016 | [P] | Depends on 3.3; parallel to 3.4 |
| [ ] | 3.6  | Move `templates_cmd` from P02 `supekku/cli/validate.py` into the group as `validate templates` | [ ] | Depends on 3.3 |
| [ ] | 3.7  | Top-level `validate-templates` + `validate` removed from `supekku/cli/main.py`; new `validate` group registered | [ ] | Atomic with 3.6 |
| [ ] | 3.8  | Ship `validate workspace --fix` consumer of `fix_hint`/`fix_kind` (rename_key + rewrite_value via `dump_markdown_file_update`) | [ ] | Depends on 3.4 |
| [ ] | 3.9  | Ship `spec_driver/presentation/cli/schema/enums.py` + top-level `schema` Typer group registration + VT-CC-015 + VA-CC-001 | [P] | Depends on 3.2; parallel to 3.4/3.5 |
| [ ] | 3.10 | VT-CC-032 group-level uniform exit-code contract test | [ ] | Depends on 3.4/3.5/3.6/3.7 |
| [ ] | 3.11 | VT-CC-026 ISSUE-054 regression test + fixture | [P] | Independent of validate group changes |
| [ ] | 3.12 | Migrate live ripple sites (lifecycle.md, PROD-010.md, SPEC-110.md, Justfile, SKILL.md callers) | [P] | Mechanical |
| [ ] | 3.13 | Confirm zero bare-form `spec-driver validate` references in live files via grep | [ ] | Gate before phase exit |
| [ ] | 3.14 | `just check`; reconcile lint + pylint ratchet | [ ] | Phase gate |
| [ ] | 3.15 | Update `notes.md` + IP-137 progress + ISSUE-054 disposition; commit phase wrap-up | [ ] | `docs(DE-137): IP-137-P03 wrap-up` |

### Task Details

- **3.1 Pre-flight grep audit**
  - **Design / Approach**:
    `rg -n 'spec-driver validate' --type-add 'md:*.md' --type md,py`
    plus `rg -n 'uv run spec-driver validate'`. Tag each call site
    `ripple` (live file, needs subcommand rewrite) or `frozen`
    (audit-trail, leave alone — DR-137 §5.4 frozen-list rule). Tag
    test references separately (CliRunner invocations may need
    updating). Capture full output in `notes.md` as authoritative
    ripple inventory.
  - **Files / Components**: read-only.
  - **Testing**: n/a.
  - **Observations & AI Notes**: confirms ripple inventory before
    code edits; protects against drift since DR ratification. Pay
    attention to skill files — `supekku/skills/audit-change/SKILL.md`
    and `supekku/skills/close-change/SKILL.md` carry pre-existing
    bare-form references that must migrate (separate from P05's
    verbatim insertions).
  - **Commits / References**: rolled into the first code commit, or
    a discrete `chore(DE-137): pre-flight audit IP-137-P03`.

- **3.2 `presentation/cli/constants.py` POL-002 vocabulary module**
  - **Design / Approach**: NEW
    `spec_driver/presentation/cli/constants.py` per DR-137 §5.4 verbatim:
    subcommand names (`VALIDATE`, `VALIDATE_WORKSPACE`,
    `VALIDATE_FILE`, `VALIDATE_TEMPLATES`, `SCHEMA_ENUMS`,
    `ADMIN_MIGRATE`, `ADMIN_REGENERATE_TEMPLATES`); flag literals
    (`FLAG_STRICT`, `FLAG_NO_TOLERATED`, `FLAG_FIX`, `FLAG_SYNC`,
    `FLAG_KIND`, `FLAG_DRY_RUN`, `FLAG_CHECK`, `FLAG_LIST`); patterns
    and path templates (`MIGRATION_FOLDER_PATTERN`,
    `MIGRATION_LOG_PATH`, `MIGRATION_LOCK_PATH`). P03 wires the
    validate/schema subset; the migration entries are imported by
    P04. Module-level docstring cites DR-137 §5.4.
  - **Files / Components**: NEW
    `spec_driver/presentation/cli/constants.py`; NEW
    `tests/spec_driver/presentation/cli/constants_test.py`.
  - **Testing**: sanity coverage — every constant exists, types
    match DR (str / `re.Pattern`); `MIGRATION_FOLDER_PATTERN`
    matches at least one canonical example
    (`v0_10_0_001_delta_blocks`).
  - **Observations & AI Notes**: this is the POL-002 hook for the
    whole DE-137 CLI surface. Typer subcommands, flag declarations,
    and (P04) orchestrator regex/path strings reference these
    constants. Keep the file small and pure — no logic.
  - **Commits / References**: `feat(DE-137): CLI vocabulary
    constants (IP-137-P03 task 3.2)`.

- **3.3 `validate` Typer group skeleton**
  - **Design / Approach**: NEW
    `spec_driver/presentation/cli/validate/__init__.py`:
    ```python
    from __future__ import annotations
    import typer

    app = typer.Typer(no_args_is_help=True)  # bare ⇒ help, exit 2

    # Subcommands wired in workspace.py, file.py, templates.py
    # imported below; each does `@app.command(VALIDATE_WORKSPACE)`, etc.
    ```
    No callback. No `invoke_without_command=True`. The group is
    minimal scaffolding; the three subcommand modules
    (`workspace.py`, `file.py`, `templates.py`) sit alongside
    `__init__.py` and self-register via the shared `app` import.
  - **Files / Components**: NEW directory
    `spec_driver/presentation/cli/validate/`.
  - **Testing**: smoke — `validate --help` lists three subcommands;
    bare `validate` exits 2.
  - **Observations & AI Notes**: chose package-with-subcommand-modules
    layout (matches `presentation/cli/`'s
    `validate/{__init__,workspace,file,templates}.py` shape) over
    a single 3-command module for cohesion + future extensibility
    (P04 adds `admin migrate`; precedent matters).
  - **Commits / References**: bundles with 3.4.

- **3.4 `validate workspace` subcommand**
  - **Design / Approach**: NEW
    `spec_driver/presentation/cli/validate/workspace.py`. Port the
    body of `supekku/cli/workspace.py:validate` verbatim, then add:
    - `--kind <kind>` flag (Optional[str], default None). When set,
      apply F-8 sweep procedure: pass `kind=kind` into the loader's
      per-kind filter; full corpus still loaded for relation
      traversal but warnings filtered to subject kind.
    - `--no-tolerated-aliases` flag (bool, default False). When set,
      pass `accept_tolerated=False` into the validator.
    - Uniform exit-code contract: 0 clean, 1 errors surfaced, 2
      usage. `--strict` promotes warnings to errors.
    Reuse `Workspace`, `find_repo_root`, `validate_ws`. The flag
    types and helper text mirror the current command.
  - **Files / Components**: NEW
    `spec_driver/presentation/cli/validate/workspace.py`; NEW
    `tests/spec_driver/presentation/cli/validate/workspace_test.py`.
  - **Testing**: VT-CC-014 (`--strict --fix` idempotency), VT-CC-017
    (`--kind delta` filters scope), VT-CC-025 (sweep procedure on
    mixed-kind corpus). CliRunner against fixture workspaces under
    `tests/fixtures/de_137/validate_workspace/`.
  - **Observations & AI Notes**: if the loader cannot cleanly filter
    on kind without a deeper refactor, fall back to "load full, then
    filter results" (the F-8 §1 vs §2 distinction collapses to §2
    alone). VT-CC-025 still passes in that variant; document the
    deviation in notes if taken.
  - **Commits / References**: `feat(DE-137): validate workspace
    subcommand + --kind (IP-137-P03 task 3.4)`.

- **3.5 `validate file <path>` subcommand**
  - **Design / Approach**: NEW
    `spec_driver/presentation/cli/validate/file.py`. Path handling
    per DR-137 §5.4 (verbatim five-branch matrix). Kind dispatch:
    read the frontmatter; if `kind:` field present, use that; else
    infer from path pattern (`<delta>/phases/phase-0N.md` ⇒
    `phase`). For inferred kinds, table-of-patterns in a
    `_kind_inference.py` helper if more than 1-2 patterns surface;
    otherwise inline. Dispatch to `MetadataValidator(metadata)`;
    format diagnostics per DEC-137-21 dotted-path shape; for YAML
    parse errors (pre-semantic), emit `path:line:col:` using the
    `yaml.MarkedYAMLError.problem_mark`. Output goes to stdout;
    exit per F-46 contract.
  - **Files / Components**: NEW
    `spec_driver/presentation/cli/validate/file.py`; NEW
    `tests/spec_driver/presentation/cli/validate/file_test.py`.
  - **Testing**: VT-CC-016 covers all five path-handling branches
    plus diagnostic shape: enum-violation, alias-warning,
    parse-error, no-frontmatter, missing file, binary file.
  - **Observations & AI Notes**: this is the ISSUE-054 lineage —
    authoring-time feedback. Keep output single-line per
    diagnostic to enable downstream parsing. "Did you mean:" hint
    is derived via `closest_match` (P01 utility) at cutoff 0.6
    (DEC-137-20).
  - **Commits / References**: `feat(DE-137): validate file
    subcommand (IP-137-P03 task 3.5)`.

- **3.6 Move `templates_cmd` into group as `validate templates`**
  - **Design / Approach**: Move
    `supekku/cli/validate.py::templates_cmd` to
    `spec_driver/presentation/cli/validate/templates.py`. Re-decorate
    as `@app.command(VALIDATE_TEMPLATES)`. Function body unchanged
    (calls `validate_templates(repo)`, prints drifts, exits 1 on
    drift). Delete `supekku/cli/validate.py` (or leave a thin
    re-export for one cycle — but DR's "no shim" stance argues for
    deletion; align with 3.7).
  - **Files / Components**: NEW
    `spec_driver/presentation/cli/validate/templates.py`; DELETE (or
    empty) `supekku/cli/validate.py`.
  - **Testing**: existing
    `spec_driver/orchestration/templates_test.py::TestValidateTemplates`
    coverage still applies through the new entrypoint; smoke that
    `spec-driver validate templates` invokes the same code path
    (VT-CC-003 already verified P02; re-confirm via the new path).
  - **Observations & AI Notes**: keep the move minimal — no
    semantic changes to the templates command itself.
  - **Commits / References**: bundles with 3.7.

- **3.7 `supekku/cli/main.py` rewiring**
  - **Design / Approach**: In
    `supekku/cli/main.py`:
    - Remove `app.command("validate", ...)(workspace.validate)`.
    - Remove `app.command("validate-templates",
      ...)(validate.templates_cmd)`.
    - Remove the now-unused `validate` import (the
      `supekku/cli/validate.py` module).
    - Add `from spec_driver.presentation.cli.validate import app
      as validate_app` (alias to avoid name clash with the deleted
      `validate` module import).
    - Add `app.add_typer(validate_app, name="validate", help="…")`.
    Atomically with 3.6 — both land in the same commit so the CLI
    surface flips in one step.
  - **Files / Components**: `supekku/cli/main.py`.
  - **Testing**: existing
    `supekku/cli/test_cli.py:51,96,284` (`validate --help` callers)
    still resolve; CliRunner smoke that `spec-driver validate
    --help` lists workspace/file/templates.
  - **Observations & AI Notes**: bare `spec-driver validate` now
    exits 2 instead of running workspace validation. Document in
    notes as a public CLI contract change (F-32). VT-CC-032 covers.
  - **Commits / References**: `feat(DE-137): validate group +
    main.py rewiring (IP-137-P03 task 3.6/3.7)`.

- **3.8 `validate workspace --fix` consumer**
  - **Design / Approach**: In `validate workspace` codepath, when
    `--fix` is set, for each diagnostic with `fix_kind ==
    'rename_key'`: read the source file via
    `dump_markdown_file_update`'s preamble (or a small
    `frontmatter_writer` helper) — extract frontmatter dict, rename
    `alias_key` ⇒ `canonical_key`, re-emit via
    `dump_markdown_file_update`. For `fix_kind == 'rewrite_value'`:
    same read path; replace the field's value with `fix_hint`. For
    any other `fix_kind`: log a warning ("--fix doesn't know how to
    apply <fix_kind>") and skip. Idempotency: post-rewrite, re-run
    the validator on the rewritten file; assert no diagnostics
    remain (VT-CC-014).
  - **Files / Components**:
    `spec_driver/presentation/cli/validate/workspace.py`; may
    extract a small `_fix.py` helper if the apply-loop grows beyond
    ~30 lines.
  - **Testing**: VT-CC-014 (idempotency on a key-rename + value-rewrite
    corpus).
  - **Observations & AI Notes**: P02 hand-off note flagged
    comment-extraction MVP is single-line scalars. The keys this
    phase rewrites (`annotation`/`nature`, `status` values) ARE all
    single-line scalars in current artefacts; multi-line scalar
    edge cases don't surface for P03's rewrite set. Document the
    accepted trade-off in notes.
  - **Commits / References**: bundles with 3.4.

- **3.9 `schema enums` CLI**
  - **Design / Approach**: NEW
    `spec_driver/presentation/cli/schema/__init__.py` (Typer group
    skeleton) + `spec_driver/presentation/cli/schema/enums.py`
    (subcommand body). Subcommand signature: `enums(target: str |
    None = None)` where target is `""` | `"<kind>"` | `"<kind>.<field>"`.
    Three branches:
    - `target is None`: list every kind whose `BlockMetadata`
      contains ≥1 field with `enum_values` ≠ `()` (Rich table:
      kind name, count of controlled-vocab fields).
    - `target == "<kind>"`: for that kind, table of every
      controlled-vocab field with its canonical values + alias
      count.
    - `target == "<kind>.<field>"`: full output per DR-137 §5.3
      shape (canonical values block; permanent aliases block with
      `alias -> canonical` lines; tolerated aliases block with
      sunset annotations).
    Wired in `supekku/cli/main.py` as a top-level `schema` Typer
    group:
    ```python
    from spec_driver.presentation.cli.schema import app as schema_app
    app.add_typer(schema_app, name="schema", help="…")
    ```
    Coexistence with `show schema` / `list schema`: the existing
    surface stays — both are subcommands within `show` and `list`
    groups, not under a top-level `schema` group. Confirm via
    CliRunner smoke that `spec-driver show schema <id>` and
    `spec-driver list schema` continue to work.
  - **Files / Components**: NEW
    `spec_driver/presentation/cli/schema/__init__.py`,
    `spec_driver/presentation/cli/schema/enums.py`; NEW
    `tests/spec_driver/presentation/cli/schema/enums_test.py`;
    `supekku/cli/main.py` (group registration).
  - **Testing**: VT-CC-015 (output-shape parity for three branches);
    VA-CC-001 (parametric sweep over every Category A controlled-vocab
    field — pytest parameterised over a list generated from
    `FRONTMATTER_METADATA_REGISTRY`).
  - **Observations & AI Notes**: STD-001 — Typer + Rich tables.
    POL-001 — reads `FRONTMATTER_METADATA_REGISTRY` directly (single
    source of truth; no parallel enum dict). If a top-level `schema`
    group collides with an existing top-level command, fall back to
    `spec-driver schema-enums` (hyphenated) and file a follow-up.
  - **Commits / References**: `feat(DE-137): schema enums CLI
    (IP-137-P03 task 3.9)`.

- **3.10 VT-CC-032 group-level exit-code contract**
  - **Design / Approach**: One pytest module covering the F-46
    uniform exit-code matrix across all three validate subcommands.
    Bare `validate` ⇒ 2 (via Typer's `no_args_is_help=True` default).
    `validate workspace` on clean corpus ⇒ 0; on corpus with
    error-severity ⇒ 1; with invalid flag ⇒ 2.
    `validate file <missing>` ⇒ 2; `<binary>` ⇒ 2; `<no-frontmatter>`
    ⇒ 0; `<clean>` ⇒ 0; `<error-severity>` ⇒ 1.
    `validate templates` clean ⇒ 0; drift ⇒ 1.
  - **Files / Components**: NEW
    `tests/spec_driver/presentation/cli/validate/group_test.py`.
  - **Testing**: this is the test.
  - **Observations & AI Notes**: this VT is the contract gate for
    F-46. If any cell of the matrix fails, the gate fails — no
    "exit code is close enough" allowances.
  - **Commits / References**: bundles with 3.4/3.5/3.6/3.7.

- **3.11 VT-CC-026 ISSUE-054 regression**
  - **Design / Approach**: Fixture workspace at
    `tests/fixtures/de_137/issue_054/` with a delta artefact whose
    frontmatter contains malformed YAML (tag-like syntax or
    unbalanced quoting that the loader rejects with a marked
    error). CliRunner: `spec-driver list deltas --root <fixture>`.
    Assertions:
    1. Exit code non-zero.
    2. stdout-or-stderr matches regex
       `\.spec-driver/deltas/[^:]+:\d+:\d+: parse-error:`.
    3. stdout-or-stderr does NOT match `Traceback \(most recent
       call last\):`.
    4. stdout-or-stderr does NOT contain Rich panel-border chars
       (`│└┘─╭╮╰╯`).
  - **Files / Components**: NEW
    `tests/fixtures/de_137/issue_054/` (workspace skeleton + bad
    delta); NEW
    `tests/supekku/cli/list_deltas_yaml_error_test.py`.
  - **Testing**: this is the test.
  - **Observations & AI Notes**: this VT either closes ISSUE-054
    alongside DE-137 (pass) or files a follow-up (fail). DR-137
    §5.4 explicitly decouples ISSUE-054 closure from `validate file`
    landing; failure here does NOT block phase exit.
  - **Commits / References**: `test(DE-137): VT-CC-026 ISSUE-054
    regression (IP-137-P03 task 3.11)`.

- **3.12 Live ripple migration**
  - **Design / Approach**: Mechanical edits per the audit (task 3.1):
    1. `supekku/about/lifecycle.md:118` —
       `uv run spec-driver validate --sync` ⇒
       `uv run spec-driver validate workspace --sync`.
    2. `.spec-driver/product/PROD-010/PROD-010.md:1022` —
       `spec-driver validate --strict` ⇒
       `spec-driver validate workspace --strict`.
    3. `.spec-driver/tech/SPEC-110/SPEC-110.md:439` — same.
    4. `Justfile:39-40` — `validate:` recipe ⇒
       `uv run spec-driver validate workspace`.
    5. `Justfile:42-43` — `validate-templates:` recipe ⇒
       `uv run spec-driver validate templates`.
    6. `supekku/skills/audit-change/SKILL.md:64` —
       `uv run spec-driver validate` ⇒
       `uv run spec-driver validate workspace`.
    7. `supekku/skills/close-change/SKILL.md:36` — same.
    Frozen files (DR-137 §5.4 list — DR-136, prior DRs, completed
    phase sheets, audit findings) NOT touched. The §10 Supersedes
    block in DR-136 remains the reconciliation surface for the old
    wording.
  - **Files / Components**: per list above.
  - **Testing**: post-edit `just validate` and
    `just validate-templates` execute the renamed targets cleanly.
  - **Observations & AI Notes**: P05 will further amend the skill
    files with verbatim insertions (DR-137 §5.5); 3.12 migrates
    only the pre-existing bare-form references. The two ripples
    don't conflict — P05's inserts use the explicit subcommand
    form from day one.
  - **Commits / References**: `docs(DE-137): migrate validate CLI
    ripple sites (IP-137-P03 task 3.12)`.

- **3.13 Confirm zero stale bare-form references**
  - **Design / Approach**:
    `rg -n 'spec-driver validate(\s|$|--)' --type-add 'md:*.md'
    --type md,py,just` after 3.12. Acceptable matches:
    - `spec-driver validate workspace` / `validate file` /
      `validate templates`
    - References in frozen audit-trail files (DR-136, prior phase
      sheets, AUD-* files, this delta's own `notes.md` entries from
      previous phases)
    - Test fixtures whose subject is the bare-form contract (e.g.
      VT-CC-032's bare-form exit-2 assertion).
    All other matches must migrate. Update notes with the final
    grep output.
  - **Files / Components**: read-only.
  - **Testing**: this is the gate.
  - **Observations & AI Notes**: F-11/F-12 closure gate.
  - **Commits / References**: bundles with 3.15.

- **3.14 Acceptance gate**
  - **Design / Approach**: `just check`. Address every failure
    (test, ruff, format, pylint ratchet). For pylint, regression on
    touched files blocks per CLAUDE.md. Out-of-scope regressions
    left as-is.
  - **Files / Components**: as needed.
  - **Testing**: this is the verification gate.
  - **Observations & AI Notes**: new CLI modules
    (`presentation/cli/{validate,schema}/...`, `constants.py`) are
    this phase's responsibility for lint. Pylint score should hold
    at ≥ baseline 9.69.
  - **Commits / References**: cleanups separate from feature
    commits where practical.

- **3.15 Phase wrap-up**
  - **Design / Approach**: Update `notes.md` with VT pass table,
    ripple inventory before/after, ISSUE-054 disposition
    (VT-CC-026 pass/fail), Justfile recipe diff, DEC-137-21
    diagnostic format examples, and a hand-off note for P04
    (migrations framework needs `MIGRATION_FOLDER_PATTERN`,
    `MIGRATION_LOG_PATH`, `MIGRATION_LOCK_PATH` from
    `presentation/cli/constants.py` — already shipped). Check
    IP-137 §9 progress box for P03. Commit phase as
    `docs(DE-137): IP-137-P03 wrap-up (tasks 3.13-3.15)`.
  - **Files / Components**: `notes.md`, `IP-137.md`,
    `phases/phase-03.md`.
  - **Testing**: n/a (paperwork).
  - **Observations & AI Notes**: phase-04 sheet is NOT scaffolded
    here. `/plan-phases` runs at P03 close.
  - **Commits / References**: final phase commit.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Loader cannot cleanly filter by `--kind` at load time; F-8 sweep procedure simplifies to "load full, then filter results" | Document deviation in notes; VT-CC-017/025 still pass under the simpler variant; F-8's reproducibility guarantee remains intact | open |
| Top-level `schema` Typer group collides with existing `show schema` / `list schema` surface | Existing surface lives inside `show` / `list` groups (subcommands), not at top level — no name clash expected. If collision surfaces, fall back to `spec-driver schema-enums` hyphenated and file follow-up | open |
| `--fix` rewrite path loses comments on a single-line scalar (regression vs P02 contract) | VT-CC-014 explicitly asserts comment survival post-rewrite via round-trip diff on a fixture with `key: value  # legacy hint` | open |
| Bare `spec-driver validate` exits 0 (Typer's `no_args_is_help` default behaviour) instead of 2 | VT-CC-032 asserts exit 2; if Typer defaults to 0, add an explicit callback raising `typer.Exit(2)` (documented Typer pattern) | open |
| Public CLI contract change (bare `validate` no longer runs workspace validation) breaks downstream scripts | F-32 documented change; notes hand-off + ripple migration cover internal callers; external scripts will see exit 2 (non-zero, still handle-able) | open |
| VT-CC-026 fails ⇒ ISSUE-054 regression detected | DR-137 §5.4 decouples — file follow-up; do NOT block phase exit; `validate file` ships on its own merit | open |
| `MetadataValidator.validate(...)` doesn't expose `fix_hint`/`fix_kind` exactly as P01 contract claims | Pre-flight check at task 3.8 start: read `validator.py` and confirm contract; if mismatch, `/consult` rather than retrofit | open |
| Existing test references to `validate --help` (`supekku/cli/test_cli.py:51,96,284`) break under group | Typer groups expose `--help`; minimal breakage expected per P02 hand-off note; if asserts on specific help-text strings fail, update them as part of this phase | open |

## 9. Decisions & Outcomes

- `2026-05-18` — P03 sheet drafted at IP-137-P02 close. Inherits
  DR-137 v3.1 decisions DEC-137-17 (bare validate ⇒ help),
  DEC-137-20 (closest_match cutoff 0.6), DEC-137-21 (dotted-path
  diagnostic format), F-46 (uniform exit-code contract). No new
  decisions yet; the phase rides on the DR verbatim.

## 10. Findings / Research Notes

- Pre-flight ripple inventory (task 3.1) to be captured here.
- VT-CC-026 disposition (ISSUE-054 closure vs follow-up) to be
  recorded at task 3.11/3.15.
- Loader `--kind` filter feasibility (task 3.4) recorded here if a
  deviation from F-8 §1 is taken.
- Top-level `schema` group placement decision (task 3.9) recorded
  here if the existing `show schema` / `list schema` surface needs
  any adjustment.

## 11. Wrap-up Checklist

- [x] Exit criteria (all bullets in §4) satisfied
- [x] Verification evidence stored in `notes.md` (VT pass status;
  ripple before/after grep; CliRunner snippets; ISSUE-054
  disposition; DEC-137-21 examples)
- [x] IP-137 §9 progress box for P03 checked
- [x] Hand-off note in `notes.md` summarising any new constraints for
  IP-137-P04 (migrations framework + workflow.toml + import-linter)
