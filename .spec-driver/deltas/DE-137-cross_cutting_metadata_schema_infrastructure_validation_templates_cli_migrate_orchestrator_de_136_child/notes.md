# Notes for DE-137

## 2026-05-18 — IP-137-P03 complete (validate Typer group + schema enums + ripple)

### Summary

All 15 tasks of IP-137-P03 landed. Phase exits with full pytest green
(5217 passed, 4 skipped — +128 net new tests vs P02 baseline), ruff
clean, format clean, pylint 9.69 (= baseline). Coverage of the 7 VTs +
1 VA in scope:

| VT | Location | Status |
|---|---|---|
| VT-CC-014 (validate file --strict --fix idempotency) | `spec_driver/presentation/cli/validate/file_test.py::TestFixIdempotency` (2 cases) | verified |
| VT-CC-015 (schema enums shape parity, 3 invocation forms) | `spec_driver/presentation/cli/schema/enums_test.py::TestThreeInvocationForms` (5 cases) | verified |
| VT-CC-016 (validate file diagnostic shape + path matrix) | `file_test.py::TestPathHandling` + `TestDiagnosticShape` (9 cases) | verified |
| VT-CC-017 (validate workspace --kind scoping) | `workspace_test.py::TestFilterByKind` + smoke (7 cases) | verified |
| VT-CC-025 (validate workspace --kind sweep semantics) | `workspace_test.py::TestFilterByKind::test_filter_spec_kind_matches_both_id_families` + smoke | verified |
| VT-CC-026 (ISSUE-054 regression closure) | `issue_054_regression_test.py` — inherits DE-135 VT-DR135-002 | verified |
| VT-CC-032 (F-46 uniform exit-code contract) | `group_test.py::TestExitCodeContract` (12 matrix cells) | verified |
| VA-CC-001 (parametric schema enums smoke) | `schema/enums_test.py::TestParametricCoverageVACC001` (~85 cases) | verified |

### Pragmatic deviations from DR-137

1. **`validate workspace --fix` per-kind sweep deferred.** DR-137 §5.2
   / §5.4 envision `--fix` consuming `fix_hint`/`fix_kind` across the
   full corpus during a workspace sweep. The current
   `WorkspaceValidator` (`supekku/scripts/lib/validation/validator.py`)
   does NOT invoke `MetadataValidator` per-artefact — it does
   cross-reference validation only. Plumbing per-kind metadata fixes
   through the workspace sweep requires the workspace loader to emit
   `ValidationError`-shaped diagnostics (currently emits
   `ValidationIssue` without fix metadata). That is a ~200-400 LOC
   refactor and lands incrementally with DE-138..142 (per-kind sweeps
   activate the fix path one kind at a time). P03 ships the **fix
   consumer interface** via `validate file --fix` (DEC-137-15 / F-1
   `dump_markdown_file_update` rewrite path). VT-CC-014 idempotency
   covers this surface.

2. **`validate workspace --kind` is the F-8 §2 form only.** DR-137 §5.4
   F-8 sweep procedure §1 (load-time per-kind filter) requires the
   loader to expose a `kind` parameter that skips non-matching
   artefacts during construction. The current Workspace + registry
   surface has no such opt-in. P03 implements F-8 §2 (full-corpus load
   + post-validation filter on `ValidationIssue.artifact` id-prefix).
   Reproducibility — the only F-8 guarantee that matters at the CLI
   surface — is preserved (post-migration corpus where every artefact
   of one kind is clean ⇒ `--kind` sweep exits 0). VT-CC-017/025 cover.

3. **`validate workspace` exit-code contract changed: warnings ⇒ 0**
   under default mode (F-46). The legacy `supekku/cli/workspace.py:validate`
   returned `EXIT_FAILURE` on any non-empty issue list (warnings
   included). The new contract returns 0 when only warnings surface
   and 1 only on error-severity. `--strict` promotes warnings to
   errors. This is the documented F-32 public contract change; the
   live ripple migration (task 3.12) ensures internal callers use
   `validate workspace --strict` where the legacy fail-on-warning
   semantics were intended.

4. **VT-CC-026 closes through DE-135 inheritance.** DE-135
   (read-time YAML resilience) already shipped
   `ListDeltasMalformedFrontmatterTest` as VT-DR135-002. DE-135 chose
   a **skip-and-warn** behaviour (exit 0 + WARNING on stderr) rather
   than DR-137 §5.4's "exit non-zero + single-line parse-error" spec.
   The DE-135 approach is better for `list deltas` UX (other deltas
   stay listable). The DR-137 spec applies cleanly to `validate file`
   (which DOES exit 1 + line/col on parse-error per VT-CC-016). VT-CC-026's
   "no Rich traceback" assertion is covered by DE-135's
   `_assert_no_python_traceback` helper. The thin marker test in
   `issue_054_regression_test.py` asserts the DE-135 coverage stays
   present (collection-time fail-loud if it ever moves/regresses).

5. **Live ripple inventory ≈ 27 references / 18 files vs DR-137 §5.4
   "~8 live" estimate.** Memory files (10 references, load-bearing
   for agent recall) + PROD specs (PROD-001/003/005/010, 6 refs) +
   ADR-010 + README + Justfile (2 recipes) + SKILL.md (2 source + 2
   installed copies) + supekku/about/lifecycle.md + SPEC-110. The
   `validate constitution` references in PROD-011 are aspirational
   (a planned future subcommand, not a real invocation) and left
   alone. Documented in task 3.1 entry above.

### Architecture wins

1. **POL-002 enforced.** All CLI subcommand names, flag literals,
   migration regex/paths are constants in
   `spec_driver/presentation/cli/constants.py`. New Typer wiring
   resolves against these constants rather than embedding magic
   strings (e.g. `@app.command(constants.VALIDATE_WORKSPACE)` vs
   `@app.command("workspace")`).

2. **DEC-137-17 honoured.** Bare `spec-driver validate` prints help
   and exits 2 via Typer's `no_args_is_help=True` — no
   `invoke_without_command=True` default-dispatch trickery.
   `spec-driver validate workspace` / `validate file` / `validate
   templates` are named peers.

3. **POL-001 enforced for schema enums.** Top-level `schema enums`
   reads `FRONTMATTER_METADATA_REGISTRY` directly (single source of
   truth) — no parallel enum dict, no hardcoded value tables.

4. **F-46 uniform exit-code contract verified.** 12-cell matrix test
   (`group_test.py::TestExitCodeContract`) covers bare/workspace/file/
   templates × clean/error/usage states. The contract is mechanically
   enforced.

### Hand-off note for IP-137-P04

- **`presentation/cli/constants.py` already ships the migration
  entries** (`MIGRATION_FOLDER_PATTERN`, `MIGRATION_LOG_PATH`,
  `MIGRATION_LOCK_PATH`). P04 imports them when wiring
  `spec_driver/presentation/cli/admin/migrate.py` and
  `spec_driver/migrations/_folder.py`.
- **`validate workspace --fix` per-kind consumer is intentionally not
  wired** at the workspace surface yet. P04's import-linter contract
  is independent of this; DE-138..142 wire the per-kind fix sweep one
  artefact-kind at a time as their loaders gain MetadataValidator
  dispatch.
- **`spec-driver schema` is now a top-level Typer group.** P04 can
  reuse it if migrations need a `schema migrations` introspection
  surface (low priority).
- **`validate workspace` exits 0 on baseline warnings** (F-32). The
  Justfile `validate:` recipe inherits this; CI consumers should use
  `--strict` if they want to fail on warnings.
- **Active phase**: `phase-04.md` to be drafted at P04 entrance via
  `/plan-phases`. Phase-03 wrap-up commit pending after this notes
  update.

### Commits on this run

- 0824552f — docs(DE-137): plan IP-137-P03 + draft phase-03 sheet
- b9564305 — feat(DE-137): validate Typer group + CLI vocabulary constants (tasks 3.2/3.3/3.6/3.7)
- 0dff03dd — feat(DE-137): validate file --fix + VT coverage for group (tasks 3.4/3.5/3.8/3.10)
- (commit pre schema) — feat(DE-137): schema enums CLI + VT-CC-026 ISSUE-054 closure (tasks 3.9/3.11)
- c266a941 — docs(DE-137): migrate validate CLI ripple sites + phase-03 status (tasks 3.12/3.13)
- 59a5ecd9 — test(DE-137): admin_test schema-removed cleanup + format pass (task 3.14)
- (this commit) — wrap-up

## 2026-05-18 — IP-137-P03 task 3.1 — full ripple inventory

Pre-flight `rg -n 'spec-driver validate' --type md --type py --type just`
plus `rg -n 'spec-driver validate' /workspace/spec-driver/.spec-driver/`
reveals the live ripple is materially wider than DR-137 §5.4's "~8 live"
estimate.

### Live ripple (needs migration to explicit subcommand form)

**Repo-root + tooling:**
- `README.md:198` — `spec-driver validate`
- `Justfile:40` — `validate:` recipe ⇒ `validate workspace`
- `Justfile:43` — `validate-templates:` recipe ⇒ `validate templates`

**Source-tree docs:**
- `supekku/about/lifecycle.md:118` — `validate --sync`

