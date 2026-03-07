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
- Decide how to expose adversarial review as a reusable fresh-agent review pattern.
- Decide how to prevent `complete delta` from tolerating `draft` status at closure time.
- Decide how aggressively skills should resist skipping DR, IP, and phase sheets.
- Decide where commit defaults belong and how they should be confirmed for the active delta.
- Decide how to make `/notes` an invariant rather than a suggestion.
- Decide how explicit the ordering contract should be between DR, IP, phase creation, and implementation.
- Decide whether to add a dedicated capture skill and stronger backlog-to-delta-to-backlog lifecycle guidance.

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

### Observed failure modes
- Deltas can be completed with lifecycle status still `draft`.
- Agents are eager to skip DR, IP, or phase sheets and proceed directly to implementation.
- Agents can fail to end each task with `/notes`, leaving records stale.
- Git commit policy is underspecified: end of task, end of phase, or other cadence is unclear.
- Ordering between DR, IP, phase-sheet creation, and phase execution is not enforced or stated strongly enough.
- There is no dedicated capture skill, and the connective tissue from backlog capture into delta creation and back to updating/resolving originating backlog items is weak.

### Work completed so far
- Created and populated the `DE-055` bundle for this workflow-improvement thread.
- Added and synced the new `using-spec-driver` routing skill.
- Strengthened `using-spec-driver` description and opening language for Claude-style underuse of skills.
- Tightened `preflight` so it no longer competes with `using-spec-driver` for first-touch routing.
- Synced skills successfully so generated `AGENTS.md` reflects the new routing surfaces.

## Fresh-agent onboarding

### Read this first
- `DE-055.md`
- `DR-055.md`
- `IP-055.md`
- `notes.md`
- `phases/phase-01.md`
- `phases/phase-02.md`

### Read these only if needed
- `supekku/skills/using-spec-driver/SKILL.md`
- `supekku/skills/preflight/SKILL.md`
- `supekku/skills/spec-driver/SKILL.md`
- `supekku/skills/boot/SKILL.md`
- `.spec-driver/AGENTS.md`

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
- Current leaning remains:
  - keep `spec-driver` narrow
  - keep routing separate
  - preserve uniform packaged skills across installs
  - preserve project-specific customisation through generated docs and hooks

### Open threads worth working next
- Prevent deltas from being completed while still `draft`
- Resist skipping DR, IP, and phase sheets
- Make `/notes` a stronger invariant
- Define commit-policy defaults and confirmation behaviour
- Strengthen the stated ordering:
  - `DR -> IP -> create phase sheet <-> implement phase`
- Add capture/backlog connective tissue:
  - capture or refine backlog item
  - promote to delta cleanly
  - update or resolve originating backlog items after delta completion
- Decide whether brainstorming and adversarial review become optional composable skills or remain prompt patterns

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
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-01.md`
- `/home/david/dev/spec-driver/.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-02.md`

### Related documents
- `/home/david/dev/spec-driver/specify/decisions/ADR-004-canonical_workflow_loop.md`
- `/home/david/dev/spec-driver/specify/decisions/ADR-005-memories_and_skills_are_the_canonical_guidance_layer.md`
- `/home/david/dev/spec-driver/.spec-driver/product/PROD-016/PROD-016.md`

### Key files
- `/home/david/dev/spec-driver/supekku/skills/using-spec-driver/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/preflight/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/spec-driver/SKILL.md`
- `/home/david/dev/spec-driver/supekku/skills/boot/SKILL.md`
- `/home/david/dev/spec-driver/.spec-driver/skills.allowlist`
- `/home/david/dev/spec-driver/.spec-driver/AGENTS.md`

### Relevant memories
- `mem.pattern.spec-driver.core-loop`
- `mem.concept.spec-driver.posture`
- `mem.pattern.installer.boot-architecture`

### Relevant doctrines
- Delta-first canon from `ADR-004`
- Skills/memories as guidance layers from `ADR-005`
- Generated guidance plus user-owned hook split from `PROD-016`

### Important user instructions and decisions
- Keep `spec-driver` narrow.
- Keep routing separate.
- Stronger description/opening language matters because Claude under-uses skills.
- Optional future patterns to preserve:
  - brainstorming for authoring/design work
  - adversarial review for fresh-agent challenge passes

### Incomplete work / loose ends
- Decide how to address:
  - deltas completed while still `draft`
  - skipping DR, IP, and phase sheets
  - missing `/notes` at task end
  - ambiguous commit policy
  - weak `DR -> IP -> phase -> implementation` ordering
  - missing capture skill / weak backlog -> delta -> backlog connective tissue
- Decide whether brainstorming and adversarial review become explicit optional skills or remain prompt patterns.

### Other advice
- Do not re-discover the whole repo. The context is already concentrated in `DE-055`.
- `uv run spec-driver validate` currently fails on unrelated pre-existing errors in `DE-049`, `DE-052`, `DE-053`, and `DE-054`.
- `uv run spec-driver skills sync` has already succeeded after escalation; use escalation again if sync must write to `.agents/skills`.

### Next logical activity
- `/preflight` on the next chosen failure mode inside `DE-055`, then implement the highest-value workflow guardrail.

### Verification status
- Skill sync succeeded and `.spec-driver/AGENTS.md` now exposes `using-spec-driver`.
- `uv run spec-driver validate` still fails on unrelated pre-existing errors in `DE-049`, `DE-052`, `DE-053`, and `DE-054`.
