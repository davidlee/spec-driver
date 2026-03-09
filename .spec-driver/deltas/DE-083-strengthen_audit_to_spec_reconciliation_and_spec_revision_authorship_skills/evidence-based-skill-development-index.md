# Evidence-Based Skill Development — DE-083 Relevance Index

Source: `../DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/evidence-based-skill-development.md`

This index identifies sections relevant to DE-083's goal of strengthening
audit-to-spec reconciliation and spec/revision authorship skills.

## High Relevance

### Skill taxonomy and structure

- **Section 3.1 "Discipline Skills"** (L:83–99) — Audit-to-spec reconciliation
  is discipline-enforcing: agents will be tempted to close deltas without
  flowing findings back into specs. Iron laws, rationalization tables, and red
  flags apply directly.
- **Section 3.3 "Process Skills"** (L:115–129) — The audit→spec-patch /
  revision / new-spec decision path is a multi-step process with non-obvious
  branch points. Flowcharts prevent premature termination of the reconciliation
  loop.

### Persuasion and compliance

- **Section 2.2 "Skills Are Not Suggestions"** (L:36–49) — Reconciliation
  guidance must be directive, not suggestive. "Consider updating the spec" will
  be rationalized away under closure pressure.
- **Section 7.1 "Effective Principles for Skill Design"** (L:431–459) —
  Authority + Commitment + Scarcity map directly: force explicit announcement of
  the reconciliation path chosen, use imperative language for the spec-update
  rule, and time-bind reconciliation to before-closure.
- **Section 9.6 "Suggestions Disguised as Rules"** (L:587–594) — Escape hatches
  like "generally" and "when possible" are the exact failure mode to avoid in
  audit-to-spec guidance.

### Design patterns

- **Section 8.1 "The Iron Law Pattern"** (L:486–499) — A short, absolute,
  testable rule anchoring the reconciliation skill. Candidate:
  `NO DELTA CLOSURE WITHOUT AUDIT FINDINGS RECONCILED INTO SPECS`.
- **Section 8.2 "The Rationalization Table"** (L:500–511) — Map the specific
  excuses agents use to skip spec updates (e.g. "the finding is minor", "I'll
  create a follow-up issue", "the spec is already close enough").
- **Section 8.4 "Flowcharts for Loops"** (L:529–539) — Make the
  finding→disposition→spec-outcome loop visually explicit so agents cannot
  short-circuit reconciliation.
- **Section 8.5 "Two-Stage Separation"** (L:540–545) — Separate the evaluative
  lens (audit finding assessment) from the authoring lens (spec/revision
  writing). Combining them causes one to dominate.

## Moderate Relevance

### Description and discoverability

- **Section 2.3 "The Description Trap"** (L:52–64) — Authorship skill
  descriptions must state triggering conditions only, not summarize the
  reconciliation workflow.
- **Section 4.1 "Frontmatter"** (L:147–159) — Keyword coverage in descriptions
  matters; use terms agents search for: "audit finding", "spec drift",
  "reconcile", "revision".

### Testing

- **Section 5.2 "Pressure Scenarios"** (L:230–266) — Agents will comply with
  reconciliation rules in calm contexts but skip them under closure pressure.
  Test with combined time + sunk-cost + pragmatic pressure.
- **Section 5.3 "Capturing Rationalizations"** (L:269–283) — Document exact
  rationalisations from testing and feed them back into the skill as explicit
  counters.
- **Section 5.4 "Meta-Testing"** (L:284–301) — When an agent skips
  reconciliation despite the skill, ask it how the skill should have been
  written.

### Structure

- **Section 4.2 "Section Order"** (L:161–184) — Consistent skill structure.
  Audit-to-spec reconciliation is likely a hybrid discipline/process skill.
- **Section 4.4 "Supporting Files"** (L:200–212) — Worked examples of
  finding→spec-patch / finding→revision / finding→new-spec could live in a
  supporting file to keep the main skill within token budget.

## Low Relevance (skim only)

- **Section 2.4 "Token Budget"** (L:68–77) — General budget guidance; relevant
  if the reconciliation skill risks bloat.
- **Section 6 "Measurement"** (L:333–420) — Useful later for validating the
  skill's effectiveness, not for initial design.
- **Section 8.6 "Description as Pure Trigger"** (L:546–551) — Already covered by
  2.3; reinforces the same point.
- **Section 10 "Checklist"** (L:598–629) — Development lifecycle checklist;
  useful when building the skill, not when scoping the delta.
