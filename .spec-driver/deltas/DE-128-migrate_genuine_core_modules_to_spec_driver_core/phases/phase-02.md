---
id: IP-128-P02
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-02"
name: "Tier 1 — migrate paths, spec_utils (decouple), frontmatter_writer, events"
created: "2026-03-24"
updated: "2026-05-31"
status: completed
kind: phase
plan: IP-128
delta: DE-128
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-128-P02
plan: IP-128
delta: DE-128
objective: >-
  Migrate 4 tier-1 modules (+ tests) with relative internal imports. DECOUPLE
  spec_utils: relocate kind-aware dump_markdown_file_create up to
  orchestration.templates and add a pure core write_markdown_file primitive so
  core/spec_utils imports nothing upward. Then repoint domain/relations/ to
  spec_driver.core (debt eliminated).
entrance_criteria:
  - Phase 1 complete (all 16 tier-0 modules + tests in spec_driver/core/; all shims in place)
  - import-linter 3/3 KEPT; core tests pass (excl. yaml_emit env issue)
exit_criteria:
  - 4 tier-1 modules (+ tests) in spec_driver/core/ with relative imports
  - spec_driver/core/repo.py lazy import repointed to spec_driver.core.paths
  - core/spec_utils.py imports NO orchestration/domain symbol (linter-verified)
  - dump_markdown_file_create lives in orchestration.templates; calls core write_markdown_file
  - new core.spec_utils.write_markdown_file primitive; dump_markdown_file_update re-expressed on it
  - legacy supekku/scripts/lib/core/spec_utils.py shim re-exports pure funcs from core + create from orchestration
  - domain/relations/ (manager.py, graph.py) import spec_driver.core; ZERO supekku.scripts.lib.core in spec_driver/domain/
  - All tests pass (spec_driver + supekku core shims); both import-linter contracts pass; ruff clean
  - 12 dump_markdown_file_create call sites unchanged (all go through legacy shim)
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
  evidence:
    - import-linter output (core has no upward edge)
    - grep showing zero legacy-core imports in spec_driver/domain/
    - grep confirming dump_markdown_file_create resolves from orchestration.templates
    - grep confirming core/spec_utils.py has zero imports of orchestration or domain symbols
tasks:
  - Migrate paths to core; repoint repo.py lazy import (tasks 1–2)
  - Decouple spec_utils: add write_markdown_file primitive + migrate pure funcs (tasks 3–5)
  - Relocate dump_markdown_file_create to orchestration.templates (task 4)
  - Migrate frontmatter_writer (task 6)
  - Migrate events (task 7)
  - Repoint domain/relations/ manager.py + graph.py to spec_driver.core (task 8)
  - Verify (task 9)
risks:
  - paths.py has 40 consumers — shim failure widely visible
  - events.py has lazy imports of repo/paths — must use spec_driver.core paths after migration
  - events_test.py has lazy imports of config (not migrated until P03) — keep legacy path for those
  - 12 dump_markdown_file_create call sites — legacy shim must re-export it so callers stay unchanged
  - frontmatter_writer already imports spec_driver.core.yaml_emit (absolute) — convert to relative per DR-128 rule
  - DumpCreateUpdateSplitTest class straddles create (→orchestration) and update (→core) tests — split required
assumptions:
  - yaml_emit_test.py collection error is a pre-existing nix-env issue (missing yaml), not caused by this phase
  - spec_driver/domain/ tests have pre-existing collection errors (missing pydantic) — unrelated to this phase
  - events_test.py lazy imports of supekku.scripts.lib.core.config stay valid through legacy path until P03
  - orchestration.templates already has UnknownKindError and render_frontmatter_for_kind — relocation adds only dump_markdown_file_create
---

# Phase 2 — Tier 1: migrate dependent core modules, decouple spec_utils, fix domain imports

## 1. Objective

Move the 4 tier-1 modules (with their tests) into `spec_driver.core` using
relative internal imports; **decouple `spec_utils` from its upward dependency**
(DR-128 §2.4, DEC-128-004); repoint `spec_driver/core/repo.py` lazy import; then
eliminate the legacy-core import debt in `spec_driver/domain/relations/`.

## 2. Modules

| Module | Lines | Depends on | Key change |
|--------|-------|-----------|------------|
| `paths.py` | 234 | `repo` | `from .repo import find_repo_root` |
| `spec_utils.py` | ~110 | `frontmatter_schema` | decouple (see §3); `from .frontmatter_schema import …` |
| `frontmatter_writer.py` | 369 | `spec_utils` | `from .spec_utils import …`; also `from .yaml_emit import …` |
| `events.py` | 184 | `repo`, `paths` (lazy) | lazy imports → `spec_driver.core.{repo,paths}` |

