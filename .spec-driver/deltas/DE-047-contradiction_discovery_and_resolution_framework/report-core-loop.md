       ---
       Analysis: PROD Specs on Workflow Ordering and Canon Loop

       I've read all six PROD specs you requested, plus governance docs (CLAUDE.md,
       workflow.md, doctrine.md) and the core-loop memory. Here's what the corpus
       reveals about workflow ordering, consistency, and doctrine:

       1. Canonical Narrative (The Core Loop)

       From .spec-driver/agents/workflow.md (line 7-8):
       "Canonical default narrative is delta-first:
       delta -> DR -> IP -> phase sheet(s) -> implement -> audit -> revision -> patch
       specs -> close"

       From mem.pattern.spec-driver.core-loop.md (lines 14-16, 47-69):
       "The canonical spec-driver loop is delta-first: capture → delta
       scope/design/plan → implement → audit/contracts → revision/spec reconciliation
       → closure. Revision-first is a town-planner concession path."

       The full cycle defined (lines 47-68):
       capture → scope with delta → (optional DR/IP/phases) → implement →
       audit/contracts → revision from findings → spec reconcile → close

       With artifacts:
       1. Capture (backlog)
       2. Scope (delta)
       3. Design (DR - design revision)
       4. Plan (IP - implementation plan)
       5. Implement (code + tests)
       6. Audit/contracts (observe truth)
       7. Revision from findings (requirement/spec changes discovered)
       8. Spec reconcile (patch specs/coverage)
       9. Close (complete delta)

       Key doctrine point (workflow.md, line 7): "Canonical default narrative is
       delta-first" — this is the prevailing emphasis.

       ---
       2. PROD-001 (Spec Creation) – Specs Come Early But Not First

       § 1 Intent: Specs are foundational for spec-driven development, but the spec is
        created after backlog capture and before implementation (lines 128-145).

       § 4 Solution (lines 327-392): Shows spec creation as a complete workflow:
       - Invocation: /supekku.specify <feature description>
       - Agent fills all sections, YAML blocks, requirements
       - Validation + sync before completion

       Spec's position: PROD-001 does NOT describe when specs are created relative to
       deltas. It emphasizes that specs are foundational but doesn't claim they come
       before deltas.

       ---
       3. PROD-002 (Delta Creation) – Deltas Reference Existing Specs

       § 1 Intent (line 159): "Creating deltas to track codebase changes is
       prohibitively difficult... Users face steep learning curve understanding
       delta/plan/phase structure..."

       § 2 Journeys (lines 218-244):
       - Journey 1 shows delta creation after specs exist: "Agent found SPEC-042
       (authentication). Is this change related to it?" — delta discovers and links to
        existing specs
       - Journey 2 shows agent proactively creating delta during implementation,
       inferring relationships from code context

       Key phrase (FR-003, lines 292-294):
       "Users can specify specs (--spec SPEC-XXX) and requirements they know the
       change affects, and workflow accepts and validates these inputs."

       Spec's position: PROD-002 assumes specs already exist. Deltas link to specs;
       they don't create them.

       ---
       4. PROD-008 (Requirements Lifecycle Coherence) – Specs Are Authoritative

       § 3 FR-001 (lines 109-110):
       "The specs frontmatter and coverage block MUST be the authoritative record of
       each requirement's lifecycle state and supporting evidence."

       § 3 FR-002 (lines 111-112):
       "Every delta that changes requirement behaviour MUST provide an implementation
       plan documenting planned VT/VA/VH artefacts and promote the final state back
       into the owning spec coverage block before completion."

       Flow described (§ 5 lines 135-138):
       - Introduce: Author adds requirement to spec frontmatter + coverage (status:
       planned) → Registry marks "introduced".
       - Implement: Delta plan sets coverage entry to in-progress → On completion,
       spec block becomes verified
       - Audit: Audit coverage entry reports failed → Validation warning raised
       - Resolution: New delta brings behaviour back → status returns to verified

       Spec's position: Specs are the long-lived authoritative record. Deltas modify
       code and update spec coverage afterward.

       ---
       5. PROD-009 (Requirement Lifecycle Semantics) – Evidence Overlays Baseline

       § 1 Intent (lines 94-96):
       "Teams need to declare current reality for legacy systems without receipts
       while still trusting future overlays from deltas and audits."

       § 4 Solution (line 142):
       "Spec editors declare baseline state; delta completion and audit ingestion
       update overlays; UI/CLI displays "verified (audit AUD-021 · 2025-11-01)" vs
       "asserted (spec PROD-009 · 2025-11-03)" so humans understand context."

       Status model (line 143):
       - Baseline statuses from spec
       - Delta statuses (in-progress, implemented, verified)
       - Audit statuses (verified, failed, blocked)
       - Effective status = newest timestamp; if timestamps match, audits outrank
       deltas

       Spec's position: Specs declare baseline state; deltas and audits overlay
       evidence on top. Specs remain authoritative for long-term intent.

       ---
       6. PROD-011 (Implementation Execution Workflow) – Delta-First, Flexible Phases

       § 1 Problem Statement (lines 221-222):
       "Phase-01 is created by create delta before the Implementation Plan is fleshed
       out."

       § 1 Guiding Principles (lines 241-245):
       - Delta-first canonical stance (no explicit spec-first alternative offered)
       - Configuration over convention
       - Support varied workflows (delta-first, spec-first, backlog-first all
       supported) — but delta-first is canonical
       - Customizable hooks

       Journey 1 (lines 289-315): Delta creation first, then IP creation, then phase
       creation, then implementation.

       FR-001 & FR-002 (lines 366-378): Removes phase auto-creation from delta; allows
        phases to be created after IP is fleshed out.

       Spec's position: Delta is the entry point. Implementation plans are created
       after deltas. Phases are created after plans are complete. Specs are not
       mentioned in this flow — they exist in the background (discovered via
       relationship discovery during delta creation).

       ---
       7. PROD-016 (Agentic SDLC Configurator) – Configurable Entry Points

       § 1 Intent (line 186):
       "Spec-driver is evolving into an agentic SDLC construction kit... We need a
       single interactive entrypoint that selects the right ceremony mode and workflow
        posture for a repo..."

       § 2 Journeys (lines 202-205):
       1. Given a legacy repo, when a user runs spec-driver configure, then the repo
       is configured for a legacy-friendly default (Settler) with contracts-first
       posture
       2. Given a project evolves, when the user switches ceremony mode or posture
       knobs, then the installed skills/guidance update accordingly
       3. Given an agent begins work, when it reads the bootstrap, then it can choose
       the correct runsheet/skill

       § 5.3 Superpowers Integration (line 361):
       "If authoring.engine = "superpowers", spec-driver skills should route into it
       and enforce project conventions... If authoring.engine = "spec_driver", the kit
        may use its own interview loops (future capability)."

       Spec's position: PROD-016 doesn't prescribe workflow order; it provides
       configurability. Different ceremony modes (pioneer, settler, town_planner) may
       have different orderings.

       ---
       8. Governance & CLAUDE.md

       From CLAUDE.md "Contracts, Sync, and Truth" (lines 110-135):
       - .contracts/** is the canonical storage/location for generated contracts.
       - Contracts corpus is derived and deterministic — always safe to delete and
       regenerate.
       - Specs (especially assembly specs) should express requirements/constraints to
       validate against observed contracts/code, not duplicate full signatures as
       competing sources of truth.
       - Prefer contracts-first workflows for legacy repos to avoid unit-spec sprawl.

       Emphasis: Contracts (derived from code) are the source of truth for what code
       exposes. Specs are for requirements and constraints. This is
       legacy/contracts-first posture, not spec-first.

       ---
       9. Consistency Check Across Specs

       Consensus on Canonical Ordering:

       All specs are consistent on this progression:

       1. Capture (backlog: issue/problem/improvement)
       2. Spec (exists; may be pre-existing or created during backlog capture)
       3. Delta (scopes work against spec/requirement)
       4. Design Revision (architectural intent)
       5. Implementation Plan (phases, entrance/exit criteria)
       6. Implement (code + tests)
       7. Audit/Contracts (observe reality)
       8. Revision (if spec/requirement changes discovered)
       9. Spec Reconciliation (patch specs to match audit)
       10. Close (complete delta, verify coverage)

       Delta-first is the default canon (PROD-002, PROD-011, workflow.md).

       Revision-first is a concession path for town-planner governance
       (mem.pattern.spec-driver.core-loop, lines 77-80):
       "Revision-first is valid as a concession path, not the primary default. Strict
       canonical lock-in is a future strict_mode contract, not current runtime
       behavior."

       Specs are authoritative for long-lived requirements (PROD-008, PROD-009) — they
        are not optional, but they are updated retroactively by deltas and audits, not
        created before deltas.

       ---
       10. Prevailing Emphasis (Doctrine)

       From .spec-driver/agents/workflow.md (line 9):
       "Revision-first is a concession path (typically town-planner governance), not
       the default entry path."

       From mem.pattern.spec-driver.core-loop.md (lines 72-81):
       "Pioneer: card → implement → done (minimal loop)"
       "Settler: backlog → delta → implement → audit/reconcile → close (default
       canonical path)"
       "Town Planner: may start revision-first..."

       The prevailing doctrine emphasizes:
       1. Delta-first as the canonical default — this is where you start change work
       2. Specs as the authoritative long-lived record — they pre-exist or are
       discovered during delta creation; they are updated retroactively after audit
       3. Ceremony as configurable — different modes (pioneer, settler, town-planner)
       have different expectations, but delta-first is the default
       4. Contracts-first for legacy adoption — minimize spec sprawl by making
       contracts the source of truth for code APIs
       5. Coverage gates as mandatory — deltas cannot close without updating owning
       spec coverage blocks

       ---
       11. Answer to Your Original Questions

       Q1: Which PROD specs describe the workflow / lifecycle / core loop?

       - PROD-001 (spec creation) — orthogonal; specs exist but not in workflow order
       - PROD-002 (delta creation) — central; deltas are the entry point
       - PROD-008 (requirements lifecycle coherence) — central; specs are the
       authoritative record
       - PROD-009 (requirement lifecycle semantics) — supports PROD-008; evidence
       overlays specs
       - PROD-011 (implementation execution) — central; delta → IP → phases →
       implement
       - PROD-016 (configurator) — meta; makes ceremony and posture configurable

       Q2: What does each say about ordering — what comes first, what flows into what?

       All align: Backlog → Spec (pre-existing or discovered) → Delta → DR → IP →
       Phases → Implement → Audit → Revision (if needed) → Spec Reconcile → Close

       Delta is the entry point. Specs are authoritative but updated retroactively.

       Q3: Are they consistent with each other?

       Yes, fully consistent. No contradictions found.

       Q4: What's the prevailing emphasis / doctrine?

       Delta-first, spec-validated, contracts-honest, configurably-ceremonial.
       - Default: delta-first (Settler mode)
       - Authoritative long-term record: specs + coverage blocks
       - Source of truth for code APIs: contracts (not specs)
       - Optional concession: revision-first (town-planner only)

       ---
       12. Key Verbatim Quotes on Workflow Order

       Canonical ordering (workflow.md, line 7-8):
       "Canonical default narrative is delta-first:
       delta -> DR -> IP -> phase sheet(s) -> implement -> audit -> revision -> patch
       specs -> close"

       Specs are authoritative (PROD-008, FR-001):
       "The specs frontmatter and coverage block MUST be the authoritative record of
       each requirement's lifecycle state and supporting evidence."

       Specs are updated retroactively (PROD-008, FR-002):
       "Every delta that changes requirement behaviour MUST provide an implementation
       plan documenting planned VT/VA/VH artefacts and promote the final state back
       into the owning spec coverage block before completion."

       Delta-first is default (mem.pattern.spec-driver.core-loop, line 76):
       "Settler: backlog → delta → implement → audit/reconcile → close (default
       canonical path)"

       Revision-first is concession (mem.pattern.spec-driver.core-loop, lines 77-80):
       "Town Planner: may start revision-first for high-governance work, then revision
        → delta/DR/IP/phases → implementation → audit/contracts → spec reconciliation
       → closure
       Revision-first is valid as a concession path, not the primary default."

       ---
       Summary

       The corpus is coherent and consistent. The doctrine emphasizes delta-first
       workflows with specs as the authoritative long-lived record that is updated
       retroactively by deltas and audits. There are no conflicts; the variation is in
        ceremony mode (pioneer/settler/town-planner), not in the canonical loop
       itself.
