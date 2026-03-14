---
id: IP-045.PHASE-01
slug: 045-memory_graph_navigation_for_agent_discoverability-phase-01
name: Graph domain + shared infrastructure
created: '2026-03-05'
updated: '2026-03-05'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-045.PHASE-01
plan: IP-045
delta: DE-045
objective: >-
  Build pure graph functions (backlinks, depth expansion) and formatters.
  Migrate show_memory to emit_artifact and add body-only mode to the shared
  helper. All domain code tested before CLI wiring in phase 2.
entrance_criteria:
  - DE-045 scoped and decisions settled
exit_criteria:
  - compute_backlinks tested with real-world expectations (≥10 backlinks for core-loop)
  - expand_link_graph tested with depth 0/1/2, cycles, and missing targets
  - format_link_graph_table and format_link_graph_tree tested
  - emit_artifact supports body_only mode with tests
  - show_memory migrated to emit_artifact (no functional change to existing flags)
  - lint clean, all existing tests pass
verification:
  tests:
    - VT-backlinks
    - VT-expand-graph
    - VT-format-graph
    - VT-body-only
    - VT-emit-body
  evidence: []
tasks:
  - id: "1.1"
    name: compute_backlinks pure function
    status: pending
  - id: "1.2"
    name: expand_link_graph pure function
    status: pending
  - id: "1.3"
    name: Graph formatters (table + tree)
    status: pending
  - id: "1.4"
    name: Add body_only to emit_artifact
    status: pending
  - id: "1.5"
    name: Migrate show_memory to emit_artifact
    status: pending
risks:
  - description: show_memory has custom logic (normalize_memory_id, registry.find) that may not fit emit_artifact pattern cleanly
    mitigation: emit_artifact takes format_fn/json_fn callbacks — resolve/find stays in the command, emit handles output dispatch
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-045.PHASE-01
```

# Phase 1 — Graph domain + shared infrastructure

## 1. Objective

Build the domain-layer graph functions and formatters as pure, tested code.
Simultaneously improve consistency by migrating `show_memory` to the shared
`emit_artifact` helper and extending it with `--body-only` support.

## 2. Links & References

- **Delta**: DE-045
- **ADR-002**: no backlinks in frontmatter — runtime computation only
- **Existing code**:
  - `supekku/scripts/lib/memory/links.py` — `parse_links()`, `resolve_all_links()`
  - `supekku/cli/common.py:517` — `emit_artifact()`
  - `supekku/cli/show.py:446` — `show_memory` (currently rolls its own dispatch)
  - `supekku/scripts/lib/formatters/memory_formatters.py` — display formatters

## 3. Entrance Criteria

- [x] DE-045 scoped, decisions settled (backlink source, output format)

## 4. Exit Criteria / Done When

- [x] `compute_backlinks()` pure function tested (9 tests)
- [x] `expand_link_graph()` pure function tested (9 tests — depth 0/1/2, cycles, missing targets)
- [x] `format_link_graph_table()`, `format_link_graph_tree()`, `format_link_graph_json()` tested (10 tests)
- [x] `emit_artifact` supports `body_only` mode with mutual-exclusivity check (3 tests)
- [x] `show_memory` uses `emit_artifact` — no behavioural change (36 existing tests pass)
- [x] Lint clean: `just lint` pass, `just pylint` 9.42/10
- [x] 2603 tests pass (32 new), 3 skipped (pre-existing)

## 5. Verification

- `just test` — all unit tests green
- `just lint` + `just pylint` — zero warnings
- Manual: `uv run spec-driver show memory mem.pattern.spec-driver.core-loop` unchanged output

## 6. Assumptions & STOP Conditions

- `parse_links()` already handles code-block stripping and dedup — reuse, don't rewrite
- `MemoryRegistry.collect()` returns all records with paths — sufficient for body parsing
- STOP if `emit_artifact` pattern can't accommodate memory's `normalize_memory_id` + `registry.find` flow without becoming complex

## 7. Tasks & Progress

| Status | ID  | Description                              | Notes                                                            |
| ------ | --- | ---------------------------------------- | ---------------------------------------------------------------- |
| [x]    | 1.1 | `compute_backlinks` pure function        | 9 tests, handles self-links, normalization, non-memory artifacts |
| [x]    | 1.2 | `expand_link_graph` pure function        | 9 tests, BFS with cycle protection, depth cap at 5               |
| [x]    | 1.3 | Graph formatters (table + tree + json)   | 10 tests across 3 formatter functions                            |
| [x]    | 1.4 | Add `body_only` to `emit_artifact`       | 3 tests (body extraction + 2 mutual exclusivity)                 |
| [x]    | 1.5 | Migrate `show_memory` to `emit_artifact` | Zero regression across 36 existing tests; `--body-only/-b` wired |

### Task Details

- **1.1 `compute_backlinks`**
  - **Signature**: `compute_backlinks(records: dict[str, MemoryRecord], root: Path) -> dict[str, list[str]]`
  - Returns `{target_id: [source_id, ...]}` by parsing each record's body with `parse_links()`
  - Must handle self-links (skip), missing targets (include — they're still inbound references), and `mem:` URI scheme normalization
  - **Files**: `memory/links.py`, `memory/links_test.py`
  - **Tests**: empty corpus, single link, hub node (≥10 backlinks), self-link exclusion

- **1.2 `expand_link_graph`**
  - **Signature**: `expand_link_graph(root_id: str, records: dict[str, MemoryRecord], root: Path, *, max_depth: int = 1) -> list[LinkGraphNode]`
  - `LinkGraphNode`: dataclass with `id`, `name`, `depth`, `memory_type`
  - BFS with visited set for cycle protection. Cap depth (hard max ~5)
  - Parses body of each visited node to discover outgoing links, resolves against records dict
  - **Files**: `memory/links.py`, `memory/links_test.py`
  - **Tests**: depth 0 (root only), depth 1, depth 2, cycle detection, missing targets gracefully skipped

- **1.3 Graph formatters**
  - `format_link_graph_table(nodes: list[LinkGraphNode]) -> str` — compact table: `depth | id | name | type`
  - `format_link_graph_tree(nodes: list[LinkGraphNode]) -> str` — indented tree using `  ` per depth level
  - `format_link_graph_json(nodes: list[LinkGraphNode]) -> str` — JSON array
  - **Files**: `formatters/memory_formatters.py`, `formatters/memory_formatters_test.py`
  - **Tests**: empty, single node, multi-depth, truncation

- **1.4 Add `body_only` to `emit_artifact`**
  - Add `body_only: bool = False` parameter
  - Update mutual-exclusivity check: `json_output`, `path_only`, `raw_output`, `body_only`
  - Body extraction: `load_markdown_file(ref.path)` → return body only
  - **Files**: `cli/common.py`, `cli/common_test.py`
  - **Tests**: body-only mode, mutual exclusivity with other flags

- **1.5 Migrate `show_memory` to `emit_artifact`**
  - Keep resolve logic (normalize_memory_id, registry.find) in the command
  - Build an `ArtifactRef` from the resolved record
  - Delegate output dispatch to `emit_artifact`
  - Verify existing `--json`, `--path`, `--raw` behaviour unchanged
  - **Files**: `cli/show.py`, `cli/memory_test.py`
  - **Tests**: existing tests must pass without modification (regression gate)
