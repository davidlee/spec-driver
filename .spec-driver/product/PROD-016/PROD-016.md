---
id: PROD-016
slug: agentic_sdlc_configurator
name: agentic sdlc configurator
created: '2026-02-23'
updated: '2026-03-04'
status: draft
kind: prod
aliases: []
relations: []
guiding_principles:
  - Prefer small, composable primitives over a single rigid workflow.
  - Support legacy repos first; scale up ceremony when justified.
  - Make “the right next step” obvious without hard constraints.
  - Keep agent onboarding token-cheap (prescription short; runsheets on demand).
  - Provider-neutral skills first; provider wrappers are thin adapters.
assumptions:
  - Teams adopt spec-driver gradually and unevenly; partial activation is normal.
  - An 80/20 set of knobs plus a small doctrine escape hatch covers most real projects.
---

# PROD-016 – agentic sdlc configurator

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-016
requirements:
  primary:
    - PROD-016.FR-001
    - PROD-016.FR-002
    - PROD-016.FR-003
    - PROD-016.FR-004
    - PROD-016.FR-005
    - PROD-016.FR-006
    - PROD-016.FR-007
    - PROD-016.FR-008
    - PROD-016.FR-009
    - PROD-016.FR-010
    - PROD-016.NF-001
    - PROD-016.NF-002
    - PROD-016.NF-003
  collaborators:
    - PROD-001
    - PROD-012
    - PROD-014
    - PROD-015
