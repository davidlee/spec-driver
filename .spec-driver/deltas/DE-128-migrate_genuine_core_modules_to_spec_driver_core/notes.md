# Notes for DE-128

## 2026-05-31 — Re-validation against current reality (plan was drafted 2026-03-24)

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

