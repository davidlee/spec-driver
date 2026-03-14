---
id: IP-036.PHASE-01
slug: "036-frontmatter_metadata_compaction_and_canonicalization_controls-phase-01"
name: IP-036 Phase 01 - Baseline and Taxonomy
created: "2026-03-03"
updated: "2026-03-03"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-036.PHASE-01
plan: IP-036
delta: DE-036
objective: >-
  Inventory metadata inflation patterns, classify canonical vs derived fields
  for memory and delta frontmatter, document baseline metrics, and fill in
  DR-036 with design decisions.
entrance_criteria:
  - Delta DE-036 accepted (status: in-progress)
exit_criteria:
  - Canonical/derived matrix documented for memory and delta frontmatter
  - Baseline inflation metrics measured and recorded
  - DR-036 filled in with design approach
  - Open design questions from IP-036 §8 answered
verification:
  tests: []
  evidence:
    - Inflation metrics in findings section
    - Canonical/derived matrix in findings section
tasks:
  - id: "0.1"
    description: Measure memory link payload inflation
    status: complete
  - id: "0.2"
    description: Build canonical/derived matrix for memory frontmatter
    status: complete
  - id: "0.3"
    description: Build canonical/derived matrix for delta frontmatter
    status: complete
  - id: "0.4"
    description: Fill in DR-036 with design decisions
    status: complete
  - id: "0.5"
    description: Answer open design questions from IP-036 §8
    status: complete
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-036.PHASE-01
```

# Phase 0 - Baseline and Taxonomy

## 1. Objective

Inventory metadata inflation, classify canonical vs derived fields across memory and delta frontmatter, and document design decisions in DR-036.

## 2. Links & References

- **Delta**: DE-036
- **Spec**: PROD-004 (FR-007 — metadata compaction)
- **Revision**: RE-019
- **Key code**: `supekku/scripts/lib/memory/links.py:249` (`links_to_frontmatter`)
- **Key code**: `supekku/scripts/lib/core/frontmatter_metadata/memory.py`
- **Key code**: `supekku/scripts/lib/core/frontmatter_metadata/delta.py`

## 3. Entrance Criteria

- [x] Delta DE-036 status: in-progress

## 4. Exit Criteria / Done When

- [x] Canonical/derived matrix documented for memory and delta frontmatter
- [x] Baseline inflation metrics measured and recorded
- [x] DR-036 filled in with design approach
- [x] Open design questions from IP-036 §8 answered

## 5. Verification

- No code changes — this is research/analysis output.
- Evidence captured in §10 below.

## 6. Assumptions & STOP Conditions

- Assumes memory corpus is representative (22 files, 70 links).
- STOP if: schema engine changes needed before P1 are more invasive than extending `FieldMetadata`.

## 7. Tasks & Progress

| Status | ID  | Description                           | Notes   |
| ------ | --- | ------------------------------------- | ------- |
| [x]    | 0.1 | Measure memory link payload inflation | See §10 |
| [x]    | 0.2 | Canonical/derived matrix: memory      | See §10 |
| [x]    | 0.3 | Canonical/derived matrix: delta       | See §10 |
| [ ]    | 0.4 | Fill in DR-036                        | Pending |
| [x]    | 0.5 | Answer open design questions          | See §9  |

## 8. Risks & Mitigations

| Risk                               | Mitigation | Status |
| ---------------------------------- | ---------- | ------ |
| None identified for research phase | —          | —      |

## 9. Decisions & Outcomes

- **2026-03-03** — Compact-by-default applies to sync commands only (not all write paths). Rationale: sync is the automation layer; manual authoring should remain unconstrained.
- **2026-03-03** — Pilot non-memory family: delta frontmatter. Rationale: deltas have clear empty-default fields (`aliases: []`, `relations: []`, `applies_to: {specs: [], requirements: []}`).
- **2026-03-03** — Link persistence default: persist `missing` only. Rationale: `missing` is a quality signal; resolved `out` entries are fully reconstructible via `resolve links`.
- **2026-03-03** — Agent guidance risk: when metadata is compacted, agents must be directed to query JSON Schema (`schema show frontmatter.*`) before authoring. Skills/workflows should be updated if compaction causes agent confusion. Monitor during P2 pilot.

## 10. Findings / Research Notes

### 10.1 Memory Link Inflation Baseline

**Corpus**: 22 memory files, 70 total `[[...]]` links, 0 unresolved.

| Metric                                   | Value        |
| ---------------------------------------- | ------------ |
| Avg links per file                       | 3.2          |
| Max links in one file                    | 9            |
| Estimated bytes per resolved link (YAML) | ~150         |
| Avg payload per file                     | ~492 bytes   |
| Avg file size                            | ~2,200 bytes |
| **Avg overhead**                         | **~22%**     |
| **Worst-case overhead (9 links)**        | **~62%**     |
| Total corpus inflation                   | ~10.8 KB     |

Currently no files have `links:` frontmatter — inflation is latent, triggered by `resolve links` or `sync --memory-links`.

### 10.2 Canonical/Derived Matrix: Memory Frontmatter

Fields from `MEMORY_FRONTMATTER_METADATA`:

| Field              | Classification | Rationale                                                            |
| ------------------ | -------------- | -------------------------------------------------------------------- |
| `id`               | **canonical**  | Identity — must persist                                              |
| `name`             | **canonical**  | Human label — must persist                                           |
| `slug`             | **canonical**  | URL-safe key — must persist                                          |
| `kind`             | **canonical**  | Always `memory` but required for polymorphic dispatch                |
| `status`           | **canonical**  | Lifecycle state                                                      |
| `created`          | **canonical**  | Immutable timestamp                                                  |
| `updated`          | **canonical**  | Mutable timestamp                                                    |
| `memory_type`      | **canonical**  | Core classification (concept/fact/pattern/signpost/system/thread)    |
| `confidence`       | **optional**   | Omit when absent (no default to reconstruct)                         |
| `verified`         | **optional**   | Omit when absent                                                     |
| `review_by`        | **optional**   | Omit when absent                                                     |
| `owners`           | **optional**   | Omit when empty `[]`                                                 |
| `auditers`         | **optional**   | Omit when empty `[]`                                                 |
| `source`           | **optional**   | Omit when absent                                                     |
| `summary`          | **optional**   | Omit when absent                                                     |
| `tags`             | **optional**   | Omit when empty `[]`                                                 |
| `relations`        | **optional**   | Omit when empty `[]`                                                 |
| `aliases`          | **optional**   | Omit when empty `[]`                                                 |
| `lifecycle`        | **optional**   | Omit when absent                                                     |
| `requires_reading` | **optional**   | Omit when empty `[]`                                                 |
| `scope`            | **optional**   | Omit when absent/empty                                               |
| `priority`         | **optional**   | Omit when absent                                                     |
| `provenance`       | **optional**   | Omit when absent                                                     |
| `audience`         | **optional**   | Omit when absent (default: both)                                     |
| `visibility`       | **optional**   | Omit when absent (default: pre)                                      |
| `links.out`        | **derived**    | Fully reconstructible from body `[[...]]` tokens via `resolve links` |
| `links.missing`    | **canonical**  | Quality signal — persist by default per design decision              |

### 10.3 Canonical/Derived Matrix: Delta Frontmatter

Fields from `DELTA_FRONTMATTER_METADATA`:

| Field             | Classification   | Rationale                                                        |
| ----------------- | ---------------- | ---------------------------------------------------------------- |
| `id`              | **canonical**    | Identity                                                         |
| `name`            | **canonical**    | Human label                                                      |
| `slug`            | **canonical**    | URL-safe key                                                     |
| `kind`            | **canonical**    | Always `delta`                                                   |
| `status`          | **canonical**    | Lifecycle state                                                  |
| `created`         | **canonical**    | Immutable timestamp                                              |
| `updated`         | **canonical**    | Mutable timestamp                                                |
| `aliases`         | **default-omit** | Omit when `[]` (empty is default)                                |
| `relations`       | **default-omit** | Omit when `[]` (empty is default)                                |
| `owners`          | **optional**     | Omit when empty `[]`                                             |
| `auditers`        | **optional**     | Omit when empty `[]`                                             |
| `source`          | **optional**     | Omit when absent                                                 |
| `summary`         | **optional**     | Omit when absent                                                 |
| `tags`            | **optional**     | Omit when empty `[]`                                             |
| `lifecycle`       | **optional**     | Omit when absent                                                 |
| `applies_to`      | **default-omit** | Omit when `{specs: [], requirements: []}` (all-empty is default) |
| `context_inputs`  | **optional**     | Omit when empty `[]`                                             |
| `outcome_summary` | **optional**     | Omit when absent                                                 |
| `risk_register`   | **optional**     | Omit when empty `[]`                                             |

### 10.4 Proposed FieldMetadata Extension

Add to `FieldMetadata`:

```python
# Persistence classification for compaction profiles
persistence: str = "canonical"
# Values:
#   "canonical"  — must always be persisted (identity, required state)
#   "derived"    — fully reconstructible; omit by default, persist in full mode
#   "optional"   — omit when absent or equal to default_value
#   "default-omit" — omit when equal to default_value (has a meaningful default)

default_value: Any = None
# When persistence is "optional" or "default-omit", this is the value
# that signals "omit during compaction". E.g., [] for empty arrays.
```

### 10.5 Compaction Semantics

| Classification | Compact mode                          | Full mode        |
| -------------- | ------------------------------------- | ---------------- |
| `canonical`    | Always persisted                      | Always persisted |
| `derived`      | Omitted                               | Persisted        |
| `optional`     | Omitted when absent/default           | Persisted as-is  |
| `default-omit` | Omitted when equal to `default_value` | Persisted as-is  |

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Research evidence stored (§10)
- [x] DR-036 updated
- [x] Hand-off notes to Phase 1: proceed with FieldMetadata extension, then memory link mode controls
