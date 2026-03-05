---
id: DL-047
name: Spec corpus reconciliation
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: drift_ledger
delta_ref: DE-047
---

# DL-047 — Spec corpus reconciliation

Drift ledger for DE-047. Tracks contradictions, stale claims, missing
decisions, and ambiguous intent across the PROD spec corpus and governance
docs.

## Corpus coverage

| Document | Surveyed | Entries |
| --- | --- | --- |
| PROD-001 | yes | .006 |
| PROD-002 | yes | .001, .011 |
| PROD-003 | yes | .005, .015 |
| PROD-004 | yes | — clean |
| PROD-005 | yes | .003 |
| PROD-006 | yes | — clean |
| PROD-007 | yes | — clean |
| PROD-008 | yes | .009, .017 |
| PROD-009 | yes | .009, .017, .018 |
| PROD-010 | yes | — clean |
| PROD-011 | yes | .001, .020 |
| PROD-012 | yes | .002, .003, .004, .012, .013 |
| PROD-013 | yes | — clean |
| PROD-014 | yes | .004, .013 |
| PROD-015 | yes | .016 |
| PROD-016 | yes | .007, .010, .014 |
| ADR-001 | yes | — clean |
| ADR-002 | yes | .005, .015 |
| ADR-003 | yes | .003, .010, .016 |
| POL-001 | yes | — clean |
| POL-002 | yes | — clean |
| CLAUDE.md | yes | .003 |
| glossary.md | yes | .008, .019 |
| workflow.md | yes | .007, .008 |
| agents/glossary.md | yes | .008 |
| doctrine.md | yes | .008, .014 |
| INIT.md | yes | .019 |

## Entries

### DL-047.001: Phase-01 auto-creation — PROD-002 vs PROD-011

- status: triaged
- entry_type: contradiction
- severity: blocking
- topic: workflow
- owner: david
- sources:
  - kind: prod
    ref: PROD-002
    note: "FR-002: default behavior creates complete delta bundle including first phase"
  - kind: prod
    ref: PROD-011
    note: "FR-001: Phase-01 creation MUST NOT auto-create during delta creation"
- claims:
  - kind: assertion
    label: A
    text: "Default behavior creates plan + first phase alongside delta"
  - kind: assertion
    label: B
    text: "Phase-01 MUST NOT auto-create during delta creation — deferred so it benefits from IP intelligence"
- analysis: PROD-011 was written specifically to reverse PROD-002's phase-01 auto-creation. PROD-002 was never revised. An agent reading PROD-002 in isolation will implement the wrong behavior.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.002: Contract write location — PROD-012 internal inconsistency

- status: triaged
- entry_type: contradiction
- severity: significant
- topic: contracts
- owner: david
- sources:
  - kind: prod
    ref: PROD-012
    note: "FR-006 vs Flows 1/9"
- claims:
  - kind: assertion
    label: A
    text: "FR-006: canonical storage under .contracts/** ; SPEC-*/contracts/ is compatibility-only"
  - kind: assertion
    label: B
    text: "Flow 1 step 6: write contracts to specify/tech/SPEC-*/contracts/; Flow 9: canonical location in spec bundle"
- analysis: FR-006 was revised to make .contracts/ canonical, but the behavioral flows and examples still describe the pre-revision write path. Agents following flows will write to the wrong location.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.003: Contract canonical location — PROD-005 vs PROD-012/014/ADR-003/CLAUDE.md

- status: triaged
- entry_type: contradiction
- severity: significant
- topic: contracts
- owner: david
- sources:
  - kind: prod
    ref: PROD-005
    note: "Decision 3: keep contracts in spec dir (specify/tech/SPEC-XXX/contracts/)"
  - kind: prod
    ref: PROD-012
    note: "FR-006: canonical under .contracts/**"
  - kind: prod
    ref: PROD-014
    note: ".contracts/ mirror tree as canonical navigation"
  - kind: adr
    ref: ADR-003
    note: "observed contracts under .contracts/** are canonical"
  - kind: doc
    ref: CLAUDE.md
    note: ".contracts/** is canonical storage for generated contracts"
- claims:
  - kind: assertion
    label: A
    text: "Contracts belong in spec dir: specify/tech/SPEC-XXX/contracts/"
  - kind: assertion
    label: B
    text: ".contracts/** is canonical storage; spec-bundle paths are compatibility only"
