# DE-097 Implementation Notes

## Summary

Cross-artifact reference graph with on-demand computation, `show relations` command, registry-aware ID normalization, and unresolved frontmatter reference validation.

## Phase 1 — Domain layer (complete)

### New: `supekku/scripts/lib/relations/graph.py`

- `GraphEdge`, `ReferenceGraph` — frozen dataclass types for graph structure
- `build_reference_graph_from_artifacts` — pure function, testable without workspace
- `build_reference_graph(workspace)` — workspace-aware entry point, iterates all registries
- `query_forward/inverse/neighbourhood` — dict lookups on pre-built indices
- `find_unresolved_references` — filters edges with unknown targets
- `_collect_all_artifacts` split into `_collect_workspace_artifacts` + `_collect_standalone_registry_artifacts` to manage complexity

### Modified: `supekku/scripts/lib/core/artifact_ids.py`

- `NormalizationResult` dataclass + `normalize_artifact_id(raw, known_ids)` function
- Tries increasing zero-padding widths (not hardcoded to 3 digits — future-proof for 4+)
- Emits diagnostic string when non-canonical form resolves

### Key decision

- Made `forward_index`/`inverse_index` public fields on `ReferenceGraph` (not private) to avoid pylint protected-access warnings while keeping the API clean

## Phase 2 — CLI & validation (complete)

### Modified: `supekku/cli/show.py`

- `show relations <ID>` command with `--direction forward|inverse|both` and `--json`
- Handles unknown IDs: tries normalization, warns, still shows inverse edges
- `_show_relations_text` / `_show_relations_json` formatting helpers

### Modified: `supekku/scripts/lib/validation/validator.py`

- `_validate_unresolved_references` method on `WorkspaceValidator`
- Skips `domain_field` and `backlog_field` source slots (already covered by existing dedicated validators like `_validate_decision_references`)
- Warns by default, errors in strict mode
- Normalization diagnostics also surfaced as warnings

## Phase 3 — Verification (complete)

- All 4087 tests pass (0 failures)
- Existing `--related-to`, `--links-to`, `--links-depth` tests unchanged
- VA-097-truncate: `list memories --truncate` renders correctly (no action needed)
- Ruff + pylint clean on all new/modified files

## Test coverage

| VT ID                         | Description                    | Status                     |
| ----------------------------- | ------------------------------ | -------------------------- |
| VT-097-graph                  | Graph builder nodes + edges    | ✅ 6 tests                 |
| VT-097-query-forward          | Forward queries                | ✅ 3 tests                 |
| VT-097-query-inverse          | Inverse queries                | ✅ 4 tests                 |
| VT-097-normalize              | ID normalization + diagnostics | ✅ 15 tests                |
| VT-097-normalize-future       | 4-digit IDs                    | ✅ 3 tests                 |
| VT-097-unresolved             | Domain: unresolved refs        | ✅ 2 tests                 |
| VT-097-unresolved (validator) | Validator: warn/error          | ✅ 3 tests                 |
| VT-097-show-relations         | CLI command                    | ✅ 6 tests                 |
| VT-097-existing               | Regression                     | ✅ all existing tests pass |
| VA-097-truncate               | --truncate rendering           | ✅ confirmed fixed         |

## Files changed

| File                                               | Action   |
| -------------------------------------------------- | -------- |
| `supekku/scripts/lib/relations/graph.py`           | new      |
| `supekku/scripts/lib/relations/graph_test.py`      | new      |
| `supekku/scripts/lib/core/artifact_ids.py`         | modified |
| `supekku/scripts/lib/core/artifact_ids_test.py`    | modified |
| `supekku/cli/show.py`                              | modified |
| `supekku/cli/show_test.py`                         | modified |
| `supekku/scripts/lib/validation/validator.py`      | modified |
| `supekku/scripts/lib/validation/validator_test.py` | modified |
