# Notes for DE-128

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

