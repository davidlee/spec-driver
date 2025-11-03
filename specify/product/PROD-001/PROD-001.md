---
id: PROD-001
slug: streamline-spec-creation
name: streamline spec creation
created: '2025-11-01'
updated: '2025-11-01'
status: draft
kind: prod
aliases: []
relations: []
guiding_principles: []
assumptions: []
---

# PROD-001 – streamline spec creation

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-001
requirements:
  primary:
    - PROD-001.FR-001
    - PROD-001.FR-002
    - PROD-001.FR-003
    - PROD-001.FR-004
    - PROD-001.FR-005
    - PROD-001.NF-001
    - PROD-001.NF-002
  collaborators: []
interactions:
  - with: SPEC-110
    nature: Uses CLI package (create, templates, schema) for spec workflows
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-001
capabilities:
  - id: frictionless-spec-creation
    name: Frictionless Spec Creation
    responsibilities:
      - Guide users through complete spec creation without confusion
      - Eliminate manual YAML editing through schema-aware assistance
      - Provide contextual help at every step of the workflow
    requirements:
      - PROD-001.FR-001
      - PROD-001.FR-002
      - PROD-001.NF-001
    summary: >-
      Ensures users can create complete, valid specifications without prior
      knowledge of spec-driver's internal structure or YAML schemas. The
      workflow guides them from initial concept to validated, registry-synced
      specification.
    success_criteria:
      - First-time users complete spec creation without external documentation
      - Zero "what do I do now?" moments during the workflow
      - Agent successfully generates valid YAML blocks without manual correction
  - id: adaptive-guidance
    name: Adaptive Guidance
    responsibilities:
      - Adjust guidance based on spec type (product vs tech)
      - Ask focused clarification questions (max 3)
      - Make informed assumptions with clear documentation
    requirements:
      - PROD-001.FR-003
      - PROD-001.FR-004
    summary: >-
      Provides intelligent, context-aware guidance that adapts to the user's
      needs and the spec type being created. Minimizes cognitive burden by
      asking only critical questions and documenting all assumptions.
    success_criteria:
      - Clarification questions limited to 3 or fewer
      - All assumptions explicitly documented in spec
      - Guidance differs appropriately between product and tech specs
  - id: integrated-validation
    name: Integrated Validation
    responsibilities:
      - Validate YAML blocks against schemas during creation
      - Sync with registry and verify relationships
      - Ensure all requirements are traceable to verification artifacts
    requirements:
      - PROD-001.FR-005
      - PROD-001.NF-002
    summary: >-
      Integrates validation throughout the creation process, catching errors
      early and ensuring the final spec is complete, consistent, and properly
      registered before workflow completion.
    success_criteria:
      - Validation errors caught before spec completion
      - All specs successfully sync to registry on first attempt
      - Verification coverage entries map to actual requirements
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-001
entries:
  - artefact: VT-001
    kind: VT
    requirement: PROD-001.FR-001
    status: planned
    notes: Test Claude command creation and spec bundle generation workflow
  - artefact: VT-002
    kind: VT
    requirement: PROD-001.FR-002
    status: planned
    notes: Verify YAML block completion with schema validation
  - artefact: VT-003
    kind: VT
    requirement: PROD-001.FR-003
    status: planned
    notes: Test adaptive guidance and clarification limiting
  - artefact: VA-001
    kind: VA
    requirement: PROD-001.NF-001
    status: planned
    notes: User testing with first-time users measuring cognitive load and friction points
  - artefact: VA-002
    kind: VA
    requirement: PROD-001.NF-002
    status: planned
    notes: Analyze registry sync success rates and validation error patterns
