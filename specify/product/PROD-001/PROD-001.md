---
id: PROD-001
slug: streamline-creation-and-refinement-of-product-and-tech-specs
name: Streamline creation and refinement of product and tech specs
created: '2025-11-01'
updated: '2025-11-01'
status: draft
kind: product
aliases: ["Create Specs"]
---

# PROD-001: Create and refine specs with zero friction

<!--
  Structured relationships block (edit YAML, regenerate any rendered table if applicable).
  `primary` should list requirements owned by this spec; `collaborators` references foreign requirements this spec contributes to.
  Extend `interactions` as needed (depends_on/collaborates_with/obsoletes/etc.).
-->
```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-XXX
requirements:
  primary:
    - SPEC-XXX.FR-001
  collaborators: []
interactions:
  - type: depends_on
    spec: SPEC-YYY
    summary: >-
      Brief rationale for dependency.
```

<!--
  Capabilities block records structured responsibilities and links to requirements.
  `id` should be stable (kebab-case). Keep prose below for richer explanation.
-->
```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-XXX
capabilities:
  - id: capability-example
    name: Example capability
    responsibilities:
      - <responsibility-id-from-frontmatter>
    requirements:
      - SPEC-XXX.FR-001
    summary: >-
      Short paragraph summarising the capability.
    success_criteria:
      - Measure executed successfully.
```
## 1. Intent & Summary
- **Problem Statement(s)**: It's too fucking hard to make a spec, considering this is spec-driven development.
- **Value Proposition**: These documents are central to the Spec-Driven workflow; there should be zero friction.
- **Guiding Principles**:
  - spec-driver should do or assist whatever it can
  - everything else should be assisted by excellent Claude commands
  - Codex, etc support to come later
  - Product specs should be given as much or more attention as Tech specs
  - Users should have freedom to refine the templates to their needs
  - Steal liberally from spec-kit; they have some great commands and ideas
  - Support a variety of workflows (spec-first, spec-last, etc)
- **Reference Materials**: 
- **Change History**: 

this is the thing I'm working on, and it's recursive because I'm also working on the
template / structure of tech & product specs. This one isn't right. AFAICT it's copied from 
supekku/templates/product-spec-template.md - it's out of date, and my attempts to get an agent to improve it and 
align it with conventions have been frustrating.

Nor in fact is the one that's used by the current 'create spec --kind tech' command. That creates a truncated file.

The closest thing to right, or what's been working so far, I realised, is the
supekku/templates/tech-spec-template.md which has been formerly used for creation
_in an informally specified agentic workflow_ -- i.e. me telling an agent to create
a spec based on this template. It contains some guidance around a code-fenced markdown block.

Now, I'm getting something of a headache thinking about the way forward but i think
it looks mostly like this:

  1. the primary means of creating a tech / product spec is to invoke an installed
  Claude command, eg `/spec-driver.create-tech-spec` or `/spec-driver.create-product-spec`
  2. this command will provide the necessary guidance, context, instruction, etc such
  that it does not need to muddy the .md template itself
  3. the command will specify how the agent is to invoke spec-driver and with what arguments. Note: this 
     might be tricksy given it can be installed with pip, uv, etc ... we possibly want to ensure something goes into the project CLAUDE.md file to ensure any changes to how it is invoked can be specified just once and understood everywhere.
  4. the spec-driver create command will use the SAME template for both kinds of spec; the differences are:
     - the path and directory structure
     - possibly slightly different frontmatter content (- kind: product|tech)
     - a tech spec will also create a sister file for testing
  5. the spec-driver create spec command will return the path to the generated artefact(s)
  6. the agent, still following the "slash command" .md, will perform an editing pass filling in details from the user's command 
     arguments (title), it's understanding from prior context, etc. Part of this might entail customising some fields 
     of the generated template according to whether it's a product or tech spec (eg: perhaps architecture section -> user stories)
  7. spec-driver has a command specifically for returning snippets of yaml/markdown for insertion into templates; eg. 
     YAML code blocks:
     ```yaml supekku:spec.capabilities@v1
     [...]
     ```
  8. the agent continues following its workflow, asking questions and making clarifications, until it is done. I'll steal liberally from the spec-kit prompts here, as they're doing some great work. (see ./spec-kit/templates/commands/specify.md and other files in that folder)
  9. the agent finishes by running a command to sync & validate the new spec in the spec-driver registry.

