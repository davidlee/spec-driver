# Notes for DE-055

## 2026-03-07

### What was done
- Created `DE-055`, `DR-055`, `IP-055`, and `IP-055.PHASE-01`.
- Reviewed current doctrine and workflow guidance:
  - `ADR-004`, `ADR-005`, `ADR-008`
  - `mem.pattern.spec-driver.core-loop`
  - `mem.concept.spec-driver.posture`
  - `mem.pattern.installer.boot-architecture`
- Reviewed current workflow skills and `/tmp/superpowers` reference skills.
- Added `supekku/skills/using-spec-driver/SKILL.md`.
- Added `using-spec-driver` to `.spec-driver/skills.allowlist`.
- Updated `supekku/skills/boot/SKILL.md` to point to `/using-spec-driver` after boot.
- Ran `uv run spec-driver skills sync` successfully after sandbox escalation to refresh installed skills and `.spec-driver/AGENTS.md`.

### Key observations
- The current `spec-driver` skill is already effective at reducing CLI misuse and should probably stay narrow.
- The biggest useful import from `using-superpowers` is earlier and stricter selection of the governing skill, not its universal ceremony.
- `PROD-016` already points toward the right customisation model:
  - generated guidance is overwritten from config
  - `.spec-driver/hooks/doctrine.md` is user-owned
  - avoid config-key explosion; use hooks for bespoke behaviour
- Likely implementation touchpoints:
  - `supekku/skills/spec-driver/SKILL.md`
  - `supekku/skills/boot/SKILL.md`
  - `supekku/templates/agents/boot.md`
  - `supekku/scripts/lib/skills/sync.py`
  - `supekku/scripts/install.py`

### Current leaning
- Link `spec-driver` more explicitly into boot-time routing.
- Introduce routing as a separate concern rather than broadening `spec-driver` into a meta-skill.
- Preserve uniform packaged skills across installs and keep repo-specific adaptation in hook stubs and generated docs.

### Open threads
- Determine the clean customisation seam for routing guidance.
- Check whether governance already states the packaged-skill plus hook-stub principle explicitly enough.
- Decide whether the routing layer should be a distinct skill, boot prose, or both.
- Decide how to expose optional brainstorming for authoring/design tasks.
- Decide whether optional brainstorming imports should split into a generic decision loop and artifact-specific authoring guidance.
- Decide how much of the new DR-first section-by-section authoring pattern should be mirrored into other authoring skills.
- Decide how to expose adversarial review as a reusable fresh-agent review pattern.
- Decide whether `complete delta` should reject `draft` now that execute-phase already requires `status: in-progress` before coding.
- Decide whether further guidance or runtime reinforcement is needed beyond the routing and execute-phase changes already landed for DR, IP, and phase-sheet skipping.
- Decide where commit defaults belong and how they should be confirmed for the active delta.
- Decide how to make `/notes` an invariant rather than a suggestion.
- Decide how explicit handoff prompts should be about carrying forward unresolved assumptions and tensions between phases and fresh agents.
- Decide how much more explicit the ordering contract should be beyond the using-spec-driver guardrail already added for `DR -> IP -> phase -> implementation`.
- Decide whether to add a dedicated capture skill and stronger backlog-to-delta-to-backlog lifecycle guidance.
- Treat `ISSUE-009` as a dependency for backlog-oriented skill workflows, because backlog status semantics are not yet canonical.

### 2026-03-07 - backlog dependency linkage
- Linked `ISSUE-009` into DE-055 as the current blocker for backlog-oriented skill workflow design.
- Rationale:
  - backlog capture/promotion/closure skills need canonical status semantics to prescribe transitions confidently
  - `ISSUE-009` already records that backlog items currently use inconsistent free-form statuses
  - this is an obstacle for defining workflow wording around backlog items without inventing non-canonical lifecycle states

### 2026-03-07 - phase 03 decision
- Chose the guidance-layer fix for the `draft` delta failure mode instead of changing `complete delta` in this phase.
- Rationale:
  - by close-out time the damage is already done; the misleading state exists during implementation
  - `execute-phase` is already the intended handoff from planning into active work
  - strengthening the mandatory invocation and `draft -> in-progress` wording keeps responsibility aligned with the implementation skill
- Runtime gating in `complete delta` remains a separate design question, not part of this change.

### 2026-03-07 - phase 03 work
- Updated `supekku/skills/execute-phase/SKILL.md` to:
  - make invocation mandatory and explicit before implementation work
  - call out that leaving the delta in `draft` is not harmless bookkeeping
  - require `status: in-progress` before coding proceeds