interactions:
  - with: PROD-015
    nature: Uses ceremony modes and the closure contract; installs only relevant skills/runsheets.
  - with: PROD-012
    nature: Configures contracts-first sync and spec auto-create posture knobs.
  - with: PROD-001
    nature: Extends creation ergonomics via interview-driven workflows and schema-aware generation.
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-016
capabilities:
  - id: workflow-switchboard
    name: Workflow Switchboard
    responsibilities:
      - Provide a single config file readable by both spec-driver and agents.
      - Capture minimal knobs that shape workflow defaults (80/20).
      - Provide a doctrine escape hatch for bespoke instructions.
    requirements:
      - PROD-016.FR-001
      - PROD-016.FR-002
      - PROD-016.FR-003
    summary: >-
      Establishes a stable “workflow contract” for a repo so agents and CLI
      commands can choose defaults correctly without reading long docs or
      reverse-engineering conventions.
    success_criteria:
      - A repo’s intended ceremony and activated primitives are explicit and machine-readable.
      - Most customization is done by editing config/doctrine, not forking skills.
  - id: configurator-installer
    name: Configurator Interview + Installer
    responsibilities:
      - Interview the user to recommend an appropriate configuration for their repo.
      - Install only the correct skills and modular guidance for that configuration.
      - Be safe to re-run (idempotent) and friendly to local overrides.
    requirements:
      - PROD-016.FR-004
      - PROD-016.FR-005
      - PROD-016.NF-001
      - PROD-016.NF-002
    summary: >-
      Provides an interactive, token-cheap entrypoint (`spec-driver configure`)
      that turns “we want better SDLC” into concrete repo artifacts: config,
      curated skills/runsheets, and a minimal bootstrap.
    success_criteria:
      - A new user can get a working kit in under 2 minutes.
      - Re-running produces minimal diffs and never deletes user-authored overrides.
  - id: bootstrap-and-skills-kit
    name: Bootstrap + Skills Kit
    responsibilities:
      - Generate a tiny prescriptive bootstrap that references modular runsheets.
      - Keep procedural steps in skills; keep docs as routing/FAQ/concepts.
      - Support project-specific overrides and hooks.
    requirements:
      - PROD-016.FR-006
      - PROD-016.FR-007
      - PROD-016.FR-008
      - PROD-016.NF-003
    summary: >-
      Ensures an agent can start work from a short bootstrap (~30 lines) and
      load detailed runsheets only on demand.
    success_criteria:
      - Bootstrap stays short and prescriptive, not encyclopedic.
      - Skills cover most “jobs to be done”; remaining docs focus on routing and FAQ.
  - id: workflow-command-surface
    name: Workflow Command Surface
    responsibilities:
      - Ensure core workflow commands are automation-safe in non-interactive contexts.
      - Provide first-class create/complete command coverage for active change primitives.
      - Keep command behavior aligned with lifecycle semantics and generated guidance.
    requirements:
      - PROD-016.FR-009
      - PROD-016.FR-010
      - PROD-016.NF-001
    summary: >-
      Reduces agent/operator friction by making lifecycle commands predictable in
      CI/headless environments and ensuring core primitives are represented by
      first-class command flows.
    success_criteria:
      - No prompt-deadlocks in non-interactive command execution.
      - Revision and audit workflows do not require ad-hoc file scaffolding.
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-016
entries:
  - artefact: VT-016-001
    kind: VT
    requirement: PROD-016.FR-001
    status: verified
    notes: "Verified by DE-031 VT-031-003: installer copies claude.settings.json + hooks with chmod +x. workflow.toml creation verified by test_initialize_creates_workflow_toml_with_detected_exec."
  - artefact: VT-016-002
    kind: VT
    requirement: PROD-016.FR-004
    status: planned
    notes: "spec-driver configure interview produces a correct recommended config for each ceremony mode."
  - artefact: VT-016-003
    kind: VT
    requirement: PROD-016.FR-005
    status: planned
    notes: "Installer installs only the relevant skills/guidance and is safe to re-run (idempotent)."
  - artefact: VT-016-004
    kind: VT
    requirement: PROD-016.FR-006
    status: verified
    notes: "Verified by DE-031 VT-031-001: installer renders all four agent modules (exec/workflow/glossary/policy) from templates with config substitutions."
  - artefact: VT-016-005
    kind: VT
    requirement: PROD-016.FR-008
    status: verified
    notes: "Verified by DE-031 VT-031-002: disabled primitives omitted from glossary/policy; paths reflect workflow.toml config."
  - artefact: VT-016-006
    kind: VT
    requirement: PROD-016.FR-009
    status: verified
    notes: "Verified by DE-039 VT-039-002 (non-interactive completion behavior + coverage messaging tests)."
  - artefact: VT-016-007
    kind: VT
    requirement: PROD-016.FR-010
    status: verified
    notes: "Verified by DE-039 VT-039-003 (create-audit + complete-revision command flow tests)."
  - artefact: VT-039-001
    kind: VT
    requirement: PROD-016.FR-002
    status: verified
    notes: "strict_mode config and enforcement paths verified in DE-039 phase 3."
  - artefact: VA-016-001
    kind: VA
    requirement: PROD-016.NF-003
    status: planned
    notes: "Agent study: bootstrap + on-demand runsheets work within context limits and reduce time-to-first-delta."
