# Requirement Lifecycle & Traceability

## Core Concept

**Status is manual. Traceability is automatic.**

## The Two Parallel Systems

### 1. Status Field (Manual)
```yaml
status: pending → in_progress → implemented → verified
```
- You control this via direct registry edits
- No automatic transitions
- No validation enforcement
- Pure lifecycle indicator

### 2. Traceability Arrays (Automatic via sync)
```yaml
implemented_by: [DE-002, DE-005]  # Deltas with "implements" relations
verified_by: [AUD-001, AUD-003]   # Audits with "verifies" relations
```
- Populated automatically by `spec-driver sync`
- Based on frontmatter `relations:` blocks
- Independent of status field
- Can be empty at any status

## How Relations Work

### Deltas → `implemented_by[]`
```yaml
# In change/deltas/DE-XXX/DE-XXX.md
relations:
  - type: implements
    target: PROD-001.FR-001
```
OR structured block:
```yaml
```yaml supekku:delta.relationships@v1
requirements:
  implements:
    - PROD-001.FR-001
```
```

### Audits → `verified_by[]`
```yaml
# In change/audits/AUD-XXX/AUD-XXX.md
relations:
  - type: verifies
    target: PROD-001.FR-001
```

## Practical Workflows

### Prospective (Delta-driven)
1. Create delta: `uv run spec-driver create delta <slug>` (scaffolds delta, design revision, implementation plan, first phase, notes)
2. Populate the design revision (architecture intent, code impacts, verification alignment)
3. Add `implements` relations in delta frontmatter
4. Complete implementation work

FIXME: no longer necessary - instead run `spec-driver delta complete`
> 5. Mark delta complete: `status: completed` in frontmatter
> 6. **Manually edit** `.spec-driver/registry/requirements.yaml`: `status: implemented`
7. Run `uv run spec-driver validate --sync` → populates `implemented_by[]`

### Retrospective (Audit-driven)
1. Code already exists (no delta was created)
2. Create audit: manually in `change/audits/AUD-XXX/`
3. Add `verifies` relations in audit frontmatter
4. Run `uv run spec-driver sync` → populates `verified_by[]`
5. **Manually edit** `.spec-driver/registry/requirements.yaml`: `status: verified`

### Hybrid (Both)
A requirement can have both:
```yaml
status: verified           # Manual
implemented_by: [DE-002]   # Delta implemented it
verified_by: [AUD-001]     # Audit verified it
```
This is ideal - full traceability!

## Key Insights

1. **Audits are for retroactive documentation** - when spec-driver is applied to existing code
2. **Deltas are for planned changes** - SPEC → change → code
3. **Status ≠ Arrays** - You can have `status: verified` with empty arrays (not recommended, but valid)
4. **No conflicts** - Deltas and audits coexist peacefully in their respective arrays
5. **Sync is safe** - Re-running never changes status, only updates arrays based on relations

## The Manual Step

```bash
# After sync, you MUST manually edit:
.spec-driver/registry/requirements.yaml

# Change:
PROD-001.FR-001:
  status: pending  # ← Edit this

# To:
PROD-001.FR-001:
  status: verified  # ← Or implemented, in_progress, etc.
```

**No CLI command exists yet** for `spec-driver requirements set-status`.

## Status Semantics

| Status | Meaning | Typical `implemented_by` | Typical `verified_by` |
|--------|---------|--------------------------|----------------------|
| `pending` | Not started | `[]` | `[]` |
| `in_progress` | Delta assigned, work ongoing | `[DE-XXX]` (draft/in-progress) | `[]` |
| `active` | Delta complete, code deployed | `[DE-XXX]` (completed) | `[]` or `[AUD-XXX]` |
| `verified` | Audit confirms alignment | `[DE-XXX]` or `[]` | `[AUD-XXX]` |

## Complete Example

```yaml
# After prospective implementation:
PROD-005.FR-001:
  status: active            
  implemented_by: [DE-002]  # Auto: sync found DE-002's "implements" relation
  verified_by: []           # Auto: no audits yet

# After retrospective audit:
PROD-005.FR-001:
  status: verified          # Manual: You updated this
  implemented_by: [DE-002]  # Auto: unchanged
  verified_by: [AUD-002]    # Auto: sync found AUD-002's "verifies" relation
```

## Reference

Full workflow: `docs/delta-completion-workflow.md`
Glossary: `supekku/about/glossary.md`
Requirements logic: `supekku/scripts/lib/requirements/registry.py:375-390`
