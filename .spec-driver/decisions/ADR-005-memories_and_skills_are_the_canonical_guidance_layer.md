---
id: ADR-005
title: "ADR-005: Memories and skills are the canonical guidance layer"
status: accepted
created: "2026-03-06"
updated: "2026-03-06"
reviewed: "2026-03-06"
owners:
  - david
supersedes: []
superseded_by: []
policies: []
specs:
  - PROD-016
requirements: []
deltas:
  - DE-047
revisions: []
audits: []
related_decisions:
  - ADR-004
related_policies: []
tags:
  - documentation
  - memories
  - skills
  - doctrine
summary: "Declare agent memories as the canonical conceptual guidance for spec-driver and skills as the canonical procedural guidance layer; reduce other documentation to minimal routing, reference, or derived views."
---

# ADR-005: Memories and skills are the canonical guidance layer

## Context

Spec-driver now has several overlapping guidance surfaces:

- agent memories
- skills
- generated agent-facing markdown under `.spec-driver/agents/`
- explanatory docs under `.spec-driver/about/`
- top-level and auxiliary READMEs
- project docs under `docs/`
- website/docs surfaces such as `wub`
- product specs and ADRs that sometimes drift into operational explanation

Before memories and skills existed, this duplication was already a drift risk.
After introducing memories and skills, it became actively harmful:

- the same concept is explained in multiple places
- agent and user guidance can diverge silently
- stale prose competes with fresher operational guidance
- installed docs and non-installed docs overlap without a clear hierarchy
- agents spend tokens reading low-authority duplicate material

Spec-driver needs a documentation hierarchy.

The goal is not to remove all prose. The goal is to make authority legible:

- one canonical layer for conceptual understanding
- one canonical layer for procedural execution
- minimal routing material elsewhere
- fewer duplicate explanations

This ADR is paired with `ADR-004`.
`ADR-004` defines the canonical workflow doctrine.
This ADR defines where that doctrine and related user understanding should live.

## Decision

### 1. Memories are the canonical conceptual guidance for spec-driver

Spec-driver agent memories are the canonical source of truth for understanding
how spec-driver works in practice.

Memories own:

- core concepts
- workflow doctrine
- posture and ceremony guidance
- command-level operating patterns
- concise signposting to source-of-truth specs and ADRs

When a human or agent asks “how does spec-driver work?”, the answer path is:
consult memories first.

### 2. Skills are the canonical procedural guidance layer

Skills are the canonical procedural layer for performing work.

Skills own:

- runsheets
- operational checklists
- sequencing guidance
- task-specific guardrails
- when to load further detail on demand

When a human or agent asks “how do I do this task?”, the answer path is:
use the relevant skill, with memories providing conceptual support where needed.

### 3. Other prose must be minimal, referential, or derived

Documentation outside memories and skills MUST NOT act as a competing handbook
for how spec-driver works.

Outside the canonical layers, docs should be one of:

- **minimal routing**: point readers to the right memory, skill, spec, or ADR
- **reference material**: schemas, file maps, installation notes, generated lists
- **derived views**: generated projections tailored to local configuration
- **governance documents**: ADRs, specs, policies, standards

If a prose document substantially explains an operational concept already owned
by memories or skills, it should be reduced, derived, or removed.

### 4. `.spec-driver/README.md` should be short and practical

`.spec-driver/README.md` SHOULD provide only enough overview to avoid immediate
frustration, then route users and agents to the canonical layers.

It should typically include:

- a very short overview of what `.spec-driver/` contains
- an explanation that memories are the primary guidance layer
- an explanation that skills are the primary procedural layer
- a note that boot loads the initial routing guidance
- a concise description of the installed file structure
- a generated or maintained list of available spec-driver memories
- pointers for asking an agent to explain spec-driver by consulting memories

It should not become a second handbook.

### 5. Generated agent-facing markdown is projection, not canon

Files under `.spec-driver/agents/` are generated, configuration-local guidance.
They exist to project the right instructions into a particular repo context.

They are important, but they do not own doctrine. Their role is projection and
adaptation, not canonical explanation of spec-driver itself.

### 6. Specs and ADRs remain governance sources, not the onboarding layer

ADRs, specs, policies, and standards remain authoritative for governance,
product intent, architecture, and lifecycle contracts.

They are not the primary onboarding or explanatory layer for everyday user
understanding of spec-driver.

Memories and skills should summarize and route to them, not duplicate them.

### 7. Duplicate guidance is a defect

When multiple docs explain the same behaviour or concept without a clearly
defined canonical owner, that is a documentation defect.

The default fix is:

- keep or create the canonical memory and/or skill
- reduce other prose to routing or reference
- delete stale or redundant documentation where practical

### 8. Canonical conflict rule

If memories/skills and prose docs disagree about operational understanding:

- memories and skills win for guidance
- ADRs/specs win for formal governance and product/architecture decisions
- duplicate prose should be reconciled or deleted rather than treated as a peer

The goal is not arbitration forever. The goal is convergence toward fewer, clearer layers.

### 9. Documentation reduction is an intended outcome

This ADR intentionally points toward reducing and consolidating:

- `.spec-driver/about/`
- legacy onboarding docs such as `INIT.md`
- duplicate glossaries
- dubious project documentation under `docs/`
- overlapping public docs such as `wub` and the main `README`

Not all of that must happen immediately. This ADR makes the direction explicit.

## Consequences

### Positive

- Establishes a clear guidance hierarchy.
- Reduces drift pressure by removing duplicate handbook surfaces.
- Makes agent operation cheaper by reducing low-authority reading.
- Gives DE-047 and follow-on cleanup work a clear standard for deletion,
  consolidation, and signposting.
- Keeps README-style docs short without making them useless.

### Negative

- Memories and skills now carry more responsibility and must be maintained carefully.
- Some users may expect richer prose docs and find the lighter documentation style unfamiliar.
- Cleanup will require deleting or shrinking documentation that may feel useful locally.

### Neutral

- This ADR does not eliminate governance docs, specs, or ADRs.
- This ADR does not require every supporting file to disappear; it requires those
  files to stop competing for doctrinal ownership.
- Some generated/reference docs will still exist where they add value without duplicating canon.

## Verification

- `.spec-driver/README.md` becomes a short router rather than a handbook.
- Memory records cover the main spec-driver concepts and workflow questions.
- Skills, not prose handbooks, carry the procedural guidance for common work.
- Duplicate explanatory docs in `.spec-driver/about/` are reduced, derived, or removed.
- Future reviews of `docs/`, `wub`, and the top-level `README` use this ADR as the authority source.

## References

- `specify/decisions/ADR-004-canonical_workflow_loop.md`
- `specify/product/PROD-016/PROD-016.md`
- `.spec-driver/AGENTS.md`
- `.spec-driver/agents/`
- `.spec-driver/about/`
- `supekku/memories/`
- `drift/DL-047-spec-corpus-reconciliation.md`
