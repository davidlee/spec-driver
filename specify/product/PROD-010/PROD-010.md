---
id: PROD-010
slug: cli-agent-ux
name: CLI Agent UX
created: '2025-11-03'
updated: '2025-11-03'
status: draft
kind: prod
aliases: []
relations:
- type: informs
  target: SPEC-110
  description: Drives CLI implementation requirements for agent workflows
guiding_principles:
- Consistency enables automation - agents learn patterns once, apply everywhere
- Predictability over features - stable contracts more valuable than rich options
- Machine-readable first - JSON output and schemas enable agent autonomy
- Progressive disclosure - simple defaults, opt-in detail flags for token efficiency
assumptions:
- Agents primarily consume JSON output for parsing and decision-making
- CLI is the primary interface for both human and agent workflows
- Agent workflows prioritize token efficiency and predictable structure
- Existing CLI architecture (SPEC-110) supports these enhancements
---

# PROD-010 – CLI Agent UX

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-010
requirements:
  primary:
    - PROD-010.FR-001
    - PROD-010.FR-002
    - PROD-010.FR-003
    - PROD-010.FR-004
    - PROD-010.FR-005
    - PROD-010.FR-006
    - PROD-010.FR-007
    - PROD-010.FR-008
    - PROD-010.FR-009
    - PROD-010.FR-010
    - PROD-010.NF-001
    - PROD-010.NF-002
    - PROD-010.NF-003
  collaborators: []
