---
id: PROD-015
slug: spec_taxonomy_and_navigation
name: spec taxonomy and navigation
created: '2026-02-21'
updated: '2026-02-21'
status: draft
kind: prod
aliases: []
relations: []
guiding_principles:
  - Default to non-breaking metadata before any filesystem migration.
  - Keep unit specs discoverable but not dominant in human workflows.
  - Treat contracts/code as observed truth; treat specs as intent and constraints.
  - Prefer warnings over hard validation failures during adoption.
assumptions:
  - Teams will create some cross-cutting specs before or alongside code.
  - Auto-generated unit specs are useful, but only when they do not drown out assembly specs.
---

# PROD-015 – spec taxonomy and navigation

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-015
requirements:
  primary:
    - PROD-015.FR-001
    - PROD-015.FR-002
    - PROD-015.FR-003
    - PROD-015.FR-004
    - PROD-015.FR-005
    - PROD-015.NF-001
    - PROD-015.NF-002
  collaborators:
    - PROD-001.FR-001
    - PROD-012.FR-005
    - PROD-014.FR-008
interactions:
  - with: ADR-003
    nature: Defines the UX and workflow consequences of the taxonomy decision.
  - with: PROD-012
    nature: Clarifies how contract sync interacts with unit-spec sprawl.
  - with: PROD-001
    nature: Extends spec creation/list UX to support taxonomy and navigation.
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-015
capabilities:
  - id: explicit-spec-taxonomy
    name: Explicit Spec Taxonomy
    responsibilities:
      - Establish a clear, explicit distinction between unit specs and assembly specs.
      - Ensure auto-generated specs are labeled consistently and predictably.
      - Support gradual adoption without breaking existing references.
    requirements:
      - PROD-015.FR-001
      - PROD-015.FR-002
      - PROD-015.FR-005
      - PROD-015.NF-002
    summary: >-
      Makes spec intent machine-readable so humans and agents can reliably tell
      whether a spec represents a 1:1 code-bound unit or a cross-cutting
      assembly/integration description.
    success_criteria:
      - Sync-created specs always declare `category` and `c4_level` defaults.
      - Teams can author assembly specs without being drowned out by unit specs.
  - id: navigable-views-and-filters
    name: Navigable Views & Filters
    responsibilities:
      - Provide ergonomic navigation by category and architectural level.
      - Support CLI filtering for humans and agents (rg/fzf-friendly).
      - Warn on missing or inconsistent classification without blocking.
    requirements:
      - PROD-015.FR-003
      - PROD-015.FR-004
      - PROD-015.FR-005
      - PROD-015.NF-001
    summary: >-
      Adds fast, low-friction ways to separate unit vs assembly specs in both
      the filesystem and CLI output, without requiring a breaking directory
      migration.
    success_criteria:
      - `list specs` can filter by `category` and `c4_level`.
      - Tech specs have stable symlink views by category and level.
      - Validation produces actionable warnings, not hard failures, during rollout.
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-015
entries:
  - artefact: VT-030-001
    kind: VT
    requirement: PROD-015.FR-001
    status: verified
    notes: "DE-030: Spec model exposes category/c4_level from frontmatter; roundtrip preserved."
  - artefact: VT-030-002
    kind: VT
    requirement: PROD-015.FR-002
    status: verified
    notes: "DE-030: Sync-created specs set category: unit, c4_level: code; create spec defaults to category: assembly."
  - artefact: VT-030-003
    kind: VT
    requirement: PROD-015.FR-003
    status: verified
    notes: "DE-030: list specs --category unit/assembly/all filter correctly; default hides unit specs."
  - artefact: VT-030-004
    kind: VT
    requirement: PROD-015.FR-004
    status: verified
    notes: "DE-030: by-category/{unit,assembly,unknown} and by-c4-level views built deterministically."
  - artefact: VT-030-005
    kind: VT
    requirement: PROD-015.FR-005
    status: verified
    notes: "DE-030: Validator warns on missing taxonomy (tech specs only); does not produce errors. 10 tests."
  - artefact: VT-030-006
    kind: VT
    requirement: PROD-015.NF-002
    status: verified
    notes: "DE-030: Existing spec IDs/paths/registries remain valid after index rebuild."
  - artefact: VA-001
    kind: VA
    requirement: PROD-015.NF-001
    status: verified
    notes: "DE-030: list specs --category all completes in ~0.2s; well under 2s target."