## 2. Personas & Scenarios
- Persona → primary goals
  - onboarding user 
     - obviousness / learnability of core concepts
     - ease of understanding the intended, permissable or appropriate workflows, next steps to take
     - tool / agent support in understanding 
     - obvious feedback on validation requirements
     - non-breakage of tools

  - experienced developer
     - focus on what's interesting or significant, not the trappings of spec-driven development 
     - minimise cognitive overhead 
     - consistency and speed
     - efficiently find & retrieve related entities & information
     - freedom to customise templates, workflows
     - efficient use and oversight of agents to assist completing docs

  - agent developer
     - learnability and context-efficient understanding of spec-driver core entities, relationships & workflows
     - discoverability 
     - ease of editing content and ensuring validity & completeness

- Core user journeys (Given/When/Then)
  - create a new product spec 
     1. to capture requirements & value drivers prior to creating a delta 
        - possibly from or referencing backlog item(s)
     2. referencing an already defined, possibly implemented delta, to give requirements and motivations a forever home
  - flesh out a tech spec auto-created 
     1. from existing code
     2. during audit of an implemented delta
  - create a new tech spec to represent an as-yet unimplemented component or subsystem
     - as part of the design process 
       - a delta may or may not yet exist
    
- Requirements: it needs to be super obvious and well documented how to: 
  - define them correctly (no template for them in this template!)
  - create them within / attached to a spec
  - move them between entities
  - work with the ambiguity resolution mechanism supported by agents
 
## 2. Stakeholders & Journeys
- **Personas / Actors** *(product)*: <Role – goals, pains, expectations.>
- **Systems / Integrations** *(tech)*: <External systems, contracts, constraints.>
- **Primary Journeys / Flows**: Given–When–Then narratives or sequence steps.
- **Edge Cases & Non-goals**: <Scenarios we deliberately exclude; failure/guard rails.>

## 3. Responsibilities & Requirements
- **Capability Overview**: Expand each capability in the YAML block (behaviour, FR/NF links).
- **Functional Requirements (FR)**: `SPEC-XXX.FR-001` / `PROD-XXX.FR-001` – statement – verification.
- **Non-Functional Requirements (NF)**: code – statement – measurement.
- **Success Metrics / Signals** *(product)* or **Operational Targets** *(tech)*: <Quantifiable indicators.>

## 4. Solution Outline
- **User Experience / Outcomes** *(product)*: <Desired behaviours, storyboards, acceptance notes.>
- **Architecture / Components** *(tech)*: tables or diagrams covering components, interfaces, data/state.
- **Data & Contracts**: Key entities, schemas, API/interface snippets relevant to both audiences.

## 5. Behaviour & Scenarios
- **Primary Flows**: Step lists linking actors/components/requirements.
- **Error Handling / Guards**: Edge-case branching, fallback behaviour, recovery expectations.
- **State Transitions** *(tech)*: Diagrams or tables if stateful.

## 6. Quality & Verification
- **Testing Strategy**: Mapping of requirements/capabilities to test levels; reference testing companion if present.
- **Research / Validation** *(product)*: UX research, experiments, hypothesis tracking.
- **Observability & Analysis**: Metrics, telemetry, analytics dashboards, alerting.
- **Security & Compliance**: Authn/z, data handling, privacy, regulatory notes.
- **Verification Coverage**: Keep `supekku:verification.coverage@v1` entries aligned with FR/NF ownership and evidence.
- **Acceptance Gates**: Launch criteria tying back to FR/NF/metrics.

## 7. Backlog Hooks & Dependencies
- **Related Specs / PROD**: How they collaborate or depend.
- **Risks & Mitigations**: Risk ID – description – likelihood/impact – mitigation.
- **Known Gaps / Debt**: Link backlog issues (`ISSUE-`, `PROB-`, `RISK-`) tracking outstanding work.
- **Open Decisions / Questions**: Outstanding clarifications for agents or stakeholders.

## Appendices (Optional)
- Glossary, detailed research, extended API examples, migration history, etc.