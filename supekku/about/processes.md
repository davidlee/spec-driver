# Process Overview

A quick reference for the core workflows in Vice's agentic development loop. Each process links the relevant specs, templates, and artefacts.

## Spec Creation
- **Tech spec**: `uv run spec-driver create spec "Component Name"` (defaults to tech)
- **Product spec**: `uv run spec-driver create spec --type product "Capability Name"`
- Fill out the generated `SPEC-XXX.md` / `PROD-XXX.md` using the templates under `.spec-driver/templates/`
- Optional `SPEC-XXX.tests.md` for detailed testing guidance
- Use `uv run spec-driver sync --allow-missing-source go:<package>` to bootstrap conceptual specs even before Go code exists

## Backlog Capture
- Issues: `uv run spec-driver create issue "Title"`
- Problems: `uv run spec-driver create problem "Title"`
- Improvements: `uv run spec-driver create improvement "Title"`
- Risks: `uv run spec-driver create risk "Title"`
- Prioritize backlog: `uv run spec-driver list backlog -p` (opens editor to reorder items)
- All items live under `backlog/` and feed delta scoping

## Delta Lifecycle
1. Scaffold with `uv run spec-driver create delta "Title" --spec SPEC-### --requirement SPEC-###.FR-###`
2. Populate `DE-XXX.md` describing scope, inputs, risks, commit references
3. Maintain companion design artefact (`DR-XXX.md`), implementation plan (`IP-XXX.md`), and phase sheets under `phases/`
4. Complete with `uv run spec-driver complete delta DE-XXX`

## Design Revision
- Template guidance lives in `.spec-driver/templates/implementation-plan-template.md` and accompanying design notes
- Elaborates code-level changes, interfaces, and testing updates for a delta

## Implementation Planning
- `IP-XXX.md` documents phases, entrance/exit criteria, and success criteria (template: `.spec-driver/templates/implementation-plan-template.md`)
- Phase execution sheets live under `change/deltas/DE-XXX/phases/` using `.spec-driver/templates/phase-sheet-template.md`
- Numbered phases map to execution order; tasks expand as work progresses

## Implementation Execution
- Agents follow the design revision + plan
- Update tests per Section 7 of the tech spec / testing companion
- Ensure verification gates in spec, delta, and plan are satisfied

## Audit / Patch-Level Review
- Template: `.spec-driver/templates/audit-template.md`
- Validates code against PROD/SPEC truths (truth-to-code and code-to-truth)
- Findings feed back into backlog, deltas, or spec revisions

## Spec Maintenance
- When behaviour deviates from the spec, update SPEC-XXX and record change history
- Use audits to confirm the spec matches reality after each change

## Spec Revision Workflow
- Draft a revision with `uv run spec-driver create revision "Summary"` and link source/destination specs plus requirements
- Edit the generated `RE-XXX.md` to document requirement moves and spec changes
- Once the revision is approved, proceed to delta planning/execution as above

## Architecture Decision Records (ADR) Workflow

### Creating a New ADR
- **New ADR**: `uv run spec-driver create adr "Decision Title"`
- Edit the generated `ADR-XXX-slug.md` file with:
  - Context: problem statement requiring a decision
  - Decision: chosen approach with rationale
  - Consequences: expected outcomes and trade-offs
  - Update frontmatter relationships: `related_decisions`, `specs`, `requirements`, etc.

### Managing ADR Lifecycle
- **Draft → Proposed**: Update `status: proposed` when ready for review
- **Proposed → Accepted**: Update `status: accepted` after approval
- **Status changes**: Use `deprecated`, `superseded`, `rejected` as appropriate
- **Sync registry**: `uv run spec-driver sync --adr` (rebuilds symlinks automatically)

### ADR Registry Operations
- **List ADRs**: `uv run spec-driver list adrs`
- **Filter by status**: `uv run spec-driver list adrs --status accepted`
- **Show ADR details**: `uv run spec-driver show adr ADR-061`
- **Validate references**: `uv run spec-driver validate` (detects broken ADR references)

### Status Directories
- `specify/decisions/accepted/` - Symlinks to accepted ADRs (auto-maintained)
- `specify/decisions/draft/` - Symlinks to draft ADRs
- `specify/decisions/deprecated/` - Symlinks to deprecated ADRs
- Symlinks are automatically updated when ADR status changes

## Testing Strategy Maintenance
- Keep Section 7 of each SPEC current
- When detail exceeds inline sections, expand `SPEC-XXX.tests.md`
- Testing companion template: `.spec-driver/templates/tech-testing-template.md`

## Multi-Language Documentation Sync

- **Sync all languages**: `uv run spec-driver sync`
- **Sync specific language**: `uv run spec-driver sync --language go|python|typescript`
- **Sync specific targets**: `uv run spec-driver sync go:internal/package python:module.py`
- **Check mode** (validate without writing): `uv run spec-driver sync --check`
- **Existing sources only**: `uv run spec-driver sync --existing`

### Language-Specific Workflows

**Go Package Documentation**:
- Auto-discovers Go packages or specify explicit targets: `--targets go:internal/application/services/git`
- Generates `public` and `internal` variants using gomarkdoc
- Creates symlinks under `specify/tech/by-language/go/` and `by-package/`

**Python Module Documentation**:
- Auto-discovers Python modules or specify explicit targets: `--targets python:.spec-driver/scripts/lib/workspace.py`
- Generates `api`, `implementation`, and `tests` variants using AST analysis
- Creates symlinks under `specify/tech/by-language/python/`

**TypeScript Support** (stub):
- Basic identifier support for `.ts`, `.tsx` files: `--targets typescript:src/components/Button.tsx`
- Auto-discovery not yet implemented - use explicit targets
- Full implementation pending (TypeDoc integration)

### Registry Management

- Registry supports multi-language source tracking with backwards compatibility
- Symlink indices automatically rebuilt: `by-language/`, `by-package/`, `by-slug/`

## Validation & Registries
- Sync all registries (changes, requirements, backlog): `uv run spec-driver validate --sync`
- Validate workspace integrity (relations, lifecycle links): `uv run spec-driver validate`