# Notes for DE-128

## 2026-05-31 — P04 executed (tier-3 final modules)

**Status**: completed. 3 tier-3 modules (+ tests) migrated. DE-128 migration
complete — all 26 genuine core modules now in `spec_driver/core/`.

### What's done

**agent_docs:**
- `agent_docs.py` → `spec_driver/core/agent_docs.py` (verbatim — already
  relative imports).
- No test file exists (confirmed).
- Legacy shim re-exports `render_agent_docs` (phase sheet template had
  `generate_agent_docs` — corrected during implementation; actual export
  is `render_agent_docs`, consumer is `install.py:18`).

**preboot:**
- `preboot.py` → `spec_driver/core/preboot.py` (verbatim — already
  relative imports).
- `preboot_test.py` → `spec_driver/core/preboot_test.py`: imports repointed
  `supekku.scripts.lib.core.preboot` → `spec_driver.core.preboot`;
  `_SUBPROCESS_TARGET` repointed accordingly.
- Legacy test deleted; 17/17 tests pass.
- Legacy shim re-exports 9 public names.

**sync_preferences:**
- `sync_preferences.py` → `spec_driver/core/sync_preferences.py` (verbatim —
  already relative imports).
- `sync_preferences_test.py` → `spec_driver/core/sync_preferences_test.py`:
  import repointed. No `@patch` paths to update.
- Legacy test deleted. Test collection blocked by missing `tomlkit` in nix-env
  (known gap, same class as yaml/click/typer/jinja2).
- Legacy shim re-exports `persist_spec_autocreate`, `spec_autocreate_enabled`.

**P02 straggler fixed:**
- Legacy `supekku/scripts/lib/core/spec_utils_test.py` had 8
  `extract_h1_title` tests not ported to `spec_driver/core/spec_utils_test.py`
  during P02. Ported now; legacy file deleted.
- Tests can't run in nix-env (yaml missing) but structurally correct.

### Verification
- `uvx import-linter lint`: 3/3 KEPT (165 files, 545 deps)
- `uv run pytest spec_driver/core/preboot_test.py`: 17/17 passed
- `uv run pytest spec_driver/core/ -x --ignore=...` (excl. nix-env gaps):
  370 passed
- `uv run ruff check spec_driver/core/ supekku/scripts/lib/core/`: clean
- `spec-driver validate file phase-04.md`: clean
- All 3 legacy shims import OK: `preboot`, `agent_docs`, `sync_preferences`
- All 3 legacy tests deleted
- Decoupling grep: zero actual `orchestration`/`domain` imports in
  `spec_driver/core/` (only docstring false positives)
- Module count: 27 non-test modules in `spec_driver/core/`
  (26 genuine migrated + 3 original; slugify merged → string_utils)
- Legacy non-shim audit: only `artifact_view_test.py` + `enums_test.py`
  remain (out of scope, orchestration tests)

### Surprises
- Phase sheet shim template for agent_docs said `generate_agent_docs` +
  `main as agent_docs_main` — neither exists. Actual export:
  `render_agent_docs`. Corrected in implementation.
- `sync_preferences_test.py` can't collect in nix-env (missing `tomlkit`)
  — same class as all other nix-env test gaps.
- P02 straggler: `extract_h1_title` tests only at legacy path, not ported
  to core test file during P02. Fixed.

### Uncommitted
All P04 changes uncommitted (cumulative with P01-P03 uncommitted).

---

## 2026-05-31 — P03 executed (tier-2 config decoupling + templates)

**Status**: completed. 2 tier-2 modules migrated, config decoupled from
frontmatter_metadata.

### What's done

**config decoupling (DEC-128-005):**
- `load_workflow_config(repo_root, known_kinds=None)`: optional `known_kinds`
  param gates `_warn_unknown_strict_kinds`.
- `_registered_kinds()` deleted — core config has zero `frontmatter_metadata`
  references (grep-verified).
- `get_strict_map(config, known_kinds: set[str])` — requires `known_kinds`
  (single caller: `validate/file.py`).
- `validate/file.py:263` wired: passes `set(FRONTMATTER_METADATA_REGISTRY.keys())`
  (zero new imports — already had the import).