interactions:
  - spec: SPEC-110
    type: informs
    description: Defines agent-focused UX requirements for CLI implementation
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-010
capabilities:
  - id: consistent-json-output
    name: Consistent JSON Output
    responsibilities:
      - Provide JSON output on all list and show commands
      - Use consistent flag patterns (--json shorthand, --format json)
      - Ensure stable, parseable JSON structure across all commands
      - Enable compact output mode for token efficiency
    requirements:
      - PROD-010.FR-001
      - PROD-010.FR-002
    summary: >-
      Agents require consistent JSON output across all CLI commands to enable
      reliable parsing and automation. Every list/show command must support
      both --json shorthand and --format=json, with stable schemas.
    success_criteria:
      - All list commands support --json and --format=json
      - All show commands support --json flag
      - JSON output passes validation and is stable across versions
      - Compact mode reduces token usage by 30-50%

  - id: universal-filtering
    name: Universal Filtering
    responsibilities:
      - Provide status filtering on all artifact types
      - Support multi-value filters (comma-separated)
      - Enable reverse relationship queries
      - Maintain consistent filter flag patterns
    requirements:
      - PROD-010.FR-003
      - PROD-010.FR-004
      - PROD-010.FR-005
    summary: >-
      Agents need predictable filtering patterns across all list commands.
      Status filters, multi-value selections, and relationship queries enable
      targeted discovery without post-processing.
    success_criteria:
      - All list commands support -s/--status filter
      - Multi-value filters work with comma-separated values
      - Reverse relationship queries implemented for major artifacts
      - Filter behavior consistent across all commands

  - id: schema-introspection
    name: Schema Introspection
    responsibilities:
      - Expose valid enum values for all artifact fields
      - Document output format differences (table/json/tsv)
      - Provide schema documentation for agent consumption
      - Enable agents to discover valid filter values
    requirements:
      - PROD-010.FR-006
      - PROD-010.FR-007
    summary: >-
      Agents need to discover valid values for status, kind, and other enum
      fields without consulting external documentation. Schema introspection
      commands expose metadata about valid values and output formats.
    success_criteria:
      - Enum schemas accessible via schema commands
      - Output mode differences documented in help text
      - Agents can query valid status/kind values programmatically
      - No external documentation required for basic discovery

  - id: machine-readable-mode
    name: Machine-Readable Mode
    responsibilities:
      - Provide unified --machine-readable flag across all commands
      - Disable ANSI colors and formatting in machine mode
      - Ensure predictable structure for parsing
      - Support streaming output for large result sets
    requirements:
      - PROD-010.FR-008
      - PROD-010.FR-009
      - PROD-010.NF-001
    summary: >-
      Agents need a single flag to optimize output for machine consumption.
      Machine-readable mode implies JSON format, compact output, no colors,
      and predictable structure.
    success_criteria:
      - --machine-readable flag available on all commands
      - No ANSI escape codes in machine-readable output
      - JSON structure stable and compact
      - Large result sets support pagination/streaming

  - id: improved-error-guidance
    name: Improved Error Guidance
    responsibilities:
      - Suggest valid options when invalid option provided
      - List valid enum values when invalid value provided
      - Provide actionable error messages with examples
      - Document undocumented features in help text
    requirements:
      - PROD-010.FR-010
      - PROD-010.NF-002
    summary: >-
      Agents benefit from actionable error messages that guide correction.
      When commands fail, errors should include valid alternatives and
      examples to enable self-correction.
    success_criteria:
      - Invalid options suggest valid alternatives
      - Invalid enum values list valid choices
      - Error messages include actionable examples
      - Help text documents all available options
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-010
entries:
  - artefact: VT-PROD010-JSON-001
    kind: VT
    requirement: PROD-010.FR-001
    status: verified
    notes: Implemented in DE-009. Unit tests verify --json flag on all list commands (deltas, adrs, requirements, revisions, changes) produces valid parseable JSON matching --format=json output. Tests in supekku/cli/test_cli.py::TestJSONFlagConsistency. 74/74 CLI tests passing.
    implemented_by: DE-009
    verified_by: IP-009.PHASE-01

  - artefact: VT-PROD010-JSON-002
    kind: VT
    requirement: PROD-010.FR-002
    status: verified
    notes: Implemented in DE-009. Unit tests verify --json flag on all show commands (spec, adr, requirement, revision) produces structured output with consistent schema. Tests in supekku/cli/test_cli.py::TestShowCommandJSON. 35 new tests added.
    implemented_by: DE-009
    verified_by: IP-009.PHASE-01

  - artefact: VT-PROD010-FILTER-001
    kind: VT
    requirement: PROD-010.FR-003
    status: verified
    notes: Implemented in DE-009. Unit tests verify -s/--status filter on specs command filters correctly and matches deltas/adrs behavior. Tests in supekku/cli/test_cli.py::TestStatusFilterParity. Supports draft, active, deprecated, superseded statuses.
    implemented_by: DE-009
    verified_by: IP-009.PHASE-01

  - artefact: VT-PROD010-FILTER-002
    kind: VT
    requirement: PROD-010.FR-004
    status: planned
    notes: Test multi-value filter support across all list commands

  - artefact: VT-PROD010-FILTER-003
    kind: VT
    requirement: PROD-010.FR-005
    status: planned
    notes: Test reverse relationship queries (--implements, --verified-by, --informed-by)

  - artefact: VT-PROD010-SCHEMA-001
    kind: VT
    requirement: PROD-010.FR-006
    status: planned
    notes: Test enum introspection via schema commands

  - artefact: VT-PROD010-SCHEMA-002
    kind: VT
    requirement: PROD-010.FR-007
    status: planned
    notes: Test output format documentation in help text

  - artefact: VT-PROD010-MACHINE-001
    kind: VT
    requirement: PROD-010.FR-008
    status: planned
    notes: Test --machine-readable flag availability and behavior

  - artefact: VT-PROD010-MACHINE-002
    kind: VT
    requirement: PROD-010.FR-009
    status: planned
    notes: Test pagination/streaming for large result sets

  - artefact: VT-PROD010-ERROR-001
    kind: VT
    requirement: PROD-010.FR-010
    status: planned
    notes: Test error message quality (suggestions, valid values, examples)

  - artefact: VA-PROD010-TOKEN-001
    kind: VA
    requirement: PROD-010.NF-001
    status: planned
    notes: Measure token usage reduction with compact mode and progressive disclosure

  - artefact: VH-PROD010-AGENT-001
    kind: VH
    requirement: PROD-010.NF-002
    status: planned
    notes: Agent workflow testing - verify agents can complete common tasks without documentation

  - artefact: VH-PROD010-UX-001
    kind: VH
    requirement: PROD-010.NF-003
    status: verified
    notes: Implemented in DE-009. Manual validation confirmed all Priority 1 findings from UX research (docs/ux-research-cli-2025-11-03.md Section 12) addressed. 74/74 CLI tests passing with 35 new tests covering all changes. JSON flag consistency and status filter parity verified.
    implemented_by: DE-009
    verified_by: IP-009.PHASE-01