```

## 1. Intent & Summary

- **Problem / Purpose**: Creating specifications is prohibitively difficult for a framework explicitly designed around spec-driven development. First-time users face a steep learning curve understanding YAML schemas, frontmatter structure, requirement naming conventions, and the relationships between specs, capabilities, and verification artifacts. This friction undermines the core value proposition of spec-driven workflows.

- **Value Signals**: Specifications are the foundation of spec-driven development. Reducing spec creation friction directly impacts:
  - Developer onboarding time (target: <1 hour to first complete spec)
  - Spec documentation coverage across codebase
  - Confidence in spec-driven workflow adoption
  - Agent-assisted development effectiveness

- **Guiding Principles**:
  - **Automate relentlessly**: spec-driver CLI handles all mechanical tasks (file creation, path resolution, schema validation)
  - **Guide comprehensively**: Claude commands provide complete workflow guidance without cluttering templates
  - **Support diversity**: Multi-agent support (Claude, Codex, etc.) as ecosystem matures
  - **Equal treatment**: Product specs receive same tooling quality as tech specs
  - **User autonomy**: Templates and workflows remain customizable to team preferences
  - **Learn from excellence**: Adopt proven patterns from spec-kit and similar tools
  - **Workflow flexibility**: Support spec-first, spec-last, and concurrent development approaches

- **Assumptions**:
  - Users have `uv` installed and spec-driver available via `uv run spec-driver`
  - Claude Code is the primary agent environment (with extensibility for others)
  - Projects using spec-driver have a `.claude/commands/` directory structure
  - Users prefer guided workflows over extensive documentation reading
  - Agent context windows can accommodate full spec template + schema documentation

- **Reference Materials**:
  - spec-kit commands: `./spec-kit/templates/commands/specify.md`
  - spec-driver templates: `supekku/templates/spec.md`
  - Schema documentation: `uv run spec-driver schema show`

- **Change History**:
  - 2025-11-01: Initial draft based on current friction points
  - 2025-11-02: Refined based on supekku.specify command implementation 

## 2. Stakeholders & Journeys

### Personas / Actors

1. **Solo Developer (Sarah)**
   - **Context**: Working on personal project or small OSS tool
   - **Goals**: Document features without process overhead; quickly create specs that aid future development
   - **Pains**: Doesn't know YAML schemas; forgets spec-driver conventions between sessions
   - **Expectations**: Type `/supekku.specify <feature idea>`, answer 2-3 questions, get complete spec

2. **Team Lead (Marcus)**
   - **Context**: Managing 3-8 developer team on larger codebase
   - **Goals**: Ensure consistent spec quality across team; reduce onboarding time for new team members
   - **Pains**: Manual spec reviews find YAML errors, missing requirements, broken relationships
   - **Expectations**: Team members create valid specs without constant guidance; agents catch errors automatically

3. **Developer in Team (Aisha)**
   - **Context**: Contributing to established project with existing spec-driven culture
   - **Goals**: Create specs that match team standards; understand how her component relates to others
   - **Pains**: Uncertain about requirement naming, capability structure, verification coverage
   - **Expectations**: Workflow guides her through team conventions; relationship discovery helps find related specs

4. **AI Agent (Claude/Codex)**
   - **Context**: Assisting user with feature implementation in spec-driven project
   - **Goals**: Generate complete, valid specifications that sync cleanly to registry
   - **Pains**: Ambiguous schema documentation; unclear workflow steps; manual YAML editing error-prone
   - **Expectations**: Clear command structure; schema documentation in context; validation before completion

### Primary Journeys / Flows

**Journey 1: First-Time User Creates Product Spec**

Given Sarah has just installed spec-driver and wants to document a new feature
1. Sarah types `/supekku.specify implement user preferences dashboard`
2. Agent generates concise spec name: "user-preferences-dashboard"
3. Agent invokes `uv run spec-driver create spec user-preferences-dashboard --kind product --json`
4. Agent receives JSON output with `spec_path: specify/product/PROD-XXX/PROD-XXX.md`
5. Agent fetches YAML schemas via `uv run spec-driver schema show spec.relationships` (etc.)
6. Agent asks Sarah 2-3 focused questions about scope, users, success metrics
7. Agent fills all sections systematically, documenting assumptions for gaps
8. Agent validates: all YAML blocks complete, requirements traceable, no placeholders
9. Agent runs `uv run spec-driver sync && uv run spec-driver validate`
10. Agent reports: "Created PROD-XXX at specify/product/PROD-XXX/PROD-XXX.md (validated)"

Then Sarah can immediately start implementation or refine the spec
And she experienced zero "what do I do now?" moments

**Journey 2: Team Developer Creates Tech Spec with Relationships**

Given Aisha needs to document a new API client component that integrates with existing auth system
1. Aisha types `/supekku.specify create oauth2 api client with token refresh`
2. Agent creates tech spec (includes testing companion automatically)
3. Agent asks: "Which existing specs handle authentication?" and offers to search
4. Aisha says "not sure, find them"
5. Agent runs `uv run spec-driver list specs | grep -i auth` and finds SPEC-045 (auth manager)
6. Agent asks: "Should this spec own the token refresh logic or collaborate with SPEC-045?"
7. Aisha clarifies ownership boundaries
8. Agent completes spec with proper `interactions` in relationships YAML block
9. Testing companion includes integration test requirements referencing SPEC-045
10. Validation confirms relationships are bi-directional and consistent

Then Aisha's spec correctly documents dependencies and integration points
And the team can understand the architecture through spec relationships

**Journey 3: Agent-Driven Spec Creation During Implementation**

Given Claude is implementing a feature and realizes a spec should exist
1. Claude recognizes: "This background job needs documentation"
2. Claude invokes `/supekku.specify background job for data export with retry logic`
3. Claude uses existing code context to infer technical details
4. Claude asks user: "Should exports include all data or configurable subsets?" (1 clarification)
5. User responds: "Configurable subsets via filter config"
6. Claude generates complete tech spec with architecture details from codebase
7. Claude links requirements to existing test files it plans to create
8. Spec validation passes; Claude continues with implementation referencing spec IDs

Then the implementation and spec remain synchronized
And requirements are traceable to code and tests

### Edge Cases & Non-goals

**Edge Cases**:
- User specifies obscure spec type → Agent defaults to tech, asks for confirmation
- Spec name conflicts with existing spec → spec-driver returns error, agent suggests alternative
- User provides minimal description → Agent makes maximum informed assumptions, documents them clearly
- Validation fails on first attempt → Agent displays specific errors, corrects, re-validates
- User wants to update existing spec → Out of scope (different workflow/command)

**Non-goals**:
- **Editing/updating existing specs** (separate `/supekku.refine-spec` or `/supekku.complete-spec` command, see RISK-007)
  - Use case: User manually created spec or sync generated placeholder tech spec
  - Need: Complete existing spec without re-running full creation workflow
  - Scope: Out of PROD-001; requires separate command/workflow
- Generating specs from code (code-first workflow, see SPEC-072 sync engine)
- Multi-spec bulk operations (team leads use scripting, not interactive workflow)
- Real-time collaborative spec editing (version control handles this)
- Git workflow integration (project-specific, configured via policies/ADRs)
- Project planning tool integration (team-specific, out of initial scope, noted for future)

## 3. Responsibilities & Requirements

### Capability Overview

See capabilities YAML block above for complete capability definitions. Key behaviors:

**Frictionless Spec Creation** ensures users can invoke a single command and receive a complete, validated specification without needing to:
- Manually edit YAML blocks (agent fills them using schema documentation)
- Look up requirement naming conventions (agent follows established patterns)
- Understand directory structure (spec-driver handles path resolution)
- Debug validation errors manually (integrated validation with clear error messages)

**Adaptive Guidance** minimizes cognitive load by:
- Asking only critical clarification questions (max 3, prioritized by impact)
- Making informed assumptions for non-critical details (documented in spec)
- Tailoring section content to spec type (product: user journeys; tech: architecture)
- Offering to discover relationships through spec-driver queries

**Integrated Validation** prevents errors from reaching the registry by:
- Validating YAML block syntax against schemas during editing
- Verifying requirement IDs follow naming conventions before finalization
- Confirming all verification coverage entries map to actual requirements
- Running `spec-driver sync` and `validate` as final workflow steps

### Functional Requirements

- **FR-001**(workflow): Claude Command Provides Complete Workflow
  The `.claude/commands/supekku.specify.md` command file contains all instructions necessary for an agent to guide a user from feature description to validated, registry-synced specification without external documentation.
  *Verification*: VT-001 - Test agent follows command from start to finish with zero external lookups

- **FR-002**(automation): Agent Completes All YAML Blocks Without Manual Editing
  The workflow instructs agents to fetch schema documentation via `spec-driver schema show` and use it to generate valid YAML blocks for `spec.relationships`, `spec.capabilities`, and `verification.coverage` without requiring users to manually edit YAML syntax.
  *Verification*: VT-002 - Validate 100 generated specs have valid YAML blocks with zero manual corrections

- **FR-003**(ux): Clarification Questions Limited to Critical Decisions
  Agents ask maximum 3 clarification questions, prioritized by scope > security > UX impact, making informed assumptions for all other details and documenting those assumptions in the spec's Intent & Summary section.
  *Verification*: VT-003 - Analyze 50 spec creation sessions, confirm ≤3 questions asked, all assumptions documented

- **FR-004**(workflow): Spec Type Determines Section Content Adaptation
  Product specs emphasize user personas, journeys, and business value; tech specs emphasize architecture, components, and integration contracts. The workflow instructs agents to adapt section content appropriately based on `--kind` flag.
  *Verification*: Manual review of 20 product specs and 20 tech specs confirms appropriate content focus

- **FR-005**(validation): Validation Integrated Before Workflow Completion
  The workflow requires agents to run `spec-driver sync` and `spec-driver validate` commands before declaring spec creation complete, catching errors (invalid relationships, missing requirements, YAML syntax issues) before user moves to next task.
  *Verification*: VT-002 - Confirm validation catches all common error types (tested via intentional error injection)

### Non-Functional Requirements

- **NF-001**(ux): First-Time User Experience Requires Minimal Cognitive Load
  Users with zero spec-driver experience can complete their first spec creation in under 1 hour with zero "what do I do now?" friction points.
  *Measurement*: VA-001 - User testing with 10 first-time users, measure time-to-completion and friction point incidents (target: 0 critical friction points)

- **NF-002**(reliability): Registry Sync Success Rate >95% on First Attempt
  Specs created through this workflow sync to the registry without errors on first attempt in >95% of cases, indicating validation catches errors early.
  *Measurement*: VA-002 - Track sync success rate over 200 spec creations across diverse projects

### Success Metrics / Signals

- **Adoption**: 80%+ of new specs created via `/supekku.specify` command (vs manual creation)
- **Quality**: <5% of created specs require manual YAML corrections post-creation
- **Onboarding**: First-time users create valid spec in <1 hour (measured via user testing)
- **Confidence**: User survey shows 85%+ agree "I felt guided throughout the process"
- **Agent effectiveness**: Agents successfully complete workflow without intervention in 90%+ of attempts
- **Validation success**: >95% first-attempt registry sync success rate

## 4. Solution Outline

### User Experience / Outcomes

**Desired Behaviors**:

1. **Single-Command Invocation**: User types `/supekku.specify <feature description>` and receives complete workflow guidance
   - No manual template copying
   - No directory structure decisions
   - No YAML syntax learning required

2. **Conversational Clarification**: Agent asks 2-3 focused, easy-to-answer questions
   - Questions presented with multiple-choice options when possible
   - Context provided for why the question matters
   - "I don't know, use your judgment" is valid answer

3. **Transparent Progress**: User sees clear indication of workflow stages
   - "Creating spec bundle..."
   - "Fetching YAML schemas..."
   - "Filling Section 3: Requirements..."
   - "Validating and syncing..."

4. **Assumption Documentation**: All agent-made assumptions visible in final spec
   - Documented in Intent & Summary section
   - User can review and adjust post-creation if needed

5. **Validation Feedback**: Clear, actionable error messages if validation fails
   - "Requirement PROD-001.FR-006 referenced in verification coverage but not defined in FR section"
   - Agent automatically fixes and re-validates

**Acceptance Criteria**:
- First-time user completes workflow without consulting external documentation
- Workflow duration: 5-15 minutes depending on clarification complexity
- User confidence: "I understand what just happened and could do it again"
- Output quality: Spec passes validation and syncs to registry on first attempt

### Data & Contracts

**Claude Command Structure** (`.claude/commands/supekku.specify.md`):
```yaml
---
description: Create or refine a product or tech specification using spec-driver
---

