# Notes for DE-083

## 2026-03-09

### What was done
- Created `DE-083` as the follow-up delta for work intentionally left unresolved when closing `DE-055`.
- Scoped the delta around two linked concerns:
  - keeping the audit loop strongly biased toward authoritative spec reconciliation
  - tuning revision/spec authorship skills so audit findings flow into existing specs, revisions, or new specs with less ambiguity

### Boundaries
- `DE-055` remains the design/implementation record for routing, DR-loop, and close-out guidance already landed.
- `DE-079` remains the implementation home for runtime audit schema, validation, and completion gates.
- `DE-083` is the skill-authoring and workflow follow-through layer that should sit on top of those two deltas rather than duplicate them.

### Immediate next step
- Shape `DR-083` before creating phases.

### Verification
- `uv run spec-driver show delta DE-083` succeeded after the delta/DR/IP rewrites.
- The plan currently has three planned phases and no phase sheet yet, by design; phase creation is deferred until `DR-083` is current.

### DR shaping update
- Resolved the main design boundary in `DR-083`: DE-083 should strengthen existing skills rather than introduce a dedicated spec-authoring skill.
- Settled the branch order as `existing spec patch -> revision -> revision-led new spec`, keeping the new-spec case inside the existing `revision` audit disposition rather than reopening the `DE-079` contract.
- Identified direct governance/spec revision targets as `PROD-011` and `SPEC-151`, with `PROD-002` and `PROD-001` treated as collaborator surfaces to confirm during implementation.

### Phase planning update
- Created `IP-083.PHASE-01` via `uv run spec-driver create phase "Shape audit-to-spec authorship design" --plan IP-083`, then re-scoped it to the first executable phase now that design shaping is already complete.
- Collapsed the remaining execution plan to two phases:
  - phase 1 applies the skill and direct governance changes
  - phase 2 verifies worked examples and reconciles the delta docs
- Added concrete entrance/exit criteria, verification expectations, STOP conditions, and task breakdown for phase 1.

---

## New Agent Instructions

### Task
**DE-083** — Strengthen audit-to-spec reconciliation and spec/revision authorship skills.
Next activity: **execute Phase 1** (IP-083.PHASE-01).

### Required reading (in order)
1. `DE-083.md` — delta scope, motivation, out-of-scope
2. `DR-083.md` — settled design decisions (DEC-083-001 through 005), branch criteria table, code impact summary
3. `IP-083.md` — 2-phase plan, verification coverage
4. `phases/phase-01.md` — task breakdown, entrance/exit criteria, STOP conditions
5. `evidence-based-skill-development-index.md` — prioritised index into the DE-055 research doc on empirical skill design

All paths relative to `.spec-driver/deltas/DE-083-strengthen_audit_to_spec_reconciliation_and_spec_revision_authorship_skills/`.

### Key files to modify (Phase 1)
- `supekku/skills/audit-change/SKILL.md` — add explicit authorship ordering + rationalization counters
- `supekku/skills/shape-revision/SKILL.md` — expand into post-audit authorship loop
- `supekku/skills/spec-driver/SKILL.md` — confirm revision-led `create spec` route (minor)
- `.spec-driver/product/PROD-011/PROD-011.md` — add reconciliation path (narrow touch, see tensions below)
- `.spec-driver/tech/SPEC-151/SPEC-151.md` — replace stub with explicit responsibilities

### Pattern source
- `supekku/skills/draft-design-revision/SKILL.md` — strongest existing authorship loop; reuse patterns for triage, doctrine pass, and section-by-section guidance
- `.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/evidence-based-skill-development.md` — iron laws, rationalization tables, flowcharts, two-stage separation

### Relevant memories
- `mem.concept.spec-driver.audit` — audit lifecycle and disposition kinds
- `mem.concept.spec-driver.spec` — specs as durable normative record
- `mem.concept.spec-driver.revision` — revisions as post-audit reconciliation artefact
- `mem.pattern.spec-driver.core-loop` — canonical delta-first workflow order

### Relevant doctrine / governance
- `ADR-004` — implementation flows through audit/contracts into revision/spec reconciliation
- `ADR-005` — memories own concepts; skills own procedures
- `ADR-008` — observed evidence triggers explicit reconciliation, not silent overwrite
- `ADR-003` — avoid competing truths
- `POL-001` — maximise code reuse, minimise sprawl
- `STD-002` — pylint signal governance (less relevant here but check if touched files trigger it)

### Dependencies (both completed)
- `DE-055` — settled routing/DR-loop doctrine
- `DE-079` — runtime audit contract (disposition kinds: `aligned`, `spec_patch`, `revision`, `follow_up_delta`, `follow_up_backlog`, `tolerated_drift`)