**config migration:**
- `config.py` → `spec_driver/core/config.py` (import `from .paths import
  SPEC_DRIVER_DIR` already relative).
- `config_test.py` → `spec_driver/core/config_test.py`; imports + `@patch` paths
  repointed; strict-kind tests updated to pass `known_kinds`.
- Legacy shim at `supekku/scripts/lib/core/config.py` re-exports 6 public names.

**templates migration:**
- `templates.py` → `spec_driver/core/templates.py` (verbatim — import already
  relative).
- `templates_test.py` → `spec_driver/core/templates_test.py`; 9 `@patch` paths
  repointed.
- Legacy shim at `supekku/scripts/lib/core/templates.py` re-exports 6 public
  names.

### Strict-kind VT results

- `test_no_warning_when_known_kinds_is_none` ✓ — infra config reads silent
- `test_warning_when_known_kinds_provided` ✓ — validating entrypoints warn
- All 4 existing strict-kind tests updated + pass with `known_kinds`
- Total: 49/49 config tests pass

### Verification
- `uvx import-linter lint`: 3/3 contracts KEPT (160 files, 519 deps)
- `uv run pytest spec_driver/core/config_test.py`: 49/49 passed
- `uv run pytest spec_driver/core/ -x --ignore=*yaml* --ignore=*spec_utils* --ignore=*frontmatter_writer* --ignore=*events* --ignore=*templates*`: 353 passed
- `grep 'frontmatter_metadata\\|_registered_kinds' spec_driver/core/config.py`: empty
- `grep 'known_kinds.*FRONTMATTER_METADATA_REGISTRY' spec_driver/presentation/cli/validate/file.py`: found
- `uv run ruff check`: clean
- `spec-driver validate file phase-03.md`: clean

### Surprises
- **registry_migration.py excluded**: confirmed absent from source tree (zero
  consumers). P03 reduced from 3→2 modules.
- **templates_test.py can't collect** in nix env (missing jinja2) — same class
  as yaml_emit, spec_utils, frontmatter_writer, events tests. Full suite in real
  env should catch any regressions.

### Uncommitted
All P03 changes uncommitted (cumulative with P01+P02 uncommitted).

---

## 2026-05-31 — P03 planned (tier-2 config decoupling + templates)

**Status**: phase sheet written, ready for execution.

### Planning decisions

- **`registry_migration.py` excluded**: does not exist in source tree (zero
  consumers, zero grep hits). Was planned for DE-146 but never landed. P03
  scope: 2 modules, not 3.
- **config decoupling approach**: `load_workflow_config(repo_root, known_kinds=None)`.
  `_warn_unknown_strict_kinds` + `get_strict_map` both accept `known_kinds`;
  `_registered_kinds()` deleted entirely. `validate/file.py:263` is the single
  entrypoint that passes the registry.
- **`get_strict_map` signature change**: now requires `known_kinds: set[str]`
  (was zero-arg). Only caller is `validate/file.py`; tests pass explicit sets.
- **config_test.py strict tests**: all updated to pass `known_kinds`. New VTs
  for silent-when-None and warn-when-injected paths.
- **templates.py**: clean migration — already uses relative `.paths` import.
  9 `@patch` paths in tests must be repointed.
- **`__init__.py`**: `.config` import resolves through shim automatically;
  no change needed.

### Phase sheet

- `.spec-driver/deltas/DE-128-.../phases/phase-03.md` — 6 tasks, 18 verification
  steps, 2 VTs + 8 VAs.
- `spec-driver validate file` — clean.

---

## 2026-05-31 — P02 executed (tier-1 migration + spec_utils decoupling + domain repoint)

**Status**: completed. 4 tier-1 modules migrated, spec_utils decoupled,
domain imports repointed.

### What's done

**Chain B (paths + events):**
- `paths.py` → `spec_driver/core/paths.py` (import already relative).
  40 test pass; shim at legacy.
- `spec_driver/core/repo.py` lazy import repointed: `supekku.scripts.lib.core.paths` → `.paths`.
- `events.py` → `spec_driver/core/events.py`; lazy imports of `repo`/`paths` repointed
  to `spec_driver.core.{repo,paths}`. Shim at legacy.

