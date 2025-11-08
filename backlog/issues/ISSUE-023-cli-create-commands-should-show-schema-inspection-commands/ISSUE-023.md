---
id: ISSUE-023
name: CLI create commands should show schema inspection commands
created: '2025-11-08'
updated: '2025-11-08'
status: open
kind: issue
categories: [cli, ux, discoverability]
severity: p3
impact: user
---

# CLI create commands should show schema inspection commands

## Problem Statement

When users run `spec-driver create` commands (delta, phase, revision, etc.), the output shows the created file path but doesn't provide guidance on how to inspect the YAML schemas within the generated document.

**Current behavior:**
```bash
$ spec-driver create phase --plan IP-019 "Phase 1"
Phase created: IP-019.PHASE-01
/home/user/project/change/deltas/DE-019/phases/phase-01.md
```

Users must separately discover that they can run `spec-driver schema show <schema-name>` to understand the structure and fields of the YAML frontmatter blocks in the generated files.

## Expected Behavior

After creating an artifact, the CLI should output the relevant schema inspection commands for all YAML blocks present in the generated template:

```bash
$ spec-driver create phase --plan IP-019 "Phase 1"
Phase created: IP-019.PHASE-01

Inspect schemas with:
  spec-driver schema show phase.overview
  spec-driver schema show phase.tracking

/home/user/project/change/deltas/DE-019/phases/phase-01.md
```

This improves discoverability and reduces friction for users learning the spec-driver workflow.

## Implementation Considerations

### 1. Template → Schema Mapping

Need centralized mapping of templates to their embedded schemas. Currently schemas are defined in `supekku/scripts/lib/core/frontmatter_schema.py` but there's no explicit mapping from template files to which schemas they contain.

**Options:**

**A. Embed schema metadata in template files**
Add YAML comment at top of each template listing schemas:
```markdown
<!-- schemas: phase.overview, phase.tracking -->
---
id: ...
```

**B. Central mapping in code**
Create mapping in `supekku/scripts/lib/core/` (e.g., `template_schemas.py`):
```python
TEMPLATE_SCHEMAS = {
    "phase-sheet-template.md": ["phase.overview", "phase.tracking"],
    "implementation-plan-template.md": ["plan.overview", "verification.coverage"],
    "delta-template.md": ["delta.overview", "verification.coverage"],
    # ...
}
```

**C. Parse templates to detect schemas**
Scan template files for `schema: <name>` in YAML blocks at generation time.
- Pro: No duplicate maintenance
- Con: Runtime parsing overhead, fragile to template changes

### 2. Output Location

Show schema commands after success message, before file path:
```
<Entity> created: <ID>

Inspect schemas with:
  spec-driver schema show <schema1>
  spec-driver schema show <schema2>

<file-path>
```

### 3. Affected Commands

All `spec-driver create` commands that generate templated files:
- `create delta`
- `create phase`
- `create revision`
- `create requirement`
- `create audit`
- Any future create commands

## Proposed Solution

1. **Add central mapping**: Create `supekku/scripts/lib/core/template_schemas.py` with template-to-schema mapping
2. **Update create commands**: Each create command calls helper function to get schema list for its template
3. **Add output helper**: Create `print_schema_inspection_commands(schemas: list[str])` utility
4. **Update all create commands**: Insert schema command output between success message and file path

## Benefits

- **Improved discoverability**: Users learn about schema inspection without reading docs
- **Better UX**: Contextual help exactly when users need it (right after creating a file)
- **Reduced support burden**: Users self-serve schema documentation
- **Consistency**: All create commands provide same helpful output pattern

## Open Questions

- [ ] Should schema commands be shown for ALL create operations, or only first-time (per session)?
- [ ] Should we also show example: `spec-driver schema show phase.overview --format=yaml-example`?
- [ ] Where is the most appropriate shared location for template→schema mapping?
  - `supekku/scripts/lib/core/template_schemas.py` (new module)
  - Add to existing `supekku/scripts/lib/core/templates.py`
  - Embed in template files themselves as metadata comments
  - Other?

## Related

- Existing schema command: `spec-driver schema show <schema-name>`
- Templates location: `.spec-driver/templates/`
- Schema definitions: `supekku/scripts/lib/core/frontmatter_schema.py`

## Success Criteria

- [ ] All `create` commands output schema inspection commands
- [ ] Template→schema mapping is DRY (single source of truth)
- [ ] Output format is consistent across all create commands
- [ ] No performance regression from template parsing/mapping
