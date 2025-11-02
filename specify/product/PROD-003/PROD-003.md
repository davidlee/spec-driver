---
id: PROD-003
slug: policy-and-standard-management
name: Policy and Standard Management
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: prod
aliases: []
relations:
  - type: extends
    target: SPEC-003
    nature: CLI create commands
  - type: extends
    target: SPEC-004
    nature: CLI list commands
  - type: collaborates
    target: SPEC-043
    nature: Registry pattern reuse
guiding_principles:
  - Policies enforce hard rules; standards provide flexible guidance
  - Bidirectional traceability between policies, standards, and decisions
  - Simple, focused metadata structure (Statement, Rationale, Scope, Verification)
assumptions:
  - Teams already use ADRs and understand the decision registry pattern
  - Policy/standard lifecycle mirrors ADR lifecycle (draft → required/default → deprecated)
  - Cross-artifact referencing is valuable for navigating governance relationships
---

# PROD-003 – Policy and Standard Management

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-003
requirements:
  primary:
    - PROD-003.FR-001
    - PROD-003.FR-002
    - PROD-003.FR-003
    - PROD-003.FR-004
    - PROD-003.FR-005
    - PROD-003.FR-006
    - PROD-003.FR-007
    - PROD-003.FR-008
    - PROD-003.NF-001
    - PROD-003.NF-002
  collaborators: []
interactions:
  - with: SPEC-003
    nature: Extends CLI create commands to support policies and standards
  - with: SPEC-004
    nature: Extends CLI list commands to support policies and standards
  - with: SPEC-043
    nature: Reuses registry pattern from decisions (ADRs)
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-003
capabilities:
  - id: policy-authoring
    name: Policy Authoring and Lifecycle
    responsibilities:
      - Enable creation of numbered policies (POL-XXX)
      - Track policy status (draft, required, deprecated)
      - Support policy supersession relationships
      - Maintain policy metadata (owners, dates, tags)
    requirements:
      - PROD-003.FR-001
      - PROD-003.FR-002
      - PROD-003.NF-001
    summary: >-
      Teams can create, update, and manage policies throughout their lifecycle,
      from initial draft through active enforcement to eventual deprecation.
      Policies represent hard rules that must be followed project-wide.
    success_criteria:
      - Policies can be created with unique IDs
      - Policy status transitions are tracked
      - Superseded policies maintain traceability
  - id: standard-authoring
    name: Standard Authoring and Lifecycle
    responsibilities:
      - Enable creation of numbered standards (STD-XXX)
      - Track standard status (draft, required, default, deprecated)
      - Support flexible "default" status for sensible recommendations
      - Maintain standard metadata (owners, dates, tags)
    responsibilities:
      - PROD-003.FR-003
      - PROD-003.FR-004
      - PROD-003.NF-001
    summary: >-
      Teams can create and manage standards with either required (must comply)
      or default (recommended unless justified) enforcement levels. Standards
      codify conventions and sensible defaults for the project.
    success_criteria:
      - Standards can be created with unique IDs
      - "default" status provides flexible guidance
      - "required" status enforces like policies
  - id: discovery-and-navigation
    name: Discovery and Navigation
    responsibilities:
      - List all policies and standards
      - Filter by status, tags, references
      - Display policy/standard details
      - Show cross-references (policies ↔ standards ↔ ADRs)
    requirements:
      - PROD-003.FR-005
      - PROD-003.FR-006
      - PROD-003.NF-002
    summary: >-
      Developers and architects can discover relevant policies and standards,
      understand their relationships, and navigate between governance artifacts
      and implementing decisions.
    success_criteria:
      - All policies/standards discoverable via CLI
      - Cross-references navigable in both directions
      - Filtering enables focused searches
  - id: traceability-integration
    name: Traceability and Integration
    responsibilities:
      - Link policies/standards to specs, requirements, deltas
      - Support bidirectional references between policies and standards
      - Display policy/standard references in ADRs and other artifacts
      - Maintain backlinks automatically
    requirements:
      - PROD-003.FR-007
      - PROD-003.FR-008
    summary: >-
      Policies and standards integrate seamlessly with existing spec-driver
      artifacts, enabling comprehensive traceability from governance rules
      through decisions to implementation artifacts.
    success_criteria:
      - Policies/standards referenced from ADRs, specs, deltas
      - Backlinks maintained automatically
      - Governance context visible when viewing decisions
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-003
entries:
  - artefact: VT-PROD-003-001
    kind: VT
    requirement: PROD-003.FR-001
    status: planned
    notes: E2E test - create policy via CLI, verify file and registry
  - artefact: VT-PROD-003-002
    kind: VT
    requirement: PROD-003.FR-002
    status: planned
    notes: Integration test - policy status transitions and supersession
  - artefact: VT-PROD-003-003
    kind: VT
    requirement: PROD-003.FR-003
    status: planned
    notes: E2E test - create standard via CLI, verify file and registry
  - artefact: VT-PROD-003-004
    kind: VT
    requirement: PROD-003.FR-004
    status: planned
    notes: Unit test - validate "default" status behavior
  - artefact: VT-PROD-003-005
    kind: VT
    requirement: PROD-003.FR-005
    status: planned
    notes: Integration test - list policies/standards with various filters
  - artefact: VT-PROD-003-006
    kind: VT
    requirement: PROD-003.FR-006
    status: planned
    notes: Integration test - show policy/standard with full details
  - artefact: VT-PROD-003-007
    kind: VT
    requirement: PROD-003.FR-007
    status: planned
    notes: Integration test - bidirectional policy ↔ standard references
  - artefact: VT-PROD-003-008
    kind: VT
    requirement: PROD-003.FR-008
    status: planned
    notes: Integration test - policy/standard references in ADRs
  - artefact: VT-PROD-003-009
    kind: VT
    requirement: PROD-003.NF-001
    status: planned
    notes: Template validation - policies/standards follow consistent structure
  - artefact: VA-PROD-003-001
    kind: VA
    requirement: PROD-003.NF-002
    status: planned
    notes: UX review - CLI discoverability and navigation patterns