## User Input
$ARGUMENTS (feature description from user)

## Workflow
[8 major steps: metadata generation → bundle creation → schema fetch →
 section filling → gap handling → validation → sync → completion report]
```

**spec-driver CLI Contracts**:
```bash
# Create spec bundle
uv run spec-driver create spec <name> --kind <product|tech> --json
# Returns: {"spec_id": "...", "spec_path": "...", "testing_path": "..."}

# Get schema documentation
uv run spec-driver schema show <block-type>
# Returns: Rich-formatted schema with parameters and examples

# Sync and validate
uv run spec-driver sync    # Updates registries
uv run spec-driver validate # Checks metadata consistency
```

**YAML Block Schemas** (see `spec-driver schema show` for details):
- `supekku:spec.relationships@v1`: Links spec to requirements and other specs
- `supekku:spec.capabilities@v1`: Defines capabilities with success criteria
- `supekku:verification.coverage@v1`: Maps requirements to verification artifacts

**Spec Template Structure** (Jinja2 template at `supekku/templates/spec.md`):
- Frontmatter: id, slug, name, status, kind
- YAML blocks (placeholder variables for spec_id, requirements, etc.)
- 7 sections: Intent, Stakeholders, Requirements, Solution, Behaviour, Quality, Backlog

## 5. Behaviour & Scenarios

### Primary Flows

**Flow 1: Minimal Description with Maximum Assumptions** (PROD-001.FR-003)

1. User provides minimal input: `/supekku.specify payment processing`
2. Agent generates name: "payment-processing"
3. Agent invokes spec creation, receives PROD-042
4. Agent makes informed assumptions:
   - Product spec (default for user-facing feature)
   - Standard payment flows (checkout, refund, receipt)
   - Typical security requirements (PCI compliance, encryption)
   - Common integrations (payment gateway, transaction log)
5. Agent documents all assumptions in Section 1
6. Agent asks 1 clarifying question: "Which payment methods to support initially?"
7. User responds or says "start with credit cards"
8. Agent completes spec with assumptions clearly marked
9. Validation passes, sync succeeds

**Flow 2: Tech Spec with Relationship Discovery** (PROD-001.FR-002, PROD-001.FR-004)

1. User: `/supekku.specify database migration orchestrator`
2. Agent creates tech spec SPEC-087 with testing companion
3. Agent asks: "Should I search for related database/migration specs?"
4. User: "Yes"
5. Agent runs `uv run spec-driver list specs | grep -i 'database\|migration'`
6. Agent finds SPEC-023 (schema evolution), SPEC-061 (data access layer)
7. Agent asks: "How does this relate to SPEC-023?" Options: [Depends on, Collaborates with, Replaces]
8. User: "Collaborates - orchestrator calls schema evolution"
9. Agent fills relationships YAML with proper interactions
10. Tech spec includes architecture diagram placeholder, integration contracts
11. Testing companion includes integration test requirements
12. Validation confirms bidirectional relationships

**Flow 3: Validation Error Recovery** (PROD-001.FR-005)

1. Agent completes spec, runs validation
2. Validation error: "Requirement PROD-001.FR-006 in verification coverage not found in FR section"
3. Agent analyzes: verification entry references non-existent requirement
4. Agent fixes: Either adds missing FR-006 or corrects verification entry reference
5. Agent re-runs validation
6. Success: spec syncs to registry

### Error Handling / Guards

**Guard: Spec Name Conflicts**
- Condition: Generated name matches existing spec slug
- Response: spec-driver returns error with existing spec ID
- Recovery: Agent appends differentiator (e.g., "payment-processing-v2" or "payment-processing-api")

**Guard: Invalid YAML Syntax**
- Condition: Agent-generated YAML has syntax errors
- Response: Validation catches before sync attempt
- Recovery: Agent re-generates using schema documentation, validates syntax locally first

**Guard: Incomplete Requirements**
- Condition: Verification coverage references requirement not defined in FR/NF sections
- Response: Validation error with specific requirement ID
- Recovery: Agent adds missing requirement or removes verification entry

**Guard: User Abandons Mid-Workflow**
- Condition: User doesn't respond to clarification questions within reasonable time
- Response: Agent saves work-in-progress spec with [NEEDS CLARIFICATION] markers
- Recovery: User can resume later; spec marked as draft status

**Guard: Registry Sync Failures**
- Condition: File permission issues, git conflicts, corrupted registry
- Response: Sync command returns specific error
- Recovery: Agent reports error to user with troubleshooting steps (check permissions, resolve conflicts, run repair)

## 6. Quality & Verification

### Testing Strategy

**VT-001: End-to-End Workflow Testing** (PROD-001.FR-001)
- **Scope**: Full workflow from `/supekku.specify` invocation to validated spec in registry
- **Method**: Automated test with Claude API simulating user interaction
- **Test Cases**:
  - Minimal input ("payment processing") → complete product spec
  - Detailed tech spec with relationships
  - Error recovery (invalid YAML, missing requirements)
- **Success Criteria**: 100% workflow completion without manual intervention

**VT-002: YAML Block Validation Testing** (PROD-001.FR-002, PROD-001.FR-005)
- **Scope**: YAML block generation and schema compliance
- **Method**: Generate 100 specs across diverse feature types, validate syntax and semantics
- **Test Cases**:
  - All three YAML block types present and valid
  - Requirement IDs follow naming conventions
  - Verification coverage entries map to actual requirements
  - Relationships reference existing specs
- **Success Criteria**: 100% valid YAML, 95% first-attempt sync success

**VT-003: Clarification Limiting Testing** (PROD-001.FR-003)
- **Scope**: Adaptive guidance and assumption documentation
- **Method**: Analyze 50 spec creation sessions, count questions and check assumption documentation
- **Test Cases**:
  - Maximum 3 clarification questions asked
  - All assumptions documented in Intent & Summary
  - No critical details missing from final spec
- **Success Criteria**: Zero sessions exceed 3 questions; all assumptions documented

**VA-001: First-Time User Experience Research** (PROD-001.NF-001)
- **Scope**: Cognitive load and friction point identification
- **Method**: User testing with 10 participants (zero spec-driver experience)
- **Protocol**:
  - Task: "Create a spec for a todo list feature"
  - Observe and record friction points ("what do I do now?" moments)
  - Measure time to completion
  - Post-task survey on confidence and clarity
- **Success Criteria**: <1 hour completion, zero critical friction points, 80%+ confidence rating

**VA-002: Registry Sync Success Analysis** (PROD-001.NF-002)
- **Scope**: Validation effectiveness and error patterns
- **Method**: Track sync outcomes over 200 real spec creations across multiple projects
- **Metrics**:
  - First-attempt sync success rate (target: >95%)
  - Common validation error categories
  - Error recovery success rate
- **Success Criteria**: >95% first-attempt success; all error categories have documented recovery paths

### Research / Validation

**Hypothesis 1**: Schema documentation in agent context eliminates manual YAML editing
- **Test**: Compare YAML error rates with/without schema documentation access
- **Metric**: YAML syntax errors per 100 specs
- **Target**: <2 errors per 100 specs with schema docs vs >20 without

**Hypothesis 2**: Three-question limit doesn't compromise spec quality
- **Test**: Compare completeness scores of 3-question-limited specs vs unlimited questions
- **Metric**: Completeness audit score (0-100) based on section fill quality
- **Target**: <5 point difference between limited and unlimited approaches

**Hypothesis 3**: First-time users prefer guided workflow over documentation
- **Test**: A/B test: guided command vs "read the docs then create manually"
- **Metric**: Time to first valid spec, user satisfaction (1-10 scale)
- **Target**: Guided workflow 3x faster, +2 points higher satisfaction

### Observability & Analysis

**Workflow Telemetry** (optional, privacy-respecting):
- Spec creation duration (start to sync completion)
- Question count per session
- Validation error categories and frequencies
- Sync attempt count before success
- Agent type (Claude, Codex, other) correlation with success rates

**Dashboard Metrics**:
- Weekly spec creation count (trend)
- First-attempt sync success rate (rolling 30-day)
- Average clarification question count
- Top validation error types
- User onboarding funnel (install → first spec → second spec)

### Security & Compliance

**Data Privacy**:
- Spec content may include sensitive business logic → no external telemetry without opt-in
- Local-only validation and registry operations
- User controls all data; spec-driver makes no external API calls

**Agent Capabilities**:
- Agents require file system write access (spec creation)
- Agents execute CLI commands (spec-driver invocation)
- Command injection risk mitigated: spec-driver uses argument parsing, not shell execution

### Verification Coverage

See `supekku:verification.coverage@v1` YAML block above. Summary:
- VT-001 → PROD-001.FR-001 (workflow completeness)
- VT-002 → PROD-001.FR-002, FR-005 (YAML generation and validation)
- VT-003 → PROD-001.FR-003 (clarification limiting)
- VA-001 → PROD-001.NF-001 (user experience quality)
- VA-002 → PROD-001.NF-002 (sync success rate)

All verification artifacts in planned status; implementation follows spec completion.

### Acceptance Gates

Must achieve before declaring feature complete:

1. **Workflow Completeness**: VT-001 passes with 100% success rate across 20 diverse test cases
2. **YAML Quality**: VT-002 shows >95% first-attempt sync success across 100 generated specs
3. **User Experience**: VA-001 demonstrates <1 hour onboarding, zero critical friction points
4. **Documentation**: Command file `.claude/commands/supekku.specify.md` reviewed and approved
5. **Real-World Validation**: 10 actual users create specs successfully without maintainer intervention

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

**Direct Dependencies**:
- **SPEC-110** (supekku/cli): CLI package providing create, templates, schema commands

**Collaborators**:
- **SPEC-110** (supekku/cli): CLI package with sync and validate commands

**Future Integration Candidates** (noted for policies/ADRs):
- Version control workflow integration (git branch creation, commit automation)
- Project planning tool integration (Jira, Linear, etc.)
- Team notification hooks (Slack, Discord) on spec creation
- Spec review/approval workflow tooling

### Risks & Mitigations

**RISK-001**: Agent context window limitations prevent including full schema documentation
- **Likelihood**: Medium (larger projects with many specs strain context)
- **Impact**: High (incomplete schema docs → YAML errors)
- **Mitigation**: Implement schema summary mode with "full details on request"; progressive disclosure

**RISK-002**: Validation edge cases not caught until production use
- **Likelihood**: Medium (spec-driver validation evolves; new edge cases emerge)
- **Impact**: Medium (sync failures frustrate users but recoverable)
- **Mitigation**: Comprehensive test suite with intentional error injection; user feedback loop for new error types

**RISK-003**: Different agent platforms (Claude, Codex, Gemini) interpret workflow differently
- **Likelihood**: High (each platform has quirks)
- **Impact**: Medium (workflow works well on Claude, fails on others)
- **Mitigation**: Platform-specific command variants if needed; abstract common patterns; test on multiple platforms

**RISK-004**: Template customization by users breaks workflow assumptions
- **Likelihood**: Medium (users modify templates to fit team needs)
- **Impact**: Low (workflow still functions; generated content may not fit custom structure)
- **Mitigation**: Document template extension points; version command file with template schema

**RISK-005**: Orphan detection deletes manually created tech specs during sync
- **Likelihood**: High (sync engine sees specs without matching code packages)
- **Impact**: Critical (data loss; user-created specs deleted incorrectly)
- **Mitigation**: Implement protection mechanism - specs without code package links marked as "manual" (via frontmatter flag or detection heuristic); sync skips deletion for manual specs; add `--dry-run` mode to show what would be deleted
- **Status**: CRITICAL - must address before widespread adoption

**RISK-006**: Users don't add INIT.md reference to CLAUDE.md, agents can't invoke spec-driver
- **Likelihood**: Very High (installer doesn't prompt; users skip setup step)
- **Impact**: High (workflow completely broken; agents don't know how to call `uv run spec-driver`)
- **Mitigation**: Installer script must prompt user to add `@supekku/INIT.md` to project CLAUDE.md; provide copy-paste instructions; verify reference exists before proceeding; create `spec-driver doctor` command to check setup
- **Status**: BLOCKER for FR-001 - must implement in installer

**RISK-007**: No workflow for completing existing/vestigial specs
- **Likelihood**: Very High (users manually create specs, sync creates placeholder tech specs)
- **Impact**: High (current workflow assumes new spec creation; user must manually sync 3 different commands)
- **Mitigation**: Create separate `/supekku.refine-spec` or `/supekku.complete-spec` command that: (a) detects existing spec file, (b) skips `create spec` invocation, (c) fills incomplete sections, (d) same validation/sync workflow
- **Status**: HIGH PRIORITY - common use case not supported by PROD-001 scope
- **Alternative**: Make `/supekku.specify` detect existing spec and adapt workflow automatically

### Known Gaps / Debt

**Gaps**:
- Multi-agent platform testing not yet conducted → test on Codex, Gemini beyond Claude
- Relationship discovery heuristics basic → could leverage NLP/semantic search for better suggestions
- **HIGH PRIORITY**: No spec refinement/completion workflow → users with existing specs (manual or sync-generated) can't use guided workflow
- Policy/constitution framework barely defined → need ADR/policy structure for team-specific preferences
- **CRITICAL**: No `supekku/INIT.md` file exists yet → must create with spec-driver invocation patterns
- **CRITICAL**: Installer doesn't guide CLAUDE.md setup → agents won't know how to invoke CLI
- **CRITICAL**: Orphan detection lacks manual spec protection → risk of data loss

**Backlog Items**:
- `ISSUE-003`: Create supekku/INIT.md with invocation patterns for agents (CRITICAL)
- `ISSUE-004`: Enhance installer to prompt CLAUDE.md setup with verification (BLOCKER)
- `ISSUE-005`: Implement orphan detection protection for manual specs (CRITICAL)
- `ISSUE-006`: Create spec refinement/completion workflow for existing specs (HIGH PRIORITY)
- TODO: Test workflow on Codex and Gemini platforms
- TODO: Implement semantic search for relationship discovery
- TODO: Create `PROB-002` - Policy framework undefined (blocks git/planning tool integration)

### Open Decisions / Questions

**Decision 1**: Should command support batch spec creation (multiple specs from single description)?
- **Context**: User describes system with multiple components
- **Options**: (A) Single command creates all related specs, (B) Separate invocations per spec
- **Leaning**: B (simpler, more controllable) but flag for discussion

**Decision 2**: How to handle template versioning when command evolves?
- **Context**: Command file references template structure; templates may change
- **Options**: (A) Version command alongside templates, (B) Command detects template version and adapts
- **Status**: Unresolved; needs ADR

**Decision 3**: Should failed validation allow "save draft anyway" option?
- **Context**: User might want to save progress even if validation fails
- **Options**: (A) Force fix before save, (B) Allow draft save with warnings
- **Leaning**: B (user autonomy) with clear warning markers

## Appendices (Optional)
- Glossary, detailed research, extended API examples, migration history, etc.