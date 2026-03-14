---
id: IP-045.PHASE-02
slug: "045-memory_graph_navigation_for_agent_discoverability-phase-02"
name: CLI wiring + integration tests
created: "2026-03-05"
updated: "2026-03-05"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-045.PHASE-02
plan: IP-045
delta: DE-045
objective: >-
  Wire phase-1 domain functions into CLI commands. Add --links-to filter
  to list memories, --links-depth/--tree to show memory. Integration tests
  for all new CLI flags. Agent walkthrough (VA).
entrance_criteria:
  - Phase 1 complete, all domain tests green
  - emit_artifact supports body_only mode
  - show_memory uses emit_artifact
exit_criteria:
  - list memories --links-to <id> returns matching backlinkers
  - show memory --links-depth N outputs graph table (default) or tree (--tree)
  - show memory --body-only outputs body without frontmatter (already wired)
  - CLI integration tests for --links-to, --links-depth, --tree, --body-only
  - VA agent walkthrough documented
  - lint clean, all tests pass
verification:
  tests:
    - VT-cli-links-to
    - VT-cli-links-depth
    - VT-cli-body-only
    - VA-agent-walkthrough
  evidence: []
tasks:
  - id: "2.1"
    name: MemoryRegistry.collect_bodies() helper
    status: done
  - id: "2.2"
    name: Wire --links-to into list memories
    status: done
  - id: "2.3"
    name: Wire --links-depth and --tree into show memory
    status: done
  - id: "2.4"
    name: CLI integration tests
    status: done
  - id: "2.5"
    name: Agent walkthrough (VA)
    status: done
risks:
  - description: list memories --links-to changes the semantics of the output (shows sources, not the target)
    mitigation: Clear help text; output format unchanged (same table columns)
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-045.PHASE-02
```

# Phase 2 — CLI wiring + integration tests

## 1. Objective

Wire phase-1 domain functions (`compute_backlinks`, `expand_link_graph`, formatters)
into CLI commands. Thin orchestration only — no new business logic.

## 2. Links & References

- **Phase 1**: phase-01.md (complete)
- **Domain**: `memory/links.py` — `compute_backlinks()`, `expand_link_graph()`
- **Formatters**: `formatters/memory_formatters.py` — table/tree/json
- **CLI targets**: `cli/list.py` (`list_memories`), `cli/show.py` (`show_memory`)

## 3. Entrance Criteria

- [x] Phase 1 complete (all 5 tasks, 32 new tests)
- [x] `emit_artifact` supports `body_only` mode
- [x] `show_memory` migrated to `emit_artifact`

## 4. Tasks & Progress

| Status | ID  | Description                                          | Notes                                                 |
| ------ | --- | ---------------------------------------------------- | ----------------------------------------------------- |
| [x]    | 2.1 | `MemoryRegistry.collect_bodies()` helper             | 3 tests; returns {id: body_text} for graph operations |
| [x]    | 2.2 | Wire `--links-to` into `list memories`               | 5 integration tests; normalizes shorthand IDs         |
| [x]    | 2.3 | Wire `--links-depth` and `--tree` into `show memory` | 5 integration tests; supports --json/--tree/table     |
| [x]    | 2.4 | CLI integration tests                                | 3 body-only tests; 13 total new CLI tests             |
| [x]    | 2.5 | Agent walkthrough (VA)                               | See §5 below                                          |

## 5. Agent Walkthrough (VA)

**Scenario**: Agent boots, discovers hub memory, navigates graph.

1. `list memories --links-to mem.pattern.spec-driver.core-loop` — **12 backlinks** (exceeds ≥10 criterion)
2. `show memory mem.signpost.spec-driver.overview --links-depth 1` — returns 11 directly linked memories
3. `show memory mem.signpost.spec-driver.overview --links-depth 1 --tree` — indented tree with type annotations
4. `show memory mem.signpost.spec-driver.overview --body-only` — clean body output, no frontmatter

## 6. Exit Criteria

- [x] `list memories --links-to <id>` returns matching backlinkers (12 results for core-loop)
- [x] `show memory --links-depth N` outputs graph table (default) or tree (`--tree`)
- [x] `show memory --body-only` outputs body without frontmatter
- [x] CLI integration tests: 16 new tests across 3 features
- [x] VA agent walkthrough documented (§5)
- [x] Lint clean: `just lint` pass, `just pylint` 9.56/10
- [x] 2619 tests pass (16 new), 3 skipped (pre-existing), 3 pre-existing failures unrelated to DE-045
