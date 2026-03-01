ok, so we're now using the canon convergence model with the entry point being @doc/policy/canon_quickstart.md and the `just cap` convenience for showing a CAP ledger entry with related context.
the thing i'm interested in now is ...
I'm the author of a spec-driven development framework we use only very lightly in this project, called spec-driver
I'm in the process of writing the accompanying skills for it to make it more generally useful.
It provides a set of composable primitives which are intended to support some fairly diverse workflows.
Given we've just invented a new bespoke workflow, I'm interested in mapping our new concepts / model to those spec-driver natively provides.
@spec-driver/supekku/about/glossary.md
here's how I understand the mapping at a high level:
- our 'reality canon' = a tech "assembly Spec": a specification describing multiple units, backed by auto-generated contracts
- our 'plan canon' = a Revision for that spec, with a bundle describing a changeset to be applied against the spec to bring about the desired functionality.
- CAP-xxx = requirements; these live in a spec (or backlog items like Improvements) and have lifecycles, validations, etc
- our kanban cards = spec-driver natively supports these, but also supports "deltas" which are slices of requirements / revisions / optimistically updated specs, which can have design docs, implementation plans, and verifications
- Audits = loosely, the research we undertook to fill out the canon documents fits this model
...
I want you to interrogate spec-driver, and our own model, to help me understand:
1. where spec-driver could or would have made things easier or better for us
2. any features of our system which don't have a clear analogue or equivalent in spec-driver
3. any improvements or amendments to either system to guide improvement (or to progress adoption of spec-driver in deck of dwarf)
---
Great prompt. Your mapping is mostly right, and the gap is now clear.
Most important observation from interrogating current state: spec-driver primitives are present, but adoption is near-zero in this repo right now (.spec-driver/registry/requirements.yaml and deltas.yaml are effectively empty), so you’re carrying workflow intent in bespoke docs/scripts instead of native registries.
1) Where spec-driver would have helped
- Requirement lifecycle + traceability: CAPs could already be first-class requirements with implemented_by / verified_by links instead of manually maintained parity semantics.
- Change packaging: your T285/T290+ decomposition maps well to DE/DR/IP; this would reduce card-as-protocol drift.
- Conflict lineage: spec revisions + audits provide a structured “why this changed” path vs ad hoc adjudication notes.
- Validation: workspace validator could catch relation breakage (missing owning change, stale references) beyond bespoke grep gates.
- Commandable UX: just cap is useful; native equivalent in spec-driver could be richer (status/history/relations) and less custom glue.
2) What your system has that spec-driver doesn’t cleanly model (yet)
- Dual-canon convergence as an explicit control plane (Plan Canon + Reality Canon + parity as router).
- Canonical v1 vs design horizon split per capability.
- Fail-loudly doctrine as a first-class policy surface (reserved fields/inert seam invariants).
- Token-efficient onboarding contract (canon_quickstart + CAP router) optimized for LLM behavior.
- Adjudication split model (Opus proposes, GPT adjudicates) with operational rules.
3) Improvements to drive convergence / adoption
- Spec-driver-side additions
  1. Add a first-class Capability concept (or convention) with ids like CAP-007.
  2. Add a parity view command: spec-driver show capability CAP-007 --with plan,reality,evidence.
  3. Add a status CLI (requirements set-status) to remove manual registry edits.
  4. Add “fail-loudly” requirement type/tag (reserved_must_fail, inert_must_reject).
  5. Add adjudication metadata support (proposed/accepted/rejected + adjudicator), so your event log becomes native.
- Deck-of-dwarf-side migration
  1. Bootstrap one assembly SPEC for this tranche and encode CAP-001..CAP-009 as requirements.
  2. Map existing cards (T290..T294, T287) to DE artifacts with implements relations.
  3. Convert parity ledger rows to requirement records (parity ledger can remain UX view initially).
  4. Keep just cap, but have it read spec-driver registry as source-of-truth, not bespoke markdown parsing.
If you want, next I can draft a concrete “T295b migration card” with exact file/command steps to move CAP-001..009 into spec-driver without breaking your existing canon workflow.
