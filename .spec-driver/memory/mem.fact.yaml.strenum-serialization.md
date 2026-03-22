---
id: mem.fact.yaml.strenum-serialization
name: StrEnum values require .value for PyYAML serialization
kind: memory
status: active
memory_type: fact
created: "2026-03-22"
updated: "2026-03-22"
verified: "2026-03-22"
confidence: high
tags:
  - yaml
  - sharp-edge
  - strenum
scope:
  globs:
    - "supekku/**/*.py"
  commands:
    - "yaml.dump"
summary:
  PyYAML serializes StrEnum with Python-specific tags; use .value at yaml.dump
  boundaries
provenance:
  sources:
    - DE-109 Phase 4 — BootstrapStatus.WARM serialized as !!python/object/apply tag
---

# StrEnum values require .value for PyYAML serialization

`yaml.dump()` serializes `StrEnum` values with Python-specific tags
(`!!python/object/apply:module.EnumClass`) instead of plain strings.
`yaml.safe_load()` cannot reconstruct these tags, causing `ConstructorError`.

- Always use `.value` when passing StrEnum values into dicts that will be
  serialized via `yaml.dump()`.
- This applies to all `build_*()` functions in review_io.py, state_io.py, etc.
  that construct dicts for YAML output.
- StrEnum comparisons (`==`) work fine since StrEnum is a str subclass — the
  issue is only at serialization boundaries.