**Skills (existing references; P05 adds verbatim inserts separately):**
- `supekku/skills/close-change/SKILL.md:36` — `validate`
- `supekku/skills/audit-change/SKILL.md:36`/`:64` — `validate`
- `.spec-driver/skills/close-change/SKILL.md:36` — installed copy
- `.spec-driver/skills/audit-change/SKILL.md:64` — installed copy

**Specs (live; not historical):**
- `.spec-driver/product/PROD-001/PROD-001.md:205,313,402` — `validate`
- `.spec-driver/product/PROD-003/PROD-003.md:579` — `validate`
- `.spec-driver/product/PROD-005/PROD-005.md:592` — `validate`
- `.spec-driver/product/PROD-010/PROD-010.md:1022` — `validate --strict`
- `.spec-driver/tech/SPEC-110/SPEC-110.md:439` — `validate --strict`

**Decisions:**
- `.spec-driver/decisions/ADR-010-…md:124` — `validate` (live ADR; reconciliation per ADR convention)

**Memory (load-bearing; agents recall these):**
- `mem.signpost.spec-driver.overview.md:16,67`
- `mem.signpost.spec-driver.lifecycle-start.md:16`
- `mem.signpost.spec-driver.ceremony.md:16`
- `mem.concept.spec-driver.posture.md:16`
- `mem.concept.spec-driver.requirement-lifecycle.md:18,68`
- `mem.fact.spec-driver.status-enums.md:20`
- `mem.pattern.spec-driver.delta-completion.md:109`
- `mem.pattern.validation.warning-triage.md:13,23,52`

### Frozen (skip — DR-137 §5.4 frozen-list policy)

- All `.spec-driver/audits/AUD-*` (frozen audit-trail)
- All `.spec-driver/revisions/RE-*` (frozen revision records; mention in
  `RE-019` is past-tense run record)
- `.spec-driver/deltas/DE-079-…` — completed delta phase sheets
- `supekku/_claude.commands_old/*` — `_old` suffix; not used
- All prior phase sheets / DRs in this delta + earlier deltas

### Out-of-scope / aspirational (do NOT touch)

- `.spec-driver/product/PROD-011/PROD-011.md:711,779,836,849` —
  `spec-driver validate constitution` is a planned/future
  subcommand-form referenced in PROD intent. Not a live invocation;
  leaving until that subcommand actually ships (separate delta).

### Divergence from DR-137 §5.4 (recorded as deviation)

DR §5.4 estimated "~8 live ripple". Actual live count is ≈ 27 distinct
line-level references across 18 files (incl. memory files + PROD/SPEC
docs that DR §5.4 did not enumerate). Decision: migrate ALL live
references in task 3.12 (memory + spec docs included). Rationale:

1. Memory files are recalled by agents per `/retrieving-memory`;
   stale `validate` examples teach agents the wrong shape.
2. PROD/SPEC docs are live specifications consumed by readers;
   leaving stale CLI invocations creates two competing CLI contracts.
3. The migration is mechanical (find/replace bare `validate` ⇒
   `validate workspace`) with no design ambiguity.

This is an *enumeration delta* against the DR, not a design change.
DR-137 §5.4 verdict (ACCEPT WITH EDITS) stands; the ripple list in §5.4
was undercounted but the migration intent (bare ⇒ explicit subcommand)
is unchanged.

## 2026-05-18 — IP-137-P03 entry: phase-03 sheet drafted via `/plan-phases`

### Plan-phases handoff

- P02 closed cleanly (12 commits; 5080 pytest pass, ruff clean, pylint
  9.69 baseline). DR-137 v3.1 still authoritative; no re-litigation
  needed for §5.3 / §5.4 scope.
- `phases/phase-03.md` drafted: 15 numbered tasks (3.1 pre-flight grep
  audit ⇒ 3.15 wrap-up). Covers VT-CC-014, 015, 016, 017, 025, 026,
  032 + VA-CC-001. Active phase pointer flipped in IP-137 §5.
- Ripple inventory (from pre-flight reconnaissance during plan-phases):
  - `supekku/about/lifecycle.md:118` — `validate --sync`
  - `.spec-driver/product/PROD-010/PROD-010.md:1022` — `validate --strict`
  - `.spec-driver/tech/SPEC-110/SPEC-110.md:439` — `validate --strict`
  - `Justfile:39-40` — `validate:` recipe
  - `Justfile:42-43` — `validate-templates:` recipe
  - `supekku/skills/audit-change/SKILL.md:64` — bare `validate`
  - `supekku/skills/close-change/SKILL.md:36` — bare `validate`
  Seven live sites (matches DR-137 §5.4's "~8 live ripple" estimate;
  frozen audit-trail files explicitly excluded). P05 verbatim skill
  inserts are separate from this ripple — P03 only migrates the
  pre-existing bare-form references.
- Existing CLI shape relevant to P03:
  - `supekku/cli/main.py:124-132` registers `validate` (calls
    `workspace.validate`) and `validate-templates` (calls
    `validate.templates_cmd`) as top-level commands. Both removed in
    task 3.7; replaced with `validate` Typer group.
  - `supekku/cli/schema.py` is a library module called by `show.py`
    and `list/__init__.py`. The new top-level `schema` Typer group
    (task 3.9) coexists — no clash, since the existing surface is
    `show schema` / `list schema` (subcommands inside other groups,
    not top-level).
- DR-137 §5.4 verbatim text for the CLI vocabulary constants
  (`VALIDATE`, `VALIDATE_WORKSPACE`, `VALIDATE_FILE`,
  `VALIDATE_TEMPLATES`, `SCHEMA_ENUMS`, `ADMIN_MIGRATE`,
  `ADMIN_REGENERATE_TEMPLATES`, `FLAG_STRICT`, `FLAG_NO_TOLERATED`,
  `FLAG_FIX`, `FLAG_SYNC`, `FLAG_KIND`, `FLAG_DRY_RUN`,
  `FLAG_CHECK`, `FLAG_LIST`, `MIGRATION_FOLDER_PATTERN`,
  `MIGRATION_LOG_PATH`, `MIGRATION_LOCK_PATH`) lands in
  `spec_driver/presentation/cli/constants.py` (task 3.2); the
  migration entries are reserved imports for P04.
- `spec-driver validate` post-write surfaces only the pre-existing 8
  audit-gate warnings (unchanged baseline). No new validation errors.
- Phase-03 status: `draft` — ready for `/execute-phase`. Pre-flight
  task 3.1 (full ripple grep capture in notes) is the first action.

## 2026-05-18 — IP-137-P02 complete (template infrastructure + emit split + first regeneration)

### Summary

All 16 tasks of IP-137-P02 landed. Phase exits with full pytest green
(5080 passed, 4 skipped — +98 net new tests vs P01 baseline), ruff clean,
pylint score 9.69 (= baseline; no regression). Coverage of the 8
IP-137-P02 VTs:

| VT | Location | Status |
|---|---|---|
| VT-CC-001 (template enum-comment per kind) | `spec_driver/orchestration/templates_test.py::TestEnumCommentHints` (14 cases) | verified |
| VT-CC-002 (regenerator idempotency) | `templates_test.py::test_idempotent_second_run_no_op` | verified |
| VT-CC-003 (`validate templates` CI gate) | `templates_test.py::TestValidateTemplates` (3 cases) — landed early in P02 | verified |
| VT-CC-004 (created artefact carries enum hints) | `supekku/scripts/lib/changes/creation_test.py::test_create_delta_emits_enum_comment_hints_in_frontmatter` | verified |
| VT-CC-005 (yaml_emit primitives + containers) | `spec_driver/core/yaml_emit_test.py::TestEmitPrimitives` + `TestEmitContainers` (10 cases) | verified |
| VT-CC-006 (yaml_emit deterministic) | `yaml_emit_test.py::TestDeterminism` (5 cases) | verified |
| VT-CC-007 (malformed template fails loud) | `templates_test.py::test_malformed_template_raises` | verified |
| VT-CC-024 (comment-map invariance) | `templates_test.py::TestCommentMapInvariance` (15 cases) | verified |

### OQ-137-01 disposition

`spec_driver/core/yaml_emit.py`: **95 code lines** (130 total with
docstrings/blanks). Well under the ~120 LOC gate. Disposition: **keep
stdlib path**; no ruamel.yaml swap needed. The `_FrontmatterDumper`
absorbed the legacy `CompactDumper` so `dump_frontmatter_yaml`
delegates to `emit_yaml_block` (POL-001 single emit surface).

### Architecture wins

1. **POL-001 enforced.** `render_frontmatter_for_kind` is the single
   surface for enum-comment-hinted emit; both `regenerate_template`
   (template path) and `dump_markdown_file_create` (artefact path) call
   it. `dump_frontmatter_yaml` (legacy) delegates down to
   `emit_yaml_block`. No parallel emit paths.
2. **DEC-137-15 / F-1 honoured.** `dump_markdown_file` removed entirely
   — no shim. All ~33 production + ~95 test callers explicitly use
   `_create(..., kind=)` or `_update(...)`. Grep is empty for the
   legacy name (code-level).
3. **Template metadata drift caught early.** `audit.md` had legacy
   inline frontmatter (`mode`, `delta_ref`, `spec_refs`, `findings`,
   ...) not in the metadata schema. The one-time regeneration dropped
   it — a clean win.