- Promoted DE-055 and IP-055 to `in-progress`.
- Created and filled `IP-055.PHASE-03` for the lifecycle-guidance tightening work.

### 2026-03-07 - phase 04 decision
- Chose to strengthen `using-spec-driver` rather than `execute-phase` or boot for the DR -> IP -> phase -> implementation ordering gap.
- Rationale:
  - the missing guardrail is in routing, where the agent decides the next governing skill
  - scope-delta, plan-phases, and execute-phase already encode the intended sequence once the agent has entered them
  - the failure mode is jumping from "there is a delta" to implementation before the bundle is execution-ready

### 2026-03-07 - phase 04 work
- Updated `supekku/skills/using-spec-driver/SKILL.md` to:
  - make execution readiness distinct from merely having a delta
  - route missing revision/scoping/planning work before `/execute-phase`
  - add a direct guardrail against treating an existing delta as permission to start implementing

### 2026-03-07 - phase 05 decision
- Keep `/notes` generic over cards and add a delta-specific execution documentation skill instead of overloading notes.
- Rationale:
  - compact implementation journaling and structured DE/IP/phase/DR reconciliation are different responsibilities
  - the generic notes skill still fits kanban and low-ceremony workflows
  - delta execution needs a stricter place to maintain phase/IP/DE/DR state without turning notes into a hidden workflow meta-skill

### 2026-03-07 - phase 05 work
- Added `supekku/skills/update-delta-docs/SKILL.md` as the delta-specific structured-doc maintenance skill.
- Updated `supekku/skills/execute-phase/SKILL.md` to call `/update-delta-docs` alongside `/notes`.
- Added `update-delta-docs` to `.spec-driver/skills.allowlist` for sync exposure.
- Ran `uv run spec-driver skills sync`; the first attempt hit sandbox restrictions writing `.agents/skills`, and the escalated retry succeeded.

### 2026-03-07 - queued research input
- Added `evidence-based-skill-development.md` to the DE-055 bundle as a pending research input.
- Do not read it yet for this delta thread; another agent is preparing a compressed extract of the relevant parts.

### 2026-03-07 - phase 07 case study and decision
- Captured a DE-053 multi-phase handover failure mode:
  - the handover named the right artefacts and next command
  - preflight summarized scope and entrance criteria
  - but it declared readiness before critically assessing DR/IP/phase tensions and unresolved implementation choices
- Decision:
  - strengthen `/preflight` so implementation-bound use must produce a critical assessment of confirmed inputs, assumptions, unresolved questions, and tensions before claiming readiness
  - strengthen `/continuation` and `/next` so handoffs preserve those unresolved questions instead of flattening them into a generic "ready to proceed"
  - reinforce `/execute-phase` so unresolved ambiguity discovered in preflight becomes a `/consult` trigger before improvisation

### 2026-03-07 - phase 07 work
- Updated `supekku/skills/preflight/SKILL.md` to require an explicit critical-assessment section and a stricter readiness standard for implementation-bound work.
- Updated `supekku/skills/continuation/SKILL.md` and `supekku/skills/next/SKILL.md` so handoff prompts must preserve unresolved assumptions, questions, and tensions.
- Updated `supekku/skills/execute-phase/SKILL.md` so `/preflight` is explicitly about surfacing assumptions and tensions before coding, and unresolved ambiguity routes to `/consult`.
- Ran `uv run spec-driver skills sync` successfully; installed skills and `.spec-driver/AGENTS.md` now reflect the stronger preflight and handoff wording.

### 2026-03-07 - evergreen GPT startup reference
- Added `gpt-skill-authoring-reference.md` to the DE-055 bundle.
- Purpose:
  - give GPT agents a short startup document before they touch spec-driver skill work
  - compress DE-055 doctrine and Superpowers-derived guidance into one practical synthesis
  - act as a staging document for future memory extraction rather than a new permanent handbook layer
- Refreshed the document after the DE-053 handover lesson so it now also captures:
  - implementation readiness as a critical-assessment outcome rather than a scope-summary vibe
  - the need for `/continuation` and `/next` to preserve unresolved assumptions and tensions in handoffs
- Main conclusions captured there:
  - preserve `spec-driver` as a narrow CLI/entity skill
  - keep routing separate in `using-spec-driver`
  - keep boot short and force early routing
  - preserve packaged-skill uniformity and push local variation into generated docs and hooks
  - import trigger-only descriptions, empirical skill testing, and anti-rationalization patterns from Superpowers
  - reject universal ceremony and any pattern that competes with ADR-004, ADR-005, or `PROD-016`
