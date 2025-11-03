---
id: SPEC-110
slug: supekku-cli
name: supekku/cli Specification
created: '2025-11-02'
updated: '2025-11-03'
status: draft
kind: spec
responsibilities:
- Provide unified command-line interface for spec-driver operations
- Orchestrate thin command layers that delegate to registries and formatters
- Enforce consistent flag patterns across all list/show/create commands
- Support multiple output formats (table, JSON, TSV) for automation workflows
- Handle user input validation and error reporting with clear exit codes
aliases: []
packages:
- supekku/cli
sources:
- language: python
  identifier: supekku/cli
  module: supekku.cli
  variants:
  - name: api
    path: contracts/api.md
  - name: implementation
    path: contracts/implementation.md
  - name: tests
    path: contracts/tests.md
owners: []
auditers: []
relations: []
---

# SPEC-110 – supekku/cli Specification

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-110
requirements:
  primary:
    - SPEC-110.FR-001
    - SPEC-110.FR-002
    - SPEC-110.FR-003
    - SPEC-110.FR-004
    - SPEC-110.FR-005
    - SPEC-110.FR-006
    - SPEC-110.FR-007
    - SPEC-110.FR-008
    - SPEC-110.FR-009
    - SPEC-110.FR-010
    - SPEC-110.NF-001
    - SPEC-110.NF-002
  collaborators: []
