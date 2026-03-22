# Notes for DE-106

## Context Assembly Guide

Use this section first when reloading context for DE-106.

### Current Position

- `DE-106` is scoped for design work, not implementation.
- The current recommended direction is:
  - keep machine-readable phase metadata
  - keep it once
  - make frontmatter the long-term canonical summary surface
  - keep markdown body for rich execution detail
- The delta scope was intentionally widened to include completing metadata-driven frontmatter validation along the affected path, because the current weakness appears to be under-finished infrastructure rather than a reason to prefer body-embedded authoritative YAML.
- An ADR is intended as part of this delta to record the placement rule for frontmatter vs code-fenced YAML vs markdown prose.

### Read These First

- [DE-106](./DE-106.md)
- [DR-106](./DR-106.md)
- [IP-106](./IP-106.md)
- [IMPR-022](../../backlog/improvements/IMPR-022-phase_sheet_template_dry_eliminate_triple_entry_bookkeeping_across_frontmatter_blocks_and_markdown/IMPR-022.md)
- [DE-004](../DE-004-phase-management-implementation/DE-004.md)
- [DE-104](../DE-104-phase_status_lifecycle_enum_registration_frontmatter_sync_and_data_normalisation/DE-104.md)

### Key Code Surfaces

- [phase template](/workspace/spec-driver/supekku/templates/phase.md)
- [phase creation](/workspace/spec-driver/supekku/scripts/lib/changes/creation.py)
- [delta/phase artifact loading](/workspace/spec-driver/supekku/scripts/lib/changes/artifacts.py)
- [delta formatting](/workspace/spec-driver/supekku/scripts/lib/formatters/change_formatters.py)
- [workspace validation](/workspace/spec-driver/supekku/scripts/lib/validation/validator.py)
- [phase block parsing/validation](/workspace/spec-driver/supekku/scripts/lib/blocks/plan.py)
- [phase/plan block metadata](/workspace/spec-driver/supekku/scripts/lib/blocks/plan_metadata.py)
- [frontmatter validation](/workspace/spec-driver/supekku/scripts/lib/core/frontmatter_schema.py)
- [frontmatter metadata registry](/workspace/spec-driver/supekku/scripts/lib/core/frontmatter_metadata/__init__.py)
- [plan/phase/task frontmatter metadata](/workspace/spec-driver/supekku/scripts/lib/core/frontmatter_metadata/plan.py)

### Important Findings Already Established

- Current phase authority is split across `phase.overview`, `phase.tracking`, and markdown body.
- Current runtime consumers mostly want compact summary data, not the full duplicated block content.
- The repo already has richer frontmatter metadata definitions for `kind: phase`, but the normal frontmatter validation path still mostly enforces base fields.
- This means the frontmatter path is under-enforced, not absent.
- The practical recommendation is therefore to invest in frontmatter validation rather than treat current block-centric code as the target architecture.

### Open Design Questions

- Which fields belong in the canonical phase summary beyond `id`, lineage, `status`, and `objective`?
- Should historical phases be bulk-migrated in DE-106 or supported via compatibility-first reads?
- How far should frontmatter-validation completion go in this delta before additional work becomes a follow-on delta or backlog item?
- Does spec reconciliation for PROD-006 land directly here, or via a revision-first step?

### Intended Deliverables

- Updated DE/DR with approved design direction
- implementation-ready plan only after the above design questions are narrowed
- ADR defining:
  - when metadata belongs in frontmatter
  - when it belongs in code-fenced YAML
  - when it should remain markdown prose
- Explicit backlog items or follow-on deltas for any adjacent work discovered but kept out of scope

### Recommended Next Step

DR-106 has passed internal and external adversarial review. All open questions resolved. Ready for approval and transition to `/plan-phases`.

### Design Review Summary

- **OQ-001**: Compatibility now, opportunistic migration later
- **OQ-002**: Canonical fields: `plan`, `delta`, `objective`, `entrance_criteria`, `exit_criteria`
- **OQ-003**: Follow ADR-004 — spec reconciliation after implementation
- **OQ-004**: Phase model is the Pydantic spike (DEC-008); fallback to inline validation if negative
- **Internal review**: 8 findings (R1-R8), all integrated
- **External review**: 4 findings (E1-E4), all integrated — notably E1 (artifacts.py choke point) and E3 (spike must include creation→load round-trip)
- **Doctrine outputs planned**: ADR (placement heuristic), 3 memories, 4 skill updates