- Likely follow-up:
  - split the synthesis into a small set of durable memories once the wording settles
  - probably a signpost, a pattern, and a few facts rather than one long memory
- Created `mem.signpost.spec-driver.skill-authoring` as the first durable extraction
  pointing future skill work back to the DE-055 synthesis and the governing
  ADR/spec/memory sources.

### 2026-03-07 - skills allowlist gotcha
- `.spec-driver/skills.allowlist` controls which packaged skills are installed into generated surfaces such as `.spec-driver/skills`, `.agents`, and `.claude`.
- If a skill is missing from the allowlist, `uv run spec-driver skills sync` will not expose it there even if the packaged skill exists under `supekku/skills/`.
- On a fresh install the allowlist is created with the full skill list.
- Deleting `.spec-driver/skills.allowlist` and rerunning sync repopulates it.

### 2026-03-07 - phase 08 brainstorming decomposition
- Re-read `/tmp/superpowers/skills/brainstorming/SKILL.md` against current DE-055 direction.
- Conclusion:
  - the imported value is not one thing
  - there is a small generic loop for resolving one open question at a time with options, tradeoffs, recommendation, and write-back
  - there is also a stronger authoring pattern where designs are presented section by section before being written out as a whole
- Current design direction:
  - keep the generic loop as a possible future composable skill
  - put the section-by-section authoring enhancements into specific authoring/revision skills first, especially DR-oriented and revision-oriented skills
  - do not import the full universal-ceremony version of brainstorming
- High-leverage shared pattern to preserve:
  - before drafting sections, explicitly think step by step about open questions, risks, underspecified areas, assumptions, and critical design decisions
  - this is likely the main upstream quality gate; if it is weak, the downstream design loop cannot recover cleanly
- Likely future targets:
  - `draft-design-revision`
  - `shape-revision`
  - a lighter delta/capture loop later if the generic question-resolution pattern proves stable

### 2026-03-07 - phase 09 DR-first authoring import
- Applied the first artifact-specific brainstorming import to `draft-design-revision`.
- Changes made there:
  - require explicit pre-draft triage of open questions, risks, underspecified areas, assumptions, and critical design decisions
  - encourage one-question-at-a-time closure with options, tradeoffs, recommendation, and write-back when unresolved design questions remain
  - require section-by-section DR drafting/validation instead of treating a full design dump as the default
  - push toward concrete design detail such as likely types, responsibilities, boundaries, and verification impact
- Rationale:
  - DRs are the strongest first target for this pattern
  - the quality of downstream planning depends heavily on closing or naming foundational design assumptions early
  - this preserves the high-value authoring behavior from brainstorming without importing its universal ceremony
- Ran `uv run spec-driver skills sync` successfully; installed skills and `.spec-driver/AGENTS.md` now reflect the stronger DR authoring wording.

### Observed failure modes
- `complete delta` still tolerates lifecycle status `draft`; execute-phase now mitigates the earlier drift, but runtime closure semantics remain undecided.
- Agents were eager to skip DR, IP, or phase sheets and proceed directly to implementation; routing and execute-phase guidance now address the main guidance gap, but the remaining question is whether stronger reinforcement is still needed.
- Multi-phase handovers can preserve the right artefact list while still flattening unresolved design questions, leading preflight to overstate implementation readiness.
- Large authoring skills may mix together generic decision closure and artifact-specific presentation choreography, making it harder to import only the high-value parts into spec-driver.
- Agents can fail to end each task with `/notes`, leaving records stale.
- Git commit policy is underspecified: end of task, end of phase, or other cadence is unclear.
- Ordering between DR, IP, phase-sheet creation, and phase execution now has an explicit routing guardrail, but may still need stronger reinforcement or closure semantics.
- There is no dedicated capture skill, and the connective tissue from backlog capture into delta creation and back to updating/resolving originating backlog items is weak.

### Work completed so far
- Created and populated the `DE-055` bundle for this workflow-improvement thread.
- Added and synced the new `using-spec-driver` routing skill.
- Strengthened `using-spec-driver` description and opening language for Claude-style underuse of skills.
- Tightened `preflight` so it no longer competes with `using-spec-driver` for first-touch routing.
- Strengthened `execute-phase` so delta implementation must move work to `in-progress`.
- Added a routing guardrail so `using-spec-driver` sends missing DR/IP/phase work to shaping/planning before `/execute-phase`.
- Added `update-delta-docs` so structured DE/IP/phase/DR maintenance is separate from generic `/notes`.
- Synced skills successfully so generated `AGENTS.md` reflects the new routing surfaces.
- Linked `ISSUE-009` as the blocker for backlog-oriented skill workflow semantics.
- Linked `evidence-based-skill-development.md` into the bundle as pending research input without reading it directly.
- Hardened `preflight`, `continuation`, `next`, and `execute-phase` so implementation readiness requires a critical assessment of assumptions, unresolved questions, and tensions.
- Decomposed the useful imports from Superpowers brainstorming into a generic decision loop and artifact-specific section-by-section authoring guidance.
- Landed the first artifact-specific authoring enhancement in `draft-design-revision`.
- Recorded the skills-allowlist install-surface gotcha for future skill work.