```

## 1. Intent & Summary
- **Problem / Purpose**: `sync` can generate many code-bound specs, but teams also need a small number of cross-cutting “assembly” specs (subsystems, integrations, functional slices). Without an explicit taxonomy and navigation support, assembly specs get drowned out, and humans/agents can’t reliably infer whether a spec expresses intended design vs observed code reality.
- **Value Signals**:
  - Assembly spec creation in legacy codebases feels tractable (no “unworkably messy” unit-stub sprawl).
  - Humans/agents can find “the spec I want” quickly (filters + views; minimal manual search).
  - Validation warns on ambiguity early instead of silently accepting incoherence.
- **Guiding Principles**: See frontmatter; emphasize non-breaking adoption and contracts-as-observed-truth.
- **Change History**:
  - 2026-02-21: Introduced to operationalize ADR-003 via taxonomy metadata + navigation tooling.

## 2. Stakeholders & Journeys
- **Personas / Actors**:
  - *Legacy adopter*: wants to write 5–20 subsystem specs without generating 500 confusing unit stubs.
  - *Agent*: needs to quickly locate the assembly spec that constrains a change, and distinguish it from unit stubs.
  - *Maintainer*: wants guardrails (warnings) when specs are unclassified or inconsistent.
- **Primary Journeys / Flows**:
  1. Given a maintainer writes a cross-cutting subsystem spec, when they mark `category: assembly`, then they can browse/list only assembly specs and ignore unit stubs.
  2. Given a repo opts into unit-spec auto-creation, when sync creates a unit spec, then it is clearly labeled `category: unit` / `c4_level: code` and appears under the unit view.
  3. Given a repo has mixed/unclassified specs, when validation runs, then it produces actionable warnings guiding classification without blocking workflow.
- **Edge Cases & Non-goals**:
  - This spec does not mandate a breaking filesystem/prefix migration (`UNIT-###`, `ASM-###`) in v1.
  - This spec does not yet define the “claims/ownership” schema for overlapping interface constraints (future delta).

## 3. Responsibilities & Requirements

### Capability Overview

Expand each capability from the `supekku:spec.capabilities@v1` YAML block above, describing concrete behaviors and linking to specific functional/non-functional requirements.

### Functional Requirements

<!--
  Requirements MUST be parseable by the registry using this format:
  - **FR-NNN**: Requirement statement

  Each requirement should be:
  - Testable and unambiguous
  - Technology-agnostic (product specs) or implementation-specific (tech specs)
  - Linked to verification artifacts in the YAML block above
-->

- **FR-001**: Tech specs MUST support explicit taxonomy via frontmatter fields: `category` and `c4_level`.
  *Verification*: VT-001 – Schema + registry roundtrip preserves the fields.

- **FR-002**: Sync-created unit specs MUST default to `category: unit` and `c4_level: code`.
  *Verification*: VT-001 – Sync stub creation produces consistent classification.

- **FR-003**: The CLI MUST support filtering spec listings by `category` and `c4_level`.
  *Notes*: Missing fields MUST be addressable via `--category unknown` / `--c4-level unknown`.
  *Verification*: VT-002 – Filter flags produce expected subsets.

- **FR-004**: The system MUST provide deterministic filesystem “views” for navigation by `category` and `c4_level` (e.g. `specify/tech/by-category/assembly/…`).
  *Notes*: Views MUST include an `unknown/` bucket for unclassified specs.
  *Verification*: VT-003 – Index build is deterministic and stable.

- **FR-005**: Validation MUST warn (not error) when a tech spec is missing taxonomy fields or uses inconsistent combinations (e.g. `category: unit` with non-`code` `c4_level`).
  *Notes*: Warnings apply to tech specs only (`SPEC-*` / `kind: spec`).
  *Verification*: VT-003 – Validation emits warnings with actionable remediation.
### Non-Functional Requirements

- **NF-001**: Taxonomy views and CLI filtering MUST remain fast enough for interactive use (target: <2s on typical repos).
  *Measurement*: VA-001 – Benchmark list/index operations.

- **NF-002**: Taxonomy adoption MUST be non-breaking: existing spec IDs, paths, and registries remain valid.
  *Measurement*: VT-003 – No registry resolution regressions during index build.
### Success Metrics / Signals

- **Adoption**: [Quantifiable usage metric]
  *Example*: 80% of target users complete onboarding within first week
- **Quality**: [Error rate or satisfaction metric]
  *Example*: <5% of user sessions encounter errors
- **Business Value**: [Measurable business outcome]
  *Example*: Reduce support tickets by 40% compared to previous solution

## 4. Solution Outline
- **User Experience / Outcomes**:
  - “Assembly spec first”: humans/agents can browse/list assembly specs without wading through unit stubs.
  - “Unit stubs are clearly labeled”: when unit stubs exist, they’re discoverable and consistently categorized.
  - “Unknown is actionable”: unclassified specs are discoverable as `unknown` and easy to clean up incrementally.
- **Data & Contracts**:
  - Taxonomy is expressed as spec frontmatter metadata (no new block schemas required in v1).

## 5. Behaviour & Scenarios
- **Primary Flows**: Step lists linking actors/components/requirements.
- **Error Handling / Guards**: Edge-case branching, fallback behaviour, recovery expectations.

## 6. Quality & Verification
- **Testing Strategy**: Mapping of requirements/capabilities to test levels; reference testing companion if present.
- **Research / Validation**: UX research, experiments, hypothesis tracking.
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