- analysis: PROD-005 made a deliberate decision to keep contracts in spec bundles. Later specs (PROD-012, PROD-014) and ADR-003 reversed this. PROD-005 was never revised to acknowledge the change.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.004: Contract mirror tree — symlinks vs real files

- status: triaged
- entry_type: ambiguous_intent
- severity: significant
- topic: contracts
- owner: david
- sources:
  - kind: prod
    ref: PROD-012
    note: "FR-009: symlink trees under specify/tech/by-**/"
  - kind: prod
    ref: PROD-014
    note: "FR-002/FR-008: v1 symlinks → v2 real files under .contracts/"
- claims:
  - kind: question
    text: "Does PROD-014's .contracts/ mirror tree replace or augment PROD-012's by-language/by-package symlink trees?"
- analysis: Two separate navigation structures specified in two specs with no explicit relationship. Unclear whether PROD-014 supersedes PROD-012 symlink trees or they coexist.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.005: PROD-003 backlinks model vs ADR-002

- status: triaged
- entry_type: contradiction
- severity: significant
- topic: governance
- owner: david
- sources:
  - kind: adr
    ref: ADR-002
    note: "accepted: do NOT store backlinks in frontmatter"
  - kind: prod
    ref: PROD-003
    note: "data model includes backlinks: dict; sync updates backlinks"
- claims:
  - kind: assertion
    label: A
    text: "Backlinks must NOT be stored in frontmatter — computed at runtime from forward references"
  - kind: assertion
    label: B
    text: "PROD-003 data model, schema examples, and workflows describe stored/persisted backlinks on policy/standard entities"
- analysis: PROD-003 was likely authored before ADR-002 was accepted and never reconciled. Resolution is clear (ADR-002 wins), but PROD-003 needs revision to use computed backlinks via registry.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.006: PROD-001 RISK-006 — INIT.md exists now

- status: triaged
- entry_type: stale_claim
- severity: cosmetic
- topic: other
- owner: david
- sources:
  - kind: prod
    ref: PROD-001
    note: "RISK-006: INIT.md doesn't exist yet (BLOCKER)"
- claims:
  - kind: observation
    label: observed
    text: "supekku/INIT.md exists on disk and is referenced from CLAUDE.md"
- analysis: File was created but PROD-001 was never updated to mark the risk resolved. Agents reading PROD-001 might waste time trying to create it.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.007: Ceremony mode dual declaration — workflow.md vs workflow.toml

- status: triaged
- entry_type: ambiguous_intent
- severity: significant
- topic: governance
- owner: david
- sources:
  - kind: doc
    ref: .spec-driver/agents/workflow.md
    note: "declares ceremony mode inline: settler"
  - kind: prod
    ref: PROD-016
    note: "proposes .spec-driver/workflow.toml as single config source"
- claims:
  - kind: question
    text: "Which is authoritative for ceremony mode — workflow.md or workflow.toml? What happens when they diverge?"
- analysis: Both declare ceremony mode. No doc establishes precedence or whether workflow.md should be generated from workflow.toml.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.008: Default posture — doctrine "prefer cards" vs workflow "delta-first canonical"

- status: triaged
- entry_type: ambiguous_intent
- severity: significant
- topic: workflow
- owner: david
- sources:
  - kind: doc
    ref: .spec-driver/hooks/doctrine.md
    note: "Prefer cards for low-ceremony operational work"
  - kind: doc
    ref: .spec-driver/agents/workflow.md
    note: "Canonical default narrative is delta-first"
- claims:
  - kind: assertion
    label: A
    text: "Cards are the default; deltas are opt-in escalation for higher ceremony"
  - kind: assertion
    label: B
    text: "Delta-first is the canonical default narrative"
- analysis: When an agent receives a task with no explicit ceremony guidance, should it create a card or a delta? "settler" ceremony mode doesn't resolve this because no doc maps it to a default artifact type. Intent is probably that doctrine describes *when* and workflow describes *how*, but "canonical default" in workflow.md creates genuine ambiguity.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.009: Requirement lifecycle authority — specs vs evidence overlays

