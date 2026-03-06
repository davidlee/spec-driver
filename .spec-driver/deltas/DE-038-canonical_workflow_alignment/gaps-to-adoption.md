# Gaps to Adoption (DE-038)

Purpose: capture evidence-backed blockers and confusion points that prevent
reliable agent/user adoption of the intended workflow.

Scope: specify gaps and evidence only. Remediation planning is follow-up work.

Snapshot date: 2026-03-04

Status legend:
- `resolved` = addressed by DE-038 outputs
- `partial` = mitigated in memory/skill surfaces, but source docs/runtime still drift
- `remains` = still open
- `deferred` = intentionally left for a follow-up delta

## 1. Hard Blockers

| Gap | Severity | Status (2026-03-04) | Affected Journey | Recommended Fix (Carry-Forward) | Evidence |
|-----|----------|----------------------|------------------|----------------------------------|----------|
| Coverage prerequisite is easy to miss before `complete delta`, causing late close-out failures | High | resolved | Implement -> close delta | Completed via memory/skill updates plus explicit prerequisite callout in canonical workflow docs | `supekku/scripts/lib/changes/coverage_check.py`, `supekku/scripts/complete_delta.py`, `memory/mem.fact.spec-driver.coverage-gate.md`, `docs/commands-workflow.md` |
| Status vocabulary in docs diverges from runtime lifecycle vocabulary | High | resolved | Requirement updates, validation, closure | Completed in DE-038 docs pass: lifecycle reference aligned and stale `RUN.md` removed | `supekku/about/lifecycle.md`, `supekku/scripts/lib/requirements/lifecycle.py`, `supekku/scripts/lib/requirements/registry.py` |
| Primary memory loop promoted revision-first as default | High | resolved | New-agent onboarding and sequencing | Completed in DE-038: retain delta-first core-loop/revision framing | `memory/mem.pattern.spec-driver.core-loop.md`, `memory/mem.concept.spec-driver.revision.md`, `change/deltas/DE-038-canonical_workflow_alignment/notes.md` |

## 2. Confusion Vectors

| Gap | Severity | Status (2026-03-04) | Affected Journey | Recommended Fix (Carry-Forward) | Evidence |
|-----|----------|----------------------|------------------|----------------------------------|----------|
| Ceremony mode is often read as runtime enforcement despite no command branching on ceremony | Medium | partial | Workflow selection and command expectations | Keep DE-038 memory/skill posture updates; align top-level docs so they repeat advisory-only semantics | `.spec-driver/workflow.toml`, `supekku/scripts/lib/core/config.py`, `memory/mem.concept.spec-driver.posture.md`, `memory/mem.signpost.spec-driver.ceremony.md` |
| "Archive" language in top-level docs does not match implemented closure behavior | Medium | resolved | End-of-change expectations | Completed: README closure narrative now uses complete/sync/validate semantics | `supekku/about/README.md`, `supekku/scripts/complete_delta.py`, `supekku/cli/complete.py` |
| Phase auto-scaffold assumptions still appear in narrative docs | Medium | resolved | Delta creation and planning | Completed: `lifecycle.md` now states phases are created via `create phase` and not auto-scaffolded | `supekku/about/lifecycle.md`, `supekku/scripts/lib/changes/creation.py`, `supekku/cli/create.py` |
| Coverage failure message points to legacy `.spec-driver/RUN.md` path | Low | remains | Delta close-out troubleshooting | Update runtime error text to point at active canonical docs (e.g., `docs/commands-workflow.md` or lifecycle guide) | `supekku/scripts/lib/changes/coverage_check.py` |

## 3. Missing Automation

| Gap | Severity | Status (2026-03-04) | Affected Journey | Recommended Fix (Carry-Forward) | Evidence |
|-----|----------|----------------------|------------------|----------------------------------|----------|
| No runtime strict-mode switch yet for canonical lock-in | Medium | deferred | Governance-grade workflow enforcement | Implement `strict_mode` runtime branching and enforcement touchpoints from DR-038 | `.spec-driver/workflow.toml`, `supekku/scripts/lib/core/config.py`, `change/deltas/DE-038-canonical_workflow_alignment/DR-038.md` |
| No first-class `create audit` command | Medium | remains | Post-implementation conformance workflow | Add CLI creation flow for audit bundles | `supekku/cli/create.py`, `supekku/about/processes.md` |
| No first-class `complete revision` command | Low | remains | Revision lifecycle management | Define and implement revision completion semantics + CLI | `supekku/cli/complete.py`, `supekku/about/processes.md` |

## 4. Documentation Debt

| File | Claim Drift | Severity | Status (2026-03-04) | Recommended Fix |
|------|-------------|----------|----------------------|-----------------|
| `supekku/about/lifecycle.md` | Previously used non-canonical statuses and outdated completion flow details | High | resolved | Rewritten to match current runtime behavior and canonical/tolerated status policy |
| `supekku/about/README.md` | Previously included "Archive" workflow step with no direct runtime implementation | Medium | resolved | Updated to close/reconcile/sync/validate lifecycle language |
| `docs/commands-workflow.md` | Canonical workflow map previously under-emphasized explicit coverage close-out prerequisite | Medium | resolved | Added explicit `complete delta` coverage prerequisite section |
| `supekku/about/RUN.md` | Legacy operational doc with stale lifecycle terminology | Medium | resolved | Removed; useful guidance migrated to canonical docs/memories |

## 5. Remaining Priority Queue

1. Update coverage failure runtime message to stop referencing legacy `.spec-driver/RUN.md`.
2. Plan follow-up automation delta(s): `strict_mode` runtime, `create audit`, `complete revision`.