```

## 1. Intent & Summary

### Problem / Purpose

spec-driver currently supports Architecture Decision Records (ADRs) to document technical decisions, but lacks dedicated artifacts for expressing project-wide **policies** (hard rules) and **standards** (conventions and sensible defaults). Teams need a way to:

1. **Document governance rules**: Policies like "code must have tests" or "never store unencrypted PII" that apply across the entire project
2. **Codify conventions**: Standards like "use Google Go style guide" or "prefer focused dependencies" that provide guidance without strict enforcement
3. **Establish sensible defaults**: Standards marked as "default" that recommend approaches unless there's justification to deviate
4. **Connect governance to decisions**: Link policies/standards to ADRs, specs, and other artifacts for complete traceability

Without this capability, teams resort to documenting policies in ADRs (conflating decisions with rules), external wikis (breaking traceability), or informal tribal knowledge (creating inconsistency).

### Value Signals

- **Governance clarity**: Explicit distinction between must-comply rules (policies) and flexible guidance (standards)
- **Decision quality**: ADRs can cite governing policies/standards, making constraints and reasoning explicit
- **Onboarding efficiency**: New team members discover established rules and conventions through the registry
- **Compliance tracking**: Policies linked to verification artifacts demonstrate adherence to governance
- **Flexibility**: "default" status standards provide recommendations without rigidity

### Guiding Principles

1. **Separation of concerns**: Policies ≠ standards ≠ decisions. Each serves a distinct purpose.
2. **Enforcement spectrum**: Policies (must), standards with "required" (must), standards with "default" (should unless justified)
3. **Bidirectional traceability**: Policies/standards reference each other and are referenced by ADRs, specs, deltas
4. **Consistent patterns**: Reuse proven patterns from ADR implementation (registry, CLI, formatters)
5. **Simplicity**: Streamlined template (Statement, Rationale, Scope, Verification) focused on governance needs

### Change History

- **2025-11-02**: Initial specification (PROD-003) created
- Based on POLICIES_STANDARDS_IMPLEMENTATION_PLAN.md analysis

## 2. Stakeholders & Journeys

### Personas / Actors

1. **Development Team**
   - **Goals**: Understand what rules apply to code, follow established conventions, justify deviations when needed
   - **Pains**: Rules scattered across docs, unclear enforcement levels, no way to discover relevant standards
   - **Expectations**: Clear, discoverable policies/standards; easy to reference in ADRs

2. **Architects / Tech Leads**
   - **Goals**: Establish and evolve project governance, ensure consistency, guide decision-making
   - **Pains**: Policies/standards conflated with decisions, no lifecycle management, hard to track compliance
   - **Expectations**: Dedicated artifacts for governance, status tracking, supersession support

3. **Project Managers / QA**
   - **Goals**: Verify compliance with policies, track governance evolution, audit decision rationale
   - **Pains**: No central registry of policies, unclear which rules are active vs deprecated
   - **Expectations**: Filterable lists, backlinks to implementing artifacts, verification traceability

### Primary Journeys / Flows

#### Journey 1: Create a New Policy (Architect)

**Given** an architect identifies a recurring problem that requires a project-wide rule
**When** they run `spec-driver create policy "Code must have tests"`
**Then**:
1. System generates POL-001 with unique ID
2. System creates file at `specify/policies/POL-001-code-must-have-tests.md`
3. File contains frontmatter with status=draft and simplified template sections
4. System syncs to `specify/.registry/policies.yaml`
5. Architect fills in Statement, Rationale, Scope, Verification
6. Architect updates status to "required" when approved
7. Policy is discoverable via `spec-driver list policies`

#### Journey 2: Establish a Sensible Default (Tech Lead)

**Given** a tech lead wants to recommend (but not mandate) a coding style guide
**When** they create STD-001 "Google Go Style Guide" with status=default
**Then**:
1. System creates standard with flexible enforcement level
2. Documentation clarifies: "recommended unless justified otherwise"
3. Developers reference STD-001 in ADRs when following the guide
4. Developers can deviate with documented rationale in their ADRs
5. Standard provides guidance without blocking progress

#### Journey 3: Link Policy to Implementing Decision (Developer)

**Given** a developer is creating an ADR for test strategy
**When** they add `policies: [POL-001]` to the ADR frontmatter
**Then**:
1. ADR explicitly cites governing policy
2. Policy's backlinks automatically include this ADR
3. `spec-driver show POL-001` displays all implementing ADRs
4. Relationship is bidirectionally navigable
5. Decision rationale is grounded in governance context

#### Journey 4: Discover Relevant Policies (Onboarding Developer)

**Given** a new developer wants to understand project rules
**When** they run `spec-driver list policies --status required`
**Then**:
1. System displays all active (required) policies
2. Developer reviews each policy's Statement and Scope
3. Developer understands what rules apply to their work
4. Developer can follow backlinks to see how policies are implemented

### Edge Cases & Non-goals

**Edge Cases**:
- **Conflicting policies**: Two required policies that contradict each other (requires architectural resolution, not tooling)
- **Policy without verification**: Valid but indicates governance gap (flagged in reports)
- **Standard that becomes policy**: Use supersession to deprecate STD-XXX and create POL-XXX
- **Deprecated policy still referenced**: Backlinks show usage; requires cleanup (detected by validation)

**Non-goals**:
- **Automated enforcement**: spec-driver documents policies/standards but doesn't enforce them in CI/CD (integration point for future)
- **Policy authoring permissions**: No access control within spec-driver (handled by git/PR workflows)
- **Policy voting/approval workflows**: Lifecycle management exists, but approval processes are external
- **Compliance dashboards**: Registry enables building dashboards, but spec-driver doesn't provide UI

## 3. Responsibilities & Requirements

### Capability Overview

**Policy Authoring and Lifecycle** enables teams to create hard rules (POL-XXX) that must be followed project-wide. Each policy progresses from draft → required → deprecated, with supersession support for rule evolution. This ensures governance is explicit, traceable, and versioned.

**Standard Authoring and Lifecycle** enables flexible guidance through STD-XXX artifacts. Standards can be "required" (like policies) or "default" (recommended unless justified), supporting both conventions and sensible defaults. This balances consistency with pragmatism.

**Discovery and Navigation** provides CLI commands to list, filter, and display policies/standards, making governance discoverable. Cross-references between policies, standards, and ADRs enable navigation from rules to implementations.

**Traceability and Integration** connects policies/standards to the broader artifact graph (specs, requirements, deltas, ADRs). Bidirectional references and automatic backlinks ensure governance context is always available.

### Functional Requirements

- **FR-001**: System MUST enable creation of policies with unique POL-XXX identifiers
  *Verification*: VT-PROD-003-001 - Create policy via CLI, verify ID assignment and file creation

- **FR-002**: System MUST support policy lifecycle statuses: draft, required, deprecated
  *Verification*: VT-PROD-003-002 - Test status transitions and supersession relationships

- **FR-003**: System MUST enable creation of standards with unique STD-XXX identifiers
  *Verification*: VT-PROD-003-003 - Create standard via CLI, verify ID assignment and file creation

- **FR-004**: System MUST support standard statuses: draft, required, default, deprecated (where "default" indicates recommended unless justified)
  *Verification*: VT-PROD-003-004 - Test default status behavior and documentation

- **FR-005**: System MUST provide CLI commands to list policies and standards with filtering (by status, tags, references)
  *Verification*: VT-PROD-003-005 - Test list commands with various filter combinations

- **FR-006**: System MUST provide CLI commands to display full policy/standard details including metadata and cross-references
  *Verification*: VT-PROD-003-006 - Test show commands with all metadata fields populated

- **FR-007**: System MUST support bidirectional cross-references between policies and standards (policies can reference standards and vice versa)
  *Verification*: VT-PROD-003-007 - Test mutual references and backlink generation

- **FR-008**: System MUST allow ADRs, specs, deltas, and other artifacts to reference policies and standards via frontmatter fields
  *Verification*: VT-PROD-003-008 - Test policy/standard references from ADRs with backlink validation

### Non-Functional Requirements

- **NF-001**: Policies and standards MUST use consistent template structure (Statement, Rationale, Scope, Verification) for predictable authoring experience
  *Measurement*: VA-PROD-003-001 - Template structure validation across all POL/STD files

- **NF-002**: CLI commands for policies/standards MUST follow existing spec-driver UX patterns (argument structure, output formats, filtering semantics)
  *Measurement*: VA-PROD-003-001 - UX consistency review against ADR/spec CLI commands

### Success Metrics / Signals

- **Adoption**: 80% of architectural decisions (ADRs) cite at least one policy or standard within 3 months of feature launch
- **Governance clarity**: All team members can list active policies when asked (measured via onboarding survey)
- **Traceability**: 100% of required policies have at least one implementing ADR or verification artifact linked
- **Flexibility**: >90% of "default" standards are followed without documented deviations (indicating good defaults)

## 4. Solution Outline

### User Experience / Outcomes

**Creating a Policy**:
```bash
$ spec-driver create policy "Code must have tests"
Policy created: POL-001
specify/policies/POL-001-code-must-have-tests.md
```

**Policy Template** (specify/policies/POL-001-code-must-have-tests.md):
```markdown
---
id: POL-001
title: 'POL-001: Code must have tests'
status: draft
created: '2025-11-02'
updated: '2025-11-02'
owners: []
supersedes: []
superseded_by: []
standards: []
specs: []
requirements: []
deltas: []
related_policies: []
related_standards: []
tags: []
summary: ''
---