## Fresh-agent onboarding

### Read this first
- `DE-055.md`
- `DR-055.md`
- `IP-055.md`
- `notes.md`
- `gpt-skill-authoring-reference.md`
- `phases/phase-01.md`
- `phases/phase-02.md`
- `phases/phase-03.md`
- `phases/phase-04.md`
- `phases/phase-05.md`
- `phases/phase-06.md`
- `phases/phase-07.md`
- `phases/phase-08.md`
- `phases/phase-09.md`

### Read these only if needed
- `supekku/skills/using-spec-driver/SKILL.md`
- `supekku/skills/preflight/SKILL.md`
- `supekku/skills/execute-phase/SKILL.md`
- `supekku/skills/update-delta-docs/SKILL.md`
- `supekku/skills/continuation/SKILL.md`
- `supekku/skills/next/SKILL.md`
- `supekku/skills/draft-design-revision/SKILL.md`
- `supekku/skills/spec-driver/SKILL.md`
- `supekku/skills/boot/SKILL.md`
- `.spec-driver/AGENTS.md`
- `evidence-based-skill-development.md` only after the compressed relevant extract is available
- `mem.signpost.spec-driver.skill-authoring` for the durable startup pointer

## 2026-03-09 - audit-loop design narrowing

### What was done
- Re-read the DE-055 audit-loop section in `DR-055` against:
  - `ADR-004`
  - `ADR-008`
  - `mem.pattern.spec-driver.core-loop`
  - `mem.concept.spec-driver.audit`
  - `mem.pattern.spec-driver.delta-completion`
  - current audit template/schema and close-out/validation touchpoints
- Tightened the DR so the audit loop now states:
  - what makes a delta qualify for audit gating
  - when a standalone `AUD-*` artifact is expected
  - why discovery/backfill audits should default to warnings while conformance audits block qualifying closure
  - what per-finding disposition data must exist for closure to reason from audit output

### Design decisions captured
- Treat audit gating as a closure rule for deltas that change requirement-bearing or spec-governed technical reality, not for every delta indiscriminately.
- Require a standalone `AUD-*` artifact for qualifying gated audits so closure, validation, and handoff all have a stable reconciliation anchor.
- Keep non-qualifying or exploratory discovery work flexible: embedded evidence is still acceptable there, but it does not satisfy the canonical gated audit checkpoint.
- Make conformance audits block closure until every blocking finding has a disposition and linked reconciliation work.
- Keep discovery/backfill audits warning-first by default, escalating only when they are being used to justify closure or when they reveal materially misleading active specs without any owned follow-up.
- Replace loose narrative audit outcomes with machine-checkable per-finding disposition data; exact final schema shape is still open.

### Assumptions carried forward explicitly
- The user wants DR/design work only for now; no implementation or runtime-gate changes were attempted in this pass.
- Doctrine still says `implement -> audit/contracts -> revision/spec reconcile -> close`.
- Runtime still only hard-gates delta closure on coverage today; the stronger audit gate remains design intent, not current behavior.
- The worktree is dirty and includes unrelated changes; inspect carefully before any later commit.
- `uv run spec-driver validate` is still failing on unrelated pre-existing `DE-076` errors, so that failure should not be treated as a regression from DE-055 design edits.

### Remaining open threads
- Final audit lifecycle/status enum vocabulary still needs settling.
- Final schema shape for per-finding disposition is still open:
  - nested disposition object
  - dedicated reconciliation block
  - or both
- Need a policy for which discovery/backfill warnings should become blockers before any future runtime strictness lands.

### 2026-03-09 - audit/disposition compatibility with drift ledger
- Follow-up design clarification after the audit-loop narrowing pass:
  - audit finding disposition should be compatible with DE-065 drift ledgers
  - drift-ledger linkage should be optional, not required for every audit finding
  - drift ledger should not become the closure-grade record for conformance audit findings
- Current recommended shape:
  - keep per-finding disposition in `AUD-*` as the authoritative closure/checkpoint record
  - allow optional refs from findings to `DL-*` entries for durable cross-work tracking
  - let drift entries record audit origin via discovery metadata rather than replacing the audit finding itself
