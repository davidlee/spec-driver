---
id: DL-047
name: Spec corpus reconciliation
created: '2026-03-05'
updated: '2026-03-06'
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
| .spec-driver/about/README.md | yes | .021 |
| .spec-driver/about/glossary.md | yes | .021 |
| .spec-driver/about/backlog.md | yes | .021 |
| .spec-driver/about/processes.md | yes | .021 |
| .spec-driver/about/lifecycle.md | yes | — clean |

## Entries

### DL-047.001: Phase-01 auto-creation — PROD-002 vs PROD-011

- status: resolved
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
- assessment: confirmed
- resolution_path: RE
- affected_artifacts:
  - PROD-002
- analysis: PROD-011 was written specifically to reverse PROD-002's phase-01 auto-creation. PROD-002 was never revised. An agent reading PROD-002 in isolation will implement the wrong behavior.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: reaffirm runtime truth — create delta does not auto-create phases. Phase creation is explicit. This is operational guidance, not architecture — RE on PROD-002, not a new ADR.

### DL-047.002: Contract write location — PROD-012 internal inconsistency

- status: adjudicated
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
- assessment: confirmed
- resolution_path: RE
- affected_artifacts:
  - PROD-012
- analysis: FR-006 was revised to make .contracts/ canonical, but the behavioral flows and examples still describe the pre-revision write path. Agents following flows will write to the wrong location.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: PROD-012 flows need revision to match FR-006. Blocked on ADR for contract role/location (resolving .003). Note: DE-044 is pursuing configurable paths — ADR should establish role and derivation model firmly but leave default location configurable.

### DL-047.003: Contract canonical location — PROD-005 vs PROD-012/014/ADR-003/CLAUDE.md

- status: adjudicated
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
- assessment: confirmed
- resolution_path: ADR
- affected_artifacts:
  - PROD-005
  - PROD-012
  - PROD-014
  - ADR-003
  - CLAUDE.md
- analysis: PROD-005 made a deliberate decision to keep contracts in spec bundles. Later specs (PROD-012, PROD-014) and ADR-003 reversed this. PROD-005 was never revised to acknowledge the change.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: contracts are derived, deterministic, and canonical as a record of what code exposes — but not a competing source of intent. One ADR for "contract role and canonical location" then REs to align affected specs. ADR should establish role and derivation model firmly but leave default location configurable (DE-044 is pursuing configurable paths; possible future move of defaults into .spec-driver/).

### DL-047.004: Contract mirror tree — symlinks vs real files

- status: adjudicated
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
- assessment: confirmed
- resolution_path: ADR
- affected_artifacts:
  - PROD-012
  - PROD-014
- analysis: Two separate navigation structures specified in two specs with no explicit relationship. Unclear whether PROD-014 supersedes PROD-012 symlink trees or they coexist.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: resolve as part of the contracts ADR (.003). The ADR should cover role, derivation model, and navigation structure. Specific location/structure decisions should accommodate DE-044 configurability.

### DL-047.005: PROD-003 backlinks model vs ADR-002

- status: resolved
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
- assessment: confirmed
- resolution_path: RE
- affected_artifacts:
  - PROD-003
- analysis: PROD-003 was likely authored before ADR-002 was accepted and never reconciled. ADR-002 is correct and authoritative. PROD-003 needs revision to remove stored backlinks from data model and use computed backlinks via registry instead.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: ADR-002 wins. RE on PROD-003 to replace stored backlinks with registry-computed model.

### DL-047.006: INIT.md — stale risk + vestigial onboarding mechanism

- status: adjudicated
- entry_type: stale_claim
- severity: significant
- topic: workflow
- owner: david
- sources:
  - kind: prod
    ref: PROD-001
    note: "RISK-006: INIT.md doesn't exist yet (BLOCKER)"
  - kind: doc
    ref: AGENTS.md
    note: "live agent bootstrap no longer references INIT.md"
- claims:
  - kind: observation
    label: observed
    text: "INIT.md was a vestigial onboarding layer. The live boot path is now `.spec-driver/agents/boot.md` + `.spec-driver/AGENTS.md` + `.spec-driver/README.md`; INIT.md has been removed."
- assessment: confirmed
- resolution_path: DE
- affected_artifacts:
  - PROD-001
  - AGENTS.md
  - .spec-driver/README.md
- analysis: PROD-001's INIT-based onboarding risk was stale. The canonical onboarding path is now boot skill + generated agent guidance + memory/skill routing; INIT.md has been removed from the live bootstrap and deleted.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: INIT.md is vestigial dead code in the installer; should be removed in favour of boot skill + memories + minimal AGENTS.md. PROD-001 RISK-006 to be marked resolved.
  - 2026-03-06 implemented: removed `@supekku/INIT.md` from the live bootstrap path, deleted `supekku/INIT.md`, and updated PROD-001 to describe the current boot path.

