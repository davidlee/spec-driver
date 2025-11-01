---
description: Create or refine a product or tech specification using spec-driver
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Overview

The text the user typed after `/spec-driver.create-spec` **is** the spec description. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that spec description, create a complete, high-quality specification following spec-driver conventions.

## Workflow

### 1. Generate Spec Metadata

From the feature description:

- **Extract a concise short name** (2-5 words):
  - Analyze description and extract meaningful keywords
  - Use action-noun format when possible (e.g., "User Authentication", "Payment Processing")
  - Preserve technical terms (OAuth2, API, GraphQL, etc.)
  - Examples:
    - "Add user authentication with OAuth" → "User OAuth"
    - "Implement payment processing" → "Payment Processing"
    - "Create analytics dashboard" → "Analytics Dashboard"

- **Determine spec kind**:
  - Product spec (`--kind product`): User-facing features, business requirements, UX flows
  - Tech spec (`--kind tech`, default): Architecture, components, implementation details

### 2. Create the Spec Bundle

Run spec-driver to generate the initial structure:

```bash
uv run spec-driver create spec <short-name> --kind <product|tech> --json
```

**CRITICAL**:
- Use `--json` flag to get machine-readable output with file paths
- The JSON output contains `spec_path` and optionally `testing_path`
- Tech specs automatically include a testing companion file (`--testing` is default)
- Product specs do not include testing companions
- Store these paths for subsequent editing

**Example output structure**:
```json
{
  "spec_id": "SPEC-001",
  "spec_path": "specify/tech/SPEC-001/SPEC-001.md",
  "testing_path": "specify/tech/SPEC-001/SPEC-001.testing.md",
  "kind": "tech"
}
```

### 3. Get Schema Documentation

Before filling in YAML blocks, fetch schema documentation for guidance:

```bash
uvx spec-driver schema show 
```

Use these to understand required and optional fields in the structured blocks.

### 4. Fill the Specification

Using the spec template and user's description, systematically complete each section:

#### Section 1: Intent & Summary

- **Product specs**: Focus on problem/purpose, user value, market context
- **Tech specs**: Define scope/boundaries, what's in/out
- Both: Value signals (metrics, outcomes), guiding principles, change history

#### Section 2: Stakeholders & Journeys

- **Product specs**: Personas, user journeys, flows
- **Tech specs**: Systems, integrations, external dependencies
- Both: Primary flows (Given-When-Then or sequence steps), edge cases, non-goals

#### Section 3: Responsibilities & Requirements

**CRITICAL - Complete the YAML blocks first**:

1. **`supekku:spec.relationships@v1`**:
   - `spec`: The spec ID (e.g., `SPEC-001`)
   - `requirements.primary`: List of FR/NF codes this spec owns (e.g., `["SPEC-001.FR-001", "SPEC-001.NF-001"]`)
   - `requirements.collaborators`: Other specs' requirements this collaborates with (optional)
   - `interactions`: List of `{with: "SPEC-XXX", nature: "description"}` for related specs (optional)

2. **`supekku:spec.capabilities@v1`**:
   - `spec`: The spec ID
   - `capabilities`: List of capability objects:
     - `id`: kebab-case-capability-id
     - `name`: Human-readable capability name
     - `responsibilities`: List of what this capability ensures
     - `requirements`: List of FR/NF codes this capability satisfies
     - `summary`: Short paragraph describing the capability
     - `success_criteria`: List of measurable success indicators

3. **`supekku:verification.coverage@v1`**:
   - `subject`: The spec ID
   - `entries`: List of verification mappings:
     - `artefact`: Verification artifact ID (VT-XXX, VA-XXX, VH-XXX)
     - `kind`: Artifact type (VT for tests, VA for analysis, VH for history)
     - `requirement`: Requirement code being verified
     - `status`: planned | implemented | validated
     - `notes`: Optional context or evidence pointer

**Then expand in prose**:
- Capability overview referencing YAML capabilities
- Functional Requirements (FR): `SPEC-XXX.FR-001` – clear, testable statement – how verified
- Non-Functional Requirements (NF): `SPEC-XXX.NF-001` – measurable constraint – measurement approach
- Success metrics (product) / Operational targets (tech)

**Discovering relationships**:
- It's valuable and important to determine and record related entities correctly.
- The User likely has some, but not all, of the relevant details.
- Ask them 2-5 focused, short-answer questions to begin to fill in the metadata. 
- Then, perform targeted research using `spec-driver` to assist in discovery and navigation.
- Check with the User periodically if you should continue your research, or ask further questions.

#### Section 4: Solution Outline

- **Product specs**: User experience, outcomes, desired behaviors, storyboards
- **Tech specs**: Architecture, components, diagrams, interfaces
- Both: Data models, entities, schemas, API contracts

#### Section 5: Behaviour & Scenarios

- Primary flows with step-by-step sequences
- Error handling, guards, recovery paths
- **Tech specs**: State transitions (diagrams/tables if stateful)

#### Section 6: Quality & Verification

- Testing strategy mapping requirements to test levels
- **Product specs**: UX research, validation experiments, hypothesis tracking
- Both: Observability (metrics, telemetry, alerting), security, compliance
- Keep verification coverage YAML block aligned
- Acceptance gates

#### Section 7: Backlog Hooks & Dependencies

- Related specs and their relationship nature
- Risks with ID, description, likelihood/impact, mitigation
- Known gaps (link to backlog items: `ISSUE-`, `PROB-`, `RISK-`)
- Open decisions/questions

### 5. Intelligent Gap Handling

When the user's description lacks detail:

1. **Make informed assumptions**:
   - Use context, industry standards, common patterns
   - Document assumptions clearly in Section 1 (Intent & Summary)
   - Use reasonable defaults (standard auth, typical performance targets, etc.)