# POL-001: Code must have tests

## Statement
All production code must be accompanied by automated tests.

## Rationale
Ensures code quality, enables safe refactoring, documents expected behavior.

## Scope
Applies to all production code in main codebase. Excludes prototypes, spikes, and explicitly marked experimental code.

## Verification
- Pre-commit hooks verify test existence
- CI fails on untested code
- Code review checklist includes test coverage

## References
- [Testing Strategy ADR-XXX]
```

**Creating a Standard** (with default status):
```bash
$ spec-driver create standard "Use Google Go Style Guide"
Standard created: STD-001
specify/standards/STD-001-use-google-go-style-guide.md
```

**Listing Policies**:
```bash
$ spec-driver list policies --status required
ID       Title                          Status    Updated
POL-001  Code must have tests           required  2025-11-02
POL-002  Never store unencrypted PII    required  2025-11-01
```

**Listing Standards**:
```bash
$ spec-driver list standards
ID       Title                          Status    Updated
STD-001  Use Google Go Style Guide      default   2025-11-02
STD-002  Prefer focused dependencies    default   2025-11-01
STD-003  Structured logging format      required  2025-10-30
```

**Showing Policy Details**:
```bash
$ spec-driver show policy POL-001
ID: POL-001
Title: Code must have tests
Status: required
Created: 2025-11-02
Updated: 2025-11-02