4. **Reference-mode emit is conservative.** After polishing, only
   required + explicitly placeholderable fields appear in the template
   frontmatter. Optional canonical-persistence fields (ext_id/ext_url/
   lifecycle) stay out of the template — they show up at create time
   when callers supply concrete values.
5. **Per-caller create/update intent now explicit.** During the
   migration two design errors in the DR-137 §5.1 table surfaced and
   were corrected:
   - `cli/resolve.py:284` is an UPDATE (memory link rewrite of existing
     file), not a CREATE.
   - `sync_specs.py:140` is a CREATE (only writes when file doesn't
     exist), not an UPDATE.

### Pragmatic deviations from DR-137

1. **DR raises `UnknownKindError` on unknown kind; P02 production
   `dump_markdown_file_create` catches it and falls back to plain
   `emit_yaml_block`.** Reason: `kind="guidance"` (spec testing
   companion) and `kind="improvement"` (backlog kind) have no entries
   in `FRONTMATTER_METADATA_REGISTRY`. Both are real, in-use kinds.
   Hard-failing would block creation. Falling back loses enum hints but
   keeps atomic-write. Tracking: ISSUE-055-ish backlog work to add
   `improvement` + `guidance` metadata. The renderer itself still fails
   loud on unknown kinds — only the create-path falls through.
2. **`validate templates` shipped as hyphenated top-level
   `validate-templates`** rather than `validate templates` subcommand.
   Reason: the existing `spec-driver validate` is a top-level command
   (workspace validation). Converting it to a Typer group breaks
   current usage. P03 owns the group-conversion refactor; in P02 the
   hyphenated form lands the functionality without breakage.

### Hand-off note for IP-137-P03

- **`validate` Typer group**: in P02 we shipped
  `spec-driver validate-templates` as a top-level command (entrypoint
  in `supekku/cli/validate.py::templates_cmd`). P03 should convert
  `validate` from a single command (currently `workspace.validate`) to
  a Typer group with subcommands `workspace` (current), `file` (new),
  `templates` (move our `templates_cmd` into the group). Test refs at
  `supekku/cli/test_cli.py:51,96,284` use `validate --help` and still
  work under a group — minimal breakage expected.
