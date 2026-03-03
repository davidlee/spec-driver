# Gaps to Adoption (DE-038)

Purpose: capture evidence-backed blockers and confusion points that prevent
reliable agent/user adoption of the intended workflow.

Scope: specify gaps and evidence only. Remediation planning is follow-up work.

## 1. Hard Blockers

| Gap | Severity | Affected Journey | Recommended Fix | Evidence |
|-----|----------|------------------|-----------------|----------|
| Coverage prerequisite is easy to miss before `complete delta`, causing late close-out failures | High | Implement -> close delta | Surface coverage prerequisite in canonical onboarding/memories and completion checklist | `supekku/scripts/lib/changes/coverage_check.py`, `supekku/scripts/complete_delta.py`, `supekku/about/RUN.md` |
| Status vocabulary in docs diverges from runtime lifecycle vocabulary | High | Requirement updates, validation, closure | Publish canonical vs tolerated status policy and align docs | `supekku/about/lifecycle.md`, `supekku/scripts/lib/requirements/lifecycle.py`, `supekku/scripts/lib/requirements/registry.py` |
| Primary memory loop currently promotes revision-first as default | High | New-agent onboarding and sequencing | Reframe core loop to delta-first; keep revision-first as explicit concession path | `memory/mem.pattern.spec-driver.core-loop.md`, `memory/mem.concept.spec-driver.revision.md`, `docs/commands-workflow.md` |

## 2. Confusion Vectors

| Gap | Severity | Affected Journey | Recommended Fix | Evidence |
|-----|----------|------------------|-----------------|----------|
| Ceremony mode is often read as runtime enforcement despite no command branching on ceremony | Medium | Workflow selection and command expectations | State clearly that ceremony is guidance-only in current runtime | `.spec-driver/workflow.toml`, `supekku/scripts/lib/core/config.py`, `docs/commands-workflow.md` |
| "Archive" language in top-level docs does not match implemented closure behavior | Medium | End-of-change expectations | Replace archive narrative with implemented close/sync/validate semantics | `supekku/about/README.md`, `supekku/scripts/complete_delta.py`, `supekku/cli/complete.py` |
| Phase auto-scaffold assumptions still appear in narrative docs | Medium | Delta creation and planning | Explicitly state phases are created via `create phase` | `supekku/about/lifecycle.md`, `supekku/scripts/lib/changes/creation.py`, `supekku/cli/create.py` |

## 3. Missing Automation

| Gap | Severity | Affected Journey | Recommended Fix | Evidence |
|-----|----------|------------------|-----------------|----------|
| No runtime strict-mode switch yet for canonical lock-in | Medium | Governance-grade workflow enforcement | Implement `strict_mode` in workflow config and wire enforcement touchpoints | `.spec-driver/workflow.toml`, `supekku/scripts/lib/core/config.py`, `change/deltas/DE-038-canonical_workflow_alignment/DR-038.md` |
| No first-class `create audit` command | Medium | Post-implementation conformance workflow | Add CLI creation flow for audit bundles | `supekku/cli/create.py`, `supekku/about/processes.md` |
| No first-class `complete revision` command | Low | Revision lifecycle management | Define and implement revision completion command semantics | `supekku/cli/complete.py`, `supekku/about/processes.md` |

## 4. Documentation Debt

| File | Claim Drift | Severity | Recommended Fix |
|------|-------------|----------|-----------------|
| `supekku/about/lifecycle.md` | Uses non-canonical requirement statuses and outdated completion flow details | High | Rewrite around current runtime behavior and canonical/tolerated status policy |
| `supekku/about/README.md` | Includes "Archive" workflow step with no direct runtime implementation | Medium | Align workflow section to implemented closure primitives |
| `docs/commands-workflow.md` | Canonical workflow map does not emphasize coverage close-out prerequisite | Medium | Add explicit prerequisite section with source references |
| `supekku/about/RUN.md` | Uses outdated wording ("live" status) that does not match current lifecycle constants | Medium | Align to `active` lifecycle terminology and current completion behavior |