**Chain A (spec_utils + frontmatter_writer):**
- New `spec_driver/core/spec_utils.py`: all pure functions + `write_markdown_file`
  primitive (wrapping `_normalise_body` + `_atomic_write`).
  `dump_markdown_file_update` re-expressed on `write_markdown_file`.
  Imports: `from .frontmatter_schema`, `from spec_driver.core.yaml_emit`.
  No orchestration/domain imports — core is provably clean.
- `dump_markdown_file_create` relocated to `spec_driver/orchestration/templates.py`
  (beside `render_frontmatter_for_kind`). Calls `core.spec_utils.write_markdown_file`.
- Legacy `supekku/scripts/lib/core/spec_utils.py` shim: re-exports pure funcs from
  `spec_driver.core.spec_utils` + `dump_markdown_file_create` from
  `spec_driver.orchestration.templates`. All 12 call sites unchanged.
- Test split: `SpecUtilsTestCase` + `DumpUpdateTest` → `spec_driver/core/spec_utils_test.py`;
  `DumpMarkdownFileCreateTest` → `spec_driver/orchestration/templates_test.py`.
- `frontmatter_writer.py` → `spec_driver/core/frontmatter_writer.py`; imports
  converted to relative (`.yaml_emit`, `.spec_utils`). Shim at legacy.

**Domain debt eliminated:**
- `domain/relations/manager.py`: `supekku.scripts.lib.core.{frontmatter_schema,spec_utils}` →
  `spec_driver.core.{frontmatter_schema,spec_utils}`.
- `domain/relations/graph.py`: `supekku.scripts.lib.core.artifact_ids` →
  `spec_driver.core.artifact_ids`.
- Zero `supekku.scripts.lib.core` imports remain in `spec_driver/domain/`.

### Verification
- `uvx import-linter lint`: 3/3 contracts KEPT (153 files, 492 deps).
  Core→orchestration edge eliminated (linter-verified).
- `grep 'supekku.scripts.lib.core' spec_driver/domain/ --include='*.py'`: empty.
- `grep 'orchestration\|domain' spec_driver/core/spec_utils.py`: only docstring mentions.
- `uv run ruff check spec_driver/core/ supekku/scripts/lib/core/`: clean.
- `uv run pytest spec_driver/core/paths_test.py`: 40/40 pass.
  (spec_utils_test, frontmatter_writer_test, events_test need yaml/click/typer —
  pre-existing nix-env issue, same as yaml_emit_test.py.)
- `spec-driver validate file phase-02.md`: clean.

### Surprises
- **nix-env test gap**: `spec_utils_test.py`, `frontmatter_writer_test.py`,
  `events_test.py` cannot be collected in this nix shell (missing yaml, click,
  typer). Same class as `yaml_emit_test.py` (264/264 reported in P01 excluded
  those). Full suite in real env should catch any regressions.
- **Legacy `supekku/scripts/lib/spec_utils_test.py`** was at `supekku/scripts/lib/`
  (not `supekku/scripts/lib/core/`). Deleted; test now at
  `spec_driver/core/spec_utils_test.py`.
- **`frontmatter_writer.py` already imported `spec_driver.core.yaml_emit`**
  (absolute). Converted to relative per DR-128 rule.

### Uncommitted
All P02 changes uncommitted (cumulative with P01 uncommitted).

---

## 2026-05-31 — P01 executed (tier-0 leaf migration)

**Status**: completed. 15 modules + `strings` merged → `string_utils`.

### What's done
- 15 verbatim copies to `spec_driver/core/`: `repo`, `version`, `relation_types`,
  `ids`, `io`, `dates`, `filters`, `artifact_ids`, `cli_utils`, `editor`, `git`,
  `go_utils`, `npm_utils`, `pylint_report`, `frontmatter_schema`.
- `slugify` from `strings.py` merged into `spec_driver/core/string_utils.py`
  (alongside existing `closest_match`); tests merged into `string_utils_test.py`.
- 11 test files moved to `spec_driver/core/` with imports repointed to
  `spec_driver.core.*`. No tests existed for `repo`, `relation_types`, `cli_utils`,
  `frontmatter_schema`.
- 16 re-export shims at legacy `supekku/scripts/lib/core/` paths.
- 0 test files remain at legacy `core/` for migrated modules.