### DL-047.007: Ceremony mode dual declaration — workflow.md vs workflow.toml

- status: dismissed
- entry_type: ambiguous_intent
- severity: cosmetic
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
- assessment: not_drift
- analysis: Not a conflict — workflow.md is generated from workflow.toml as part of the installer script. workflow.toml is authoritative; workflow.md is a derived view. Minor gap: no way to regenerate workflow.md from config after post-install changes to workflow.toml. Filed as backlog issue.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 dismissed: not drift. workflow.md is generated from workflow.toml by installer. Gap filed as ISSUE-040.

### DL-047.008: Default posture — doctrine "prefer cards" vs workflow "delta-first canonical"

- status: adjudicated
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
- assessment: confirmed
- resolution_path: RE
- affected_artifacts:
  - .spec-driver/hooks/doctrine.md
  - .spec-driver/agents/workflow.md
  - .spec-driver/agents/glossary.md
- analysis: |
    Not a true contradiction — it's configuration-dependent, ultimately resolved by the interview-based installer (PROD-016.FR-004) setting workflow options per project. Depending on ceremony level, kanban cards or deltas (or both) may be active.

    Key clarifications:
    1. Kanban is a simpler, looser mode — a gateway drug to spec-driven work. Not deprecated, but positioned as low-ceremony entry point.
    2. "Card" is intentionally overloaded in boot scripts to mean "whatever artifact tracks active work in this project" — could be kanban card, delta, revision, or audit. It's the identifying thing you search for and write up work on.
    3. The apparent conflict between doctrine and workflow dissolves once ceremony mode properly maps to default artifact types — which is installer/config territory, not a doc-level decision.

    Patch doctrine.md and workflow.md for clarity. glossary.md should clarify the polymorphic "card" concept. Full resolution depends on PROD-016 installer work.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-06 adjudicated: configuration-dependent, not a contradiction. Kanban = low-ceremony gateway; "card" = polymorphic work-tracking artifact. Patch docs for clarity; full resolution via PROD-016 installer.

### DL-047.009: Requirement lifecycle authority — specs vs evidence overlays

- status: adjudicated
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
- assessment: confirmed
- resolution_path: ADR
- affected_artifacts:
  - PROD-008
  - PROD-009
- analysis: PROD-008 is a single-source model (spec is truth). PROD-009 is a merge model (latest evidence is truth). Resolution: specs own normative truth (what should be); evidence overlays record observed truth (what is). Drift between the two is resolved explicitly via ADR/RE, not silently by timestamp precedence. One ADR to unify PROD-008/009 semantics, then REs to align both specs.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: specs own normative truth; evidence overlays own observed truth. Drift resolved explicitly (ADR/RE), not silently. One lifecycle ADR, then REs on PROD-008 and PROD-009.

### DL-047.010: Spec auto-creation opt-in — marker file vs TOML config

- status: adjudicated
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
- assessment: confirmed
- resolution_path: DE
- affected_artifacts:
  - ADR-003
  - PROD-016
- analysis: "workflow.toml should be canonical for this setting — migrate from marker file. Small delta to patch. Longer term, auto-creation may only make sense for Go (and possibly only given a specific package/glob), but that doesn't block resolving the config sprawl now."
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: workflow.toml canonical. Small delta to migrate marker file to TOML config. Future: auto-creation scope may narrow (Go-only, package/glob-scoped) but that's separate.

### DL-047.011: Missing revision on PROD-002 FR-002 after PROD-011 reversal

- status: resolved
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
- assessment: confirmed
- resolution_path: RE
- affected_artifacts:
  - PROD-002
- analysis: PROD-011 was created to undo part of PROD-002's behavior but PROD-002 was never formally revised. An agent implementing PROD-002 has no signal that FR-002 is partially superseded.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: same resolution as .001 — RE on PROD-002 to align FR-002 with current reality. Single RE covers both .001 and .011.

### DL-047.012: PROD-012 flows stale after FR-006 canonical storage revision

- status: adjudicated
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
- assessment: confirmed
- resolution_path: RE
- affected_artifacts:
  - PROD-012
- analysis: The requirement was updated but the spec's behavioral flows were not. A revision pass on PROD-012 is needed to align flows with revised FR-006.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: RE on PROD-012 to align flows with FR-006. Blocked on contracts ADR (.003) — flows should reflect the ADR's decisions, not just the current FR-006 text.

### DL-047.013: Missing decision — PROD-014 mirror tree vs PROD-012 symlink trees

- status: adjudicated
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
- assessment: confirmed
- resolution_path: ADR
- affected_artifacts:
  - PROD-012
  - PROD-014
