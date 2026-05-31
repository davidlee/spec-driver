---
id: IP-128-P02
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-02"
name: "Tier 1 — migrate paths, spec_utils (decouple), frontmatter_writer, events"
created: "2026-03-24"
updated: "2026-05-31"
status: draft
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
  - Phase 1 complete (tier 0 landed)
exit_criteria:
  - paths, spec_utils, frontmatter_writer, events (+ tests) in spec_driver/core/
  - core/spec_utils.py imports NO orchestration/domain symbol (linter-verified)
  - dump_markdown_file_create lives in orchestration.templates; legacy shim re-exports it
  - new core.spec_utils.write_markdown_file primitive; create + update use it
  - domain/relations/ (manager.py, graph.py) import spec_driver.core; zero supekku.scripts.lib.core in spec_driver/domain/
  - All tests pass; both import-linter contracts pass; ruff clean
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
  evidence:
    - import-linter output (core has no upward edge)
    - grep showing zero legacy-core imports in spec_driver/domain/
tasks:
  - Migrate paths, frontmatter_writer, events (+ tests) with relative internal imports
  - Add core.spec_utils.write_markdown_file (wraps _normalise_body + _atomic_write)
  - Relocate dump_markdown_file_create to orchestration.templates (render -> write_markdown_file)
  - Migrate pure spec_utils (+ test) to core; legacy shim re-exports pure funcs + create (from orchestration)
  - Repoint domain/relations/ manager.py + graph.py to spec_driver.core
  - Verify
risks:
  - paths.py has 40 consumers — shim failure widely visible
  - events.py has lazy imports of repo/paths — must use spec_driver.core paths
  - 12 dump_markdown_file_create call sites — legacy shim must re-export it so callers stay unchanged
```

# Phase 2 — Tier 1: migrate dependent core modules, decouple spec_utils, fix domain imports

## 1. Objective

Move the 4 tier-1 modules (with their tests) into `spec_driver.core` using
relative internal imports; **decouple `spec_utils` from its upward dependency**
(DR-128 §2.4); then eliminate the legacy-core import debt in
`spec_driver/domain/relations/`.

## 2. Modules

| Module | Lines | Depends on | Key change |
|--------|-------|-----------|------------|
| `paths.py` | 234 | `repo` | `from .repo import find_repo_root` |
| `spec_utils.py` | 92 | `frontmatter_schema` | decouple (see §3); `from .frontmatter_schema import …` |
| `frontmatter_writer.py` | 369 | `spec_utils` | `from .spec_utils import …` (was absolute) |
| `events.py` | 184 | `repo`, `paths` (lazy) | lazy imports → `spec_driver.core.*` |

## 3. spec_utils decoupling (DEC-128-004 / adversarial F1)

Only `dump_markdown_file_create` reaches up to
`spec_driver.orchestration.templates` (`render_frontmatter_for_kind`,
`UnknownKindError`). It also uses core-private `_normalise_body` + `_atomic_write`.

1. **Add a pure core write primitive** to `spec_driver/core/spec_utils.py`:
   `write_markdown_file(path, fm_yaml: str, body: str)` wrapping
   `_normalise_body` + `_atomic_write`. Re-express `dump_markdown_file_update`
   on it.
2. **Relocate `dump_markdown_file_create`** into
   `spec_driver/orchestration/templates.py` (beside `render_frontmatter_for_kind`).
   Its body: render kind-aware `fm_yaml` (or `emit_yaml_block` fallback) → call
   `core.spec_utils.write_markdown_file`.
3. **Migrate the pure spec_utils** (+ its test) to `spec_driver/core/spec_utils.py`:
   `load_markdown_file`, `dump_markdown_file_update`, `write_markdown_file`,
   `_atomic_write`, `_normalise_body`, `_extract_inline_comments`,
   `_read_existing_frontmatter_text`, `ensure_list_entry`, `append_unique`,
   `extract_h1_title`, `load_validated_markdown_file`. Depends only on
   `core.yaml_emit` — no upward edge.
4. **Legacy shim** `supekku/scripts/lib/core/spec_utils.py` re-exports the pure
   funcs from `spec_driver.core.spec_utils` AND `dump_markdown_file_create` from
   `spec_driver.orchestration.templates` — all 12 call sites stay unchanged.

## 4. Domain import debt cleanup

`manager.py` uses only the pure `load_markdown_file` + `dump_markdown_file_update`;
`graph.py` only `normalize_artifact_id` (landed P01). Repoint:

| File | Old | New |
|------|-----|-----|
| `domain/relations/manager.py:8` | `supekku.scripts.lib.core.frontmatter_schema` | `spec_driver.core.frontmatter_schema` |
| `domain/relations/manager.py:9` | `supekku.scripts.lib.core.spec_utils` | `spec_driver.core.spec_utils` |
| `domain/relations/graph.py:19` | `supekku.scripts.lib.core.artifact_ids` | `spec_driver.core.artifact_ids` |

## 5. Exit Criteria

- [ ] 4 tier-1 modules (+ tests) in `spec_driver/core/` with relative imports
- [ ] `core/spec_utils.py` imports no orchestration/domain symbol (linter-verified)
- [ ] `dump_markdown_file_create` in `orchestration.templates`; `write_markdown_file` in core; legacy shim re-exports both
- [ ] domain/relations repointed; zero `supekku.scripts.lib.core` in `spec_driver/domain/`
- [ ] (Out of scope: `spec_driver/orchestration/` legacy-core imports — follow-on)
- [ ] All tests pass; both contracts pass; ruff clean