Statement:
All production code must be accompanied by automated tests.

Backlinks:
  specs: SPEC-099
  deltas: DE-042
  related_decisions: ADR-023, ADR-035
```

**Referencing in ADR**:
```yaml
---
id: ADR-023
title: Adopt TDD for critical business logic
policies: [POL-001]
standards: [STD-003]
---
```

### Data & Contracts

**PolicyRecord / StandardRecord Data Model** (mirrors DecisionRecord):
```python
@dataclass
class PolicyRecord:
  id: str                          # POL-001
  title: str                       # Full title with ID prefix
  status: str                      # draft | required | deprecated
  created: date | None
  updated: date | None
  reviewed: date | None
  owners: list[str]                # Owner names/emails
  supersedes: list[str]            # Previous policy IDs
  superseded_by: list[str]         # Replacing policy IDs
  standards: list[str]             # Referenced standard IDs
  specs: list[str]                 # Referenced spec IDs
  requirements: list[str]          # Referenced requirement IDs
  deltas: list[str]                # Referenced delta IDs
  related_policies: list[str]      # Related policy IDs
  related_standards: list[str]     # Related standard IDs
  tags: list[str]                  # Classification tags
  summary: str                     # Short summary
  path: str                        # File path
  backlinks: dict[str, list[str]]  # Reverse references