- Rationale:
  - preserves DE-065 as a drift-management primitive instead of turning it into a competing closure system
  - reuses the drift lifecycle where it is strongest: discovery-heavy, cross-cutting, or long-lived adjudication
  - avoids forcing extra ceremony on every conformance audit

### Governing context already established
- `ADR-004` is the workflow canon.
- `ADR-005` says skills and memories own guidance.
- `PROD-016` is the key anchor for generated guidance vs user-owned hooks.
- `/tmp/superpowers` has already been reviewed for:
  - `using-superpowers`
  - `brainstorming`
  - `writing-plans`
  - `executing-plans`

Do not spend tokens re-reading broad repo docs unless a new conflict appears.

### Current design state
- `using-spec-driver` now exists and is synced into generated agent metadata.
- `preflight` has been narrowed so it should no longer compete with `using-spec-driver` for first-touch routing.
- `preflight` now also requires a critical assessment before implementation-readiness claims.
- `execute-phase` now makes the `draft -> in-progress` transition explicit.
- `update-delta-docs` now exists for structured DE/IP/phase/DR reconciliation during execution.
- `draft-design-revision` now requires explicit design triage and section-by-section validation before treating a DR as coherent.
- Current leaning remains:

## 2026-03-08 - phase 10 memory-effectiveness follow-up

### Decision
- Improve memory effectiveness in the skill layer first, not via a new runtime hook in this phase.
- Rationale:
  - the request is explicitly for a skills-based solution
  - ADR-005 says skills own procedural guidance
  - the main gaps were not missing primitives, but missing prompts in the execution and close-out skills

### Work in progress
- Created `IP-055.PHASE-10` to track this follow-up under the existing plan.
- Updated `supekku/skills/retrieving-memory/SKILL.md` so agents query memories with concrete `--path` targets before touching a subsystem; memories scoped by `scope.globs` should surface through those path queries.
- Updated `supekku/skills/execute-phase/SKILL.md` and `supekku/skills/implement/SKILL.md` so scoped memory lookup happens before deep subsystem work and durable discoveries trigger memory capture/maintenance during execution.
- Updated `supekku/skills/notes/SKILL.md`, `supekku/skills/capturing-memory/SKILL.md`, and `supekku/skills/close-change/SKILL.md` so phase and delta wrap-up explicitly review for durable facts, patterns, and gotchas worth preserving in memory.

### Expected verification
- `uv run spec-driver skills sync`
- targeted pytest on skill sync/install CLI surfaces

### Verification results
- `uv run spec-driver skills sync` passed; `.spec-driver/skills` was refreshed and both agent targets reported all skill symlinks `ok`.
- `uv run pytest supekku/scripts/lib/skills/sync_test.py supekku/scripts/lib/install_test.py supekku/cli/skills_test.py` passed: 148 tests.
- Created `mem.pattern.git.spec-driver-commit-cleanliness` and confirmed it surfaces for:
  - `uv run spec-driver list memories -p .spec-driver/hooks/doctrine.md -c "git commit"`

### Open edge
- This does not solve proactive surfacing automatically on every file read/write. `PROB-004` still captures that possible hook-based follow-up if the skill-layer prompts prove insufficient.

### Verification results
- `uv run spec-driver skills sync` passed; `.spec-driver/skills` was refreshed and both agent targets reported all skill symlinks `ok`.
- `uv run pytest supekku/scripts/lib/skills/sync_test.py supekku/scripts/lib/install_test.py supekku/cli/skills_test.py` passed: 148 tests.
- Created `mem.pattern.skills.memory-retrieval-and-wrapup` and confirmed it surfaces for both:
  - `uv run spec-driver list memories -p supekku/skills/retrieving-memory/SKILL.md -c "uv run spec-driver list memories"`
  - `uv run spec-driver list memories -p supekku/skills/close-change/SKILL.md -c "uv run spec-driver complete delta"`

## 2026-03-08 - phase 11 configurable `.spec-driver` commit guidance

### Decision
- Put the repo-specific `.spec-driver` commit preference in `.spec-driver/hooks/doctrine.md`.
- Keep packaged skill guidance generic: follow doctrine, and absent stronger repo guidance prefer frequent, small `.spec-driver` commits with a clean-repo bias.

### Work in progress
- Created `IP-055.PHASE-11` for this follow-up.
- Updated `.spec-driver/hooks/doctrine.md` with the local default:
  - prefer frequent, small `.spec-driver` commits
  - bias toward a clean repo over waiting for perfectly related `.spec-driver` batches
  - commit `.spec-driver` changes with code or separately, whichever comes first while keeping the worktree clean
  - use short, conventional commit messages