2. **Limit clarifications**:
   - Maximum **3 [NEEDS CLARIFICATION]** markers total
   - Only for critical decisions that significantly impact:
     - Feature scope or boundaries
     - Security/compliance requirements
     - User experience with multiple valid interpretations
   - Each marker must include: `[NEEDS CLARIFICATION: specific question]`

3. **Create backlog items for gaps**:
   - Use spec-driver to create backlog entries:
     - `uv run spec-driver create issue <title>` – for missing details
     - `uv run spec-driver create problem <title>` – for identified problems
     - `uv run spec-driver create risk <title>` – for identified risks
   - Link these in Section 7 (Backlog Hooks)

### 6. Quality Validation

Before declaring completion, validate the spec:

**Content Quality**:
- [ ] Product specs: No implementation details (languages, frameworks, specific tools)
- [ ] Tech specs: Implementation details grounded in project architecture
- [ ] Both: Clear, testable requirements
- [ ] Both: Measurable success criteria
- [ ] All mandatory sections completed
- [ ] YAML blocks valid and complete

**Requirement Completeness**:
- [ ] ≤3 [NEEDS CLARIFICATION] markers (preferably 0)
- [ ] Every FR/NF has verification approach
- [ ] Capabilities link to requirements
- [ ] Edge cases identified
- [ ] Dependencies and assumptions documented

**YAML Block Validation**:
- [ ] All blocks have correct schema markers
- [ ] Required fields populated
- [ ] Requirement codes follow naming convention (`SPEC-XXX.FR-NNN`, `SPEC-XXX.NF-NNN`)
- [ ] Verification entries map to actual requirements

### 7. Handle Clarifications (If Needed)

If [NEEDS CLARIFICATION] markers remain after your best effort:

1. Present clarifications to user in this format:

```markdown
## Clarification Needed [N/3]: [Topic]

**Context**: [Quote relevant spec section]

**Question**: [Specific question from marker]

**Options**:

| Choice | Answer | Implications |
|--------|--------|--------------|
| A | [First option] | [What this means] |
| B | [Second option] | [What this means] |
| C | [Third option] | [What this means] |
| Custom | Your answer | Provide alternative |

**Your choice**: _[Wait for response]_
```

2. Present all clarifications together before waiting
3. Wait for user responses (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
4. Update spec by replacing [NEEDS CLARIFICATION] markers with chosen answers
5. Re-validate

### 8. Sync and Finalize

Once the spec is complete and validated:

1. **Sync the registry**:
   ```bash
   uv run spec-driver sync
   ```
   This updates registries and validates relationships.

2. **Verify the spec**:
   ```bash
   uv run spec-driver validate
   ```
   Check for metadata consistency and relationship integrity.

3. **Report completion**:
   - Spec ID and path
   - Kind (product/tech)
   - Validation status
   - Any backlog items created
   - Next steps (implementation, review, etc.)

## Execution Guidelines

### Make It Excellent

- **Clarity**: Use precise, unambiguous language
- **Traceability**: Link requirements to capabilities to verification
- **Completeness**: Fill all sections meaningfully or remove if N/A
- **Consistency**: Ensure YAML blocks align with prose sections
- **Practicality**: Ground in project context and existing architecture

### Product vs Tech Spec Differences

**Product Specs** (`--kind product`):
- Focus on WHAT and WHY
- User-centric language
- Business value and outcomes
- Personas and user journeys
- No technical implementation details
- No testing companion

**Tech Specs** (`--kind tech`):
- Focus on HOW
- Technical architecture and components
- Implementation constraints
- System integrations
- Code references and diagrams
- Includes testing companion

### Testing Companion (Tech Specs Only)

The auto-generated `.testing.md` file covers:
- Test strategy per requirement
- Test levels (unit, integration, e2e)
- Test data and fixtures
- Coverage expectations
- Performance benchmarks

Fill this alongside the main spec for comprehensive documentation.

## Common Patterns

### Reasonable Defaults

Don't ask for clarification on these:

- **Authentication**: Standard session-based or OAuth2 for web apps
- **Performance**: Standard web/mobile expectations unless otherwise specified
- **Error handling**: User-friendly messages with appropriate fallbacks
- **Data retention**: Industry-standard practices for the domain
- **Integration patterns**: RESTful APIs (web) unless specified otherwise

### When to Clarify (≤3 total)

Only for critical, high-impact decisions:

- Feature scope boundaries (include/exclude specific use cases)
- Security/compliance requirements (legal/financial impact)
- User permissions and access control (multiple conflicting interpretations)
- Data privacy requirements (regulatory implications)

## Tooling Reference


## Final Checklist

Before reporting completion:

- [ ] Spec created via `spec-driver create spec --json`
- [ ] All YAML blocks properly formatted with correct schema markers
- [ ] Every section filled with meaningful content or removed if N/A
- [ ] Requirements numbered sequentially (FR-001, FR-002, etc.)
- [ ] Capabilities link to requirements
- [ ] Verification coverage entries map to actual requirements
- [ ] ≤3 [NEEDS CLARIFICATION] markers (ideally 0)
- [ ] Assumptions documented in Section 1
- [ ] Backlog items created and linked in Section 7
- [ ] Testing companion filled (tech specs only)
- [ ] `spec-driver sync` executed successfully
- [ ] `spec-driver validate` passed
- [ ] Spec path reported to user

## Success Criteria

The spec is ready when:

1. A human stakeholder can understand the feature/component without asking clarifying questions
2. A developer can use it to plan implementation
3. A QA engineer can use it to design test cases
4. All requirements are verifiable and traceable
5. The spec integrates cleanly into the spec-driver registry