```

**StandardRecord** (same structure, but status includes "default"):
- status: draft | required | default | deprecated

**Registry YAML Output** (specify/.registry/policies.yaml):
```yaml
policies:
  POL-001:
    id: POL-001
    title: 'POL-001: Code must have tests'
    status: required
    path: specify/policies/POL-001-code-must-have-tests.md
    summary: All production code must be accompanied by automated tests
    created: '2025-11-02'
    updated: '2025-11-02'
    standards: [STD-003]
    specs: []
    requirements: []
    deltas: []
    related_policies: []
    related_standards: [STD-003]
    tags: [quality, testing]
    backlinks:
      specs: [SPEC-099]
      deltas: [DE-042]
      related_decisions: [ADR-023, ADR-035]
```

## 5. Behaviour & Scenarios

### Primary Flow 1: Create and Publish a Policy

1. **Architect identifies governance need**: Recurring problem requires project-wide rule
2. **Run create command**: `spec-driver create policy "Code must have tests" --author "Jane Architect"`
3. **System generates POL-001**: Assigns next available ID, creates file with frontmatter and template
4. **Architect fills template**: Completes Statement, Rationale, Scope, Verification sections
5. **Update status**: Change from `status: draft` to `status: required` in frontmatter
6. **Sync registry**: Run `spec-driver sync` to update registry YAML
7. **Policy is active**: Discoverable via `spec-driver list policies --status required`

### Primary Flow 2: Establish a Sensible Default Standard

1. **Tech lead identifies common pattern**: Most code follows Google Go style, but not mandated
2. **Create standard with default status**: `spec-driver create standard "Use Google Go Style Guide"`
3. **Set status to default**: Indicates recommendation rather than requirement
4. **Document in Scope section**: Add note: "Recommended unless justified otherwise"
5. **Reference from ADRs**: Developers cite STD-001 when following guide, note deviations when not
6. **Monitor adoption**: Check backlinks to see how often standard is followed vs justified deviations

### Primary Flow 3: Link Policy to Decision

1. **Developer creates ADR**: Working on testing strategy for new service
2. **Add policy reference**: Include `policies: [POL-001]` in ADR frontmatter
3. **Sync registry**: Run `spec-driver sync` to update backlinks
4. **Bidirectional navigation**: `show policy POL-001` displays ADR in backlinks; `show adr ADR-023` displays policy reference
5. **Governance context visible**: Reviewers see policy constraint when reviewing ADR

### Primary Flow 4: Supersede a Policy

1. **Architect refines policy**: POL-001 is too broad, needs splitting
2. **Create new policies**: POL-005 for unit tests, POL-006 for integration tests
3. **Update POL-001**: Set `status: deprecated` and `superseded_by: [POL-005, POL-006]`
4. **Update new policies**: Set `supersedes: [POL-001]` in frontmatter
5. **Sync registry**: Registry reflects supersession relationships
6. **Deprecation visible**: `list policies --status deprecated` shows POL-001; `show policy POL-001` explains replacement

### Error Handling / Guards

- **Duplicate ID**: Creation fails if POL-XXX or STD-XXX already exists (deterministic ID generation prevents collisions)
- **Invalid status**: Validation rejects unknown status values (must be from allowed set)
- **Broken references**: `spec-driver validate` flags references to non-existent policies/standards
- **Missing frontmatter**: Parser handles missing fields gracefully, warns on sync
- **Circular supersession**: A supersedes B, B supersedes A (validation detects and flags)

## 6. Quality & Verification

### Testing Strategy

**Unit Tests** (formatters, ID generation, status validation):
- policy_formatters_test.py: Table/JSON/TSV output formatting
- standard_formatters_test.py: Display formatting with "default" status
- creation_test.py: ID generation, frontmatter building, template rendering

**Integration Tests** (registry, CLI commands, cross-references):
- registry_test.py: File parsing, YAML serialization, filtering, backlinks
- CLI integration: Create → sync → list → show → validate workflows
- Cross-reference integrity: Policy ↔ standard ↔ ADR bidirectional links

**E2E Tests** (full workflows):
- Create policy → reference from ADR → verify backlinks
- Create standard with "default" status → verify documentation
- Supersede policy → verify deprecation cascade
- Filter policies by tags/status → verify result accuracy

### Observability & Analysis

**Governance Metrics**:
- Count of active policies/standards (by status)
- Policy reference frequency (which policies are most cited)
- Standard adoption rate (% of ADRs citing defaults vs deviating)
- Orphan detection (policies with no backlinks = not implemented)

**Registry Health**:
- Broken reference detection (references to non-existent IDs)
- Supersession chain validation (no cycles, complete chains)
- Template conformance (all required sections present)

### Security & Compliance

- **No sensitive data in policies**: Policies should reference security requirements but not include credentials, keys, or PII
- **Git-based access control**: Policy creation/modification follows standard PR approval workflows
- **Audit trail**: Git history provides complete audit log of policy evolution

### Verification Coverage

All requirements mapped to test artifacts in the `supekku:verification.coverage@v1` block above. Testing strategy ensures:
- Every FR has corresponding VT (verification test)
- Every NF has corresponding VA (verification analysis/audit)
- Coverage includes unit, integration, and E2E levels

### Acceptance Gates

Before feature launch:
- [ ] All VT-PROD-003-* tests passing
- [ ] `just test` passes with new tests
- [ ] `just lint` and `just pylint` pass
- [ ] Can create POL-001 and STD-001 via CLI
- [ ] Can list/filter/show policies and standards
- [ ] Bidirectional cross-references working (policy ↔ standard ↔ ADR)
- [ ] ADR frontmatter extended with `standards:` field
- [ ] Registry YAML includes policies.yaml and standards.yaml
- [ ] Documentation updated (CLI help text, README examples)

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

- **SPEC-003** (supekku/cli/create.py): Extends create commands to support `policy` and `standard` subcommands
- **SPEC-004** (supekku/cli/list.py): Extends list commands to support `policies` and `standards` subcommands
- **SPEC-006** (supekku/cli/show.py): Extends show commands to support policy/standard details
- **SPEC-043** (decisions/registry.py): Reuses registry pattern; extends DecisionRecord with `standards:` field
- **SPEC-042** (decisions/creation.py): Pattern for creation logic; extends frontmatter building
- **SPEC-055** (decision_formatters.py): Pattern for formatter implementation

**Interaction nature**:
- **Extends**: Policies/standards add new commands to existing CLI modules
- **Reuses**: Registry, creation, and formatter patterns from decisions domain
- **Integrates**: Cross-references from ADRs, specs, deltas to policies/standards

### Risks & Mitigations

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|------------|--------|------------|
| RISK-001 | Policy/standard proliferation (too many governance artifacts) | Medium | Medium | Establish creation criteria; periodic review/consolidation |
| RISK-002 | Inconsistent enforcement (policies documented but not followed) | Medium | High | Link policies to verification artifacts; CI integration (future) |
| RISK-003 | Confusion between policies and standards | Low | Medium | Clear documentation; status naming ("required" vs "default") |
| RISK-004 | Orphaned policies (no implementing ADRs) | Medium | Low | Registry reports; encourage linking during ADR creation |

### Known Gaps / Debt

- **[Future]** Automated policy enforcement via pre-commit hooks or CI checks (registry provides foundation)
- **[Future]** Policy compliance dashboard showing coverage and adherence metrics
- **[Future]** Policy templates for common governance patterns (security, quality, operations)
- **[Future]** Policy approval workflow integration (currently handled via git/PR)

### Open Decisions / Questions

- **Q1**: Should policies/standards support versioning beyond supersession? (e.g., POL-001 v2)
  - **Current approach**: Use supersession (POL-001 → POL-002) for clarity
  - **Alternative**: Inline versioning (version: field in frontmatter)
  - **Decision**: Defer until user feedback indicates need

- **Q2**: Should "default" standards have expiration dates to force periodic review?
  - **Current approach**: No expiration; rely on reviewed: field and manual audits
  - **Alternative**: Add expires: field that triggers warnings
  - **Decision**: Start simple; add if governance drift becomes issue

## Appendices

### Glossary

- **Policy (POL-XXX)**: Hard rule that must be followed project-wide. Status: draft → required → deprecated.
- **Standard (STD-XXX)**: Convention or sensible default. Status: draft → required | default → deprecated.
  - **required**: Enforced like a policy (must comply)
  - **default**: Recommended unless justified otherwise (flexible guidance)
- **Supersession**: Relationship where a newer policy/standard replaces an older one (preserves history and reasoning)
- **Backlink**: Reverse reference (e.g., policy knows which ADRs cite it)

### Examples of Policies vs Standards

**Policies** (required compliance):
- POL-001: Code must have tests
- POL-002: Never store unencrypted PII
- POL-003: All APIs must use authentication
- POL-004: Security vulnerabilities must be patched within 48 hours

**Standards** (required):
- STD-003: Use structured logging format (required for production services)
- STD-007: Database migrations must be reversible (required for deployments)

**Standards** (default):
- STD-001: Use Google Go Style Guide (recommended unless project-specific needs differ)
- STD-002: Prefer focused dependencies with active maintainers (sensible default)
- STD-004: Use UTC for all timestamps (recommended convention)
- STD-005: Favor composition over inheritance (design principle)

### Migration from Existing Governance Docs

Teams with existing governance documentation can:
1. Identify hard rules → create policies
2. Identify conventions → create standards with "default" status
3. Link from ADRs → add `policies:` and `standards:` frontmatter
4. Deprecate wiki/doc governance → centralize in spec-driver registry