### Verification
- `spec_driver/core/`: 264/264 tests pass (excl. pre-existing `yaml_emit_test.py` yaml import error)
- Full suite: 3,793 passed (excl. cli/tui needing click/textual)
- `uvx import-linter lint`: 3/3 contracts KEPT
- `uv run ruff check spec_driver/core/ supekku/scripts/lib/core/`: clean
- `spec-driver validate file phase-01.md`: clean

### Surprises
- **`repo.py` lazy-imports `.paths`**: Bridges `SPEC_DRIVER_DIR` via
  `supekku.scripts.lib.core.paths` (with `# noqa: PLC0415` + P02 TODO). Will
  break if `find_repo_root()` called between phases, but no consumers do so
  outside tests (which all go through shims). Will repoint in P02.
- **`filters_test.py` bug**: `parse_multi_value_filter` call was inadvertently
  spread to 3 args during manual test migration. Caught and fixed.

### Follow-ups (P02)
- Repoint `spec_driver/core/repo.py` lazy import to `spec_driver.core.paths`.

### Uncommitted
All changes uncommitted. Total: 31 new files in `spec_driver/core/`,
16 modified files in `supekku/scripts/lib/core/`, plus phase/notes edits.

---

## 2026-05-31 — Re-validation (plan drafted 2026-03-24, never executed)

Migration **not started**: `spec_driver/core/` still holds only `file_ops`,
`string_utils`, `yaml_emit`. All 22 original targets remain in
`supekku/scripts/lib/core/`.

### Inventory drift (vs DR-128's 22-module plan)

`core/` now contains 6 modules not in the DR:

| Module | Verdict | Reason |
|--------|---------|--------|
| `dates.py` (38L) | **ADD** — tier-0 leaf | zero deps; added by DE-115 |
| `ids.py` (34L) | **ADD** — tier-0 leaf | zero deps |
| `io.py` (50L) | **ADD** — tier-0 leaf | zero deps |
| `registry_migration.py` (48L) | **ADD** — tier ~2 | relative-imports `.git` (t0) + `.paths` (t1); added by DE-146 |
| `enums.py` | **OUT** — already migrated | pure re-export shim → `spec_driver.orchestration.enums` |
| `artifact_view.py` | **OUT** — already migrated | pure re-export shim → `spec_driver.orchestration.artifact_view` |

Revised genuine-core count: 22 + 4 = **26** modules to migrate.

### Domain import debt (DR's primary unblock target) — STILL VALID

3 legacy-core imports remain in `spec_driver/domain/`:
- `relations/manager.py:8` → `core.frontmatter_schema`
- `relations/manager.py:9` → `core.spec_utils`
- `relations/graph.py:19` → `core.artifact_ids`

### NEW BLOCKERS — upward dependencies grown since DR (import-linter
`root_package=spec_driver`; supekku/ is unlinted, which is why these pass today
but will FAIL once the module lands in `spec_driver.core`)

1. **`spec_utils.py:138`** lazy-imports `spec_driver.orchestration.templates`
   (`render_frontmatter_for_kind`, `UnknownKindError`) inside
   `dump_markdown_file`. Migrating spec_utils into core as-is = core→orchestration
   = POL-003 violation + linter failure. spec_utils is THE unblocker for
   domain/relations, so it cannot simply be deferred.