interactions:
  - spec: SPEC-123
    type: uses
    description: Uses SpecRegistry to load and filter specifications for list/show commands
  - spec: SPEC-117
    type: uses
    description: Uses DecisionRegistry to load and manage ADRs; supports separate ADR registry sync
  - spec: SPEC-122
    type: uses
    description: Uses RequirementsRegistry to load, filter, and update requirement lifecycle status
  - spec: SPEC-115
    type: uses
    description: Uses ChangeRegistry and creation functions for delta/revision/audit operations
  - spec: SPEC-120
    type: uses
    description: Uses formatters for table/JSON/TSV output (delegates all display logic)
  - spec: SPEC-125
    type: uses
    description: Uses WorkspaceValidator for workspace integrity validation (validate command)
  - spec: SPEC-TBD
    type: uses
    description: Uses core.repo for repository root detection
  - spec: SPEC-TBD
    type: uses
    description: Uses core.templates for template loading and rendering
  - spec: SPEC-TBD
    type: uses
    description: Uses blocks.metadata and schema_registry for schema commands (blocks and frontmatter)
  - spec: SPEC-TBD
    type: uses
    description: Uses sync adapters for code-to-spec synchronization (Python, Go, TypeScript)
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-110
capabilities:
  - id: unified-cli-interface
    name: Unified CLI Interface
    responsibilities:
      - Provide single entry point (`spec-driver`) for all operations
      - Route commands to appropriate subcommand groups (list, show, create, sync, etc.)
      - Handle version display and help text
      - Ensure consistent CLI UX across all commands
    requirements:
      - SPEC-110.FR-001
      - SPEC-110.NF-001
    summary: |
      Provides unified command-line interface using Typer framework, routing user requests
      to specialized subcommand groups while maintaining consistent UX and error handling.
    success_criteria:
      - All commands accessible via single `spec-driver` entry point
      - Help text available at all levels (--help)
      - Version information accurate and accessible

  - id: thin-orchestration-layer
    name: Thin Orchestration Layer
    responsibilities:
      - Parse command-line arguments and options
      - Load appropriate registries (specs, requirements, changes, decisions)
      - Apply filters based on user-provided flags
      - Delegate formatting to formatter modules
      - Output results and set appropriate exit codes
    requirements:
      - SPEC-110.FR-002
      - SPEC-110.FR-003
      - SPEC-110.FR-004
    summary: |
      Implements "skinny CLI" pattern: commands orchestrate but never implement business logic.
      All filtering, formatting, and data access is delegated to specialized modules.
    success_criteria:
      - CLI files remain <200 lines each
      - Zero business logic in CLI modules (only orchestration)
      - All formatting delegated to formatters package

  - id: standardized-flag-patterns
    name: Standardized Flag Patterns
    responsibilities:
      - Enforce consistent flag naming across all list commands (--format, --json, --filter, --regexp, etc.)
      - Provide reusable option types (FormatOption, JsonOutputOption, StatusOption, RootOption, etc.)
      - Support common filtering patterns (substring, regexp, case-sensitive/insensitive, status)
      - Enable automation-friendly output via --format=json or --json shorthand
    requirements:
      - SPEC-110.FR-005
      - SPEC-110.FR-006
      - SPEC-110.FR-007
    summary: |
      Ensures consistent user experience by standardizing flag patterns across all commands.
      Users learn flag patterns once and apply them everywhere. The --json shorthand improves
      CLI ergonomics for automation workflows, and status filtering enables focused artifact exploration.
    success_criteria:
      - All list commands support --format, --json, --filter, --regexp
      - List specs supports --status/-s for status filtering
      - JSON output parseable and stable across versions
      - Regexp filtering works consistently across all artifact types

  - id: artifact-crud-operations
    name: Artifact CRUD Operations
    responsibilities:
      - Create new artifacts (specs, deltas, revisions, ADRs, backlog items) from templates
      - Show detailed artifact information with formatted display
      - List artifacts with filtering and multiple output formats
      - Complete deltas and update requirement lifecycle status
      - Delegate synchronization to sync adapters
    requirements:
      - SPEC-110.FR-008
      - SPEC-110.FR-009
      - SPEC-110.FR-010
    summary: |
      Provides comprehensive create/read/update operations for all workspace artifacts.
      Commands follow consistent patterns and delegate to registries/formatters.
      Complete workflow automates requirement lifecycle transitions.
    success_criteria:
      - All artifact types have create/list/show commands
      - Templates used for all creation operations
      - Detailed views formatted via dedicated formatters
      - Delta completion updates requirement statuses automatically

  - id: schema-documentation
    name: Schema Documentation
    responsibilities:
      - List available YAML block schemas and frontmatter schemas separately
      - Display schema details in multiple formats (json-schema, yaml-example)
      - Help users understand expected metadata structure for blocks and frontmatter
    requirements:
      - SPEC-110.FR-007
    summary: |
      Provides self-documentation for YAML block schemas (e.g., spec.relationships)
      and frontmatter schemas (e.g., frontmatter.delta), enabling users to understand
      expected structures without consulting external docs.
    success_criteria:
      - Block and frontmatter schemas separately listable via `schema list blocks|frontmatter`
      - Schema details available in JSON Schema and YAML example formats
      - Examples match actual validation schemas
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-110
entries:
  - artefact: VT-CLI-LIST-001
    kind: VT
    requirement: SPEC-110.FR-002
    status: verified
    notes: |
      supekku/cli/test_cli.py - List command tests for specs, deltas, requirements, ADRs
      Tests thin orchestration: args → registry → filter → format → output

  - artefact: VT-CLI-FILTER-001
    kind: VT
    requirement: SPEC-110.FR-005
    status: verified
    notes: |
      supekku/cli/test_cli.py - Filter flag tests (substring, regexp, case-sensitive)
      Tests consistent filtering across all list commands

  - artefact: VT-CLI-FORMAT-001
    kind: VT
    requirement: SPEC-110.FR-006
    status: verified
    notes: |
      supekku/cli/test_cli.py - Output format tests (table, JSON, TSV)
      Tests JSON output is parseable and stable

  - artefact: VT-CLI-CREATE-001
    kind: VT
    requirement: SPEC-110.FR-008
    status: verified
    notes: |
      supekku/cli/create_test.py - Create command tests for all artifact types
      Tests template rendering and file creation

  - artefact: VT-CLI-SHOW-001
    kind: VT
    requirement: SPEC-110.FR-009
    status: verified
    notes: |
      supekku/cli/show_test.py - Show command tests for detailed artifact display
      Tests delegation to formatters

  - artefact: VT-CLI-SCHEMA-001
    kind: VT
    requirement: SPEC-110.FR-007
    status: verified
    notes: |
      supekku/cli/schema_test.py - Schema listing and display tests
      Tests schema documentation commands

  - artefact: VT-CLI-SYNC-001
    kind: VT
    requirement: SPEC-110.FR-004
    status: verified
    notes: |
      supekku/cli/sync_test.py - Sync command tests
      Tests delegation to sync adapters

  - artefact: VT-CLI-BACKFILL-001
    kind: VT
    requirement: SPEC-110.FR-003
    status: verified
    notes: |
      supekku/cli/backfill_test.py - Backfill command tests
      Tests stub detection and template replacement

  - artefact: VT-CLI-COMMON-001
    kind: VT
    requirement: SPEC-110.FR-005
    status: verified
    notes: |
      Tests for common utilities (matches_regexp, option callbacks)
      Tests reusable flag patterns

  - artefact: VT-CLI-COMPLETE-001
    kind: VT
    requirement: SPEC-110.FR-010
    status: verified
    notes: |
      supekku/cli/complete.py - Delta completion with requirement lifecycle updates
      supekku/cli/test_cli.py::TestCompleteCommands - Complete delta tests

  - artefact: VT-CLI-INTEGRATION-001
    kind: VT
    requirement: SPEC-110.NF-001
    status: verified
    notes: |
      supekku/cli/test_cli.py - Integration tests for command responsiveness
      Tests CLI commands complete in <2s for typical operations

  - artefact: VT-CLI-STRUCTURE-001
    kind: VT
    requirement: SPEC-110.FR-001
    status: verified
    notes: |
      supekku/cli/test_cli.py::TestCommandStructure - Verb-noun pattern tests
      supekku/cli/test_cli.py::TestMainApp - Main app structure tests

  - artefact: VT-CLI-REGEXP-001
    kind: VT
    requirement: SPEC-110.FR-005
    status: verified
    notes: |
      supekku/cli/test_cli.py::TestRegexpFiltering - 9 detailed regexp tests
      Tests field-specific filtering, case sensitivity, invalid patterns

  - artefact: VT-CLI-ERROR-001
    kind: VT
    requirement: SPEC-110.NF-002
    status: verified
    notes: |
      supekku/cli/test_cli.py::TestErrorHandling - Invalid command and missing arg tests
      Ensures clear error messages for user input errors

  - artefact: VT-CLI-WORKSPACE-001
    kind: VT
    requirement: SPEC-110.FR-001
    status: verified
    notes: |
      supekku/cli/test_cli.py::TestWorkspaceCommands - Install and validate tests
      Tests workspace initialization and integrity validation

  - artefact: VT-CLI-JSON-001
    kind: VT
    requirement: SPEC-110.FR-005
    status: verified
    notes: |
      supekku/cli/test_cli.py::TestJSONFlagConsistency - 13 tests for --json flag across all list commands
      Tests --json flag equivalence to --format=json and help documentation

  - artefact: VT-CLI-STATUS-FILTER-001
    kind: VT
    requirement: SPEC-110.FR-006
    status: verified
    notes: |
      supekku/cli/test_cli.py::TestStatusFilterParity - 7 tests for --status/-s filter on list specs
      Tests status filtering (draft, active, deprecated, superseded) and JSON integration

  - artefact: VT-CLI-JSON-SCHEMA-001
    kind: VT
    requirement: SPEC-110.FR-006
    status: verified
    notes: |
      supekku/cli/test_cli.py::TestJSONSchemaRegression - 2 tests for JSON output schema stability
      Tests backward compatibility of JSON output structure for specs and deltas

  - artefact: VT-CLI-SHOW-JSON-001
    kind: VT
    requirement: SPEC-110.FR-009
    status: verified
    notes: |
      supekku/cli/test_cli.py::TestShowCommandJSON - 8 tests for --json flag on show commands
      Tests --json flag on show spec, show adr, show requirement, show revision, show delta