## 3. Task Breakdown

### Task 1 — Migrate `paths` to core

1. Copy `supekku/scripts/lib/core/paths.py` → `spec_driver/core/paths.py`.
   Change: `from .repo import find_repo_root` (was absolute `from .repo`).
   No other imports to change — `Path`, `warnings`, `supekku` (lazy in `get_package_skills_dir`) stay.
2. Move `supekku/scripts/lib/core/paths_test.py` → `spec_driver/core/paths_test.py`.
   Repoint imports:
   - `import supekku.scripts.lib.core.paths as paths_mod` → `import spec_driver.core.paths as paths_mod`
   - `from supekku.scripts.lib.core.paths import …` → `from spec_driver.core.paths import …`
   Delete legacy test file.
3. Create legacy shim `supekku/scripts/lib/core/paths.py` re-exporting all names
   from `spec_driver.core.paths` (mirror P01 shim pattern).
4. Verify: `uv run pytest spec_driver/core/paths_test.py -x` passes.

### Task 2 — Repoint `repo.py` lazy import

5. In `spec_driver/core/repo.py`: change
   `from supekku.scripts.lib.core.paths import SPEC_DRIVER_DIR` →
   `from .paths import SPEC_DRIVER_DIR` (remove `# TODO(DE-128-P02)` comment).
6. Verify: `uv run pytest spec_driver/core/repo.py` tests (if any exist — none
   existed in P01; verify import resolves by running any test that transitively
   imports repo).

### Task 3 — Add `write_markdown_file` primitive + migrate pure spec_utils

7. Create `spec_driver/core/spec_utils.py` containing:
   - All pure functions from legacy `spec_utils.py`: `load_markdown_file`,
     `_normalise_body`, `_atomic_write`, `_extract_inline_comments`,
     `_read_existing_frontmatter_text`, `dump_markdown_file_update`,
     `ensure_list_entry`, `append_unique`, `extract_h1_title`,
     `load_validated_markdown_file`, `MarkdownLoadError`.
   - **NEW**: `write_markdown_file(path: Path, fm_yaml: str, body: str) → None`
     wrapping `_normalise_body` + `_atomic_write`:
     ```python
     def write_markdown_file(path: Path, fm_yaml: str, body: str) -> None:
         combined = f"---\n{fm_yaml}\n---\n\n{_normalise_body(body)}"
         _atomic_write(path, combined)
     ```
   - **RE-EXPRESS** `dump_markdown_file_update` to call `write_markdown_file`
     instead of inline `_atomic_write`.
   - Import `from .frontmatter_schema import FrontmatterValidationResult, validate_frontmatter`
     (relative). Import `from spec_driver.core.yaml_emit import emit_yaml_block`
     (absolute — yaml_emit is a thin wrapper; relative also valid but absolute
     avoids ambiguity with third-party `yaml`).
   - Does NOT include `dump_markdown_file_create`.
   - `__all__` includes all public names.

8. Move tests to `spec_driver/core/spec_utils_test.py`:
   - `SpecUtilsTestCase` (all pure-function tests) — repoint imports:
     `from supekku.scripts.lib.core.spec_utils import …` → `from spec_driver.core.spec_utils import …`
   - `DumpCreateUpdateSplitTest` — **split**:
     - `test_create_renders_enum_comment_hints`, `test_create_refuses_existing_path` →
       move to orchestration test (see Task 4).
     - `test_update_preserves_existing_trailing_comments`,
       `test_update_no_comments_when_none_present`,
       `test_update_idempotent_round_trip` → stay in core test (these test
       `dump_markdown_file_update`, repointed to `spec_driver.core.spec_utils`).
   - Delete legacy test file.

### Task 4 — Relocate `dump_markdown_file_create` to `orchestration.templates`

9. Add `dump_markdown_file_create` to `spec_driver/orchestration/templates.py`:
   - Function body unchanged except: remove the lazy imports of
     `render_frontmatter_for_kind`/`UnknownKindError` (they're already local
     in this module); import `write_markdown_file` from
     `spec_driver.core.spec_utils`; import `emit_yaml_block` from
     `spec_driver.core.yaml_emit` (already imported in this module).
   - Replace the `_normalise_body` + `_atomic_write` tail with:
     `write_markdown_file(path, fm_yaml, body)`.
   - Add to `__all__`.