2. **`config.py:209`** lazy-imports `.frontmatter_metadata` (comment: "deferred
   to break cycle"). `frontmatter_metadata/` is an 18-kind metadata subpackage
   (adr/spec/delta/…) = domain knowledge, NOT core per POL-003. config→it is an
   upward/cycle smell; config is a tier-2 target.

### Other observations

- `core/templates.py` (4.3K, generic Jinja2 loader) is DISTINCT from
  `spec_driver/orchestration/templates.py` (12K, kind-aware frontmatter render).
  DR's "templates tier-2" = the generic core loader; still migratable.
- `frontmatter_metadata/` subpackage (not in DR) consumed by config + many
  domain lifecycle modules. Doctrinally domain, not core → likely OUT of scope.
- Existing clean core→core consumers already present:
  `orchestration/templates.py`, `domain/.../validator.py`,
  `frontmatter_writer.py`, `spec_utils.py` already import
  `spec_driver.core.{yaml_emit,string_utils}`.

### Doctrine in view

- POL-003: 5-layer one-way contract; core may import only stdlib + approved
  third-party; upward deps forbidden. import-linter enforces on `spec_driver.*`.
- The two blockers above are the central re-plan design problems.

### Decisions (2026-05-31 re-plan)

- Scope: 26 genuine modules (incl. dates/ids/io/registry_migration; drop
  enums/artifact_view/frontmatter_metadata). `slugify` folds into existing
  `string_utils.py`.
- spec_utils: **relocate** `dump_markdown_file_create` → orchestration.templates
  (DEC-128-004); core gains public `write_markdown_file` primitive.
- config: **DI** `known_kinds` into `load_workflow_config` (DEC-128-005); core
  drops `frontmatter_metadata` import.

### Adversarial review findings (integrated into DR §2.4 / §4)

- **F1 (must-fix):** relocated `create` used core-private `_normalise_body` +
  `_atomic_write`. Resolved: add public `core.spec_utils.write_markdown_file`;
  orchestration renders fm_yaml then calls it. Core owns write mechanics,
  orchestration owns kind rendering.
- **F3:** single validating entrypoint = `presentation/cli/validate/file.py:263`
  (`get_strict_map(load_workflow_config(...))`); already imports the registry, so
  DI is zero-new-import there. `core/config_test.py` asserts the eager warning →
  must update; VT pins warn-when-injected + silent-when-not.
- **F2:** module-count precision — 26 migrated units, ~25 new files (strings
  merges, not a new file).
- **F4:** no bare `import io` shadowing stdlib anywhere → non-issue.

---

## New Agent Instructions

### What's needed

**Audit DE-128** — all 4 phases are complete, all changes uncommitted.
Run `/audit-change` to reconcile implementation against specs,
disposition findings, and close the delta.

### Required reading

- Delta: `.spec-driver/deltas/DE-128-migrate_genuine_core_modules_to_spec_driver_core/DE-128.md`
- Design Revision: `.spec-driver/deltas/DE-128-migrate_genuine_core_modules_to_spec_driver_core/DR-128.md`
- Implementation Plan: `.spec-driver/deltas/DE-128-migrate_genuine_core_modules_to_spec_driver_core/IP-128.md`
- Phase sheets: `phases/phase-01.md` through `phase-04.md`
- Notes: `notes.md` (this file)

### Key files touched

- 27 non-test modules in `spec_driver/core/` (26 migrated + 3 original)
- 26 re-export shims in `supekku/scripts/lib/core/`
- `spec_driver/orchestration/templates.py` (received relocated `dump_markdown_file_create`)
- `spec_driver/domain/relations/manager.py` + `graph.py` (repointed to `spec_driver.core`)
- `spec_driver/presentation/cli/validate/file.py:263` (DI `known_kinds` wiring)

### Relevant memories

- `mem.pattern.architecture.domain-migration` — migration recipe
- `mem.pattern.architecture.migration-principles` — migration ordering rules
- `mem.pattern.testing.nix-pytest-via-python` — use `uv run python -m pytest`, not `uv run pytest`

### Verification summary (all phases)

- `uv run python -m pytest spec_driver/core/ -x` (excl. yaml/jinja2/click/typer nix-gaps): 382 passed
- `uvx import-linter lint`: 3/3 KEPT
- `uv run ruff check`: clean
- `spec-driver validate file phase-0[1-4].md`: clean
- `spec_driver/domain/`: zero legacy-core imports remain
- Decoupling: zero domain/orchestration imports in `spec_driver/core/`

### Pre-existing validation errors (not from P04)

- DE-128.md: relation types `follows_from`/`operationalises` not in allowed values
- DR-128.md: `code_impacts[].current_state`/`target_state` required fields missing

### Commit state

**All P01-P04 changes uncommitted.**  This includes ~55 new files in
`spec_driver/core/`, ~26 modified shim files in `supekku/scripts/lib/core/`,
plus phase/notes/IP edits. Prefer frequent small commits per repo doctrine.

### Next step

```
/using-spec-driver → /audit-change DE-128
```