- Updated `supekku/templates/hooks/doctrine.md` so fresh installs get the same commit-policy seam instead of an empty doctrine template.
- Updated `supekku/skills/execute-phase/SKILL.md`, `supekku/skills/notes/SKILL.md`, `supekku/skills/close-change/SKILL.md`, and `supekku/skills/continuation/SKILL.md` so agents check doctrine and keep pending `.spec-driver` commit state explicit.

### Expected verification
- `uv run spec-driver skills sync`
- targeted pytest on skill sync/install CLI surfaces
  - keep `spec-driver` narrow
  - keep routing separate
  - preserve uniform packaged skills across installs
  - preserve project-specific customisation through generated docs and hooks

### Open threads worth working next
- Decide whether `complete delta` should still permit `draft` after the execute-phase guidance change
- Make `/notes` a stronger invariant
- Define commit-policy defaults and confirmation behaviour
- Decide whether the new handoff/preflight critical-assessment wording is sufficient in practice or needs even stronger enforcement
- Decide how much of the DR-first authoring pattern should move next into `shape-revision` or other authoring skills
- Decide whether to create a generic decision-loop skill and which artifact skills should gain section-by-section authoring guidance first
- Add capture/backlog connective tissue:
  - capture or refine backlog item
  - promote to delta cleanly
  - update or resolve originating backlog items after delta completion
- Decide whether brainstorming and adversarial review become optional composable skills or remain prompt patterns
- Decide whether the newly landed routing and execution guardrails are sufficient or need stronger follow-up enforcement
- Incorporate the compressed DE-055-relevant extract from `evidence-based-skill-development.md` once it is available

### Verification caveats
- `uv run spec-driver skills sync` succeeded after escalation and is not the current blocker.
- `uv run spec-driver validate` still fails on unrelated pre-existing errors in:
  - `DE-049`
  - `DE-052`
  - `DE-053`
  - `DE-054`

Do not treat those validation failures as evidence that `DE-055` is broken.

### Efficient next-step pattern
1. Read the delta bundle files listed above.
2. Inspect only the specific skill or sync/install file needed for the chosen failure mode.
3. Update `DE-055`, `DR-055`, `IP-055`, `notes.md`, and the active phase as you go.
4. Avoid broad repo rediscovery unless a source-of-truth conflict appears.

## New Agent Instructions

### Task card code
- `DE-055`