10. Move `test_create_renders_enum_comment_hints` and
    `test_create_refuses_existing_path` into a new or existing orchestration
    test file. Simplest: add a test class in
    `spec_driver/orchestration/templates_test.py` (create if absent) or a
    standalone `spec_driver/orchestration/dump_create_test.py`.
    If no orchestration test file exists, create
    `spec_driver/orchestration/templates_test.py` with these two tests
    (import `dump_markdown_file_create` from `spec_driver.orchestration.templates`).

### Task 5 — Create `spec_utils` legacy shim

11. Replace `supekku/scripts/lib/core/spec_utils.py` with a re-export shim:
    - Pure funcs from `spec_driver.core.spec_utils`: `load_markdown_file`,
      `dump_markdown_file_update`, `write_markdown_file`, `MarkdownLoadError`,
      `ensure_list_entry`, `append_unique`, `extract_h1_title`,
      `load_validated_markdown_file`.
    - `dump_markdown_file_create` from `spec_driver.orchestration.templates`.
    - `__all__` includes all re-exported names.

    > This shim is the single point that keeps all 12 `dump_markdown_file_create`
    > call sites working unchanged.

### Task 6 — Migrate `frontmatter_writer`

12. Copy `supekku/scripts/lib/core/frontmatter_writer.py` → `spec_driver/core/frontmatter_writer.py`.
    Convert imports:
    - `from spec_driver.core.yaml_emit import _FrontmatterDumper as CompactDumper` → `from .yaml_emit import _FrontmatterDumper as CompactDumper`
    - `from spec_driver.core.yaml_emit import emit_yaml_block` → `from .yaml_emit import emit_yaml_block`
    - `from supekku.scripts.lib.core.spec_utils import dump_markdown_file_update, load_markdown_file` → `from .spec_utils import dump_markdown_file_update, load_markdown_file`
13. Move `supekku/scripts/lib/core/frontmatter_writer_test.py` → `spec_driver/core/frontmatter_writer_test.py`.
    Repoint imports:
    - `from .frontmatter_writer import …` → `from spec_driver.core.frontmatter_writer import …`
    - `from .spec_utils import load_markdown_file` → `from spec_driver.core.spec_utils import load_markdown_file`
    Delete legacy test file.
14. Create legacy shim `supekku/scripts/lib/core/frontmatter_writer.py`
    re-exporting all public names from `spec_driver.core.frontmatter_writer`.

### Task 7 — Migrate `events`

15. Copy `supekku/scripts/lib/core/events.py` → `spec_driver/core/events.py`.
    Convert lazy imports inside functions:
    - `_get_run_dir()`: `from supekku.scripts.lib.core.repo import find_repo_root` → `from .repo import find_repo_root`
      and `from supekku.scripts.lib.core.paths import get_run_dir` → `from .paths import get_run_dir`
    No other imports to change.
16. Move `supekku/scripts/lib/core/events_test.py` → `spec_driver/core/events_test.py`.
    Repoint imports:
    - `from supekku.scripts.lib.core import events` → `from spec_driver.core import events`
    - Lazy imports of `supekku.scripts.lib.core.config` (lines 209, 217, 235):
      **keep** — config is migrated in P03; these resolve through the legacy
      shim path (which will be created in P03).
    - Lazy imports of `supekku.scripts.lib.core.paths` (line 218): repoint to
      `spec_driver.core.paths`.
    - Other lazy imports (`changes.creation`, `specs.creation`, `install`):
      **keep** — not core modules, stay on legacy paths.
    Delete legacy test file.
17. Create legacy shim `supekku/scripts/lib/core/events.py` re-exporting all
    public names from `spec_driver.core.events`.

### Task 8 — Repoint domain/relations imports

18. In `spec_driver/domain/relations/manager.py`:
    - Line 8: `from supekku.scripts.lib.core.frontmatter_schema import Relation` →
      `from spec_driver.core.frontmatter_schema import Relation`
    - Line 9: `from supekku.scripts.lib.core.spec_utils import (` →
      `from spec_driver.core.spec_utils import (`
      (imports `load_markdown_file`, `dump_markdown_file_update` — both pure, no
      orchestration dep)
19. In `spec_driver/domain/relations/graph.py`:
    - Line 19: `from supekku.scripts.lib.core.artifact_ids import normalize_artifact_id` →
      `from spec_driver.core.artifact_ids import normalize_artifact_id`

### Task 9 — Verify

20. `uvx import-linter lint` — both contracts KEPT. Core must show zero upward
    edges (no core→orchestration, no core→domain).