- analysis: Two contract navigation structures in two PRODs with no explicit relationship declaration. Implementation could produce redundant or conflicting navigation.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: resolve as part of the contracts ADR (.003). Same ADR covers role, location, and navigation structure.

### DL-047.014: Missing decision — doctrine.md/workflow.md relationship to workflow.toml

- status: resolved
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
  - kind: doc
    ref: .spec-driver/hooks/README.md
    note: "doctrine.md is user-owned, seeded by installer, never overwritten"
- claims:
  - kind: gap
    text: "No doc specifies whether doctrine.md and workflow.md become generated from workflow.toml, remain manually authored, or are deprecated"
- assessment: confirmed
- resolution_path: RE
- affected_artifacts:
  - PROD-016
- analysis: "These are two distinct things: (1) doctrine.md is a user-owned hook file, seeded on install, never overwritten — for per-project customisation (see .spec-driver/hooks/README.md). It is NOT generated from workflow.toml. (2) workflow.md IS generated from workflow.toml by the installer — it describes spec-driver conventions activated by settings. The original entry conflated these. No missing decision — just missing clarity in PROD-016. RE should patch PROD-016 for precision. Also consider a memory on install/config semantics (what's generated, what's user-owned, what's overwritten)."
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: not a missing decision — missing clarity. doctrine.md is user-owned (hooks/); workflow.md is generated from workflow.toml. RE on PROD-016 to make this distinction explicit. Memory on install/config semantics recommended.

### DL-047.015: Missing decision — PROD-003 backlinks implementation given ADR-002

- status: resolved
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
- assessment: confirmed
- resolution_path: RE
- affected_artifacts:
  - PROD-003
- analysis: "Backlinks should be computed at runtime by scanning forward references — no stored backlinks in frontmatter or registry cache. This aligns with ADR-002 and the precedent set by DE-045 (memory graph navigation), which elected runtime scanning over registry caching until performance demands otherwise. PROD-003's data model, registry YAML examples, and capability descriptions should be revised to describe computed backlinks. The feature itself is low-priority — backlinks haven't been missed in practice."
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-06 adjudicated: runtime-computed backlinks, no cache. Consistent with ADR-002 and DE-045 precedent. RE on PROD-003 to revise data model and examples. Low priority — feature not yet needed in practice.

### DL-047.016: c4_level "interaction" value — undefined

- status: resolved
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
- assessment: confirmed
- resolution_path: RE
- affected_artifacts:
  - ADR-003
  - CLAUDE.md
- analysis: "Likely agent confabulation based on a desire to home UX/interaction design specs. C4 is the wrong model for this — C4 levels describe system decomposition, not interaction modalities. Remove 'interaction' from the c4_level enum in ADR-003 and CLAUDE.md. Backlog the idea of a proper home for UX/visual design/interactivity specifications as a separate concept (not a C4 level)."
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: remove "interaction" from c4_level enum (ADR-003, CLAUDE.md). Suspected confabulation — C4 is wrong home for UX specs. Backlog item for UX/interaction spec concept.

### DL-047.017: Requirement lifecycle — specs vs requirements registry as source of truth

- status: adjudicated
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
- assessment: confirmed
- resolution_path: ADR
- affected_artifacts:
  - PROD-008
  - PROD-009
  - supekku/about/glossary.md
- analysis: Resolved by the lifecycle ADR (.009). The registry is a derived view — it aggregates from specs (normative) and evidence overlays (observed) but is not itself authoritative. Specs own normative truth; the registry presents a computed snapshot. Glossary should be updated to clarify "derived" status.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: registry is derived, not authoritative. Same lifecycle ADR as .009 establishes this. Glossary update as part of RE pass.

### DL-047.018: PROD-009 baseline statuses "asserted" and "legacy_verified" — undefined

- status: adjudicated
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
- assessment: confirmed
- resolution_path: ADR
- affected_artifacts:
  - PROD-009
- analysis: These statuses support the normative/observed distinction. "asserted" = claimed without evidence (normative baseline for pre-existing requirements). "legacy_verified" = considered verified before the system existed (grandfathered observed truth). Definitions should be formalized in the lifecycle ADR and reflected in PROD-009 RE.
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: define in lifecycle ADR (.009). "asserted" = normative claim without evidence; "legacy_verified" = grandfathered observed truth. RE on PROD-009 to add definitions.

### DL-047.019: Two glossaries with divergent contract definitions

- status: adjudicated
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
- assessment: confirmed
- resolution_path: DE
- affected_artifacts:
  - supekku/about/glossary.md
  - .spec-driver/agents/glossary.md
  - supekku/INIT.md
