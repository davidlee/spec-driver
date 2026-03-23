---
id: mem.pattern.architecture.domain-migration
name: Domain module migration pattern
kind: memory
status: active
memory_type: pattern
created: '2026-03-24'
updated: '2026-03-24'
verified: '2026-03-24'
confidence: high
tags:
- architecture
- migration
- domain
- import-linter
summary: How to migrate modules into spec_driver.domain with re-export shims, ordered
  internal layers contract, and incremental verification.
scope:
  globs:
  - spec_driver/domain/**
  - supekku/scripts/lib/relations/**
  - supekku/scripts/lib/policies/registry.py
  - supekku/scripts/lib/standards/registry.py
  paths:
  - pyproject.toml
provenance:
  sources:
  - DE-125
  - DR-125
---

# Domain module migration pattern

## Domain internal layer ordering

`pyproject.toml` enforces via import-linter (lower may not import higher):

1. `spec_driver.domain.lifecycle`
2. `spec_driver.domain.records`
3. `spec_driver.domain.registries`
4. `spec_driver.domain.relations`
5. `spec_driver.domain.validation`

Verify: `uvx import-linter lint`

## Migration recipe

1. **Copy** module to `spec_driver/domain/<sub-area>/`.
2. **Update internal imports** to use relative imports within domain. Legacy
   `supekku.scripts.lib.core` imports are acceptable until core itself migrates.
3. **Create re-export shim** in the legacy location — forward all public names.
4. **Run** `uvx import-linter lint` and full test suite.
5. **Track shims as debt** — they must be removed eventually.

## Sharp edges

- **Domain modules may import legacy core.** `manager.py` and `graph.py` import
  `supekku.scripts.lib.core.*`. Architecturally backwards but tolerable until
  core migrates. The contract says domain is above core, but the import path
  goes upward into the legacy tree.
- **Split modules that mix concerns.** `graph.py` had to be split — pure graph
  model moved to domain, workspace artifact collection stayed in legacy because
  it's orchestration-level glue. Check for mixed concerns before moving.
- **Registries still lazy-import siblings for data collection.** Extracting
  computation (e.g. `build_backlinks()`) is useful but doesn't eliminate the
  import — someone still collects source data. The orchestration boundary
  question (who composes cross-registry data?) remains open.
- **Re-export shims mask location issues.** New code added to the shim location
  instead of the canonical location is a real risk.

## Related

- [[DE-125]], [[DR-125]] — governing delta and design revision
- [[POL-003]] — module boundary policy
- [[ADR-009]] — registry API convention (single-property protocols)