```

## 1. Intent & Summary

- **Scope / Boundaries**:
  - IN: Command-line interface, argument parsing, option standardization, command orchestration, output formatting delegation
  - IN: All user-facing commands (list, show, create, sync, schema, backfill, complete, workspace)
  - OUT: Business logic (delegated to registries), display logic (delegated to formatters), validation logic (delegated to validators)
  - OUT: Direct file I/O (delegated to registries and creation functions), template engines (delegated to core.templates)

- **Value Signals**:
  - Single unified interface reduces cognitive load (users learn one tool, not many scripts)
  - Consistent flag patterns enable muscle memory and scripting (<5min to learn patterns)
  - JSON output enables CI/CD automation (100% of operations scriptable)
  - Thin orchestration keeps CLI maintainable (CLI files average <150 lines)

- **Guiding Principles**:
  - **Skinny CLI pattern**: Parse → Load → Filter → Format → Output (no business logic in CLI)
  - **Consistency over features**: Same flags work the same way everywhere
  - **Automation-first**: JSON output stable and parseable for machine consumption
  - **Fail fast**: Validate inputs early, provide clear error messages with actionable guidance
  - **Delegate everything**: Registries for data, formatters for display, core modules for utilities

- **Change History**: Initial implementation in DE-001; extended for ADR support in DE-003; backfill command added in DE-005

## 2. Stakeholders & Journeys

- **Systems / Integrations**:
  - **SpecRegistry (SPEC-123)**: Load and filter specifications
  - **DecisionRegistry (SPEC-117)**: Load and manage ADRs; ADR registry synchronization
  - **RequirementsRegistry (SPEC-122)**: Load, filter, and update requirement lifecycle status
  - **ChangeRegistry (SPEC-115)**: Load deltas, revisions, audits; creation functions
  - **WorkspaceValidator (SPEC-125)**: Validate workspace integrity and cross-references
  - **Formatters (SPEC-120)**: Table/JSON/TSV output for all artifact types
  - **Core modules (SPEC-TBD)**: Repository detection, template rendering, path utilities
  - **Sync adapters (SPEC-TBD)**: Code-to-spec synchronization (Python, Go, TypeScript)
  - **Schema registry (SPEC-TBD)**: YAML block and frontmatter schema documentation
  - **Typer framework**: CLI application framework (external dependency)

- **Primary Journeys / Flows**:

  **Journey 1: Developer Lists Specs**
  1. **Given** a spec-driver workspace
  2. **When** developer runs `spec-driver list specs --filter validation --format=table`
  3. **Then** CLI parses args, loads SpecRegistry, filters by substring "validation"
  4. **And** delegates to `format_spec_list_table()` formatter
  5. **And** outputs formatted table to stdout
  6. **And** exits with code 0

  **Journey 2: CI Script Exports Requirements to JSON**
  1. **Given** a CI/CD pipeline script
  2. **When** script runs `spec-driver list requirements --format=json`
  3. **Then** CLI loads RequirementsRegistry
  4. **And** outputs JSON array of all requirements
  5. **And** script parses JSON for downstream processing
  6. **And** pipeline continues based on requirement status

  **Journey 3: Developer Creates New ADR**
  1. **Given** a need to document an architectural decision
  2. **When** developer runs `spec-driver create adr "Use PostgreSQL for persistence" --status=accepted`
  3. **Then** CLI calls DecisionRegistry creation function with next available ID
  4. **And** template is rendered with title and metadata
  5. **And** file is written to `specify/decisions/ADR-XXX-slug.md`
  6. **And** success message displayed with file path

  **Journey 4: Automation Syncs Code to Specs**
  1. **Given** Python code changes merged to main
  2. **When** CI runs `spec-driver sync --language=python`
  3. **Then** CLI delegates to Python sync adapter
  4. **And** adapter extracts contracts from Python AST
  5. **And** contracts written to `specify/tech/SPEC-XXX/contracts/`
  6. **And** sync summary displayed with counts

  **Journey 5: Developer Explores Available Schemas**
  1. **Given** a developer writing spec frontmatter
  2. **When** developer runs `spec-driver schema show spec.relationships --format=yaml-example`
  3. **Then** CLI loads schema registry
  4. **And** displays YAML example of spec.relationships block
  5. **And** developer copies structure into spec

  **Journey 6: Developer Completes Delta**
  1. **Given** a delta (DE-005) with associated requirements
  2. **When** developer runs `spec-driver complete delta DE-005`
  3. **Then** CLI loads delta and associated requirements
  4. **And** marks delta status as completed
  5. **And** updates associated requirement statuses to 'live' in revision source files
  6. **And** displays completion summary with updated requirements

  **Journey 7: CI Validates Workspace Integrity**
  1. **Given** a PR with spec/requirement/delta changes
  2. **When** CI runs `spec-driver validate --strict`
  3. **Then** CLI delegates to WorkspaceValidator
  4. **And** validates all cross-references (requirements ↔ deltas ↔ specs)
  5. **And** reports any broken references or inconsistencies
  6. **And** exits with code 1 if errors found (blocking merge)

- **Edge Cases & Non-goals**:
  - **OUT OF SCOPE**: Interactive prompts for complex workflows (use declarative flags instead)
  - **OUT OF SCOPE**: Rich TUI/interactive mode (CLI is batch-oriented)
  - **EDGE CASE**: Invalid regexp patterns → CLI catches `re.error` and displays helpful message
  - **EDGE CASE**: Missing repository root → CLI auto-detects or errors with clear guidance
  - **EDGE CASE**: No matches for filter → CLI displays empty result (not an error; exit code 0)
  - **GUARD RAIL**: Unknown artifact IDs → CLI validates existence before operations

## 3. Responsibilities & Requirements

### Capability Overview

The CLI module provides five core capabilities as defined in the YAML block above:

1. **Unified CLI Interface** (FR-001, NF-001): Single entry point routing to specialized subcommands
2. **Thin Orchestration Layer** (FR-002, FR-003, FR-004): Skinny CLI pattern with delegation to registries/formatters
3. **Standardized Flag Patterns** (FR-005, FR-006, FR-007): Consistent flags across all commands
4. **Artifact CRUD Operations** (FR-008, FR-009, FR-010): Create/read/update operations for all artifact types, including lifecycle automation
5. **Schema Documentation** (FR-007): Self-documenting YAML block and frontmatter schemas

### Functional Requirements

- **SPEC-110.FR-001**(cli): CLI MUST provide single unified entry point (`spec-driver`) routing to all subcommand groups (list, show, create, sync, schema, backfill, complete, workspace)
  *Rationale*: Single tool reduces cognitive load and installation complexity
  *Verification*: VT-CLI-LIST-001 - All commands accessible via `spec-driver` main entry point

- **SPEC-110.FR-002**(architecture): List commands MUST delegate all data access to registries and all formatting to formatters (zero business logic in CLI)
  *Rationale*: Skinny CLI pattern keeps code maintainable and testable
  *Verification*: VT-CLI-LIST-001 - Tests verify thin orchestration: args → registry → filter → format → output

- **SPEC-110.FR-003**(automation): Backfill command MUST detect stub specs (status='stub' or ≤30 lines) and replace body with template while preserving frontmatter
  *Rationale*: Enables spec completion workflow (reduces backfill time from 2hrs to 10min)
  *Verification*: VT-CLI-BACKFILL-001 - Stub detection and template replacement tests

- **SPEC-110.FR-004**(integration): Sync command MUST delegate to sync adapters for multi-language code-to-spec synchronization (Python, Go, TypeScript) and MUST support separate ADR registry synchronization via `--adr` flag
  *Rationale*: Thin CLI layer orchestrates; adapters implement language-specific logic; ADR sync is opt-in
  *Verification*: VT-CLI-SYNC-001 - Sync delegation tests, ADR sync flag tests

- **SPEC-110.FR-005**(cli): All list commands MUST support consistent flag patterns (--format, --json, --filter, --regexp, --case-insensitive, --root) and MUST apply regexp filtering to artifact-specific fields:
  - ADRs: title, summary
  - Backlog items: ID, title
  - Changes (deltas/revisions/audits): ID, slug, name
  - Requirements: UID, label, title
  - Specs: ID, slug, name

  The --json flag is a shorthand for --format=json and takes precedence when both are specified.
  *Rationale*: Consistent UX enables muscle memory; field-specific filtering ensures relevant matches; --json shorthand improves CLI ergonomics
  *Verification*: VT-CLI-COMMON-001, VT-CLI-FILTER-001, VT-CLI-REGEXP-001, VT-CLI-JSON-001 - Flag pattern and filtering tests

- **SPEC-110.FR-006**(cli): All list commands MUST support output formats: table (default), json, tsv; list specs command MUST additionally support --status/-s filter for filtering by spec status (draft, active, deprecated, superseded)
  *Rationale*: JSON output enables automation; table output optimizes human readability; status filtering enables focused spec exploration
  *Verification*: VT-CLI-FORMAT-001, VT-CLI-STATUS-FILTER-001, VT-CLI-JSON-SCHEMA-001 - Output format tests verify JSON is parseable and stable, status filtering works correctly

- **SPEC-110.FR-007**(documentation): Schema commands MUST list block schemas and frontmatter schemas separately (via `schema list blocks|frontmatter|all`) and MUST display schema details in json-schema or yaml-example formats
  *Rationale*: Self-documentation reduces external documentation burden; separate listing enables focused exploration
  *Verification*: VT-CLI-SCHEMA-001 - Schema listing and display tests for both block and frontmatter types

- **SPEC-110.FR-008**(cli): Create commands MUST support all artifact types using templates:
  - Specifications (SPEC/PROD)
  - Changes: deltas, revisions, phases
  - Decisions: ADRs
  - Requirements: breakout requirement files
  - Backlog: issues, problems, improvements, risks
  *Rationale*: Template-based creation ensures consistency and completeness across all artifact types
  *Verification*: VT-CLI-CREATE-001 - Create command tests for all artifact types

- **SPEC-110.FR-009**(cli): Show commands MUST display detailed artifact information for all major types (specs, deltas, revisions, ADRs, requirements) and MUST include `show template` for displaying spec templates
  *Rationale*: Separation of concerns: CLI orchestrates, formatters implement display logic; template display aids spec creation
  *Verification*: VT-CLI-SHOW-001 - Show command delegation tests

- **SPEC-110.FR-010**(automation): Complete delta command MUST mark delta as completed AND update associated requirement statuses to 'live' in revision source files
  *Rationale*: Automates requirement lifecycle transitions; prevents manual status update errors; maintains traceability
  *Verification*: VT-CLI-COMPLETE-001 - Delta completion with requirement lifecycle tests

### Non-Functional Requirements

- **SPEC-110.NF-001**(performance): CLI commands MUST complete typical operations (list, show, create) in <2 seconds on standard hardware
  *Rationale*: Fast response times keep interactive workflows fluid
  *Measurement*: VT-CLI-INTEGRATION-001 - Integration tests measure command responsiveness

- **SPEC-110.NF-002**(architecture): CLI modules MUST average <200 lines per file to maintain thin orchestration pattern
  *Rationale*: Enforces architectural constraint that business logic stays out of CLI
  *Measurement*: Static analysis of CLI file line counts (current average: ~150 lines)

### Operational Targets

- **Performance**: Typical commands complete in <2s; list operations with filters <1s; JSON output generation <500ms
- **Reliability**: 100% command success rate for valid inputs; clear error messages for invalid inputs
- **Maintainability**: CLI files average <200 lines; test coverage ≥90%; zero business logic in CLI modules

## 4. Solution Outline

### Architecture / Components

| Component | Responsibility | Key Commands |
|-----------|---------------|-------------|
| `main.py` | Entry point, version handling, Typer app routing | N/A (routing only) |
| `common.py` | Shared option types, flag standardization, utility functions | `FormatOption`, `RootOption`, `matches_regexp()` |
| `list.py` | List commands for all artifact types | `list specs`, `list deltas`, `list requirements`, `list adrs`, `list changes`, `list backlog` |
| `show.py` | Show commands for detailed views | `show spec`, `show delta`, `show adr`, `show requirement`, `show revision`, `show template` |
| `create.py` | Create commands for artifact generation | `create spec`, `create delta`, `create revision`, `create adr`, `create requirement`, `create phase`, `create issue`, `create problem`, `create improvement`, `create risk` |
| `sync.py` | Code-to-spec and ADR registry synchronization | `sync` (delegates to adapters; `--adr` for ADR sync) |
| `schema.py` | Schema documentation commands | `schema list [blocks\|frontmatter\|all]`, `schema show <type>` |
| `backfill.py` | Spec backfill workflow | `backfill spec` |
| `complete.py` | Delta completion with requirement lifecycle updates | `complete delta` |
| `workspace.py` | Workspace management and validation | `install`, `validate` |

**Thin CLI Pattern** (enforced across all commands):
```
User Input → Typer Parse → Load Registry → Apply Filters → Delegate Format → Output → Exit
```

### Data & Contracts

**Standard Option Types** (defined in `common.py` and list commands):
```python
FormatOption = Annotated[str, typer.Option(..., help="Output format: table|json|tsv")]
JsonOutputOption = Annotated[bool, typer.Option("--json", help="Output as JSON (shorthand for --format=json)")]
StatusOption = Annotated[str | None, typer.Option("--status", "-s", help="Filter by status")]
RootOption = Annotated[Path | None, typer.Option(..., callback=root_option_callback)]
RegexpOption = Annotated[str | None, typer.Option(..., help="Regexp pattern")]
CaseInsensitiveOption = Annotated[bool, typer.Option(..., help="Case-insensitive matching")]
TruncateOption = Annotated[bool, typer.Option(..., help="Truncate fields in table")]
```

**Exit Codes**:
- `EXIT_SUCCESS = 0`: Operation completed successfully
- `EXIT_FAILURE = 1`: Operation failed (validation error, missing file, etc.)

**Registry Contracts** (from collaborators):
- `SpecRegistry(root).all_specs()` → iterable of Spec objects
- `DecisionRegistry(root).collect()` → dict of decision_id → Decision
- `RequirementsRegistry(root)` → registry with records
- `ChangeRegistry(root, kind).collect()` → dict of change_id → ChangeArtifact

**Formatter Contracts** (from SPEC-120):
- `format_spec_list_table(specs, options)` → Rich Table
- `format_decision_list_table(decisions, options)` → Rich Table
- `format_spec_details(spec)` → formatted output
- JSON/TSV formatters use standard serialization

## 5. Behaviour & Scenarios

### Primary Flows

**Standard List Command Flow** (all list commands follow this pattern):
1. Parse arguments (filters, format, root)
2. Detect/validate repository root
3. Load appropriate registry
4. Filter results based on flags (--filter, --regexp, --status, etc.)
5. Delegate to formatter for chosen output format
6. Print to stdout
7. Exit with appropriate code

**Standard Create Command Flow**:
1. Parse arguments (title, metadata, root)
2. Validate inputs (e.g., spec ID doesn't exist)
3. Load template via `core.templates`
4. Render template with provided values
5. Determine output path
6. Write file
7. Display success message with path
8. Exit SUCCESS

**Sync Command Flow** (delegates to adapters):
1. Parse arguments (language, targets, options, `--adr` flag)
2. Detect repository root
3. If spec sync: Route to appropriate adapter (Python/Go/TypeScript)
   - Adapter extracts contracts from code
   - Adapter writes contracts to spec directories
4. If `--adr` flag: Sync ADR registry
   - Update decision registry
   - Rebuild symlink indices
5. Display sync summary
6. Exit with appropriate code

**Complete Delta Flow** (lifecycle automation):
1. Parse arguments (delta_id, flags: `--dry-run`, `--force`, `--skip-sync`, `--skip-update-requirements`)
2. Load delta and validate status
3. If not `--skip-sync`: Run workspace sync
4. Mark delta as completed in change registry
5. If not `--skip-update-requirements`:
   - Load associated requirements from delta relations
   - Update requirement status to 'live' in revision source files
   - Persist changes to filesystem
6. Display completion summary with affected requirements
7. Exit SUCCESS

**Validate Workspace Flow** (delegates to validator):
1. Parse arguments (root, `--sync`, `--strict` flags)
2. If `--sync`: Run workspace sync first
3. Detect repository root
4. Create workspace instance
5. Delegate to WorkspaceValidator(workspace, strict=strict)
6. Display validation issues (errors and warnings)
7. Exit with code 0 if no errors, code 1 if errors found

### Error Handling / Guards

- **Invalid regexp**: Catch `re.error`, display user-friendly message
- **Missing repository root**: Try auto-detect; if fails, show error with --root hint
- **Unknown artifact IDs**: Validate existence before operations, error if not found
- **Template not found**: Catch `TemplateNotFoundError`, show available templates
- **Registry load failure**: Catch and display specific error (missing directory, corrupt YAML, etc.)
- **Empty results**: Display empty result set (not an error; exit SUCCESS)

## 6. Quality & Verification

### Testing Strategy

All requirements verified at **unit and integration test levels**:

| Requirement | Test Module | Test Level |
|-------------|------------|-----------|
| FR-001 | `test_cli.py` | Integration |
| FR-002 | `test_cli.py`, per-command tests | Unit + Integration |
| FR-003 | `backfill_test.py` | Unit |
| FR-004 | `sync_test.py` | Unit |
| FR-005 | `test_cli.py` (TestJSONFlagConsistency, TestRegexpFiltering) | Integration |
| FR-006 | `test_cli.py` (TestStatusFilterParity, TestJSONSchemaRegression) | Integration |
| FR-007 | `schema_test.py` | Unit |
| FR-008 | `create_test.py` | Unit |
| FR-009 | `show_test.py`, `test_cli.py` (TestShowCommandJSON) | Unit + Integration |
| FR-010 | `test_cli.py` (TestCompleteCommands) | Integration |
| NF-001 | `test_cli.py` | Integration (timing) |
| NF-002 | Static analysis | N/A |

**Test Strategy**:
- Use temporary directories for filesystem operations
- Mock registries where appropriate to isolate CLI logic
- Test all flag combinations
- Verify JSON output structure and stability
- Measure command execution time

**Coverage Target**: ≥90% line coverage for CLI modules

### Observability & Analysis

- **Metrics**: None (CLI is stateless; no telemetry)
- **Logging**: Errors written to stderr; normal output to stdout
- **Exit Codes**: SUCCESS (0) or FAILURE (1) for CI/CD integration

### Security & Compliance

- **Input Validation**: All user inputs validated before use (paths, IDs, regexps)
- **Path Traversal Protection**: Repository root detection prevents arbitrary path access
- **Template Injection**: Templates use safe rendering (no eval or exec)
- **Data Handling**: Read-only for list/show; creates files only in workspace directories

### Verification Coverage

See `supekku:verification.coverage@v1` YAML block above for detailed verification artifact mapping.

All FRs and NFs have associated test coverage in CLI test modules.

### Acceptance Gates

- [ ] All unit tests passing (`just test`)
- [ ] Linters passing (`just lint`, `just pylint`)
- [ ] Test coverage ≥90% for CLI modules
- [ ] All commands documented in --help text
- [ ] JSON output stable and parseable
- [ ] CLI file line counts average <200 lines

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

**Direct Dependencies** (external collaborators):
- **SPEC-123** (SpecRegistry): Load and filter specifications
- **SPEC-117** (DecisionRegistry): ADR operations and ADR registry synchronization
- **SPEC-122** (RequirementsRegistry): Requirement listing, filtering, and lifecycle status updates
- **SPEC-115** (ChangeRegistry): Delta/revision/audit operations and lifecycle management
- **SPEC-125** (WorkspaceValidator): Workspace integrity validation (used by `validate` command)
- **SPEC-120** (Formatters): All output formatting

**Dependency on Core Modules** (SPEC-TBD):
- **core.repo**: Repository root detection (`find_repo_root`)
- **core.templates**: Template loading and rendering
- **core.paths**: Path utilities for workspace structure
- **blocks.metadata**: Schema-to-JSON-schema conversion
- **sync adapters**: Multi-language code-to-spec synchronization

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CLI files grow beyond thin orchestration threshold | Medium | Medium | Enforce <200 line limit in code review; refactor if exceeded |
| Inconsistent flag patterns across commands | Low | High | Reusable option types in `common.py`; enforce in tests |
| JSON output schema breaks | Low | High | Integration tests verify JSON structure; version contract if needed |
| Performance degradation with large registries | Medium | Low | Lazy loading in registries; filter early to reduce processing |

### Known Gaps / Debt

- **[ASSUMPTION: Core module specs not yet created]** - SPEC-TBD references for core.repo, core.templates, core.paths should be backfilled
- **[ASSUMPTION: Sync adapter specs not yet created]** - Multi-language adapters need dedicated specs
- **[ASSUMPTION: Schema registry spec not yet created]** - blocks.metadata and schema_registry need specs
- Interactive workflows currently require multiple commands (no single-command wizards)
- No shell completion support yet (future enhancement)

### Open Decisions / Questions

None. All assumptions documented inline.