- status: triaged
- entry_type: contradiction
- severity: significant
- topic: lifecycle
- owner: david
- sources:
  - kind: prod
    ref: PROD-008
    note: "FR-001: specs MUST be the authoritative record of lifecycle state"
  - kind: prod
    ref: PROD-009
    note: "Timestamp-based precedence: newest wins; audits outrank deltas"
- claims:
  - kind: assertion
    label: A
    text: "Specs are the single authoritative record of requirement lifecycle state"
  - kind: assertion
    label: B
    text: "Effective status determined by newest timestamp; overlays from audits/deltas can override spec baseline"
- analysis: PROD-008 is a single-source model (spec is truth). PROD-009 is a merge model (latest evidence is truth). When an audit records a regression newer than the spec's coverage block, which wins? PROD-008 FR-002's "promote back to spec" requirement suggests eventual consistency, but the interim state is ambiguous.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.010: Spec auto-creation opt-in — marker file vs TOML config

- status: triaged
- entry_type: ambiguous_intent
- severity: cosmetic
- topic: contracts
- owner: david
- sources:
  - kind: adr
    ref: ADR-003
    note: "opt in via .spec-driver/enable_spec_autocreate"
  - kind: prod
    ref: PROD-016
    note: ".spec-driver/workflow.toml as single config source"
- claims:
  - kind: question
    text: "Should the spec auto-creation opt-in migrate from a marker file to workflow.toml, or do both coexist?"
- analysis: Minor configuration sprawl. The marker file pattern pre-dates PROD-016's centralized config vision. No doc addresses the transition.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.011: Missing revision on PROD-002 FR-002 after PROD-011 reversal

- status: triaged
- entry_type: missing_decision
- severity: blocking
- topic: workflow
- owner: david
- sources:
  - kind: prod
    ref: PROD-002
    note: "FR-002 still reads as active — default creates plan + first phase"
  - kind: prod
    ref: PROD-011
    note: "FR-001 specifically reverses phase-01 auto-creation"
- claims:
  - kind: gap
    text: "No revision (RE-xxx), supersedes annotation, or deprecation marker on PROD-002 FR-002 to signal partial supersession by PROD-011"
- analysis: PROD-011 was created to undo part of PROD-002's behavior but PROD-002 was never formally revised. An agent implementing PROD-002 has no signal that FR-002 is partially superseded.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.012: PROD-012 flows stale after FR-006 canonical storage revision

- status: triaged
- entry_type: missing_decision
- severity: significant
- topic: contracts
- owner: david
- sources:
  - kind: prod
    ref: PROD-012
    note: "FR-006 revised but Flows 1, 9 and narrative sections not updated"
- claims:
  - kind: gap
    text: "PROD-012 behavioral flows, examples, and appendices still describe the pre-revision contract write path"
- analysis: The requirement was updated but the spec's behavioral flows were not. A revision pass on PROD-012 is needed to align flows with revised FR-006.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.013: Missing decision — PROD-014 mirror tree vs PROD-012 symlink trees

- status: triaged
- entry_type: missing_decision
- severity: significant
- topic: contracts
- owner: david
- sources:
  - kind: prod
    ref: PROD-012
    note: "FR-009: by-language/by-package symlink trees"
  - kind: prod
    ref: PROD-014
    note: ".contracts/ mirror tree"
- claims:
  - kind: gap
    text: "Does PROD-014 replace PROD-012's symlink trees entirely? Do both coexist? Which navigational entry points survive?"
- analysis: Two contract navigation structures in two PRODs with no explicit relationship declaration. Implementation could produce redundant or conflicting navigation.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.014: Missing decision — doctrine.md/workflow.md relationship to workflow.toml

- status: triaged
- entry_type: missing_decision
- severity: significant
- topic: governance
- owner: david
- sources:
  - kind: doc
    ref: .spec-driver/hooks/doctrine.md
  - kind: doc
    ref: .spec-driver/agents/workflow.md
  - kind: prod
    ref: PROD-016
    note: "config-tailored guidance generated as markdown"
- claims:
  - kind: gap
    text: "No doc specifies whether doctrine.md and workflow.md become generated from workflow.toml, remain manually authored, or are deprecated"
- analysis: PROD-016 says "config-tailored guidance generated as markdown" suggesting these might become generated artifacts. No explicit transition statement.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.015: Missing decision — PROD-003 backlinks implementation given ADR-002

