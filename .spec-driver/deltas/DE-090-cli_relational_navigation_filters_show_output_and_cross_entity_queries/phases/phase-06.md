---
id: IP-090.PHASE-06
slug: "090-cli_relational_navigation_filters_show_output_and_cross_entity_queries-phase-06"
name: IP-090 Phase 06 — P5 neighbourhood view (show --related)
created: "2026-03-14"
updated: "2026-03-14"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-090.PHASE-06
plan: IP-090
delta: DE-090
objective: >-
  Add --related flag to show spec, show delta, show requirement, and show issue.
  When passed, replace count-based "Related:" section with a full one-hop
  "Referenced by" neighbourhood listing. Support both rendered and JSON output.
entrance_criteria:
  - Phase 05 complete (P4 reverse reference filtering landed, commit e31eca9)
  - DR-090 §P5 design approved
exit_criteria:
  - format_related_section() in relation_formatters.py
  - --related flag on show spec, show delta, show requirement, show issue
  - --related replaces count view on show spec (not shown alongside)
  - --related --json includes related key with forward/referenced_by structure
  - Entity with no references produces no "Referenced by" section
  - Per-kind registry loading (not all registries unconditionally)
  - VT-090-P5-1 through VT-090-P5-5 passing
  - Lint clean (ruff + pylint)
verification:
  tests:
    - VT-090-P5-1
    - VT-090-P5-2
    - VT-090-P5-3
    - VT-090-P5-4
    - VT-090-P5-5
  evidence: []
tasks:
  - id: 6.1
    description: "Add format_related_section() to relation_formatters.py"
  - id: 6.2
    description: "Add --related flag to show spec with forward + reverse refs"
  - id: 6.3
    description: "Add --related flag to show delta"
  - id: 6.4
    description: "Add --related flag to show requirement"
  - id: 6.5
    description: "Add --related flag to show issue"
  - id: 6.6
    description: "Add --related --json output structure for all 4 commands"
  - id: 6.7
    description: "Write tests for VT-090-P5-1 through VT-090-P5-5"
risks:
  - description: "Per-kind registry loading may need careful import patterns to avoid circular imports"
    mitigation: "Use lazy imports matching existing show.py patterns"
  - description: "show issue currently uses inline lambda formatters, not dedicated functions"
    mitigation: "Extract to proper format function as part of --related integration"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-090.PHASE-06
