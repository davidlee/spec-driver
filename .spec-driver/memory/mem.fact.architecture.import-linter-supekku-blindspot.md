---
id: mem.fact.architecture.import-linter-supekku-blindspot
name: import-linter lints only spec_driver; supekku upward-deps hide until migrated
kind: memory
status: active
memory_type: fact
created: "2026-05-31"
updated: "2026-05-31"
verified: "2026-05-31"
confidence: high
tags: [architecture, import-linter, migration, core, footgun]
scope:
  paths: [pyproject.toml]
  globs: [spec_driver/core/**, supekku/scripts/lib/core/**]
provenance:
  sources: [pyproject.toml, DE-128, DR-128, POL-003]
summary: "import-linter root_package=spec_driver, so legacy supekku/ is unlinted: upward deps in would-be-core modules pass silently and only fail once the module lands in spec_driver.core. Audit before migrating."
links:
  missing:
    - raw: POL-003
    - raw: DR-128
---

# import-linter lints only spec_driver; supekku upward-deps hide until migrated

## Fact

`pyproject.toml` sets `[tool.importlinter] root_package = "spec_driver"`. The
layer contract is therefore enforced **only** within `spec_driver.*`. Legacy
`supekku/scripts/lib/**` is invisible to the linter.

Consequence for [[POL-003]] migrations into `spec_driver.core`: a legacy core
module can hold an **upward** dependency (core → orchestration/domain) that
passes `uvx import-linter lint` today — because it lives in unlinted `supekku/`.
The violation only surfaces the instant you move that module into
`spec_driver.core`, where the linter then fails the build.

## How to apply

- **Before migrating any `core/` module, grep it for upward edges**, not just
  internal-core deps:
  `grep -nE "from (spec_driver\.(orchestration|domain)|supekku\.scripts\.lib\.(blocks|registries|formatters|domain|sync|validation))" <module>`
- Lazy/deferred imports (`# noqa: PLC0415`) count — they bind at call time but
  still violate the layer contract once linted.
- If found, **decouple before/with the move** (relocate the higher-layer concern
  up, or inject it as a param) — do not move the upward edge into core.

## Worked examples (DE-128)

- `core/spec_utils.py` → `orchestration.templates` (kind-aware
  `dump_markdown_file_create`). Fix: relocate the create fn up; add a pure
  `core.spec_utils.write_markdown_file` primitive.
- `core/config.py` → `frontmatter_metadata` (domain kind registry, lazy "break
  cycle" import — comment was stale). Fix: inject `known_kinds` into
  `load_workflow_config`.

## Related

- [[mem.pattern.architecture.domain-migration]] — migration recipe (notes the
  *inverse*: legacy-core imports tolerated until core migrates; this fact is the
  gotcha when core itself migrates)
- [[mem.fact.architecture.core-misplaced-modules]] — core audit input
- [[POL-003]] — the layer contract being enforced
- [[DE-128]] / [[DR-128]] — re-plan that surfaced this