- status: triaged
- entry_type: missing_decision
- severity: significant
- topic: governance
- owner: david
- sources:
  - kind: prod
    ref: PROD-003
    note: "data model describes stored backlinks"
  - kind: adr
    ref: ADR-002
    note: "no stored backlinks"
- claims:
  - kind: gap
    text: "How should PROD-003's backlink features be implemented? Computed at display time? Cached in registry YAML? ADR-002 prohibits frontmatter storage but is silent on registry caching."
- analysis: Registry-computed backlinks (like the decision registry) are likely the answer, but no doc confirms this.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.016: c4_level "interaction" value — undefined

- status: triaged
- entry_type: ambiguous_intent
- severity: cosmetic
- topic: taxonomy
- owner: david
- sources:
  - kind: adr
    ref: ADR-003
    note: "lists c4_level: system|container|component|code|interaction"
  - kind: prod
    ref: PROD-015
    note: "references c4_level but doesn't define allowed values"
- claims:
  - kind: question
    text: "What is the 'interaction' c4_level? It doesn't correspond to any standard C4 model level. What kind of spec would use it?"
- analysis: ADR-003 introduces "interaction" without definition. No other doc references or constrains it. Likely intended for cross-system integration specs but needs explicit definition.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.017: Requirement lifecycle — specs vs requirements registry as source of truth

- status: triaged
- entry_type: ambiguous_intent
- severity: significant
- topic: lifecycle
- owner: david
- sources:
  - kind: prod
    ref: PROD-008
    note: "FR-001: specs are authoritative"
  - kind: prod
    ref: PROD-009
    note: "evidence overlays with timestamp precedence"
  - kind: doc
    ref: supekku/about/glossary.md
    note: "Requirements Registry: generated catalogue with lifecycle metadata"
- claims:
  - kind: question
    text: "Is the requirements registry a derived view of spec coverage blocks, or does it merge data from specs + deltas + audits? If it merges, it becomes a competing source of truth with specs."
- analysis: Related to .009 but distinct question. The glossary describes the registry as carrying lifecycle metadata, which could mean it's either a snapshot of spec data or a merge layer. The answer determines whether the registry is authoritative or derived.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.018: PROD-009 baseline statuses "asserted" and "legacy_verified" — undefined

- status: triaged
- entry_type: ambiguous_intent
- severity: cosmetic
- topic: lifecycle
- owner: david
- sources:
  - kind: prod
    ref: PROD-009
    note: "introduces asserted and legacy_verified as baseline statuses"
- claims:
  - kind: question
    text: "What do 'asserted' and 'legacy_verified' mean? When is each used? How do they differ from other lifecycle states like 'planned' or 'verified'?"
- analysis: Appear to be initial states for pre-existing requirements, but no definition in PROD-009 or glossary. "asserted" likely means "claimed without evidence"; "legacy_verified" likely means "considered verified before system existed." Should be explicit.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.019: Two glossaries with divergent contract definitions

- status: triaged
- entry_type: stale_claim
- severity: cosmetic
- topic: other
- owner: david
- sources:
  - kind: doc
    ref: supekku/about/glossary.md
    note: "Contract: auto-generated public/private API docs at .contracts/ and specify/tech/by-package/.../contracts/"
  - kind: doc
    ref: .spec-driver/agents/glossary.md
    note: "Contract: auto-generated API documentation. Location: .contracts/"
  - kind: doc
    ref: supekku/INIT.md
    note: "also references by-package symlink tree"
- claims:
  - kind: observation
    label: observed
    text: "supekku glossary and INIT.md still reference the old by-package symlink tree; agents glossary only mentions .contracts/"
- analysis: Two glossary sources with slightly different definitions. The supekku glossary's mention of by-package paths may be stale given PROD-014 evolution.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)

### DL-047.020: VCS abstraction scope — undefined

- status: triaged
- entry_type: missing_decision
- severity: cosmetic
- topic: workflow
- owner: david
- sources:
  - kind: prod
    ref: PROD-011
    note: "FR-008: VCS abstraction (git, jj, etc.)"
- claims:
  - kind: gap
    text: "No design doc or ADR addresses how deep VCS abstraction goes, what operations need it, or what the interface looks like"
- analysis: Supporting multiple VCS tools affects many subsystems (delta creation, SHA tracking, commit workflows). Mentioned as a single FR without design guidance.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