```

## 1. Intent & Summary
- **Problem / Purpose**: Spec-driver is evolving into an agentic SDLC construction kit, but today users and agents must stitch together documentation, commands, and conventions manually. We need a single interactive entrypoint that selects the right ceremony mode and workflow posture for a repo, installs only the relevant skills/guidance, and generates a tiny project bootstrap that routes agents to on-demand runsheets.
- **Value Signals**:
  - Works for a repo’s first commit or 10,000th without “process bankruptcy”.
  - Legacy-friendly defaults (contracts-first; low unit-spec sprawl) are easy to adopt.
  - Agents can start work with a ~30-line bootstrap and pull in details only as needed.
  - “Jobs to be done” are handled by skills/runsheets; docs are routing/FAQ/concepts.
- **Guiding Principles**: See frontmatter; especially “token-cheap onboarding” and “provider-neutral skills”.
- **Change History**:
  - 2026-02-23: Introduced workflow switchboard + configurator + installer + bootstrap as a first-class product capability.
  - 2026-03-04: Clarified command-surface requirements for non-interactive completion behavior and first-class revision/audit lifecycle commands.

## 2. Stakeholders & Journeys
- **Personas / Actors**:
  - *Legacy adopter*: wants to start with minimal ceremony and scale up when justified.
  - *Maintainer*: wants a coherent, tunable default workflow without forking spec-driver.
  - *Agent*: wants minimal context plus precise runsheets, not a pile of long overview docs.
- **Primary Journeys / Flows**:
  1. Given a legacy repo, when a user runs `spec-driver configure`, then the repo is configured for a legacy-friendly default (Settler) with contracts-first posture and the correct skills installed.
  2. Given a project evolves, when the user switches ceremony mode or posture knobs, then the installed skills/guidance update accordingly, without breaking existing artifacts.
  3. Given an agent begins work, when it reads the bootstrap, then it can choose the correct runsheet/skill without reading the entire “full system” overview.
- **Edge Cases & Non-goals**:
  - We do not enforce a One True Way; the kit supplies defaults and guardrails.
  - We do not store user interview answers long-term (v1); they guide recommendations only.

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

- **FR-001**: The repository MUST have a single workflow configuration file (TOML) readable by both spec-driver and agents (e.g. `.spec-driver/workflow.toml`).
  *Verification*: VT-016-001.

- **FR-002**: The configuration MUST cover the majority of workflow shaping needs with a minimal set of knobs (80/20), including:
  - ceremony mode (`pioneer|settler|town_planner`)
  - activated primitives (policy/backlog/spec/delta/ip/audit)
  - posture knobs that influence “suggest vs ask vs assume” and evidence expectations
  - strict workflow lock-in control (for canonical sequencing enforcement)
  *Verification*: VT-016-001.

- **FR-003**: The system MUST provide an escape hatch for bespoke project instructions as a small plain-text doctrine note that is loaded at the right time (instead of exploding the config keyspace).
  *Verification*: VT-016-001.

- **FR-004**: The system MUST provide a configurator command/skill that interviews the user and recommends a configuration appropriate for their repo (legacy-biased defaults).
  *Verification*: VT-016-002.

- **FR-005**: The configurator MUST write/update config and install skills/guidance deterministically and idempotently:
  - installs only relevant modules for the selected configuration
  - removes/disables irrelevant modules when configuration changes
  - preserves user overrides/hooks
  *Verification*: VT-016-003.

- **FR-006**: The system MUST generate a short prescriptive project agent bootstrap (~30 lines) that `@references` modular runsheets and is appropriate to the selected configuration.
  *Verification*: VT-016-004.

- **FR-007**: The system MUST provide customization hooks for projects to add local skills/guidance and policy without forking canonical content.
  *Verification*: VT-016-004.

- **FR-008**: The system MUST generate project-local, config-tailored guidance markdown (installed/overwritten by the installer) for skills to reference, to:
  - insert correct project paths/conventions via templating
  - hide disabled primitives to conserve agent tokens
  - avoid making skills dynamically parse config at runtime
  *Notes*: `.spec-driver/agents/` is the canonical home for generated agent-facing markdown referenced by skills.
  *Verification*: VT-016-005.

- **FR-009**: Workflow completion commands MUST be automation-safe in non-interactive contexts:
  - no mandatory stdin prompt choreography in headless execution
  - deterministic defaults for optional prompts
  - explicit flags for override/bypass behavior
  *Verification*: VT-016-006.

- **FR-010**: The CLI MUST provide first-class create/complete command coverage for active change primitives (`delta`, `revision`, `audit`) with lifecycle-consistent semantics.
  *Verification*: VT-016-007.
### Non-Functional Requirements

- **NF-001**: The configurator and installer MUST be safe to re-run and produce minimal diffs (idempotent, deterministic).
  *Measurement*: VT-016-003.

- **NF-002**: Skills/guidance MUST be provider-neutral at the core, with provider-specific wrappers as thin adapters.
  *Measurement*: VT-016-003.

- **NF-003**: The default bootstrap MUST be token-cheap and route an agent to the right runsheet/skill without loading long overview docs.
  *Measurement*: VA-016-001.
### Success Metrics / Signals

- **Adoption**: [Quantifiable usage metric]
  *Example*: 80% of target users complete onboarding within first week
- **Quality**: [Error rate or satisfaction metric]
  *Example*: <5% of user sessions encounter errors
- **Business Value**: [Measurable business outcome]
  *Example*: Reduce support tickets by 40% compared to previous solution

## 4. Solution Outline
- **User Experience / Outcomes**:
  - One command (`spec-driver configure`) converts intent into an executable kit.
  - Switching ceremony mode adjusts what gets installed and what agents are encouraged to do, without hard enforcement.
  - Procedural guidance lives in skills/runsheets; docs focus on routing and FAQ.
- **Data & Contracts** (v1 shape, indicative):
  - `.spec-driver/workflow.toml`: ceremony + toggles + posture knobs (minimal).
  - `.spec-driver/doctrine.md`: a few sentences of bespoke project instruction (escape hatch).
  - A modular guidance root (`docs/guidance/`) with small runsheets installed per configuration.
  - A canonical skills root (e.g. `openskills/`) with provider wrappers (Claude/Codex/etc.) as thin adapters.

## 5. Configuration Contract (v1)

The configurator MUST be able to support real projects with a minimal config surface area. The config exists to help
skills and tooling make correct default choices and route work without hardcoding project-specific paths.

### 5.1 Minimal switchboard (example shape)

This is an indicative (not final) sketch of the smallest useful `.spec-driver/workflow.toml`:

```toml
ceremony = "pioneer" # pioneer | settler | town_planner

