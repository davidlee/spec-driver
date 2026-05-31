---
id: IP-128-P03
slug: "128-migrate_genuine_core_modules_to_spec_driver_core-phase-03"
name: "Tier 2 — migrate config (decouple), templates, registry_migration"
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
phase: IP-128-P03
plan: IP-128
delta: DE-128
objective: >-
  Migrate 3 tier-2 modules (+ tests) with relative imports. DECOUPLE config:
  inject known_kinds into load_workflow_config so core stops importing the
  domain frontmatter_metadata subpackage.
entrance_criteria:
  - Phase 2 complete (tier 0 + 1 landed)
exit_criteria:
  - config, templates, registry_migration (+ tests) in spec_driver/core/
  - core/config.py imports NO frontmatter_metadata (linter/grep-verified)
  - load_workflow_config takes known_kinds; validate/file.py passes the registry
  - strict-kind warning VT pins warn-when-injected + silent-when-not
  - All tests pass; both import-linter contracts pass; ruff clean
verification:
  tests:
    - uvx import-linter lint
    - uv run pytest supekku spec_driver -x
    - uv run ruff check
  evidence:
    - grep showing core/config.py has no frontmatter_metadata import
tasks:
  - Add known_kinds param to load_workflow_config; gate _warn_unknown_strict_kinds on it
  - Repoint validate/file.py:263 to pass set(FRONTMATTER_METADATA_REGISTRY.keys())
  - Update core/config_test.py for the new warning contract; add VT for both paths
  - Migrate config, templates, registry_migration (+ tests) with relative imports
  - Create re-export shims
  - Verify
risks:
  - templates.py depends on jinja2 (path-independent)
  - config DI must not silently drop the warning — covered by VT + entrypoint wiring
  - registry_migration already uses relative .git/.paths — confirm those resolve post-migration
```

# Phase 3 — Tier 2: config (decouple), templates, registry_migration

## 1. Modules

| Module | Lines | Depends on | Notes |
|--------|-------|-----------|-------|
| `config.py` | 432 | `paths` | decouple from `frontmatter_metadata` (see §2) |
| `templates.py` | 160 | `paths`, jinja2 | generic Jinja2 loader (distinct from orchestration/templates.py) |
| `registry_migration.py` | 48 | `git`, `paths` | already uses relative `.git`/`.paths` |

## 2. config decoupling (DEC-128-005 / adversarial F3)

`_warn_unknown_strict_kinds` (called eagerly in `load_workflow_config:145`) uses
`FRONTMATTER_METADATA_REGISTRY.keys()` — domain knowledge. The "break cycle"
comment is stale (frontmatter_metadata no longer imports config).

1. **Signature**: `load_workflow_config(repo_root, known_kinds: set[str] | None = None)`;
   skip the strict-kind warning when `known_kinds is None`. Remove the
   `frontmatter_metadata` import from core config.
2. **Wire the one validating entrypoint** — `presentation/cli/validate/file.py:263`
   (`get_strict_map(load_workflow_config(repo_root))`) passes
   `known_kinds=set(FRONTMATTER_METADATA_REGISTRY.keys())`. It already imports the
   registry → zero new imports.
3. **Tests**: update `supekku/scripts/lib/core/config_test.py` (currently asserts
   the eager warning); add a VT covering warn-when-injected + silent-when-not.
4. **Behaviour change** (deliberate): strict-kind warnings fire only at the
   validating entrypoint, not on every infra config read.

## 3. Exit Criteria

- [ ] 3 tier-2 modules (+ tests) in `spec_driver/core/` with relative imports
- [ ] `core/config.py` imports no `frontmatter_metadata` (verified)
- [ ] `validate/file.py` passes `known_kinds`; warning VT green
- [ ] Re-export shims at legacy locations
- [ ] All tests pass; both contracts pass; ruff clean