```

## 1. Intent & Summary

- **Problem / Purpose**:
  AI agents using spec-driver CLI encounter inconsistent patterns that require special-case handling and external documentation. The 2025-11-03 UX research identified critical gaps: JSON output inconsistency (`--json` vs `--format json`), missing status filters on specs, undocumented features, and lack of metadata introspection. These gaps force agents to:
  - Implement command-specific logic instead of learning universal patterns
  - Consume excessive tokens parsing table output when JSON unavailable
  - Post-process results with grep/jq for missing filters
  - Rely on external documentation for valid enum values

- **Value Signals**:
  - **Agent Autonomy**: Reduce documentation lookups by 80% via schema introspection
  - **Token Efficiency**: Compact JSON mode reduces token usage 30-50% for typical workflows
  - **Reliability**: Consistent patterns eliminate special-case handling across 14+ commands
  - **Developer Velocity**: Standard workflows complete 2-3x faster with predictable CLI behavior

- **Guiding Principles**:
  - **Consistency enables automation**: Agents learn patterns once, apply everywhere
  - **Predictability over features**: Stable contracts more valuable than rich options
  - **Machine-readable first**: JSON output and schemas enable agent autonomy
  - **Progressive disclosure**: Simple defaults, opt-in detail flags for token efficiency
  - **Self-documenting**: Valid values discoverable via CLI, not external docs

- **Change History**: Initial specification based on 2025-11-03 UX research report (`docs/ux-research-cli-2025-11-03.md`)

## 2. Stakeholders & Journeys

- **Personas / Actors**:
  - **AI Agent (Primary)**: Autonomous coding assistant using CLI for discovery, validation, and automation
    - Goals: Complete workflows without documentation, minimize token usage, reliable parsing
    - Pains: Inconsistent patterns require special cases, missing JSON output forces table parsing, undiscoverable valid values
    - Expectations: Predictable behavior, self-documenting schemas, stable JSON contracts

  - **Developer (Secondary)**: Human using CLI interactively or in scripts
    - Goals: Fast discovery, scriptable workflows, clear error messages
    - Pains: Trial-and-error to find valid options, verbose output wastes screen space
    - Expectations: Helpful errors, consistent patterns, good defaults

- **Primary Journeys / Flows**:

  **Journey 1: Agent Discovers Available Deltas**
  1. **Given** agent needs to find draft deltas for implementation planning
  2. **When** agent runs `spec-driver list deltas --status draft --json`
  3. **Then** JSON output contains all draft deltas with stable schema
  4. **And** agent parses results without external documentation
  5. **And** agent proceeds to next workflow step

  **Journey 2: Agent Filters Specs by Status** (currently broken)
  1. **Given** agent needs to list active specifications
  2. **When** agent tries `spec-driver list specs --status active --json`
  3. **Then** command succeeds (currently fails with "No such option")
  4. **And** JSON output contains filtered specs
  5. **Result**: Agent workflow completes without workaround

  **Journey 3: Agent Discovers Valid Status Values**
  1. **Given** agent needs to query deltas by status
  2. **When** agent runs `spec-driver schema show enums.delta.status`
  3. **Then** output lists valid values: `["draft", "in-progress", "completed", "deferred"]`
  4. **And** agent constructs valid filter without guessing
  5. **Result**: Zero documentation lookups required

  **Journey 4: Agent Finds Requirements Verified by Test**
  1. **Given** agent needs to find requirements verified by VT-CLI-001
  2. **When** agent runs `spec-driver list requirements --verified-by VT-CLI-001 --json`
  3. **Then** JSON output contains requirements with verification linkage
  4. **And** agent avoids post-processing with jq (currently required)
  5. **Result**: Single command replaces multi-step grep/jq pipeline

  **Journey 5: Agent Exports Large Dataset Token-Efficiently**
  1. **Given** agent needs full requirements list for analysis
  2. **When** agent runs `spec-driver list requirements --machine-readable`
  3. **Then** output is compact JSON with no ANSI formatting
  4. **And** token usage 40% lower than table format
  5. **And** result set supports pagination for large datasets
  6. **Result**: Token budget preserved for analysis phase

  **Journey 6: Agent Self-Corrects on Invalid Input**
  1. **Given** agent provides invalid format option
  2. **When** agent runs `spec-driver list deltas --format xml`
  3. **Then** error message shows: "Invalid format: xml. Valid: table, json, tsv"
  4. **And** agent retries with `--format json` without user intervention
  5. **Result**: Self-correction reduces failure cascades

- **Edge Cases & Non-goals**:
  - **IN SCOPE**: All read-only operations (list, show, schema, validate)
  - **IN SCOPE**: Filter consistency across all artifact types
  - **OUT OF SCOPE**: Interactive TUI mode (future enhancement)
  - **OUT OF SCOPE**: Natural language query translation
  - **EDGE CASE**: Empty result sets → return `{"items": []}` (not error)
  - **EDGE CASE**: Very large result sets (>1000 items) → pagination required
  - **GUARD RAIL**: Invalid relationship targets → validate existence, suggest valid options

## 3. Responsibilities & Requirements

### Capability Overview

The CLI Agent UX improvements provide five core capabilities:

1. **Consistent JSON Output** (FR-001, FR-002): Universal JSON support across all list/show commands with stable schemas
2. **Universal Filtering** (FR-003, FR-004, FR-005): Status filters everywhere, multi-value selections, reverse relationship queries
3. **Schema Introspection** (FR-006, FR-007): Discoverable enum values, output format documentation
4. **Machine-Readable Mode** (FR-008, FR-009, NF-001): Unified flag for agent-optimized output with pagination
5. **Improved Error Guidance** (FR-010, NF-002): Actionable error messages with valid alternatives and examples

### Functional Requirements

**Priority 1: Consistency (Critical for agent reliability)**

- **PROD-010.FR-001**: All list commands MUST support both `--json` (shorthand) and `--format=json` flags with identical behavior
  *Rationale*: Eliminates command-specific logic; agents use single pattern across all list operations
  *Current Gap*: `list specs` has `--json`, others use `--format json`
  *Verification*: VT-PROD010-JSON-001 - Test JSON availability on specs, deltas, adrs, requirements, revisions, changes

- **PROD-010.FR-002**: All show commands MUST support `--json` flag for structured output
  *Rationale*: Enables programmatic access to detailed artifact information
  *Current Gap*: `show delta --json` works but undocumented; `show spec --json` missing
  *Verification*: VT-PROD010-JSON-002 - Test JSON on show spec/delta/adr/requirement/revision

- **PROD-010.FR-003**: All list commands MUST support `-s`/`--status` filter for consistent status-based filtering
  *Rationale*: Status filtering is universal need across all artifact types
  *Current Gap*: `list specs` lacks status filter entirely
  *Verification*: VT-PROD010-FILTER-001 - Test status filter on specs command

**Priority 2: Enhanced Filtering (High value for agent workflows)**

- **PROD-010.FR-004**: All list commands MUST support multi-value filters via comma-separated values (e.g., `-s draft,in-progress`)
  *Rationale*: Eliminates need for regex workarounds or multiple commands
  *Current Gap*: Only single-value filters supported; agents use complex regex
  *Verification*: VT-PROD010-FILTER-002 - Test multi-value status, kind, and custom filters

- **PROD-010.FR-005**: List commands MUST support reverse relationship queries:
  - `list deltas --implements SPEC-110.FR-001` (deltas implementing requirement)
  - `list requirements --verified-by VT-*` (requirements verified by test pattern)
  - `list specs --informed-by ADR-001` (specs informed by decision)
  *Rationale*: Enables discovery without post-processing with jq/grep
  *Current Gap*: Requires manual JSON parsing or grep pipelines
  *Verification*: VT-PROD010-FILTER-003 - Test reverse relationship queries

**Priority 3: Self-Documentation (Reduces external dependencies)**

- **PROD-010.FR-006**: Schema commands MUST expose enum values for all artifact fields:
  - `schema show enums.delta.status` → `["draft", "in-progress", "completed", "deferred"]`
  - `schema show enums.spec.kind` → `["prod", "tech"]`
  - `schema show enums.requirement.kind` → `["FR", "NF"]`
  *Rationale*: Agents discover valid values without documentation
  *Current Gap*: No introspection; agents guess or fail
  *Verification*: VT-PROD010-SCHEMA-001 - Test enum introspection for all artifact types

- **PROD-010.FR-007**: All list command help text MUST document output format differences (table/json/tsv) with examples
  *Rationale*: Clarifies when to use each format and what fields are included
  *Current Gap*: Format differences undocumented
  *Verification*: VT-PROD010-SCHEMA-002 - Validate help text includes format documentation

**Priority 4: Machine-Readable Mode (Token efficiency)**

- **PROD-010.FR-008**: All commands MUST support `--machine-readable` flag that implies:
  - `--format=json` (structured output)
  - `--compact` (no whitespace in JSON)
  - `--no-color` (no ANSI escape codes)
  *Rationale*: Single flag optimizes for agent consumption
  *Current Gap*: Agents must specify multiple flags
  *Verification*: VT-PROD010-MACHINE-001 - Test machine-readable flag behavior

- **PROD-010.FR-009**: List commands MUST support pagination for large result sets (>100 items):
  - `--limit N --offset M` (SQL-style pagination)
  - Alternative: `--page N --per-page M` (page-based pagination)
  *Rationale*: Prevents token exhaustion on large registries
  *Current Gap*: All results returned at once (77 requirements in single response)
  *Verification*: VT-PROD010-MACHINE-002 - Test pagination on large result sets

**Priority 5: Error Guidance (Self-correction)**

- **PROD-010.FR-010**: Error messages MUST provide actionable guidance:
  - Invalid option → suggest valid options with examples
  - Invalid enum value → list valid choices
  - Unknown artifact ID → suggest similar IDs (fuzzy match)
  - Missing required arg → show example usage
  *Rationale*: Enables agent self-correction without user intervention
  *Current Gap*: Errors like "invalid format: xml" don't show valid formats
  *Verification*: VT-PROD010-ERROR-001 - Test error message quality across scenarios

### Non-Functional Requirements

- **PROD-010.NF-001**: Compact JSON mode MUST reduce token usage by 30-50% compared to table format for typical workflows
  *Rationale*: Token efficiency critical for agent economics
  *Measurement*: VA-PROD010-TOKEN-001 - Measure token usage across representative workflows (list, filter, show)

- **PROD-010.NF-002**: Common agent workflows (discover → filter → show) MUST complete without consulting external documentation
  *Rationale*: Self-documenting CLI reduces cognitive load and latency
  *Measurement*: VH-PROD010-AGENT-001 - Agent workflow testing with zero-knowledge baseline

- **PROD-010.NF-003**: Implemented improvements MUST address all Priority 1-2 findings from 2025-11-03 UX research report
  *Rationale*: Validates solution solves documented pain points
  *Measurement*: VH-PROD010-UX-001 - Cross-reference implementation with research findings

### Success Metrics / Signals

- **Agent Autonomy**: 80% reduction in documentation lookups (via schema introspection)
- **Token Efficiency**: 40% average token reduction for list operations (compact JSON + pagination)
- **Reliability**: Zero special-case command handling (consistent patterns across all commands)
- **Workflow Velocity**: Common workflows (list+filter+show) complete 2-3x faster
- **Error Recovery**: 90% of invalid inputs result in successful retry without user intervention

## 4. Solution Outline

- **User Experience / Outcomes**:

  **Agent Workflow Before Improvements**:
  ```bash
  # Agent tries to list active specs - fails
  $ spec-driver list specs --status active --json
  Error: No such option: --status

  # Agent falls back to post-processing
  $ spec-driver list specs --json | jq '.items[] | select(.status == "active")'
  # Agent consumed 2x tokens (full list + jq filtering)

  # Agent guesses valid status values - fails
  $ spec-driver list deltas --format xml
  Error: invalid format: xml
  # No guidance on valid formats
  ```

  **Agent Workflow After Improvements**:
  ```bash
  # Status filter works everywhere
  $ spec-driver list specs --status active --json
  {"items": [{"id": "SPEC-110", "status": "active", ...}]}

  # Discover valid formats via schema
  $ spec-driver schema show enums.command.format
  ["table", "json", "tsv"]

  # Machine-readable mode optimized for agents
  $ spec-driver list requirements --machine-readable
  {"items":[{"id":"PROD-010.FR-001","status":"planned",...}]}
  # Compact JSON, no colors, 45% fewer tokens

  # Reverse relationships without jq
  $ spec-driver list deltas --implements SPEC-110.FR-001 --json
  {"items": [{"id": "DE-004", "implements": ["SPEC-110.FR-001"], ...}]}

  # Self-correcting errors
  $ spec-driver list deltas --format xml
  Error: invalid format: xml
  Valid formats: table, json, tsv
  Try: spec-driver list deltas --format json
  ```

- **Data & Contracts**:

  **Standard JSON Response Schema** (all list commands):
  ```json
  {
    "items": [<array of artifacts>],
    "total": <count>,
    "page": <optional page number>,
    "per_page": <optional page size>
  }
  ```

  **Enum Schema Response** (schema commands):
  ```json
  {
    "type": "enum",
    "artifact": "delta",
    "field": "status",
    "values": ["draft", "in-progress", "completed", "deferred"],
    "default": "draft"
  }
  ```

  **Error Response Schema** (consistent across all commands):
  ```json
  {
    "error": "<error message>",
    "valid_options": ["option1", "option2"],
    "suggestion": "<actionable guidance>",
    "example": "<corrected command>"
  }
  ```

## 5. Behaviour & Scenarios

### Primary Flows

**Standard List Command Flow** (with enhancements):
1. Parse arguments (filters, format, pagination, machine-readable)
2. If `--machine-readable`: Set format=json, compact=true, no-color=true
3. Detect repository root
4. Load appropriate registry
5. Apply filters (status, regexp, relationships)
6. If pagination requested: Apply limit/offset
7. Delegate to formatter (JSON/TSV/table)
8. Output to stdout (with optional pagination metadata)
9. Exit with appropriate code

**Schema Introspection Flow** (new):
1. Parse arguments (schema type: enums.<artifact>.<field>)
2. Load schema registry
3. Extract enum definition for requested field
4. Format as JSON array or human-readable list
5. Output valid values with optional default
6. Exit SUCCESS

**Reverse Relationship Query Flow** (new):
1. Parse arguments (relationship filter: --implements, --verified-by, --informed-by)
2. Load registry and related registries (requirements, deltas, specs)
3. Build reverse index from relationships
4. Filter artifacts matching relationship criteria
5. Return filtered results
6. Exit SUCCESS

### Error Handling / Guards

**Enhanced Error Messages**:
- **Invalid option**: "No such option: --status. Available for specs: --kind, --package, --filter, --regexp. See 'spec-driver list specs --help'"
- **Invalid enum**: "Invalid status: activ. Did you mean: active? Valid: draft, active, deprecated, superseded"
- **Invalid format**: "Invalid format: xml. Valid formats: table, json, tsv. Try: --format json"
- **Unknown artifact**: "Delta not found: DE-999. Similar: DE-009, DE-099. List all: spec-driver list deltas"

**Guards**:
- Validate status/kind values against known enums before filtering
- Check artifact existence before show operations
- Limit pagination to reasonable bounds (max 1000 per page)
- Validate relationship targets exist before querying

## 6. Quality & Verification

### Testing Strategy

**Unit Tests** (per requirement):
- FR-001/FR-002: Test JSON flag availability and output schema stability
- FR-003: Test status filter on specs command
- FR-004: Test multi-value filter parsing and application
- FR-005: Test reverse relationship query correctness
- FR-006: Test enum introspection accuracy
- FR-007: Test help text documentation completeness
- FR-008: Test machine-readable mode behavior
- FR-009: Test pagination mechanics and edge cases
- FR-010: Test error message quality and suggestions

**Integration Tests**:
- End-to-end agent workflows (discover → filter → show)
- Cross-command consistency (same flags work identically)
- Performance regression testing (commands stay <2s)
- Token usage measurement (compact mode achieves 30-50% reduction)

**Coverage Target**: ≥90% line coverage for new/modified CLI code

### Research / Validation

**Validation Plan**:
1. **Baseline Measurement**: Token usage for 10 common agent workflows (before improvements)
2. **Implementation**: Apply Priority 1-3 improvements
3. **Validation Testing**: Run same workflows, measure token reduction and success rate
4. **Agent Testing**: Zero-knowledge agent completes workflows without documentation
5. **Success Criteria**:
   - 80% reduction in documentation lookups
   - 40% average token reduction
   - 100% workflow completion without external docs

**Research Traceability**:
- FR-001/FR-002 address UX Research Section 2 (JSON inconsistency - HIGH priority)
- FR-003 addresses Section 8 (Status filter gaps - HIGH priority)
- FR-004 addresses Section 8 (Multi-value filters - MEDIUM priority)
- FR-005 addresses Section 8 (Reverse relationship queries - MEDIUM priority)
- FR-006/FR-007 address Section 7 (Schema introspection - MEDIUM priority)
- FR-010 addresses Section 6 (Error messages - MEDIUM priority)

### Observability & Analysis

**Metrics** (optional telemetry for validation):
- JSON output parsing success rate by command
- Token usage per command type (table vs JSON vs compact)
- Error self-correction rate (retry success after initial failure)
- Documentation lookup frequency (external vs CLI-based discovery)

**Success Signals**:
- Zero special-case handling required in agent code for CLI operations
- Agent workflows complete without user intervention in 95% of cases
- Token budget preserved for analysis phase (not consumed by discovery)

### Security & Compliance

- **Input Validation**: Enum values validated against schema before processing
- **Path Safety**: Pagination limits prevent denial-of-service via large result sets
- **Data Exposure**: No sensitive data in error messages or examples
- **Stability**: JSON schema versioning prevents breaking changes

### Verification Coverage

See `supekku:verification.coverage@v1` YAML block above for detailed verification artifact mapping.

All requirements have planned test coverage across unit (VT), analysis (VA), and human validation (VH) levels.

### Acceptance Gates

- [ ] All Priority 1 requirements (FR-001, FR-002, FR-003) implemented and tested
- [ ] All Priority 2 requirements (FR-004, FR-005) implemented and tested
- [ ] All Priority 3 requirements (FR-006, FR-007, FR-008, FR-009, FR-010) implemented and tested
- [ ] Unit tests passing (`just test`)
- [ ] Token efficiency validation (NF-001) confirms 30-50% reduction
- [ ] Agent workflow testing (NF-002) shows zero documentation lookups
- [ ] UX research validation (NF-003) confirms all findings addressed
- [ ] JSON output schemas stable and documented
- [ ] Help text updated with examples and format documentation
- [ ] Error messages provide actionable guidance with examples

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

**Direct Dependencies**:
- **SPEC-110** (supekku/cli): Implementation target for all agent UX requirements
  - Relationship: PROD-010 informs SPEC-110 functional requirements
  - Impact: SPEC-110 FR/NF requirements must align with PROD-010
  - Collaboration: PROD-010 drives CLI architecture decisions for agent workflows

**Informed By**:
- **docs/ux-research-cli-2025-11-03.md**: Comprehensive UX research identifying agent pain points
  - Priority 1-3 findings mapped to FR-001 through FR-010
  - Medium-term enhancements (FR-004, FR-005) selected based on research recommendations

### Risks & Mitigations

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|-----------|--------|------------|
| RISK-001 | Breaking changes to existing JSON schemas disrupt agent workflows | Medium | High | Version JSON schemas; provide migration period; test with existing agent code |
| RISK-002 | Performance degradation with pagination overhead | Low | Medium | Lazy loading in registries; benchmark pagination vs full load |
| RISK-003 | Enum introspection exposes implementation details | Low | Low | Document only user-facing enum values; exclude internal states |
| RISK-004 | Multi-value filters complicate filtering logic | Medium | Low | Use standard parsing library; comprehensive test coverage |
| RISK-005 | Reverse relationship queries require index maintenance | Medium | Medium | Build indices lazily; cache for performance; document rebuild process |

### Known Gaps / Debt

**Assumptions Requiring Validation**:
- Token reduction estimates (30-50%) based on typical workflows; actual reduction depends on agent usage patterns
- Pagination limits (max 1000 per page) may need tuning based on registry growth
- Reverse relationship query performance acceptable for current registry sizes; may need optimization at scale

**Future Enhancements** (explicitly deferred):
- Interactive TUI mode for exploration (UX Research Section 13, Long-Term item 6)
- Workflow-specific commands (audit coverage, audit drift) - Section 13, Long-Term item 5
- Natural language query translation (not in research scope)
- Streaming JSON output for very large result sets (Section 13, Long-Term item 4)

**Backlog Items to Create**:
- Create ISSUE for JSON schema versioning strategy
- Create IMPROVEMENT for workflow-specific convenience commands
- Create RISK for registry performance at scale (>1000 artifacts per type)

### Open Decisions / Questions

None remaining. All scope and priority decisions resolved via user clarification (Q1A, Q2: comprehensive, Q3: B).

## Appendices

### A. UX Research Traceability Matrix

Mapping of UX Research findings to requirements:

| Research Finding | Priority | Requirement | Status |
|------------------|----------|-------------|--------|
| JSON output inconsistency (--json vs --format) | HIGH | FR-001, FR-002 | Scoped |
| Status filter missing from specs | HIGH | FR-003 | Scoped |
| Missing usage examples | MEDIUM | FR-007 | Scoped |
| TSV detail flags inconsistent | MEDIUM | Deferred | Out of scope (human-focused) |
| Show commands missing --json docs | MEDIUM | FR-002 | Scoped |
| Error messages lack guidance | MEDIUM | FR-010 | Scoped |
| No machine-readable mode | HIGH | FR-008 | Scoped |
| Schema introspection partial | MEDIUM | FR-006 | Scoped |
| No streaming/pagination | MEDIUM | FR-009 | Scoped |
| Multi-value filters unavailable | MEDIUM | FR-004 | Scoped |
| Reverse relationship queries unavailable | MEDIUM | FR-005 | Scoped |

### B. Implementation Priorities

Recommended delta breakdown for implementation:

**Delta 1: Critical Consistency (P1)**
- FR-001: Standardize --json across list commands
- FR-002: Add --json to show commands
- FR-003: Add status filter to specs
- NF-003: Validate against UX research findings

**Delta 2: Enhanced Filtering (P2)**
- FR-004: Multi-value filter support
- FR-005: Reverse relationship queries
- NF-001: Token efficiency validation

**Delta 3: Self-Documentation (P3)**
- FR-006: Enum introspection
- FR-007: Help text enhancement
- FR-010: Error message improvements
- NF-002: Agent workflow validation

**Delta 4: Machine-Readable Mode (P3)**
- FR-008: --machine-readable flag
- FR-009: Pagination support
- NF-001: Token efficiency final validation

### C. Agent Workflow Examples

**Example 1: Delta Implementation Planning**
```bash
# Discover draft deltas
$ spec-driver list deltas -s draft --json

# Get detailed plan for specific delta
$ spec-driver show delta DE-008 --json

# Find requirements implemented by delta
$ spec-driver list requirements --implemented-by DE-008 --json

# Check verification coverage
$ spec-driver list requirements --verified-by VT-* --json
```

**Example 2: Spec Coverage Analysis**
```bash
# List active specs
$ spec-driver list specs -s active --machine-readable

# Get requirements for specific spec
$ spec-driver list requirements --spec SPEC-110 --json

# Find deltas implementing spec requirements
$ spec-driver list deltas --implements SPEC-110 --json

# Validate workspace integrity
$ spec-driver validate --strict
```

**Example 3: Discovery Without Documentation**
```bash
# Discover valid delta statuses
$ spec-driver schema show enums.delta.status

# Discover valid output formats
$ spec-driver list deltas --help | grep -A3 "format"

# Self-correct invalid input
$ spec-driver list specs --format yaml
Error: Invalid format: yaml. Valid: table, json, tsv
Try: spec-driver list specs --format json
```