[cards]
enabled = true
root = "kanban"
lanes = ["backlog", "next", "doing", "finishing", "done"]
id_prefix = "T" # produces T123-* ids

[docs]
artefacts_root = "doc/artefacts" # design docs / artefacts, keyed by T123-*
plans_root = "doc/plans"         # implementation plans, keyed by T123-*

[policy]
adrs = true
policies = false
standards = false

[contracts]
enabled = true
root = ".contracts"

[bootstrap]
doctrine_path = ".spec-driver/doctrine.md"

[authoring]
engine = "superpowers" # superpowers | spec_driver
```

Design intent:
- Keep this stable and boring. It is a switchboard, not a process encyclopedia.
- Everything not covered by 80/20 knobs should be handled by doctrine/hooks, not by key explosion.

### 5.2 File ownership semantics

The installer manages two categories of files with different ownership rules:

| Category | Location | On install | On re-install | Editable by user |
| --- | --- | --- | --- | --- |
| **Generated** | `.spec-driver/agents/*.md` | Created from `workflow.toml` | Overwritten | No (will be lost) |
| **User-owned** | `.spec-driver/hooks/doctrine.md` | Seeded with defaults | Never overwritten | Yes (primary purpose) |

- **Generated guidance** (FR-008): config-tailored markdown that skills reference.
  These files are deterministic projections of `workflow.toml` settings. Users
  should not edit them — changes are made in `workflow.toml` and regenerated.
- **Doctrine hooks** (FR-007): user-authored bespoke instructions loaded at
  specific hook points. Seeded once with sensible defaults; the user owns the
  file thereafter. The installer MUST NOT overwrite user edits.

### 5.3 Doctrine hook points (escape hatch)

`doctrine.md` should be loaded at the right times to cover bespoke conventions without forking skills.

Canonical hook points (v1):
- `bootstrap/start`: always
- `work/preflight`: before suggesting next steps (implement vs design vs plan vs policy update)
- `cards/new`: before filling a new card template
- `work/brainstorm`: before generating a design artefact (engine-specific)
- `work/plan`: before generating a plan (engine-specific)
- `work/notes`: before writing progress notes and follow-ups
- `work/handover`: before writing a “start here” and handover prompt

### 5.4 Superpowers integration posture

The v1 kit SHOULD treat superpowers/obra-style interview+progressive writing as a first-class authoring engine:
- If `authoring.engine = "superpowers"`, spec-driver skills should route into it and enforce project conventions
  (paths, naming, required “start here” sections) rather than trying to replace it.
- If `authoring.engine = "spec_driver"`, the kit may use its own interview loops (future capability).

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