### Unresolved questions to assess before coding
1. **PROD-011 insertion point**: PROD-011 is 1006 lines focused on workflow hooks, automation metadata, and constitution enforcement. It has no section on audit-to-spec reconciliation. DR-083 says to "reconcile workflow guidance" there, but the spec's current shape has no natural home for it. Recommendation: add a guiding principle or a short new section — do not add a new capability/requirement block.
2. **SPEC-151 scope**: Currently a blank stub for `supekku/scripts/lib/skills` (Python package). DR-083 wants explicit responsibilities for "routing, authorship guidance, and create-spec reuse" — but those are properties of the packaged skill markdown, not the Python library API. Confirm whether SPEC-151 should cover both the runtime library and the skill content, or just one.
3. **Skill token budget vs evidence-based patterns**: The research index advocates iron laws, rationalization tables, and flowcharts. `audit-change` is currently 59 lines. Target ~100-120 lines per skill to stay within reasonable token budgets while adding the needed directive structure.

### Design tensions
- **PROD-011 scope creep**: Adding audit reconciliation language to a spec about workflow hooks risks awkward fit. Keep the touch minimal.
- **SPEC-151 category mismatch**: Unit spec for Python package vs skill-content responsibilities. May need the spec to acknowledge both layers.
- **No new disposition kinds**: DE-083 must work within DE-079's existing `spec_patch` and `revision` dispositions. "New spec" is a sub-branch of `revision`, not a peer.

### Commit guidance
- `.spec-driver/**` changes from phase 1 can be committed together or separately per doctrine (`doctrine.md`: prefer frequent small commits, bias toward keeping worktree clean).
- Skill file changes (`supekku/skills/`) and spec/PROD changes (`.spec-driver/`) can go in one commit or separate commits — whichever comes first while keeping the worktree clean.
- Run `uv run spec-driver install -y .` before final commit to keep installed copies aligned.

### Loose ends
- Phase 2 sheet does not exist yet — create it after phase 1 closes.
- `PROD-001` and `PROD-002` are collaborator surfaces: only edit if phase 1 implementation reveals an explicit wording gap.
- VA-083-001/002/003 are `planned` — phase 2 owns execution of these verification artefacts.

### Phase 1 execution update
- Started phase execution by reconciling lifecycle state:
  - `DE-083` moved to `in-progress`
  - `IP-083` moved to `in-progress`
  - `IP-083.PHASE-01` is now `completed`
- Updated packaged skill sources:
  - `supekku/skills/audit-change/SKILL.md`
  - `supekku/skills/shape-revision/SKILL.md`
  - `supekku/skills/spec-driver/SKILL.md`
- Reconciled direct governance surfaces:
  - `PROD-011` now states the canonical audit-to-spec reconciliation posture without adding a new capability block
  - `SPEC-151` now defines the skills subsystem boundary across packaged skills, installed copies, and sync/install support
- Confirmed collaborator surfaces did not need direct edits:
  - `PROD-001` unchanged
  - `PROD-002` unchanged

### Verification
- `uv run spec-driver install -y .` succeeded and refreshed the installed skill copies under `.spec-driver/skills/`
- `uv run spec-driver show delta DE-083` succeeded with `Status: in-progress`
- Discovered that `uv run spec-driver skills sync` is stale guidance in this repo; the implemented install/sync path is `uv run spec-driver install -y .`

### Worktree / follow-through
- Uncommitted work remains in this repo, including unrelated user changes outside `DE-083`; do not revert them.
- `.spec-driver/AGENTS.md` and installed skill copies changed as a consequence of `spec-driver install`.
- Next step is to create `IP-083.PHASE-02` and execute the worked-example verification/doc-reconciliation pass.

---

## 2026-03-10

### Phase 2 execution

- Created `IP-083.PHASE-02` phase sheet with concrete tasks, entrance/exit criteria, and verification expectations.
- Fixed a malformed duplicate phase entry in `IP-083.md` left by the phase creation command.
- Executed all three verification artefacts:
  - **VA-083-001** (decision path review): PASS — branch criteria explicit and doctrine-aligned across all 5 surfaces (audit-change, shape-revision, spec-driver, PROD-011, SPEC-151). Checked against ADR-003/004/005/008.
  - **VA-083-002** (authorship-skill gap review): PASS — no remaining gaps. The three skills form a coherent chain: audit-change (disposition) → shape-revision (authority movement) → spec-driver (entity creation).
  - **VA-083-003** (worked examples): PASS — three concrete scenarios covering spec_patch (imprecise wording fix), revision (validation logic moved between specs), and revision-led new spec (cross-cutting observability subsystem emerges). All branches are exercisable and distinguishable.
- Updated verification coverage in IP-083 and SPEC-151 from `planned` to `verified`.
- Reconciled IP-083: removed duplicate phase entry, updated Phase 2 status to in-progress, marked verification gates passed.

### Next step
- Update DR-083 status to accepted, complete Phase 2 exit criteria, hand off to closure.