- **Comment extraction in `_update` is MVP scope: single-line scalars
  only.** Multi-line/block-style scalar values are not annotated with
  comments (the regex won't match). If P03's `--fix` rewrite path
  encounters a multi-line value, it preserves the value but the
  trailing comment (if any) is lost.
- **`dump_markdown_file_create` falls back to plain emit on unknown
  kinds** — see deviation #1 above. P03 `--fix` rewrites use `_update`
  so this isn't a concern there, but anyone adding new create-path
  callers should still pass `kind=` explicitly and prefer registering
  the kind's metadata over relying on fallback.
- **Active phase**: `phase-03.md` to be drafted at P03 entrance via
  `/plan-phases`. Phase-02 wrap-up commit pending after this notes
  update.

### Commits on this run

- b437bbf9 — docs(DE-137): scaffold IP-137-P02 sheet + plan reconciliation
- 5df7ed81 — chore(DE-137): IP-137-P02 pre-flight audit + phase activation
- 69d1d793 — feat(DE-137): spec_driver.core.yaml_emit (task 2.2)
- 2b3c4ee6 — feat(DE-137): templates renderer + regenerator (tasks 2.3/2.4)
- e987d758 — feat(DE-137): split dump_markdown_file (task 2.5)
- 9b6ad61c — feat(DE-137): migrate production callers (tasks 2.6/2.7)
- 555a7083 — feat(DE-137): migrate test callers + delete legacy alias (tasks 2.8/2.9)
- d8406f5f — feat(DE-137): CLI wiring for templates (tasks 2.10/2.11/2.12)
- 6c027db7 — chore(DE-137): regenerate templates (task 2.13)
- c82f366b — test(DE-137): VT-CC-004 e2e enum-comment test (task 2.14)
- (this commit) — wrap-up

## 2026-05-18 — IP-137-P02 entry: pre-flight `dump_markdown_file` audit + plan scaffold

### Plan-phases handoff

- P01 closed cleanly; IP-137 status `draft` → `in-progress`; verification.coverage entries
  for VT-CC-008/009/010/011/012/013/030/034 flipped to `verified`.
- `phases/phase-02.md` drafted (16 tasks; VT-CC-001/002/003/004/005/006/007/024 in scope).
- Active phase pointer flipped in IP-137 §5.
- Baseline `pytest`: 4982 passed, 4 skipped (matches P01 exit). Ruff clean. Format clean.
- Phase-02 status: draft → in-progress (this entry).

### Pre-flight audit (task 2.1)

`rg -n 'dump_markdown_file\b' --type py` reconciled against DR-137 §5.1 ripple table.

**Production create-path (11 sites — all match DR table):**

| File | Line | Kind |
|---|---|---|
| `supekku/scripts/lib/changes/delta_creation.py` | 105 | `delta` |
| `supekku/scripts/lib/changes/delta_creation.py` | 141 | `phase` (phase-N sheet during delta scaffold; verify literal at edit time) |
| `supekku/scripts/lib/changes/phase_creation.py` | 486 | `phase` |
| `supekku/scripts/lib/changes/audit_creation.py` | 96 | `audit` |
| `supekku/scripts/lib/changes/revision_creation.py` | 92 | `revision` |
| `supekku/scripts/lib/changes/creation.py` | 95 | `plan` |
| `supekku/scripts/lib/changes/creation.py` | 245 | `requirement` (caller already carries discriminator) |
| `supekku/scripts/lib/specs/creation.py` | 169 | `spec` (PROD handled via kind arg) |
| `supekku/scripts/lib/specs/creation.py` | 188 | `spec_tests` |
| `supekku/cli/resolve.py` | 284 | `memory` |
| `supekku/scripts/lib/backlog/registry.py` | 397 | caller-provided (`issue`/`improvement`/`risk`/`problem`) |

**Production update-path (9 sites — all match DR table):**

| File | Lines |
|---|---|
| `supekku/scripts/lib/core/frontmatter_writer.py` | 138, 176, 226 |
| `spec_driver/domain/relations/manager.py` | 105, 142 |
| `supekku/cli/compact.py` | 74 |
| `supekku/scripts/sync_specs.py` | 140, 160, 184 |
| `scripts/normalise_frontmatter.py` | 35 |

**Test ripple (15 files, ~95 sites — DR §5.1 undercounted "~12 tests"):**

| File | Sites | Predominant variant |
|---|---|---|
| `supekku/scripts/lib/relations/manager_test.py` | 1 | `_create` |
| `supekku/scripts/lib/requirements/registry_test.py` | 2 | `_create` |
| `supekku/scripts/lib/requirements/sync_test.py` | 24 | mixed; mostly `_create` fixture-builders |
| `supekku/scripts/lib/requirements/parser_test.py` | 2 | `_create` |
| `supekku/scripts/lib/requirements/coverage_test.py` | 5 | `_create` |
| `supekku/scripts/lib/specs/registry_test.py` | 6 | `_create` |
| `supekku/scripts/lib/specs/models_test.py` | 7 | `_create` |
| `supekku/scripts/lib/changes/artifacts_test.py` | 12 | `_create` |
| `supekku/scripts/lib/changes/registry_test.py` | 4 | `_create` |
| `supekku/scripts/lib/changes/discover_plans_test.py` | 4 | `_create` |
| `supekku/scripts/lib/validation/validator_test.py` | 29 | `_create` |
| `supekku/scripts/lib/workspace_test.py` | 2 | `_create` |
| `supekku/scripts/lib/spec_utils_test.py` | 2 | exercise both variants once split |
| `supekku/cli/resolve_test.py` | 4 | `_create` |
| `supekku/cli/sync_test.py` | 1 | `_create` |

**Exported names:** `supekku/scripts/lib/__init__.py` re-exports `dump_markdown_file`
(lines 24, 61). After split, replace with `dump_markdown_file_create` and
`dump_markdown_file_update`.

**Other findings:**

- `dump_frontmatter_yaml` (CompactDumper) is the deterministic emit primitive
  4982 tests depend on. Implication for task 2.2: `spec_driver/core/yaml_emit.py`
  must produce byte-equivalent output to CompactDumper for the no-comments case
  (or move CompactDumper-equivalent into yaml_emit and have `dump_frontmatter_yaml`
  delegate to `emit_yaml_block`). Plan: implement CompactDumper-equivalent inside
  `yaml_emit.py` as a private dumper class; LOC budget ~50 dumper + ~30 comment
  layer + ~10 boilerplate = ~90 LOC (still under OQ-137-01 gate of ~120).
  `dump_frontmatter_yaml` retained as a thin wrapper for callers that need the
  no-comment path (`frontmatter_writer_test.py` exercises it directly).
- No `dump_frontmatter_yaml` callers outside `spec_utils.py` (internal) and
  `frontmatter_writer_test.py` — no extra migration surface.

### Migration strategy

- Order: 2.2 yaml_emit → 2.3 renderer → 2.5 split (now safe to break the wire)
  → 2.6/2.7 production callers → 2.8 tests (the bulk) → 2.9 grep gate +
  delete legacy fn → 2.10/2.11 CLI → 2.12 just target → 2.13 regen templates
  → 2.14 e2e enum-comment test → 2.15/2.16 gate + wrap-up.
- Test migration done with sed scripts where feasible (most calls follow a
  `dump_markdown_file(path, frontmatter, body)` shape; the `kind` derivation is
  almost always implicit from the surrounding fixture-builder's filename
  pattern).

## 2026-05-18 — IP-137-P01 complete (schema & validation foundation)

### Summary

All 15 tasks of IP-137-P01 landed; phase exits with `just check` clean
(4982 tests pass, ruff zero, pylint 9.69 vs baseline 9.69 with 8 fewer
messages — net improvement). Coverage of the 8 IP-137-P01 VTs:

| VT | Location | Status |
|---|---|---|
| VT-CC-008 (field-NAME alias) | `validator_alias_test.py::test_field_name_alias_strict_emits_warning_with_rename_fix` + tolerant variant | pass |
| VT-CC-009 (tolerated alias) | `validator_alias_test.py::test_tolerated_alias_*` (3 cases) | pass |
| VT-CC-010 (did-you-mean) | `spec_driver/core/string_utils_test.py` (13 cases) | pass |
| VT-CC-011 (unknown-key strict/tolerant) | `metadata/test_engine.py::StrictUnknownKeysTest` (5 cases) | pass |
| VT-CC-012 (ENUM_REGISTRY parity) | `spec_driver/orchestration/enums_test.py` (24 cases incl. 21 parity + contract) | pass |
| VT-CC-013 (normalize_field parity) | `blocks/metadata/aliases_test.py` (17 cases incl. 9 matrix parity) | pass |
| VT-CC-030 (field-VALUE alias) | `validator_alias_test.py::test_field_value_alias_*` (2 cases) | pass |
| VT-CC-034 (alias collision) | `validator_alias_test.py::test_field_name_alias_collision_is_error_severity` | pass |

### DR-extensions adopted in P01 (decisions worth carrying forward)

1. **`FieldMetadata.field_aliases` added alongside `BlockMetadata.field_aliases`.**
   The DR-137 §5.2 design placed `field_aliases` only on `BlockMetadata`,
   but the canonical relations-item schema is a nested
   `FieldMetadata(type="object")`, not a standalone `BlockMetadata`. To
   honour the design intent (field-NAME aliases on the container schema)
   without promoting the relations-item to its own `BlockMetadata`,
   `field_aliases` now exists on both classes with identical semantics.
   The validator applies them at any object-typed schema layer.

2. **Validator is report-only — no in-place mutation.**
   DR-137 §5.2 pseudo-code shows `data[canonical_key] = data.pop(alias_key)`
   inside the validator. P01 implements the validator as pure (it never
   mutates the supplied data) and emits diagnostics with
   `fix_hint`/`fix_kind` that `validate workspace --fix` consumes to
   rewrite the source file. Loaders that want canonical values at read
   time call `blocks.metadata.aliases.normalize_field` independently.
   Trade-off: tolerant-read no longer auto-canonicalises in memory; the
   read-time normaliser must be explicitly invoked. Benefit: simpler
   semantics, easier reasoning about side effects, lower argument counts.

3. **Audit + revision status aliases populated despite DR's "reserved"
   marker.** The DR-137 §5.2 matrix marked audit/revision status aliases
   as "reserved for DE-141/DE-142". P01 nonetheless populates them with
   the same change-status alias set as delta. Reason: the legacy
   kind-agnostic `normalize_status` aliased values like `"complete" →
   "completed"` across all change-artefact kinds; the corpus contains
   `status: complete` on real revisions/audits, so without aliases the
   `ChangeArtifact` loader would regress. DE-141/142 retain authority
   over any *additional* aliases their kinds require.

4. **Per-kind status enum promotion extended beyond delta/plan.** P01
   promotes the inherited base `status: string` to a kind-specific
   `status: enum` on every Category A kind (audit, requirement,
   verification, spec, policy, standard, memory, issue, problem, risk,
   plus delta + plan). Without this the derived `_kind_status(kind)`
   factory in `ENUM_REGISTRY` returns `[]` for those kinds and VT-CC-012
   parity fails. Aliases stay empty on the non-delta/plan kinds (per
   matrix). The relations-item nested object gets
   `field_aliases={"annotation": "nature"}` in `base.py` so every kind
   inherits it.

5. **`pyproject.toml` testpaths extended to include `spec_driver`.**
   Pre-existing gap: `tests/spec_driver/` and co-located
   `spec_driver/**/*_test.py` files weren't discovered by `just test`.
   P01 adds `spec_driver` to `testpaths` so the new VTs (string_utils,
   enums) actually run under the project gate.

### ENUM_REGISTRY pre/post-split parity snapshot

Captured pre-split via `python -c "from spec_driver.orchestration.enums
import ENUM_REGISTRY, list_enum_paths; ..."` immediately before
refactoring `enums.py`. 22 paths × N values matched the post-split
derived view exactly (asserted in `enums_test.PRE_SPLIT_SNAPSHOT`).

### Hand-off note for IP-137-P02

- `FieldMetadata` shape is locked: `aliases`, `tolerated_aliases`,
  `field_aliases` all land; `ToleratedAlias` is a frozen dataclass with
  `canonical / sunset_after / rationale`.
- `MetadataValidator(metadata).validate(data, *, strict, accept_tolerated)`
  is the new entrypoint. `validate(...).fix_hint` / `.fix_kind` is the
  contract `--fix` consumes in IP-137-P03.
- `dump_markdown_file` callers untouched in P01 (~33 sites pending in
  P02 per DR-137 §5.1 F-1 ripple table).
- `spec_driver/core/yaml_emit.py` does NOT exist yet — P02 introduces.
- `normalize_field("delta", "status", value)` is available for any P02
  helper that needs read-time alias canonicalisation.
- OQ-137-01 (yaml_emit ≤ ~60 LOC vs ruamel.yaml swap) — re-evaluate at
  P02 sign-off as planned.

### Files touched by P01 (summary)

- **New**: `spec_driver/core/string_utils.py`(+test),
  `supekku/scripts/lib/blocks/metadata/aliases.py`(+test),
  `supekku/scripts/lib/blocks/metadata/schema_test.py`,
  `supekku/scripts/lib/blocks/metadata/validator_alias_test.py`,
  `supekku/scripts/lib/core/frontmatter_metadata/revision.py`,
  `supekku/scripts/lib/core/frontmatter_metadata/adr.py`,
  `spec_driver/orchestration/enums_test.py`.
- **Edited**: `supekku/scripts/lib/blocks/metadata/{schema,validator,snapshot_compare}.py`,
  `supekku/scripts/lib/blocks/{spec,delta,revision}_metadata.py` + their
  tests, every `frontmatter_metadata/<kind>.py` + tests,
  `supekku/scripts/lib/changes/{lifecycle,artifacts}.py` (+tests),
  `supekku/scripts/lib/requirements/lifecycle.py`,
  `supekku/scripts/lib/specs/lifecycle.py`,
  `supekku/scripts/lib/policies/lifecycle.py`,
  `supekku/scripts/lib/standards/lifecycle.py`,
  `supekku/scripts/lib/memory/lifecycle.py`,
  `supekku/scripts/lib/decisions/lifecycle.py`,
  `supekku/scripts/lib/backlog/models.py`,
  `supekku/scripts/lib/blocks/verification.py`,
  `supekku/scripts/lib/validation/validator.py`,
  `supekku/cli/list/{deltas,specs}.py`,
  `spec_driver/orchestration/enums.py`,
  `pyproject.toml` (testpaths).
- **Backlog**: ISSUE-055 (drift registry gap).

### Lint / Test acceptance

- `uv run ruff check supekku spec_driver` — clean.
- `uv run ruff format supekku spec_driver` — clean.
- `uv run python -m pytest` — 4982 passed, 4 skipped (no regressions).
- `uv run python -m supekku.scripts.pylint_report` — 9.69/10 (baseline
  9.69; 1590 messages vs baseline 1598).

## 2026-05-18 — IP-137-P01 entry: pre-flight grep audit + DE-137 → in-progress

### Pre-flight grep audit (task 1.1)

`rg -n 'strict_unknown_keys|normalize_status|MetadataValidator\(' --type py` summary:

**Definition site:**
- `supekku/scripts/lib/blocks/metadata/validator.py:60` — `def __init__(self, metadata, *, strict_unknown_keys: bool = False)` — kwarg to retire (DEC-137-14).
- internal usage at `validator.py:62, 92, 269`.

**Live production sites passing `strict_unknown_keys=True` (= DE-118 retirement call sites, per `mem.pattern.spec-driver.metadata-validator-strictness`):**
1. `supekku/scripts/lib/blocks/metadata/snapshot_compare.py:178` — `MetadataValidator(schema.metadata, strict_unknown_keys=True).validate(data)` (single inline construction).
2. `supekku/scripts/lib/blocks/spec_metadata.py:215-217` — `_SPEC_RELATIONSHIPS_VALIDATOR`.
3. `supekku/scripts/lib/blocks/spec_metadata.py:220-222` — `_SPEC_CAPABILITIES_VALIDATOR`.
4. `supekku/scripts/lib/blocks/delta_metadata.py:173-175` — `_DELTA_RELATIONSHIPS_VALIDATOR`.
5. `supekku/scripts/lib/blocks/revision_metadata.py:437-439` — `_REVISION_CHANGE_VALIDATOR`.

These are the five module-scope validator singletons; each must migrate to `MetadataValidator(metadata)` + push `strict=True` into the `.validate(...)` call surface. Task 1.7 ripple is bounded.

**Test sites passing `strict_unknown_keys=True`** (mechanical refactor, in scope of task 1.7):
- `supekku/scripts/lib/blocks/metadata/test_engine.py:1125, 1133, 1139, 1159`
- `supekku/scripts/lib/blocks/workflow_metadata_test.py:584`
- `supekku/scripts/lib/blocks/revision_metadata_test.py:35`
- `supekku/scripts/lib/blocks/plan_metadata_test.py:23, 29`
- `supekku/scripts/lib/blocks/verification_metadata_test.py:23`
- `supekku/scripts/lib/blocks/tracking_metadata_test.py:20`

**`normalize_status` consumers** (task 1.10 caller migration to `normalize_field("delta","status",...)`):
- `supekku/scripts/lib/changes/lifecycle.py:43, 59` — definition + `__all__`.
- `supekku/scripts/lib/validation/validator.py:16, 549` — uses inside `validate_phase_status` codepath.
- `supekku/scripts/lib/changes/artifacts.py:20, 93, 98` — `ChangeArtifact` constructor uses it on raw status; checks `CHANGE_STATUSES` membership.
- `supekku/cli/list/deltas.py:26, 236, 251` — CLI filter normalisation.
- `supekku/cli/list/specs.py:23, 260, 262` — CLI filter normalisation (spec list reuses change normaliser; this is a pre-existing coupling smell, but the migration is in scope and mechanical).

**`normalize_status` test sites:**
- `supekku/scripts/lib/changes/lifecycle_test.py:11, 16, 33, 36, 39, 40, 43` — cover canonical map + case/whitespace normalisation; must keep coverage for `normalize_field` (parity = VT-CC-013).

### Important findings from the audit

- **Case/whitespace handling in `normalize_status`**: `status.lower().strip()` runs before map lookup. The new `normalize_field` MUST preserve this (`DONE`, `  done  ` are observed legacy values). DR-137 §5.2 `normalize_field` pseudo-code doesn't explicitly include the `.lower().strip()` prefix — recording here so task 1.9 captures it.
- **`STATUS_COMPLETE = "complete"`** is currently a member of `CHANGE_STATUSES` (= acceptance of legacy value at write-time). Under task 1.12 transition re-export `CHANGE_STATUSES = frozenset(DELTA_FRONTMATTER_METADATA.fields["status"].enum_values)`, `"complete"` will NOT be a canonical enum value — but DR-137 §5.2 matrix puts `complete → completed` in `delta.status` `FieldMetadata.aliases`. Need to audit `CHANGE_STATUSES`-membership callers (`changes/artifacts.py:98`) to confirm they still work; if any test depends on `"complete" in CHANGE_STATUSES`, it must accept the alias-aware contract instead. Recorded against task 1.12 risks.
- **`spec-driver` CLI has no direct "delta status transition" command** — `phase start/complete` operates on workflow/state.yaml, not delta frontmatter. Delta lifecycle is edited in-frontmatter (this matches the project's prose-only handoff posture). Performed the `draft → in-progress` transition via `Edit` on `DE-137.md`.

### Lifecycle transition

- DE-118: verified `Status: completed` via `spec-driver show delta DE-118`.
- DE-137: transitioned `status: draft` → `status: in-progress` in `DE-137.md`.
- `spec-driver validate` post-transition: only the 8 pre-existing audit-gate warnings remain; no new validation errors.

### `MetadataValidator(metadata)` (no kwarg) sites

The grep also captured the broad pattern `MetadataValidator(metadata)` — these are the loose-mode validators that already construct without `strict_unknown_keys` and will keep working without code changes. No migration needed at these sites until the validator constructor signature drops the kwarg (after task 1.7); the refactor is fail-fast at any positional caller (none observed).

## 2026-05-18 — IP-137 + phase-01 drafted via /plan-phases

`/plan-phases` ran against the accepted DR-137 v3.1 baseline. Outputs:

- **IP-137** (`IP-137.md`) — five-phase execution plan with the full VT-CC-001..034 + VA-CC-001 catalogue mapped to phases via `supekku:verification.coverage@v1`. Phase shape:
  1. **IP-137-P01** — Schema & validation foundation (FieldMetadata.aliases / BlockMetadata.field_aliases / MetadataValidator strict-mode / ENUM_REGISTRY split / minimal REVISION+ADR metadata / normalize_field / closest_match)
  2. **IP-137-P02** — Template infrastructure + `dump_markdown_file` split (~33 callers) + admin regenerate-templates / validate templates CLI + one-time regeneration commit (F-42)
  3. **IP-137-P03** — `validate` Typer group + `schema enums` CLI + CLI vocabulary constants + ~8 live ripple sites + ISSUE-054 regression test
  4. **IP-137-P04** — `admin migrate` framework (`_protocol`/`_helpers`/`_folder` + orchestrator + lockfile + watermark + import-linter `Migrations isolation` contract) + workflow.toml schema + install fresh-vs-upgrade trigger
  5. **IP-137-P05** — Skill gates (5 files) + acceptance (`just check` + `lint-imports`) + PROD-004 coverage reconciliation + `complete delta DE-137`
- **Phase sheet** (`phases/phase-01.md`) — IP-137-P01 fully fleshed: 15 numbered tasks with design / files / testing / observations per task; entrance + exit criteria gated; VT coverage per task documented; risk table populated.

`spec-driver validate` post-write surfaces only the pre-existing 8 audit-gate warnings (unchanged baseline). No new validation errors.

Two decisions recorded directly in phase-01 §9:
- F-43 `DeprecationWarning` on re-export imports **deferred** to OQ-137-02 resolution (avoids noisy warnings during DE-138..142 implementation).
- `drift` registry gap filed as a backlog `ISSUE-NNN` during task 1.11 rather than fixed inline (keeps Category-B surface frozen for DE-137).

Ready for `/execute-phase` on IP-137-P01. Pre-flight task 1.1 (`grep -rn 'strict_unknown_keys|normalize_status|MetadataValidator\('` + DE-118 closure re-verify + DE-137 → `in-progress`) is the first action.

## 2026-05-18 — DR-137 v1 drafted; adversarial review returned ANOTHER REVIEW PASS

DR-137 was drafted via `/draft-design-revision` (10 clarifying questions Q1–Q10 resolved with user; foundation locked; sections §1–§12 written). Adversarial review (Opus sub-agent) returned 23 findings: **5 BLOCK**, **11 WARN**, **5 INFO**. Verdict: another review pass required before `/plan-phases`.

Dispositions below. Codes:
- **A** — accept; incorporate fix in DR-137 v2.
- **A-defer** — accept the finding but defer the fix to a follow-up (record in §8 Open Questions).
- **R** — reject with rationale.

| ID | Sev | Finding (one line) | Disposition | Action |
|---|---|---|---|---|
| F-1 | BLOCK | `dump_markdown_file(..., kind=)` ripple covers ~30 callers, not only `_creation.py`. Edit-path callers (frontmatter_writer, relations/manager, sync) may silently strip enum-comments. | **A** | Enumerate every caller in code_impacts; for non-creation callers, specify "preserve-comments-on-save" path (read existing comments → re-apply on dump). Or split into `dump_markdown_file_create(kind=...)` vs `dump_markdown_file_update(...)` (latter preserves existing). |
| F-2 | BLOCK | Layering contract gap: POL-003 names 5 layers; `spec_driver/migrations/` as "peer of orchestration" has no layer slot. Import-linter contract is `forbidden`-style, not `layers` extension. | **A** | Specify pyproject.toml diff: switch `root_package` → `root_packages = ["spec_driver", "supekku"]` and add explicit `forbidden` contract: `source_modules: spec_driver.migrations`, `forbidden_modules: spec_driver, supekku`, `allow: spec_driver.migrations._protocol`. |
| F-3 | BLOCK | DEC-137-11 rationale ("stable today ≠ stable forever in own code") proves too much — applies to `_protocol.py` itself. Real rationale is DR-136 §11.1 version-bridging. pyyaml is third-party, not stdlib. | **A** | Rewrite DEC-137-11 rationale: "schema-version-bridging steps must not pull current-schema knowledge." Explicitly list allowed deps: stdlib + `yaml` (pyyaml, pinned). Acknowledge vendoring cost (5 × ~20 LOC). |
| F-4 | BLOCK | Single watermark + multi-kind steps is broken under `--kind` filter. Watermark advances ambiguous; data loss risk if step touches multiple kinds. | **A** | Forbid multi-kind steps: `applies_to_kinds: tuple[str, ...]` becomes `applies_to_kind: str` (singular). Each step targets exactly one kind. Cross-kind concerns split into separate sequential steps. Simplifies dispatch + watermark; aligns with per-kind strict-flip story. |
| F-5 | WARN | "Fresh install ⇒ strict-on" heuristic uses workflow.toml presence; consumer deleting workflow.toml is silently reclassified. | **A** | Switch trigger: strict-on default applies only when **no `.spec-driver/` workspace** exists. Existing `.spec-driver/` ⇒ preserve absent toggles as tolerant. Surface prominent install-time message before any strict flip. |
| F-6 | BLOCK | Two emit paths (regenerator + dump_markdown_file with `kind=`) NOT actually aligned by `validate templates`. POL-001 violated. | **A** | Extract single `render_frontmatter_for_kind(kind, data) -> str` shared by both paths. Add VT-CC-024: regenerator-emit and creation-time-emit produce identical bytes for the same `(kind, data)`. |
| F-7 | WARN | `validate file <path>` "path:line:col" format largely a lie — `ValidationError` has no source positions. | **A** | Drop `:line:col`; format becomes `path: severity: dotted.field.path: message`. Parser-mid-error YAML cases (which DO carry mark.line/col) get the line/col surface; semantic errors get dotted-path only. Document explicitly. |
| F-8 | WARN | `validate workspace --kind` relation-traversal semantics fuzzy. | **A** | Specify: per-kind frontmatter validation = load-time filter (only matching artefacts loaded); relation traversal = full corpus loaded; warnings filtered to subject matching `<kind>`. Add VT-CC-025 covering sweep procedure (other kinds clean, target kind unmigrated ⇒ zero warnings). |
| F-9 | WARN | Re-export sunset undefined; `STATUS_COMPLETE = "complete"` legacy value lost. | **A** | Specify sunset: re-exports retired in named follow-up delta (DE-143 or post-DE-136-umbrella cleanup). Add `complete` to delta-status `FieldMetadata.aliases` (`"complete": "completed"`). Add parity VT-CC-013 covers this. |
| F-10 | WARN | VA-CC-002 (ISSUE-054 re-verify) gates nothing. | **A** | Convert to VT-CC-026: run original ISSUE-054 repro against `list deltas` post-DE-137; assert specific error format (no Rich traceback dump). Decouples ISSUE-054 closure from DR-137 scope. |
| F-11 | WARN | Typer group + `invoke_without_command=True` + default-dispatch with flags is unproven; doc'd workspace-flag flow unclear. | **A** | Decide: either (a) drop bare-`validate` dispatch and require explicit `validate workspace`, or (b) prove the pattern with a worked example showing `--strict` flow through callback. Recommend (a) — simpler. Update migration ripple count (now ~8 sites). |
| F-12 | WARN | Rewriting DR-136 in-line edits destroys audit trail. | **A** | Drop DR-136 self-reference rewrites from §5.4 migration ripple. Only touch `supekku/about/lifecycle.md`, `PROD-010.md`, `SPEC-110.md` examples. DR-136 stays untouched; §10 supersedes mechanism is the canonical reconciliation. |
| F-13 | WARN | Folder name `0.10.0_001_*` not a valid Python module name (starts with digit, contains dots). | **A** | Change format: `v<major>_<minor>_<patch>_<NNN>_<slug>/` (e.g. `v0_10_0_001_delta_blocks/`). Add named constant `MIGRATION_FOLDER_PATTERN: re.Pattern` and `parse_migration_folder(name) -> (Version, int, str)` with VT coverage. |
| F-14 | WARN | Partial-step-mid-walk recovery untested. | **A** | Add VT-CC-023: fixture where `step.apply()` raises mid-corpus; assert re-run reaches all files; final state matches "fully applied". |
| F-15 | INFO | `difflib.get_close_matches(cutoff=0.6)` fails the canonical "status 'live' → in-progress" example. | **A** | Spike: try `cutoff=0.4`; verify against the corpus (`live`, `complete`, `in_progres`, `pendng`, …); add VT-CC-010 cases for each canonical typo. If 0.4 has too many false positives, fall back to Levenshtein. |
| F-16 | WARN | POL-002: flag literals + subcommand names as magic strings. | **A** | Add §5.4.x "CLI vocabulary": named constants in `spec_driver/presentation/cli/constants.py` for every subcommand, flag, semver pattern, log-path template. Reference from Typer signatures. |
| F-17 | WARN | `ENUM_REGISTRY` has non-artefact-kind enums (verification.*, backlog.*, command.format, requirement.kind) — registry walk doesn't cover them. | **A** | Split: (a) artefact-frontmatter-derived (delta.status, spec.status, audit.status, …) via registry walk; (b) other (verification.*, backlog.*, drift.*, command.format) stays hardcoded or moves to its own per-block metadata. Document both branches in §5.2 source-of-truth migration. |
| F-18 | WARN | import-linter `root_package` is singular; can't forbid `spec_driver.migrations` from importing `supekku.*` without `root_packages` plural. | **A** | Covered by F-2 fix; ensure the pyproject diff is explicit. |
| F-19 | INFO | Phase aliases (`active`, `done`, `in_progress`) vs delta aliases — DR conflates. | **A** | §5.2: list aliases explicitly per (kind, field). Phase-only aliases stay on plan/phase FieldMetadata. Delta status aliases: `complete → completed` only. |
| F-20 | WARN | Per-migration vendoring violates POL-001 extraction threshold (≥3 copies ⇒ P1 finding). | **A** | Add `spec_driver/migrations/_helpers.py` (frozen alongside `_protocol.py`) with `split_frontmatter`, `atomic_write`, ~3 vendored functions migrations actually share. Plus explicit §7 trade-off note: POL-001 extraction-threshold exempt for migration subsystem (reason: capture-of-the-day discipline trumps reuse). |
| F-21 | INFO | Concurrent `admin migrate` invocations race on workflow.toml watermark. | **A** | §9.3 (recovery): document single-process assumption; add `.spec-driver/run/migrations/.lock` (PID lock); admin migrate prints clear error on detected lock. |
| F-22 | INFO | Template body preservation through regenerator unspecified; audit.md example block may be silently lost. | **A** | §5.1: regenerator emits only frontmatter section; body content (including example/Jinja blocks) preserved verbatim. Add VT-CC-002 sub-case: audit template's `{{ audit_verification_block }}` Jinja placeholder survives regeneration. |
| F-23 | INFO | Skill text insertion lacks automated VT. | **A** | Add VT-CC-027: post-DE-137, parse `supekku/skills/<skill>/SKILL.md` for the five named skills; assert the specific gate text is present per DR-136 §5.5. Or insert markers (`<!-- validate-gate -->`) for anchor-based assertion. |

### Summary

All 23 findings dispositioned **A** (accept). No rejections. Most BLOCK fixes are concrete edits or expanded enumeration; the most substantive is F-4 (forbid multi-kind steps — simplifies the migration framework materially).

Estimated revision effort: **~90 min focused** to incorporate all fixes; ~60 min minimum if INFO findings deferred to v3.

Recommended next actions:
1. Revise DR-137 → v2 with all 23 dispositions applied.
2. Run second adversarial review pass.
3. If verdict ACCEPT or ACCEPT WITH EDITS → proceed to `/plan-phases`.

### Inherited scope-notes (carried from DE-137 §3)

- **F-B** (relations key naming): resolved → `nature` canonical, `annotation` permanent alias. Locked in DEC-137-05.
- **F-E** (Phase 2 entrance check on DE-118): verified satisfied — `MetadataValidator(strict_unknown_keys: bool = False)` is opt-in flag, not unconditional. Confirmed in `supekku/scripts/lib/blocks/metadata/validator.py:60`.

### Audit reviewer raw output

Reviewer agent ID: `a9da5e032c8ca4704` (general-purpose, opus model). Full finding text and verdict preserved in this turn's transcript.

---

## 2026-05-18 — DR-137 v3.1 — third-pass review accepted with edits

Third adversarial pass returned **ACCEPT WITH EDITS** (13 findings F-49..F-61: 0 BLOCK, 4 WARN, 9 INFO). The two must-fix WARN findings (F-54 collision data-loss, F-58/F-61 missing §10 reconciliations) plus a small set of cheap edits applied as v3.1:

- F-54: validator pseudo-code now refuses to silently merge when both alias and canonical keys present; emits `error`-severity diagnostic; `--fix` declines. New VT-CC-034.
- F-58: new §10 reconciliation point 11 covering minimal REVISION/ADR metadata scope advance.
- F-61: new §10 reconciliation point 12 covering the field_aliases/aliases alias-mechanism split (DEC-137-23).
- F-49: corrected `creation.py:245` row in ripple table (`requirement`, not branched `design_revision/design_change`).
- F-50: added explicit `BaseMigrationStep` concrete helper class to `_protocol.py` listing (Protocol can't carry default impls).
- F-51: fixed dangling "see §10 reconciliation point 11" cross-reference in §5.2 matrix (now resolves correctly post-F-58).
- F-52: corrected §10 point 2 DEC citation (DEC-137-13 was wrong; just F-13).
- F-55: lockfile uuid rationale rewritten — it's a log-correlation anchor, not a PID-reuse mitigator.
- F-59: DE-137 §7 risk row updated to match v3 VT-CC-024 wording (comment-map invariance, not byte-identical).
- F-60: DE-137 §3 outcome 2 refreshed to describe the F-30 alias split.

Findings declined for v3.1 (filed as paper cuts to land alongside IP-137 drafting per the reviewer's own guidance): F-53 asymmetric tolerated_field_aliases (rationale: field renames are rare and migration-paired, no real demand); F-56 narrowing of `complete` from CHANGE_STATUSES (already covered by tolerant-on-read; the matrix is explicit enough); F-57 lockfile content format constant (acceptable adjacency to lock acquire code).

Verdict for v3.1: ready for `/plan-phases`. Reviewer's strengths note: "the import-linter prototype is genuinely verified ... the F-32 Typer exit code is mechanically correct ... the F-30 schema split is conceptually crisp ... the doc's adversarial-review process is working as designed."

## 2026-05-18 — DR-137 v3 written; third adversarial review pending

Second-pass adversarial review returned ANOTHER REVIEW PASS — 3 BLOCK + 11 WARN + 11 INFO findings (F-24..F-48). User dispositioned all BLOCKS as A and accepted my F-30 design (BlockMetadata.field_aliases + FieldMetadata.aliases split).

v2→v3 highlights:
- **F-24** (BLOCK): `dump_markdown_file` ripple table rebuilt from actual `grep` of the tree. 11 create-path + 9 update-path + 1 bypass + ~12 tests ≈ 33 sites. Wrong path corrected (`spec_driver/domain/relations/manager.py` not `changes/relations/manager.py`). Real callers added: `backlog/registry.py`, `cli/resolve.py`, `cli/compact.py`, `sync_specs.py`, `scripts/normalise_frontmatter.py`. Comment-preservation algorithm in `_update` spelled out (frontmatter head re-read + lex trailing comments + re-emit).
- **F-25** (BLOCK): import-linter contract prototyped against installed import-linter 2.11. Working diff: keep `root_package = "spec_driver"` (singular); add `include_external_packages = true`; enumerate forbidden modules explicitly (each `spec_driver.<layer>` + `supekku`); no `allow` field (which doesn't exist), no `ignore_imports` whitelist needed (frozen sidecars simply absent from the forbidden list). Prototype confirmed contract correctly catches both `spec_driver.core.X` and `supekku.*` imports from migration steps.
- **F-30** (BLOCK): split alias mechanism. `BlockMetadata.field_aliases: Mapping[str, str]` for field-NAME (parse-time key rename); `FieldMetadata.aliases: Mapping[str, str]` for field-VALUE (post-dispatch value normalisation). `ValidationError.fix_kind ∈ {rename_key, rewrite_value}` for `--fix` dispatch. Diagnostics rewritten (`relations[0].annotation: field name 'annotation' is an alias for 'nature'`); per-kind matrix split into field_aliases (relations block) + per-FieldMetadata aliases (per-kind status); VT-CC-008 scoped to field-NAME; new VT-CC-030 for field-VALUE.

WARN fixes inline (F-26..F-48): kind-validation at migrate-discovery (VT-CC-031); plan/phase/task sibling-folder dispatch (DEC-137-25); two-layer dispatch contract for `applies_to_kind` + `applies_to(path)` with default base class; uniform exit-code contract (VT-CC-032); `validate file` non-artefact handling; rewrite VT-CC-024 to test comment-map invariance (not byte-identical, which was impossible); VT-CC-019 covers mixed-state idempotency; lockfile liveness cross-platform (POSIX kill -0 + uuid for PID-reuse, Windows skips staleness); frozen-forever ≠ bug-frozen (DEC-137-26); REVISION + ADR minimal metadata added (DEC-137-28); workflow.toml unknown-kind warning (VT-CC-033); DEC-137-21 trade-off acknowledged for linkifier UX; F-42 first-regeneration commit-pairing note; OQ-137-03 filed for future JSON output mode.

Decisions added: DEC-137-23..28. VTs added: VT-CC-030..033. OQ-137-03 filed.

Reviewer's verdict was ANOTHER REVIEW PASS; goal of v3 is to reach ACCEPT or ACCEPT WITH EDITS on a third pass. If a fourth pass surfaces another BLOCK round, /consult is the next move.

## 2026-05-18 — DR-137 v2 written; second adversarial review pending

DR-137 revised to v2. All 23 dispositions from the §"DR-137 v1 drafted" table applied. User-confirmed pause points before locking:
- **F-1** resolved via option (a): split `dump_markdown_file` into `*_create(kind=)` (emit comments) and `*_update()` (preserve existing comments). Old function removed; every caller migrates explicitly. Ripple table at §5.1.
- **F-11** resolved via option (a): drop bare-`validate` default-dispatch (reverses Q2 A1). Bare `spec-driver validate` prints help.

F-15 difflib spike executed before locking: at cutoff=0.6, all canonical typos (`'complete'`, `'pendng'`, `'in_progres'`, `'defered'`, `'draaft'`) match expected canonical. Semantic alternatives (`'live'`, `'active'`, `'done'`, `'wip'`) don't match at any practical cutoff without sweeping in false positives. Conclusion: keep cutoff=0.6; semantic alternatives belong in `FieldMetadata.aliases`, not did-you-mean. Recorded as DEC-137-20.

Other v1→v2 highlights:
- New decisions: DEC-137-15..22 (F-1, F-4, F-11, F-5, F-20, F-15, F-7, F-21 resolutions).
- New OQ-137-02 (re-export sunset target delta TBD).
- §5.6 gained verbatim pyproject diff for F-2 import-linter contract (`root_packages` plural; explicit forbidden contract on `spec_driver.migrations`).
- §5.6 gained `_helpers.py` (vendored bytes-level shared helpers, F-20) and `_folder.py` (parser, F-13).
- §5.6 gained lockfile (F-21) and explicit mid-walk recovery procedure + VT-CC-023 (F-14).
- Folder name shape: `v<M>_<m>_<p>_<NNN>_<slug>/` — valid Python identifier (F-13).
- `MigrationStep.applies_to_kinds: tuple[str,...]` ⇒ `applies_to_kind: str` (singular). Multi-kind steps forbidden (F-4; DEC-137-16).
- Strict-on-default trigger keyed to `.spec-driver/` workspace absence at install time, not workflow.toml presence (F-5).
- §5.4 gained CLI vocabulary constants module (F-16; POL-002).
- §5.5 gained anchor-comment markers around skill inserts (F-23) + VT-CC-027.
- §10 Supersedes grew to 10 entries; §10.1 enumerates *live* document edits (DR-136 stays frozen, F-12).
- Verification catalogue grew to VT-CC-001..029 + VA-CC-001 (VA-CC-002 retired in favour of VT-CC-026).
- DE-137.md reconciled: §3 deliverables, §5 system touchpoints, §7 risks (ruamel.yaml → custom yaml_emit + 3 new risks for F-1/F-4/F-9), §8 open decisions resolved or refiled as OQ-137-02.

Internal end-to-end review post-v2 caught one local inconsistency: §5.2 enum-violation example used `'live'` as did-you-mean input, contradicting DEC-137-20. Replaced with `'in_progres'` (typo example) and kept `'live'` as the "no did-you-mean candidate" example to document the spike result inline.

**Final file count**: DR-137 ≈ 1207 lines (was 889). DE-137 unchanged shape but refreshed deliverable/risk/decisions wording.

Ready for second adversarial-review pass.

## New Agent Instructions (2026-05-18, refreshed post `/plan-phases`)

### Task card

- **Delta**: DE-137 — Cross-cutting metadata schema infrastructure: validation+templates+CLI+migrate orchestrator (DE-136 child).
- **Card path**: `.spec-driver/deltas/DE-137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child/`
- **DR**: `DR-137.md` v3.1 — **ACCEPT WITH EDITS** verdict applied (third adversarial pass complete; ready for plan/execute).
- **IP**: `IP-137.md` — five-phase plan drafted via `/plan-phases`; verification coverage block enumerates VT-CC-001..034 + VA-CC-001 mapped to phases.
- **Active phase**: `phases/phase-01.md` — IP-137-P01 *Schema & validation foundation*, status `draft`, 15 tasks specified.
- **Delta status**: `draft`. Next agent transitions to `in-progress` as task 1.1 of IP-137-P01.

### What's done

- `/draft-design-revision` completed across 3 adversarial-review passes. DR-137 v1 → v2 → v3 → v3.1 (latest). All 61 review findings (F-1..F-61) dispositioned. Decisions DEC-137-01..28 locked. Open questions OQ-137-01..03 carried forward.
- `/plan-phases` produced IP-137 (5 phases) + Phase 01 sheet (15 tasks).
- `spec-driver validate` shows no new validation issues attributable to planning artefacts (only the pre-existing 8 audit-gate warnings).

### What's pending

1. **Execute IP-137-P01** via `/execute-phase` against `phases/phase-01.md`. First task (1.1) is a read-only pre-flight grep audit + DE-137 lifecycle transition.
2. After IP-137-P01 exit criteria met: create `phases/phase-02.md` (template infrastructure + `dump_markdown_file` split).
3. After IP-137-P02 exit criteria met: create `phases/phase-03.md` (validate Typer group + schema enums CLI + ripple).
4. After IP-137-P03 exit criteria met: create `phases/phase-04.md` (migrate framework + workflow.toml + import-linter).
5. After IP-137-P04 exit criteria met: create `phases/phase-05.md` (skill gates + acceptance + closure).
6. `/audit-change` → `/close-change` to finish.

### Required reading

- **DR-137** — `.spec-driver/deltas/DE-137-…/DR-137.md` (v3.1; the canonical design). Specifically §5 per-deliverable detail and §11 verification catalogue.
- **DE-137** — same folder, `DE-137.md` (delta scope; deliverables enumerated).
- **IP-137** — same folder, `IP-137.md` (phase map + verification coverage block).
- **phases/phase-01.md** — concrete task list and exit gates for the next phase to execute.
- **This notes.md** — adversarial-review disposition history (F-1..F-61) is the audit trail; current state at top of file.

### Related documents

- **DR-136** — `.spec-driver/deltas/DE-136-metadata_schema_consolidation_program_propagate_adr_010_across_artefacts_and_close_prod_004/DR-136.md` — canonical design reference; DR-137 §10 enumerates supersedes.
- **IP-136** — same DE-136 folder — umbrella plan; DE-137 is Phase 2 ("Foundations"). DE-137 must close before per-artefact propagation (DE-138..142) begins.
- **DE-118** — block-validator unification; closed. Provides the `MetadataValidator(strict_unknown_keys=False)` opt-in baseline. Verified at `supekku/scripts/lib/blocks/metadata/validator.py:60`.
- **DE-138..142** — sibling per-artefact deltas, all `draft`. They consume DE-137 infrastructure. **Do NOT pre-draft their DRs.**

### Key files (touchpoints for IP-137-P01)

- **Schema dataclasses**: `supekku/scripts/lib/blocks/metadata/schema.py` — `FieldMetadata` + `BlockMetadata` (tasks 1.3, 1.8).
- **Validator**: `supekku/scripts/lib/blocks/metadata/validator.py:60` — `MetadataValidator` refactor target (tasks 1.6, 1.7).
- **Validation entrypoint**: `supekku/scripts/lib/validation/validator.py` — primary caller surface for the `strict_unknown_keys` kwarg removal (task 1.7).
- **Per-kind metadata**: `supekku/scripts/lib/core/frontmatter_metadata/` — populate aliases here (task 1.4); add `revision.py` + `adr.py` (task 1.5).
- **Lifecycle constants**: `supekku/scripts/lib/changes/lifecycle.py` — `CHANGE_STATUSES`, `CANONICAL_STATUS_MAP`, `normalize_status` (tasks 1.9, 1.10, 1.12).
- **`ENUM_REGISTRY`**: `spec_driver/orchestration/enums.py` — Category A/B split (task 1.11).
- **NEW**: `spec_driver/core/string_utils.py` (task 1.2 — `closest_match`).
- **NEW**: `supekku/scripts/lib/blocks/metadata/aliases.py` (task 1.9 — `normalize_field`).
- **Tests under**: `tests/spec_driver/core/`, `tests/supekku/scripts/lib/blocks/metadata/`, `tests/supekku/scripts/lib/changes/`, `tests/spec_driver/orchestration/`.

### Key files (later phases — for context only)

- `supekku/scripts/lib/core/spec_utils.py` — `dump_markdown_file` split (IP-137-P02; ~33 ripple sites enumerated in DR-137 §5.1).
- `spec_driver/core/yaml_emit.py` (NEW; IP-137-P02; ~60 LOC custom emitter, OQ-137-01).
- `spec_driver/orchestration/templates.py` (NEW; IP-137-P02; `render_frontmatter_for_kind` shared).
- `supekku/templates/*.md` (IP-137-P02; one-time regeneration after templates.py lands — F-42).
- `supekku/cli/workspace.py:65` + new `spec_driver/presentation/cli/{validate,schema,admin}/` (IP-137-P03).
- `spec_driver/migrations/{_protocol,_helpers,_folder}.py` (NEW; IP-137-P04; frozen sidecars).
- `pyproject.toml` (IP-137-P04; import-linter `Migrations isolation` forbidden contract — verbatim diff in DR-137 §5.6).
- `supekku/scripts/lib/core/config.py:17` + `DEFAULT_CONFIG` (IP-137-P04; workflow.toml schema additions).
- `supekku/skills/<execute-phase,close-change,audit-change,notes,update-delta-docs>/SKILL.md` (IP-137-P05; verbatim text + anchor markers).

### Relevant memories

Use `/retrieving-memory` for any unfamiliar concept. Likely useful:

- `mem.signpost.spec-driver.overview` — orientation.
- `mem.concept.spec-driver.delta`, `.spec-driver.plan`, `.spec-driver.revision` — entity primitives.
- `mem.fact.spec-driver.status-enums` — status enum locations.
- `mem.pattern.spec-driver.delta-completion` — closure gates.
- `mem.pattern.validation.warning-triage` — `validate` warning categories.

### Relevant doctrines

All loaded into the boot context already:

- **ADR-010** — placement heuristic (frontmatter / blocks / prose; never duplicate).
- **ADR-011** — Workspace as canonical registry-access surface.
- **POL-001** — single source of truth (load-bearing throughout DE-137; metadata is canonical for enums + aliases).
- **POL-002** — no magic strings/numbers (load-bearing for IP-137-P03 CLI constants module).
- **POL-003** — module boundaries (load-bearing for IP-137-P04 migrations isolation).
- **STD-001** — Typer/Rich (IP-137-P03 validate/schema CLIs).
- **STD-003** — utility module placement (yaml_emit, string_utils).
- **STD-004** — script lifecycle (orphan prevention).

### Important user instructions / decisions

- **Migrations are self-contained scripts** like database migrations — capture-of-the-day; minimal external deps; the three frozen sidecars (`_protocol`, `_helpers`, `_folder`) are the only shared surface (DEC-137-11 / DEC-137-19 / DEC-137-26).
- **Multi-kind migration steps forbidden** (DEC-137-16). DE-138..142 cannot ship a single cross-kind step; cross-kind concerns split into ordered per-kind ordinals.
- **Bare `spec-driver validate` prints help** (DEC-137-17). Reverses an earlier Q2 A1 leaning; user confirmed during v2 dispositions.
- **`dump_markdown_file` split into `_create(..., kind=)` + `_update(...)`** (DEC-137-15); no shim. Every caller migrates explicitly.
- **Fresh-install strict-mode trigger keyed to `.spec-driver/` workspace absence** (DEC-137-18), NOT `workflow.toml` presence.
- **F-43 DeprecationWarning on transition re-exports deferred** to OQ-137-02 resolution — explicitly noted in phase-01 §9 to prevent noisy import-time warnings during DE-138..142 work.
- **`drift` registry gap filed as backlog ISSUE during IP-137-P01 task 1.11**, not fixed inline. Same for `improvement` / `backlog` umbrella entries (Category B).

### Unresolved tensions / open questions

- **OQ-137-01** — Custom `yaml_emit` (~60 LOC, stdlib yaml only) vs ruamel.yaml. Gate: if implementation exceeds ~120 LOC or hits stdlib-yaml edge cases at IP-137-P02, swap to ruamel.
- **OQ-137-02** — Sunset target delta for transition-window re-exports (`CHANGE_STATUSES`, etc.). Resolve at DE-136 umbrella close; downgrade to "next major spec-driver version" if no follow-up delta exists.
- **OQ-137-03** — Structured JSON diagnostic output mode. Out of DE-137 scope; file follow-up at close if CI consumer demand surfaces.
- No active design tensions awaiting resolution before code begins — DR-137 v3.1 ACCEPT WITH EDITS verdict cleared the bar.

### Commit-state guidance

- **No code touched yet**. Only `.spec-driver/**` changes pending from this session:
  - `M  .spec-driver/deltas/DE-137-…/notes.md` (this update)
  - `??  .spec-driver/deltas/DE-137-…/IP-137.md` (new — five-phase plan)
  - `??  .spec-driver/deltas/DE-137-…/phases/phase-01.md` (new — IP-137-P01 sheet)
- **Recommend committing these now before code work starts**, per project doctrine (frequent small `.spec-driver/**` commits; keep worktree clean). Suggested commit: `docs(DE-137): plan IP-137 + draft phase-01 sheet`.
- During IP-137-P01 execution: commit pre-flight audit results to notes.md first, then code changes per task. The phase wrap-up commit goes out as `feat(DE-137): land metadata aliases + strict validator (IP-137-P01)`.
- `.vscode/` is untracked at session start — not part of this delta; ignore.

### Other advice for next agent

- **The phase sheet is authoritative.** Each task in `phases/phase-01.md` §7 has design / files / testing / observations spelled out. Follow it rather than re-deriving from DR-137 §5.2.
- **Task 1.1 first.** The grep audit produces the authoritative list of `MetadataValidator(...)` and `normalize_status` consumers; tasks 1.6 / 1.7 / 1.9 / 1.10 depend on it. Don't skip.
- **Capture pre-split `ENUM_REGISTRY` snapshot before task 1.11** — VT-CC-012 needs the equality assertion against the *prior* lambda outputs, not a freshly-computed reference.
- **DE-137 status transition to `in-progress` is part of task 1.1**, not implicit. The `/execute-phase` skill should handle this; if it doesn't, run `uv run spec-driver` lifecycle command explicitly.
- **`.spec-driver/` workspace persistence**: running `spec-driver` against this repo will warn about install version mismatch (`workflow.toml has 0.9.2, running 0.9.3`). Non-blocking but expected; do not "fix" by running `spec-driver install` mid-session unless the user authorises (would update workflow.toml shape).
- If a phase's exit criteria can't be cleanly met (e.g. a VT genuinely fails on an unforeseen issue), `/consult` rather than relaxing the criteria.