### Required reading
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/DE-055.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/DR-055.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/IP-055.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/notes.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/gpt-skill-authoring-reference.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-01.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-02.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-03.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-04.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-05.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-06.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-12.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-13.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-14.md`

### Related documents
- `/home/david/dev/spec-driver/specify/decisions/ADR-004-canonical_workflow_loop.md`
- `/home/david/dev/spec-driver/specify/decisions/ADR-005-memories_and_skills_are_the_canonical_guidance_layer.md`
- `/home/david/dev/spec-driver/specify/decisions/ADR-008-normative_lifecycle_truth_and_observed_evidence_reconciliation.md`
- `/home/david/dev/spec-driver/.spec-driver/product/PROD-016/PROD-016.md`

### Key files
- `/home/david/dev/spec-driver/supekku/skills/using-spec-driver/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/preflight/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/execute-phase/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/update-delta-docs/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/continuation/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/next/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/spec-driver/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/boot/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/audit-change/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/close-change/SKILL.md`
- `/home/david/dev/spec-driver/supekku/templates/audit.md`
- `/home/david/dev/spec-driver/supekku/scripts/lib/core/frontmatter_metadata/audit.py`
- `/home/david/dev/spec-driver/supekku/scripts/complete_delta.py`
- `/home/david/dev/spec-driver/supekku/scripts/lib/requirements/registry.py`
- `/home/david/dev/spec-driver/supekku/scripts/lib/validation/validator.py`
- `/home/david/dev/spec-driver/.spec-driver/skills.allowlist`
- `/home/david/dev/spec-driver/.spec-driver/AGENTS.md`

### Relevant memories
- `mem.pattern.spec-driver.core-loop`
- `mem.concept.spec-driver.posture`
- `mem.concept.spec-driver.audit`
- `mem.concept.spec-driver.revision`
- `mem.pattern.installer.boot-architecture`
- `mem.signpost.spec-driver.skill-authoring`

### Relevant doctrines
- Delta-first canon from `ADR-004`
- Skills/memories as guidance layers from `ADR-005`
- Observed evidence triggers explicit reconciliation, not silent overwrite, from `ADR-008`
- Generated guidance plus user-owned hook split from `PROD-016`

### Important user instructions and decisions
- Keep `spec-driver` narrow.
- Keep routing separate.
- Stronger description/opening language matters because Claude under-uses skills.
- The user explicitly asked for a DR deliverable, not implementation.
- Optional future patterns to preserve:
  - brainstorming for authoring/design work
  - adversarial review for fresh-agent challenge passes

### Incomplete work / loose ends
- Decide how to address:
  - whether `complete delta` should still accept `draft`
  - missing `/notes` at task end
  - ambiguous commit policy
  - missing capture skill / weak backlog -> delta -> backlog connective tissue
  - how much of the DR-first authoring pattern should move into `shape-revision` or other authoring skills next
  - whether to add a generic decision-loop skill and where to embed section-by-section authoring guidance first
  - whether the new handoff/preflight critical-assessment wording is sufficient or needs stronger reinforcement
  - whether the newly landed routing/execution guardrails are sufficient or need stronger follow-up reinforcement
- Decide the audit-loop design details now captured in `DR-055`:
  - only if the workflow doctrine changes
  - concrete audit contract/schema/runtime questions now belong to `DE-079`
- Decide whether brainstorming and adversarial review become explicit optional skills or remain prompt patterns.
- Use `evidence-based-skill-development.md` only after the compressed delta-relevant extract is available.

### Pending commit-state guidance
- Repo doctrine prefers frequent, small `.spec-driver` commits, but do not commit blindly here.
- Current worktree is not clean:
  - intended design-doc changes: `DE-055.md`, `DR-055.md`
  - incidental sync output: `.spec-driver/registry/requirements.yaml`
  - unrelated pre-existing code changes also exist outside DE-055
- Next agent should inspect the worktree before committing and avoid bundling unrelated code changes with this DE-055 design work unless the user explicitly wants that.

### Other advice
- Do not re-discover the whole repo. The context is already concentrated in `DE-055`.
- `uv run spec-driver validate` currently fails on unrelated pre-existing errors in `DE-076`.
- `uv run spec-driver skills sync` has already succeeded after escalation; use escalation again if sync must write to `.agents/skills`.
- `uv run spec-driver sync` succeeded in this turn and refreshed generated docs plus the requirements registry.

### Next logical activity
- `/using-spec-driver` for `DE-055`, then either:
  - `/preflight` any remaining DE-055 doctrine/workflow question that is still unresolved, or
  - switch to the `DE-079` bundle for audit schema/runtime implementation and review, or
  - fold in the compressed `evidence-based-skill-development.md` extract once available and reconcile it against the updated DR.

### Verification status
- Skill sync succeeded and `.spec-driver/AGENTS.md` now exposes `using-spec-driver` and `update-delta-docs`.
- `uv run spec-driver show delta DE-055` passed.
- `uv run spec-driver sync` passed.
- `uv run spec-driver validate` still fails on unrelated pre-existing errors in `DE-076`.

## 2026-03-08

### 2026-03-08 - phase 12 DR review-loop tightening
- Extended `supekku/skills/draft-design-revision/SKILL.md` again to tighten the post-draft loop.
- New guidance added there:
  - keep DR authoring progressive and section-scoped rather than whole-file-by-default
  - bias toward code-adjacent examples when they remove ambiguity about APIs, responsibilities, data shapes, or tricky seams
  - require the planning agent to run an adversarial self-review of the DR before treating it as coherent
  - after integrating that local feedback, offer to print a prompt for an external adversarial reviewer
  - require reconciling `DE-XXX.md` after DR feedback and before offering `/plan-phases` or new phase-sheet work
- Rationale:
  - section-by-section drafting alone still leaves room for polished but under-specific DRs
  - a mandatory internal challenge pass raises quality without forcing every DR through a second external agent
  - planning from a stale DE recreates drift immediately, so DE reconciliation belongs inside the DR loop itself
- Updated `DE-055.md`, `DR-055.md`, `IP-055.md`, and `IP-055.PHASE-12` to record the new accepted design direction.

### 2026-03-08 - phase 13 doctrine in the DR loop
- Updated `draft-design-revision` so it explicitly runs `/doctrine` before drafting.
- The DR loop now treats governance as part of both:
  - pre-draft design triage
  - adversarial self-review
- Added guidance to stop and `/consult` if the doctrine pass reveals conflicting or ambiguous ADR/policy/standard constraints.
- Rationale:
  - governance is easy to treat as passive background reading unless the skill makes it an explicit step
  - the critical review loop should attack missing or weakly applied ADR/policy/standard constraints just as hard as vague prose or weak verification

## 2026-03-09

### 2026-03-09 - phase 14 backlog follow-through in close-change
- Updated `supekku/skills/close-change/SKILL.md` so delta closure now:
  - checks for originating backlog entries during pre-check
  - revisits them during post-check
  - nudges status/note/link updates instead of leaving backlog records stale after the delta completes
- Updated `mem.pattern.spec-driver.delta-completion` with a dedicated backlog follow-through step.
- Rationale:
  - closing the delta without touching the originating backlog item leaves traceability and backlog state behind
  - `ISSUE-009` still blocks inventing a canonical backlog status vocabulary, so the close-out skill should nudge and escalate ambiguity rather than guess

### 2026-03-09 - audit-loop DR extension
- Treated the user request as design only, not implementation.
- Extended `DR-055.md` and reconciled `DE-055.md` to cover the missing canonical audit loop:
  - documented the doctrine/runtime gap between `ADR-004` and `ADR-008` and the current workflow behavior
  - added an explicit audit contract for qualifying deltas
  - defined the intended relationship between `audit-change`, the AUD artifact, revisions/spec patches, validation, and `complete delta`
  - recorded new design decisions and open questions around when audits are mandatory, whether standalone AUD artifacts are always required, and how hard audit drift should gate closure
- Concrete gaps now called out in the DR:
  - `audit-change` is still only advisory
  - `create audit` scaffolds a weak shell
  - the audit schema/template are richer than the runtime semantics that consume them
  - `complete delta` gates only on coverage, not audit reconciliation
  - requirements sync records audit IDs but not unresolved audit drift as a closure-grade outcome
- Verification performed:
  - `uv run spec-driver show delta DE-055` passed
  - `uv run spec-driver sync` passed and refreshed generated agent docs
  - `uv run spec-driver validate` still fails on unrelated pre-existing `DE-076` requirement-reference errors
- Important worktree note:
  - `uv run spec-driver sync` also rewrote `.spec-driver/registry/requirements.yaml`
  - there are unrelated pre-existing code/worktree changes outside DE-055; do not assume a clean tree

### 2026-03-09 - DE-079 dependency scoping pass
- Re-scoped `DE-055`/`DR-055` so the audit loop stays doctrine-first here and the concrete contract now clearly belongs to `DE-079`.
- Changes made:
  - updated `DE-055.md` earlier in the turn to say `DE-079` owns canonical audit reconciliation implementation
  - removed audit-schema/open-question ownership from `DR-055` frontmatter
  - reconciled `DR-055` audit-language to stop implying that stored `closure_effect`, unresolved schema shape, or `accepted_drift` remain live decisions here
  - kept `DR-055` focused on the workflow contract: qualifying deltas, standalone `AUD-*` expectation, conformance-vs-discovery posture, and optional drift-ledger linkage
- Guidance for future agents:
  - use `DR-055` when the question is about doctrine, workflow posture, or skill expectations
  - use `DR-079` when the question is about audit schema, validation rules, lifecycle enums, or `complete delta` gate mechanics

### 2026-03-09 - phase 15 DR-before-IP handoff tightening
- Follow-up issue observed during live use: agents still too often try to skip DR work and jump straight into IP or phase planning.
- Root cause captured:
  - `draft-design-revision` itself was strong
  - but `using-spec-driver` and `plan-phases` still left enough room to treat IP planning as a substitute for missing or stale non-trivial design
- Changes made:
  - created `IP-055.PHASE-15`
  - updated `using-spec-driver` so missing or stale non-trivial DR work routes back to `/draft-design-revision` before `/plan-phases`
  - updated `scope-delta` so `/plan-phases` is clearly downstream of DR work for non-trivial changes
  - updated `plan-phases` so it treats missing or stale non-trivial DR work as a stop condition rather than planning ahead
  - reconciled `DE-055`, `DR-055`, and `IP-055` so the stronger DR-before-IP rule is explicit
- Design takeaway:
  - IP and phase creation are execution planning artefacts, not a substitute for current design intent
  - the target ordering for non-trivial work is now explicitly `DR -> IP -> phase sheet -> implementation`
- Verification:
  - packaged skills updated: `supekku/skills/using-spec-driver/SKILL.md`, `supekku/skills/scope-delta/SKILL.md`, `supekku/skills/plan-phases/SKILL.md`
  - generated workspace copies refreshed after rerunning the current install flow
  - verified generated copies now match the new DR-before-IP wording in `.spec-driver/skills/*`
