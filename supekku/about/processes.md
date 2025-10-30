# Process Overview

A quick reference for the core workflows in Vice's agentic development loop. Each process links the relevant specs, templates, and artefacts.

## Spec Creation
- **Tech spec**: `just new-spec "Component Name"` (defaults to tech)
- **Product spec**: `just new-spec -- --type product "Capability Name"`
- Fill out the generated `SPEC-XXX.md` / `PROD-XXX.md` using the templates under `supekku/templates/`
- Optional `SPEC-XXX.tests.md` for detailed testing guidance
- Use `just supekku::sync-spec --allow-missing-go <package>` to bootstrap conceptual specs even before Go code exists

## Backlog Capture
- Issues: `just supekku::new-issue "Title"`
- Problems: `just supekku::new-problem "Title"`
- Improvements: `just supekku::new-improvement "Title"`
- Risks: `just supekku::new-risk "Title"`
- Append to shared backlog list: `just supekku::backlog-append`
- All items live under `backlog/` and feed delta scoping

## Delta Lifecycle
1. Scaffold with `just supekku:delta-new "Title" [-- --spec SPEC-### --requirement SPEC-###.FR-###]`
2. Populate `DE-XXX.md` describing scope, inputs, risks, commit references
3. Maintain companion design artefact (`DR-XXX.md`), implementation plan (`IP-XXX.md`), and phase sheets under `phases/`
4. After merge, archive under `archive/deltas/`

## Design Revision
- Template guidance lives in `supekku/templates/implementation-plan-template.md` and accompanying design notes
- Elaborates code-level changes, interfaces, and testing updates for a delta

## Implementation Planning
- `IP-XXX.md` documents phases, entrance/exit criteria, and success criteria (template: `supekku/templates/implementation-plan-template.md`)
- Phase execution sheets live under `change/deltas/DE-XXX/phases/` using `supekku/templates/phase-sheet-template.md`
- Numbered phases map to execution order; tasks expand as work progresses

## Implementation Execution
- Agents follow the design revision + plan
- Update tests per Section 7 of the tech spec / testing companion
- Ensure verification gates in spec, delta, and plan are satisfied

## Audit / Patch-Level Review
- Template: `supekku/templates/audit-template.md`
- Validates code against PROD/SPEC truths (truth-to-code and code-to-truth)
- Findings feed back into backlog, deltas, or spec revisions

## Spec Maintenance
- When behaviour deviates from the spec, update SPEC-XXX and record change history
- Use audits to confirm the spec matches reality after each change

## Spec Revision Workflow
- Draft a revision with `just supekku::new-revision "Summary"` and link source/destination specs plus requirements
- Use `uv run python supekku/scripts/requirements.py move SPEC-AAA.FR-### SPEC-BBB --introduced-by RE-###` to migrate requirements while keeping lifecycle data aligned
- Once the revision is approved, proceed to delta planning/execution as above

## Architecture Decision Records (ADR) Workflow

### Creating a New ADR
- **New ADR**: `just supekku::decision-registry new "Decision Title" --author "Your Name"`
- Edit the generated `ADR-XXX-slug.md` file with:
  - Context: problem statement requiring a decision
  - Decision: chosen approach with rationale
  - Consequences: expected outcomes and trade-offs
  - Update frontmatter relationships: `related_decisions`, `specs`, `requirements`, etc.

### Managing ADR Lifecycle
- **Draft → Proposed**: Update `status: proposed` when ready for review
- **Proposed → Accepted**: Update `status: accepted` after approval
- **Status changes**: Use `deprecated`, `superseded`, `rejected` as appropriate
- **Sync registry**: `just supekku::decision-registry sync` (rebuilds symlinks automatically)

### ADR Registry Operations
- **List ADRs**: `just supekku::decision-registry list`
- **Filter by status**: `just supekku::decision-registry list --status accepted`
- **Show ADR details**: `just supekku::decision-registry show ADR-061`
- **Validate references**: `just supekku::registry-validate` (detects broken ADR references)

### Status Directories
- `specify/decisions/accepted/` - Symlinks to accepted ADRs (auto-maintained)
- `specify/decisions/draft/` - Symlinks to draft ADRs
- `specify/decisions/deprecated/` - Symlinks to deprecated ADRs
- Symlinks are automatically updated when ADR status changes

## Testing Strategy Maintenance
- Keep Section 7 of each SPEC current
- When detail exceeds inline sections, expand `SPEC-XXX.tests.md`
- Testing companion template: `supekku/templates/tech-testing-template.md`

## Multi-Language Documentation Sync

- **Sync all languages**: `uv run python supekku/scripts/sync_specs.py`
- **Sync specific language**: `uv run python supekku/scripts/sync_specs.py --language go|python|typescript`
- **Sync specific targets**: `uv run python supekku/scripts/sync_specs.py --targets go:internal/package python:module.py`
- **Check mode** (validate without writing): `uv run python supekku/scripts/sync_specs.py --check`
- **Existing sources only**: `uv run python supekku/scripts/sync_specs.py --existing`

### Language-Specific Workflows

**Go Package Documentation**:
- Auto-discovers Go packages or specify explicit targets: `--targets go:internal/application/services/git`
- Generates `public` and `internal` variants using gomarkdoc
- Creates symlinks under `specify/tech/by-language/go/` and `by-package/`

**Python Module Documentation**:
- Auto-discovers Python modules or specify explicit targets: `--targets python:supekku/scripts/lib/workspace.py`
- Generates `api`, `implementation`, and `tests` variants using AST analysis
- Creates symlinks under `specify/tech/by-language/python/`

**TypeScript Support** (stub):
- Basic identifier support for `.ts`, `.tsx` files: `--targets typescript:src/components/Button.tsx`
- Auto-discovery not yet implemented - use explicit targets
- Full implementation pending (TypeDoc integration)

### Registry Management

- **Migrate to v2 format**: `uv run python supekku/scripts/migrate_spec_registry_v2.py`
- Registry supports multi-language source tracking with backwards compatibility
- Symlink indices automatically rebuilt: `by-language/`, `by-package/`, `by-slug/`

### Justfile Commands (Recommended)

- **Sync all languages**: `just supekku::sync-all` (recommended default)
- **Language-specific sync**: `just supekku::sync-go`, `just supekku::sync-python`, `just supekku::sync-typescript`
- **Flexible language targeting**: `just supekku::sync-lang python`
- **Specific targets**: `just supekku::sync-targets go:internal/package python:module.py`
- **Check mode**: `just supekku::sync-check`
- **Existing sources only**: `just supekku::sync-existing`
- **Registry migration**: `just supekku::migrate-registry`

### Legacy Compatibility

- Old Go-only commands still supported for backwards compatibility:
  - `just supekku::sync-specs [<package> ...]`

## Validation & Registries
- Refresh change registries: `just supekku::change-registry [<kind>]`
- Regenerate requirement registry: `just supekku::sync-requirements`
- Validate overall workspace integrity (relations, lifecycle links): `just supekku::validate-workspace`
