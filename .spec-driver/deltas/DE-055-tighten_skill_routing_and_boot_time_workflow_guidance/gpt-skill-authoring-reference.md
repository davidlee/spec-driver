# GPT Skill Authoring Reference

Purpose: give GPT agents a short, high-signal startup document for creating or
refining skills in spec-driver. This is a synthesis for DE-055 and a likely
source for future memory extraction, not a competing doctrine layer.

## 1. Ground Truth

- `ADR-004` is the workflow canon: code-changing work is delta-first,
  observation-led, and closed only after reconciliation.
- `ADR-005` sets the guidance hierarchy:
  - memories own conceptual guidance
  - skills own procedural guidance
  - other prose should route, summarize, or record research rather than compete
- `PROD-016` is the customization contract:
  - packaged skills stay uniform across installs
  - project-specific behavior belongs in generated guidance and
    `.spec-driver/hooks/*`
  - boot must stay token-cheap and route to on-demand runsheets

Implication: when designing skills for spec-driver, optimize for a stable
packaged core plus local projection through generated docs and hooks.

## 2. Startup Posture For DE-055

Before doing substantive work:

1. Run `boot`.
2. Route through `using-spec-driver`.
3. Use `spec-driver` for CLI/entity work.
4. Use `retrieving-memory` before assuming local truth.
5. If changing an active delta, do not implement until the needed
   `DE/DR/IP/phase` artifacts exist.

Do not treat "there is a delta" as permission to start editing skills. Routing
and planning still govern.

## 3. What To Preserve

### Keep `spec-driver` narrow

`spec-driver` works because it is specific: it handles spec-driver entities,
command discovery, and memory routing. Do not expand it into a general workflow
meta-skill.

### Keep routing separate

`using-spec-driver` should choose the governing skill before exploration or
implementation. This is the right import from Superpowers.

### Keep boot short

Boot should load only the minimum startup context and force early routing. Do
not turn it into a handbook.

### Keep generated and user-owned layers separate

If a behavior differs by repo, prefer:

- generated `.spec-driver/agents/*.md` for config-shaped projection
- `.spec-driver/hooks/*` for user-owned local doctrine

Avoid per-project forks of packaged skills.

## 4. What To Import From Superpowers

These patterns transfer well to spec-driver:

- Description as pure trigger:
  descriptions should answer "when do I load this skill?" and not summarize the
  workflow.
- Skills are testable:
  treat skill changes like code changes; verify behavior change, not prose
  elegance.
- Strong directive wording for discipline skills:
  if a behavior must survive pressure, write it as a rule, not a suggestion.
- Red-flag and rationalization patterns:
  use them where agents are tempted to skip workflow steps.
- Explicit loop structure for process skills:
  if a workflow depends on re-entry, make the loop obvious.
- Readiness as an assessed state, not a vibe:
  implementation-facing skills should force the agent to surface assumptions,
  unresolved questions, and tensions before claiming the work is ready.

These imports fit spec-driver because they strengthen procedural compliance
without changing the repo's doctrine.

## 5. What To Reject Or Adapt

- Do not import universal ceremony.
  Spec-driver is posture-aware and permissive; stronger guidance must still
  respect project posture.
- Do not require brainstorming, planning, or adversarial review for every task.
  Those are optional composable patterns unless governance says otherwise.
- Do not duplicate doctrine across README-like docs, skills, memories, and
  generated agent docs.
- Do not force-load large referenced content into skill bodies.
- Do not confuse research notes with reusable guidance.

If a Superpowers idea conflicts with `ADR-004`, `ADR-005`, or `PROD-016`,
adapt it or reject it.

## 6. Authoring Rules For Spec-Driver Skills

- Frontmatter description:
  trigger conditions only
- Main body:
  procedural guidance only
- Concepts, taxonomy, and "how spec-driver works":
  route to memories or ADR/spec references
- Local repo conventions:
  route through generated agent docs and hooks
- Cross-skill references:
  name the skill; do not inline or `@`-load large files by default
- Length:
  keep always-loaded and frequently used skills short enough that startup
  guidance stays cheap

Use stronger structure when the skill is discipline-enforcing:

- a bright-line opening rule
- explicit failure modes or red-flag thoughts
- direct counters to common rationalizations
- explicit readiness criteria when the skill hands off to implementation

Use lighter structure when the skill is reference-oriented:

- short command examples
- lookup-friendly bullets
- minimal prose

## 7. How To Evaluate A Skill Change

Minimum bar:

1. Identify the real failure mode.
2. Confirm whether the problem is:
   - missing routing
   - weak wording
   - wrong skill boundary
   - missing critical assessment before readiness claims
   - missing local projection
   - missing runtime enforcement
3. Change the smallest layer that fixes the failure.
4. Verify the new guidance appears in the installed/generated surface when
   relevant.
5. Record the decision in the delta bundle and, if durable, in memory.

Prefer guidance-layer fixes when the failure is agent behavior during work.
Prefer runtime enforcement only when guidance is insufficient or the rule must
hold outside agent discipline.

For implementation-bound skills and handoff skills, treat "ready to proceed" as
a claim that needs support. The minimum support is:

- confirmed inputs
- assumptions being carried forward
- unresolved questions
- tensions or ambiguities across the governing artefacts and code

## 8. Testing Heuristics

Use the Superpowers empirical stance, adapted to spec-driver:

- Start from an observed failure or rationalization, not from a theory that the
  skill "seems clearer."
- Test naive prompts that should trigger the skill.
- Check for premature action:
  the agent should load the governing skill before exploring or editing.
- For process skills, test that the agent follows the intended order rather than
  compressing it.
- For implementation-bound preflight or handoff skills, test that the agent does
  not declare readiness before surfacing assumptions, open questions, and
  tensions.
- Measure token cost only after the skill is doing the right thing.

In spec-driver, high-value checks include:

- does boot route to the right startup skill?
- does `using-spec-driver` stop premature exploration?
- does `spec-driver` still handle entity/CLI tasks without scope creep?
- do sync/install surfaces expose the intended skill cleanly?

## 9. Current Design Heuristics From DE-055

- Stronger startup routing is worth keeping.
- `spec-driver` should remain narrow.
- `using-spec-driver` should own early workflow routing.
- `execute-phase` should enforce `draft -> in-progress` during implementation.
- `preflight` should require a critical assessment before implementation-readiness claims.
- `continuation` and `next` should preserve unresolved assumptions and tensions in handoffs.
- Structured delta-document maintenance should stay separate from generic
  `/notes`.
- Backlog-oriented skill design is partially blocked by `ISSUE-009` until
  backlog statuses are canonical.
- Brainstorming and adversarial review are promising optional patterns, not
  default workflow gates.

## 10. Candidate Memory Split

This document is probably too dense to remain the final guidance surface. A good
follow-up split is:

- signpost:
  startup path for skill work in spec-driver
- pattern:
  skill authoring and evaluation loop for spec-driver
- fact:
  description metadata must be trigger-only
- fact:
  packaged skills vs generated guidance vs hook customization boundary
- thread or delta note:
  DE-055-specific open questions and pending follow-ups

Until then, use this file as the short synthesis before touching skill design in
spec-driver.
