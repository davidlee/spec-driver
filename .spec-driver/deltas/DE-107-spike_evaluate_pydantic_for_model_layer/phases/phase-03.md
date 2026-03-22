---
id: IP-107-P03
slug: "107-spike_evaluate_pydantic_for_model_layer-phase-03"
name: "Phase 03 — Drift, diagnostics, sync, docs models"
created: "2026-03-22"
updated: "2026-03-22"
status: in-progress
kind: phase
plan: IP-107
delta: DE-107
objective: >-
  Convert remaining @dataclass models to Pydantic BaseModel. Frozen
  dataclasses become ConfigDict(frozen=True). Spec model excluded
  (structurally different — wrapper pattern).
entrance_criteria:
  - Phase 2 complete
exit_criteria:
  - Drift models converted (Source, Claim, DiscoveredBy frozen; DriftEntry, DriftLedger mutable)
  - Diagnostics models converted (DiagnosticResult, CategorySummary frozen)
  - Sync models converted (SourceUnit, DocVariant, SourceDescriptor frozen; SyncOutcome mutable)
  - Doc/python models converted (VariantSpec, DocResult)
  - All existing tests passing
  - Lint clean
---

# Phase 03 — Drift, diagnostics, sync, docs models

## 1. Objective

Convert all remaining `@dataclass` models to Pydantic `BaseModel`. Frozen dataclasses become `ConfigDict(frozen=True)`. Spec model excluded (see phase-02 §10).

## 2. Tasks

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [x]    | 3.1 | Convert drift models | Done — 3 frozen + 2 mutable |
| [x]    | 3.2 | Convert diagnostics models | Done — 2 frozen |
| [x]    | 3.3 | Convert sync models | Done — 3 frozen + 1 mutable. TYPE_CHECKING Path import fix needed. |
| [x]    | 3.4 | Convert docs/python models | Done — VariantSpec classmethods work, TYPE_CHECKING Path fix |
| [x]    | 3.5 | Run tests | 277/277 passing. ~24 tests updated (positional→kwargs, AttributeError→ValidationError) |
| [x]    | 3.6 | Lint and format | ruff check + ruff format clean |

### Notes

- **Frozen models**: `model_config = ConfigDict(frozen=True)` replaces `@dataclass(frozen=True)`
- **CategorySummary.results**: `tuple[DiagnosticResult, ...]` — Pydantic handles tuples
- **VariantSpec**: has `@classmethod` factories (public, all_symbols, tests) — Pydantic supports these
- **DocVariant/SourceDescriptor**: have `Path` fields — Pydantic handles Path natively
- **DriftEntry.sources/claims**: typed as `list[Source]`/`list[Claim]` — Pydantic handles nested models
- No `from_frontmatter()` or `to_dict()` on any of these models — pure conversion
