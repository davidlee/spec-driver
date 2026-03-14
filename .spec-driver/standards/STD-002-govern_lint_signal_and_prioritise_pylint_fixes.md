---
id: STD-002
title: "STD-002: govern lint signal and prioritise pylint fixes"
status: required
created: "2026-03-07"
updated: "2026-03-07"
reviewed: "2026-03-07"
owners: []
supersedes: []
superseded_by: []
policies: []
specs: [PROD-003]
requirements: []
deltas: [DE-058]
related_policies: []
related_standards: []
tags: [lint, pylint, quality, maintenance]
summary: "Keep pylint output decision-useful: do not excuse new warnings with existing debt, prioritize high-signal message families, and treat test docstring noise as low-priority."
---

# STD-002: govern lint signal and prioritise pylint fixes

## Statement

Pylint output must remain decision-useful. Teams should fix or explicitly justify
new warnings instead of dismissing them as acceptable because similar debt
already exists elsewhere in the repository.

Warning families should be prioritized by engineering risk, not by raw warning
count. As a default:

- Treat correctness, safety, and maintainability warnings as first-class work:
  `broad-exception-caught`, `consider-using-with`, `unspecified-encoding`,
  `import-outside-toplevel` when not required by cycle/lazy-load constraints,
  `duplicate-code`, and the complexity families
  (`too-complex`, `too-many-branches`, `too-many-locals`,
  `too-many-statements`, `too-many-arguments`).
- Treat test-only ergonomics warnings as lower priority. Test functions do not
  need docstrings when the test name is already clear, and tests may probe
  protected APIs when that is the most direct way to verify behavior.
- Do not narrow verification scope to changed files as a substitute for the
  repo-level lint gates. File-local lint runs are for diagnosis; `just pylint`
  remains the authoritative check.
- Keep `fail-under` on pylint's real 0-10 scale and ratchet it from proven
  full-repo results, not optimistic local runs.

## Rationale

The current pylint report mixes actionable architecture signals with a large
volume of low-value noise. That makes it too easy to rationalize away warning
families, to focus on score movement instead of message quality, or to justify
new warnings by pointing at older ones.

This standard pushes the repo in a better direction without pretending the
existing debt can be cleared in one step:

- Preserve strong scrutiny on production code and architectural hotspots.
- Reduce warning noise that does not materially improve maintainability.
- Make "no new warnings without justification" the default posture even in the
  presence of existing debt.
- Keep the repo-level lint gates meaningful instead of letting selective runs
  redefine success.

## Scope

Applies to Python code and lint configuration in this repository.

- Applies to new code, refactors, and lint configuration changes.
- Recommended for existing warning cleanup work and review decisions.
- Applies to both CLI and library modules.
- Applies to tests for verification posture, but with lower priority for
  docstring and protected-access warnings where the test naming already carries
  intent.
- Does not require immediate cleanup of all historical warnings.

## Verification

Adoption is tracked by:

- `just pylint` remaining the authoritative repository-level gate.
- `fail-under` being maintained on the 0-10 pylint score scale and raised only
  from demonstrated full-repo baselines.
- Lint configuration changes reducing noise by fixing broken ignores or tuning
  message scope intentionally, not by broadly disabling high-signal warnings.
- Code review rejecting "pre-existing debt" as a blanket justification for
  introducing new warnings of the same kind.
- Cleanup work favoring high-signal families before low-value bulk churn.

## References

- PROD-003 Policy and Standard Management
- DE-058 govern pylint signal and document lint standard