- analysis: ".contracts/ is correct location. The two glossaries should be compared and consolidated into a single file — definitions are foundational and having divergent sources is a liability. This is a purposeful agent task, likely in a later phase of this delta or a follow-up. Stale by-package references in supekku glossary and INIT.md should be corrected as part of consolidation."
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-05 adjudicated: .contracts/ is correct. Consolidate two glossaries into one canonical file as a deliberate activity (later phase or follow-up). Fix stale by-package references during consolidation.

### DL-047.021: Core loop — no canonical authoritative description of workflow permutations

- status: adjudicated
- entry_type: missing_decision
- severity: blocking
- topic: workflow
- owner: david
- sources:
  - kind: doc
    ref: .spec-driver/agents/workflow.md
    note: "delta-first canonical narrative — single linear sequence"
  - kind: prod
    ref: PROD-002
    note: "delta creation assumes specs pre-exist"
  - kind: prod
    ref: PROD-008
    note: "specs are authoritative; deltas promote back to spec coverage"
  - kind: prod
    ref: PROD-009
    note: "evidence overlays on spec baseline"
  - kind: prod
    ref: PROD-011
    note: "delta → IP → phases → implement"
  - kind: prod
    ref: PROD-016
    note: "ceremony modes configure posture but don't define loop variants"
  - kind: doc
    ref: supekku/memories/mem.pattern.spec-driver.core-loop.md
    note: "describes pioneer/settler/town-planner variants"
- claims:
  - kind: gap
    text: |
      No single authoritative document defines the core spec-driver workflow loop
      and its permutations. The facts are distributed across 5+ sources with different
      emphases. Agents consistently produce varying descriptions depending on which
      subset they read first.

      Key permutations that need canonical definition:
      1. Delta-first (default settler): backlog → delta → DR/IP → implement → audit → revision (if needed) → spec reconcile → close
      2. Revision-first (town-planner concession): spec change drives delta scoping
      3. Eager spec edit: spec modified during implementation rather than post-audit
      4. Pioneer minimal: card → implement → done

      Unresolved questions:
      - When exactly does each variant apply? What triggers the choice?
      - Is "eager spec edit" a valid variant or an anti-pattern?
      - Where does spec creation itself fit? (PROD-001 is orthogonal to the loop)
      - How do audits, contracts, and requirements registries feed back?
      - What's optional vs mandatory at each ceremony level?
- assessment: confirmed
- resolution_path: ADR
- affected_artifacts:
  - .spec-driver/agents/workflow.md
  - supekku/memories/mem.pattern.spec-driver.core-loop.md
  - .spec-driver/about/README.md
  - .spec-driver/about/glossary.md
  - .spec-driver/about/backlog.md
  - .spec-driver/about/processes.md
  - PROD-002
  - PROD-008
  - PROD-011
  - PROD-016
- analysis: |
    This is arguably the most important gap in the corpus. The core loop is the
    foundational concept — if agents can't converge on a consistent description,
    everything downstream wobbles. Individual specs are consistent on their piece
    of the loop, but no document owns the full narrative with all permutations
    precisely defined. An ADR should canonically stake out the loop and its variants.
    May ultimately deserve its own PROD spec.

    Heresy audit of .spec-driver/about/ found active contamination:
    - README.md lines 71-78: describes a spec-first waterfall loop (Capture →
      Specify → Scope → ...) that contradicts delta-first doctrine. Worst offender.
    - README.md line 72: positions spec creation/update before delta scoping.
    - README.md line 72: implies revision is an alternative to delta for non-code
      changes, conflating their purposes.
    - glossary.md line 8: delta definition says "brings code back into alignment
      with specs" — spec-first bias; in delta-first flow, specs reconcile to code.
    - backlog.md: stale terms ("Constitution"), possibly stale commands and kinds.
    - processes.md line 3: references "Vice" — stale project name.
    - lifecycle.md: clean — verified against code, cites sources. Gold standard.
- evidence:
  - 2026-03-06 discovered during Phase 2 adjudication review — pattern of agent divergence on core loop emphasis observed across multiple sessions
  - 2026-03-06 adjudicated: ADR to canonically define core loop and permutations. Potentially a PROD spec later.

### DL-047.020: VCS abstraction scope — undefined

- status: resolved
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
- assessment: confirmed
- resolution_path: backlog
- affected_artifacts:
  - PROD-011
- analysis: "Real gap, but not felt yet — git is the practical reality. Catalogue as a backlog issue for future consideration if/when the need arises. No design work or ADR needed now."
- evidence:
  - 2026-03-05 discovered during PROD spec cross-reference survey (VA-047-001)
  - 2026-03-06 adjudicated: acknowledged gap. Backlog issue to track; no action until need is felt.