21. `uv run pytest spec_driver/core/ -x` — all core tests pass. Check specifically:
    - `paths_test.py`, `spec_utils_test.py` (pure), `frontmatter_writer_test.py`,
      `events_test.py` all pass.
    - Orchestration test for `dump_markdown_file_create` passes.
22. `uv run pytest supekku/scripts/lib/core/ -x` — legacy tests that were NOT
    migrated (config_test, templates_test, etc.) still pass via shim paths.
23. `uv run ruff check spec_driver/core/ supekku/scripts/lib/core/` — clean.
24. Confirm zero legacy-core imports in domain:
    `grep -rn 'supekku.scripts.lib.core' spec_driver/domain/` → empty.
25. Confirm core/spec_utils.py has no upward deps:
    `grep -n 'orchestration\|domain' spec_driver/core/spec_utils.py` → empty.
26. Confirm dump_markdown_file_create resolves from orchestration:
    `grep 'def dump_markdown_file_create' spec_driver/orchestration/templates.py` → found.
27. Confirm all 12 call sites still import `dump_markdown_file_create` correctly:
    `grep -rn 'dump_markdown_file_create' supekku/ spec_driver/ --include='*.py' -l`
    — every call site imports it from the legacy shim or core, none broken.

## 4. spec_utils decoupling detail (DEC-128-004 / adversarial F1)

Only `dump_markdown_file_create` reaches up to
`spec_driver.orchestration.templates` (`render_frontmatter_for_kind`,
`UnknownKindError`). It also uses core-private `_normalise_body` + `_atomic_write`.

1. **Add a pure core write primitive** `write_markdown_file(path, fm_yaml: str, body: str)`:
   wraps `_normalise_body` + `_atomic_write`. `dump_markdown_file_update` is
   re-expressed on it (DRY, single write path).
2. **Relocate `dump_markdown_file_create`** into `orchestration.templates`:
   render kind-aware `fm_yaml` (or `emit_yaml_block` fallback) → call
   `core.spec_utils.write_markdown_file`.
3. **Migrate the pure spec_utils** (+ its test, minus `test_create_*`) to
   `spec_driver/core/spec_utils.py`. Depends only on `core.yaml_emit` and
   `core.frontmatter_schema` — no upward edge.
4. **Legacy shim** re-exports the pure funcs from `spec_driver.core.spec_utils`
   AND `dump_markdown_file_create` from `spec_driver.orchestration.templates` —
   all 12 call sites stay unchanged.

## 5. Domain import debt cleanup

`manager.py` uses only the pure `load_markdown_file` + `dump_markdown_file_update`;
`graph.py` only `normalize_artifact_id` (landed P01). Repoint:

| File | Old | New |
|------|-----|-----|
| `domain/relations/manager.py:8` | `supekku.scripts.lib.core.frontmatter_schema` | `spec_driver.core.frontmatter_schema` |
| `domain/relations/manager.py:9` | `supekku.scripts.lib.core.spec_utils` | `spec_driver.core.spec_utils` |
| `domain/relations/graph.py:19` | `supekku.scripts.lib.core.artifact_ids` | `spec_driver.core.artifact_ids` |

## 6. Verification (VT/VA)

| Step | Type | What | Evidence |
|------|------|------|----------|
| import-linter | **VT** | Both contracts KEPT; core→orchestration/domain forbidden | CLI output |
| pytest core/ | **VT** | All migrated test suites pass | pytest summary |
| pytest supekku core shims | **VT** | Legacy consumers still work through shims | pytest summary |
| ruff check | **VT** | Zero lint warnings | ruff output |
| domain grep | **VA** | `grep -rn 'supekku.scripts.lib.core' spec_driver/domain/` → empty | Agent confirms |
| spec_utils upward-dep grep | **VA** | `spec_driver/core/spec_utils.py` imports no orchestration/domain symbol | Agent confirms |
| dump_create relocation | **VA** | `dump_markdown_file_create` defined in `orchestration/templates.py` | Agent confirms |
| call-site audit | **VA** | 12 call sites unchanged; imports resolve via legacy shim | Agent confirms |

## 7. Out of Scope

- `spec_driver/orchestration/` legacy-core imports (`operations.py`,
  `artifact_view.py`, ~20 mock-patch refs) — follow-on, not gated.
- Migrating `config`, `templates`, `registry_migration` — P03.
- Updating `events_test.py` lazy imports of `supekku.scripts.lib.core.config` —
  those stay on legacy path until P03.
- `frontmatter_metadata/`, `enums.py`, `artifact_view.py` — domain / already
  migrated per DR-128 §2.5.