```

# Phase 06 — P5 Neighbourhood View (`show --related`)

## 1. Objective

Add a `--related` flag to `show spec`, `show delta`, `show requirement`, and `show issue` (the four primary navigation anchors per DEC-090-13). When passed, the output includes a full one-hop "Referenced by" neighbourhood listing — forward references (what this entity references) and reverse references (what references this entity), grouped by kind.

For `show spec`, `--related` **replaces** the count-based "Related:" section (DEC-090-08, internal review finding #3).

## 2. Links & References

- **Delta**: DE-090
- **Design Revision Sections**: DR-090 §P5-1
- **Specs / PRODs**: PROD-010.FR-005
- **Design Decisions**: DEC-090-12 (one-hop only), DEC-090-13 (4 anchor kinds), DEC-090-15 (per-kind registry loading)
- **Prerequisites**: P4 infrastructure (collect_references, find_related_to, load_all_artifacts, partition_by_reverse_references)

## 3. Entrance Criteria

- [x] Phase 05 complete (P4 reverse reference filtering landed, commit e31eca9)
- [x] DR-090 §P5 design approved

## 4. Exit Criteria / Done When

- [x] `format_related_section()` in `relation_formatters.py`
- [x] `--related` flag on `show spec` (replaces count view)
- [x] `--related` flag on `show delta`
- [x] `--related` flag on `show requirement`
- [x] `--related` flag on `show issue`
- [x] `--related --json` output includes `related` key with `forward` + `referenced_by` structure
- [x] Entity with no references → no "Referenced by" section
- [x] Per-kind registry loading (DEC-090-15)
- [x] VT-090-P5-1 through VT-090-P5-5 passing
- [ ] Lint clean (ruff binary not available in env; AST-parses clean, patterns match existing code)

## 5. Verification

- `pytest supekku/scripts/lib/formatters/relation_formatters_test.py -v`
- `pytest supekku/cli/show_test.py -v`
- `just` (full suite)

## 6. Assumptions & STOP Conditions

- Assumes P4 infrastructure (collect_references, find_related_to, load_all_artifacts) working and committed
- Assumes existing show spec already has reverse lookup counts (P2 work)
- STOP if: Per-kind registry loading reveals circular import issues not solvable with lazy imports

## 7. Tasks & Progress

| Status | ID  | Description                          | Parallel? | Notes                                       |
| ------ | --- | ------------------------------------ | --------- | ------------------------------------------- |
| [x]    | 6.1 | `format_related_section()` formatter | [x]       | relation_formatters.py                      |
| [x]    | 6.2 | `--related` on `show spec`           | [ ]       | Replaces count view; loads 7 registry types |
| [x]    | 6.3 | `--related` on `show delta`          | [x]       | Loads audit/revision/backlog registries     |
| [x]    | 6.4 | `--related` on `show requirement`    | [x]       | Loads delta/adr/policy/standard registries  |
| [x]    | 6.5 | `--related` on `show issue`          | [x]       | Loads delta registries                      |
| [x]    | 6.6 | `--related --json` output            | [ ]       | forward + referenced_by structure           |
| [x]    | 6.7 | Tests (VT-090-P5-1 through P5-5)     | [ ]       | 13 tests (5 formatter + 8 integration)      |

### Task Details

- **6.1 — `format_related_section()`**
  - **Files**: `supekku/scripts/lib/formatters/relation_formatters.py`
  - **Design**: Pure function taking `reverse_refs_by_kind: dict[str, list[tuple[str, str]]]` (kind → [(id, name), ...]). Returns formatted lines per DR-090 §P5-1 template. Empty dict → empty list.

- **6.2 — `show spec --related`**
  - **Files**: `supekku/cli/show.py`
  - **Design**: Add `--related` option. When set:
    1. Forward refs: `collect_references(spec)` → group by inferred kind from target ID prefix
    2. Reverse refs: Load per-kind registries (ChangeRegistry for delta/revision/audit, DecisionRegistry, RequirementsRegistry, PolicyRegistry, StandardRegistry), call `find_related_to()` on each
    3. Rendered: append `format_related_section()` output, **replacing** the count-based "Related:" section
    4. JSON: add `related` key with `forward` + `referenced_by` sub-keys
  - **Per-kind registries** (DEC-090-15): ChangeRegistry(delta), ChangeRegistry(revision), ChangeRegistry(audit), DecisionRegistry, RequirementsRegistry, PolicyRegistry, StandardRegistry

- **6.3 — `show delta --related`**
  - **Files**: `supekku/cli/show.py`
  - **Design**: Same pattern. Reverse registries: ChangeRegistry(audit), ChangeRegistry(revision), BacklogRegistry
  - Already has linked_audits/linked_revisions from P2; `--related` expands to full neighbourhood including backlog items

- **6.4 — `show requirement --related`**
  - **Files**: `supekku/cli/show.py`
  - **Design**: Reverse registries: ChangeRegistry(delta), DecisionRegistry, PolicyRegistry, StandardRegistry

- **6.5 — `show issue --related`**
  - **Files**: `supekku/cli/show.py`
  - **Design**: Reverse registries: ChangeRegistry(delta). Currently uses inline lambda for formatting — will need to extract or augment.

- **6.6 — JSON output**
  - **Structure** (per DR-090):
    ```json
    {
      "related": {
        "forward": [
          { "type": "informs", "target": "SPEC-110", "source": "relation" }
        ],
        "referenced_by": {
          "delta": [{ "id": "DE-009", "name": "CLI JSON fixes" }],
          "revision": [{ "id": "RE-024", "name": "..." }]
        }
      }
    }
    ```

## 8. Risks & Mitigations

| Risk                                                  | Mitigation                                                          | Status |
| ----------------------------------------------------- | ------------------------------------------------------------------- | ------ |
| Circular imports from lazy registry loading           | Follow existing show.py patterns (lazy import inside function body) | open   |
| show issue uses inline lambdas, not proper formatters | Extract or extend inline formatting to accommodate --related        | open   |
| Performance with many registries loaded               | Per-kind loading (DEC-090-15); current corpus ~150 artifacts        | open   |

## 9. Decisions & Outcomes

- Following DR-090 §P5 design with DEC-090-12 (one-hop), DEC-090-13 (4 anchor kinds), DEC-090-15 (per-kind loading)

## 10. Findings / Research Notes

- `show spec` already has reverse lookup counts (P2) — `--related` replaces this section
- `show delta` already has linked_audits/linked_revisions (P2) — `--related` extends to full neighbourhood
- `show requirement` currently has no reverse lookups — new capability
- `show issue` currently has minimal formatting (inline lambda) — may need more structure
- `load_all_artifacts()` from P4 (cli/common.py) can be reused for registry loading, but DR suggests per-kind loading directly for finer control

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
