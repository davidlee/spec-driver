---
id: mem.pattern.dr-authoring-review-loop
name: DR authoring review loop
kind: memory
status: active
memory_type: pattern
created: '2026-03-08'
updated: '2026-03-08'
verified: '2026-03-08'
tags:
- skills
- workflow
- design
summary: 'For draft-design-revision work: keep the DR progressive, add code-adjacent
  examples where needed, consult doctrine, run an internal adversarial pass, reconcile
  DE, then optionally print an external-review prompt before planning.'
scope:
  paths:
  - supekku/skills/draft-design-revision/SKILL.md
  - .spec-driver/skills/draft-design-revision/SKILL.md
  commands:
  - uv run spec-driver skills sync
provenance:
  sources:
  - kind: delta
    ref: DE-055
  - kind: design_revision
    ref: DR-055
links:
  missing:
  - raw: DR-055
---

# DR authoring review loop

## Summary
- Use this when refining `draft-design-revision` guidance or when checking whether a DR-writing loop is complete enough to hand off to planning.

## Context
- Current canonical implementation lives in [[DE-055]] and [[DR-055]].
- This pattern is the repo-approved import from brainstorming for DR authoring; it is not a universal workflow rule.

## Loop
- Run `/doctrine` before drafting so relevant ADRs, policies, and standards are in view for the current design surface.
- Keep the interaction progressive and section-scoped. Do not treat a full-file rewrite as the default unit of progress.
- Add code-adjacent detail when prose stays vague:
  - sketch APIs or signatures
  - outline data shapes
  - show short pseudocode or code samples for tricky seams
- After the DR feels coherent, run an internal adversarial review:
  - attack vague claims
  - attack weak verification
  - attack missing code-impact detail
  - attack hidden assumptions
  - attack missing, misread, or weakly applied ADR/policy/standard constraints
- Integrate that feedback into the DR before moving on.
- Reconcile the owning delta after DR feedback so scope, risks, acceptance criteria, and follow-up direction match the revised design.
- Only then offer to print an external adversarial-review prompt or initiate planning.
