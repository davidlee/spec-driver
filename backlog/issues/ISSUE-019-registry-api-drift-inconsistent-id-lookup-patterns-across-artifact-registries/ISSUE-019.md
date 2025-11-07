---
id: ISSUE-019
name: 'Registry API drift: inconsistent ID lookup patterns across artifact registries'
created: '2025-11-04'
updated: '2025-11-04'
status: open
kind: issue
categories: [architecture, technical-debt]
severity: p2
impact: developer
---

# Registry API drift: inconsistent ID lookup patterns across artifact registries

## Problem

Registries have evolved with inconsistent APIs for ID-based artifact lookup, making it impossible to implement generic "resolve any artifact ID to path" functionality without type-specific logic. This blocks features like universal `tag` or `edit` commands that work with any artifact type.

## Current State

**Three different ID lookup patterns:**

1. **`get(id)` pattern**: SpecRegistry only
   ```python
   spec = spec_registry.get("SPEC-001")  # Returns Spec | None
   ```

2. **`find(id)` pattern**: DecisionRegistry, StandardRegistry, PolicyRegistry
   ```python
   adr = decision_registry.find("ADR-023")  # Returns DecisionRecord | None
   ```

3. **No basic lookup**: RequirementsRegistry, ChangeRegistry, BacklogRegistry
   ```python
   # Must use collect() then dict lookup or custom filters
   artifacts = change_registry.collect()
   delta = artifacts.get("DE-005")  # Workaround
   ```

**Architectural inconsistency:**
- Backlog is functional (`discover_backlog_items()`) vs class-based registries
- SpecRegistry uses `reload()` while others use `sync()`
- Different collection methods: `all_specs()` vs `collect()` vs `discover_*()`

## Impact

- **Cannot build generic artifact resolution** - each registry needs custom logic
- **API confusion** - developers must remember which registry uses `get()` vs `find()` vs neither
- **Maintenance burden** - patterns diverge further as new registries are added
- **Inconsistent developer experience** - same conceptual operation has different APIs

## Evidence

Analysis of auto-generated contracts in `specify/tech/by-package/supekku/scripts/lib/*/spec/contracts/*-registry-public.md` shows:

| Registry | ID Lookup Method | Notes |
|----------|-----------------|-------|
| Specs | `get(id)` | Only registry using `get()` |
| Decisions | `find(id)` | Newer pattern |
| Standards | `find(id)` | Follows Decisions pattern |
| Policies | `find(id)` | Follows Decisions pattern |
| Changes | ❌ None | Has `find_by_implements()` only |
| Requirements | ❌ None | Uses `search()` with complex filters |
| Backlog | ❌ None | Uses `discover_backlog_items()` |

**Convergence observed**: Recent registries (Decisions, Standards, Policies) share common patterns:
- `collect() -> dict[str, Record]`
- `find(id) -> Record | None`
- `filter(...) -> list[Record]`
- `iter(status=...) -> Iterator[Record]`

## Proposed Solution

**Hybrid approach** (incremental, low-risk):

1. **Immediate** - Add `find(id)` to ChangeRegistry
   - High value (unblocks DE/RE/AUD lookup)
   - Low risk (isolated change)
   - Follows emerging convention

2. **Short-term** - Build artifact resolver in `supekku/scripts/lib/core/artifact_resolution.py`
   - Handles current inconsistencies
   - Pattern-matches ID to determine registry
   - Delegates to appropriate lookup method
   - Documents current state

3. **Long-term** - Gradual API normalization
   - Standardize on `find(id)` pattern (deprecate `get()`)
   - Add `find(id)` to remaining registries where applicable
   - Convert Backlog to class-based registry
   - Document migration path in ADR

## Acceptance Criteria

- [ ] ChangeRegistry has `find(id)` method
- [ ] Artifact resolver can resolve all major ID types to paths
- [ ] Tests cover resolution for: SPEC, PROD, ADR, DE, RE, AUD, ISSUE, PROB, IMPR, RISK
- [ ] Documentation explains current patterns and convergence path
- [ ] ADR created if breaking changes needed for normalization

## References

- Auto-generated contracts: `specify/tech/by-package/supekku/scripts/lib/*/spec/contracts/*-registry-public.md`
- ID patterns: `supekku/scripts/lib/blocks/verification_metadata.py:19-22`
- Workspace facade: `supekku/scripts/lib/workspace.py:20`
