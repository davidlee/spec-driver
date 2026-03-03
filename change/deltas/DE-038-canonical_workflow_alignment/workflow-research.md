# Workflow Research: Delta-First Canonical Model

Code-truth research mapping spec-driver workflow behavior with two explicit modes:

- current runtime mode (permissive)
- future canonical-lock mode (switch in `workflow.toml`, not yet implemented)

**Date**: 2026-03-03  
**Scope**: workflows, status semantics, flag compatibility, lock-in surface area

---

## A. Canonical Narrative and Runtime Reality

### A1. Target Canonical Spine (Lockable, Future)

```
delta -> DR -> IP -> phase sheet(s) -> implement -> audit -> revision (from findings) -> patch specs -> close
```

This is the intended high-rigor narrative to be optionally enforced by a future
`workflow.toml` switch.

### A2. Current Runtime Default (Permissive, Today)

Current code allows multiple sequences. The only hard close-out gate is coverage
verification in parent specs during `complete delta`.

Current default sequence often seen in practice:

```
delta -> (optional DR/IP/phases) -> implement -> update parent spec coverage -> complete delta
-> (optional audit -> revision -> patch specs)
```

### A3. Step-by-Step (Current Behavior + Canonical Intent)

1. **Create delta**
   - `uv run spec-driver create delta "Title" --spec SPEC-XXX --requirement SPEC-XXX.FR-XXX`
   - Scaffolds: `DE-XXX.md`, `DR-XXX.md`, `IP-XXX.md` (unless `--allow-missing-plan`), `notes.md`
   - Phase files are **not** auto-created; use `create phase` explicitly.

2. **Create phases when needed**
   - `uv run spec-driver create phase "Phase Name" --plan IP-XXX`

3. **Implement**
   - Execute planned tasks; update evidence.

4. **Coverage prerequisite for close-out**
   - Parent spec coverage block entries for each `applies_to.requirements` item must be `status: verified`
     for normal completion.

5. **Complete delta (canonical close-out command)**
   - `uv run spec-driver complete delta DE-XXX`
   - Updates delta status to `completed`.
   - By default updates requirement lifecycle via revision sources (and creates completion revision when needed).

6. **Audit / revision / spec patching**
   - Supported today, and canonical in future lock mode, but not currently sequence-enforced.

---

## B. Path Compatibility Matrix (Including Flags)

| Path | Default Runtime (Today) | Canonical-Lock Mode (Future, Proposed) | Relevant Flags | Evidence |
|------|--------------------------|------------------------------------------|----------------|----------|
| Delta full: `delta -> DR -> IP -> phases -> implement -> ...` | Supported | Canonical | `--allow-missing-plan` (off) | `changes/creation.py` |
| Delta lean: `delta -> implement -> ...` without IP/phases | Supported | Likely disallowed or warning in lock mode | `--allow-missing-plan` | `cli/create.py` + `changes/creation.py` |
| Backlog-driven delta creation | Supported | Supported (if sequence after delta is canonical) | `--from-backlog` | `cli/create.py` |
| Complete delta with requirement updates | Supported/default | Supported/default | (none) | `scripts/complete_delta.py`, `cli/complete.py` |
| Complete delta while skipping requirement updates | Supported | Likely restricted in lock mode | `--skip-update-requirements` | `cli/complete.py`, `scripts/complete_delta.py` |
| Coverage-bypass close-out | Supported | Likely restricted in lock mode | `--force`, `SPEC_DRIVER_ENFORCE_COVERAGE=false` | `scripts/complete_delta.py`, `coverage_check.py` |
| Complete delta before audit/revision/spec patch | Supported | Should be disallowed in lock mode | (none) | sequence is not currently enforced |
| Audit -> revision -> patch specs before close | Supported (manual sequencing) | Canonical | (none) | docs + manual flow support |
| Revision-first workflow | Supported/concession | Allowed only when lock-mode policy permits | (none) | `cli/create.py`, `docs/commands-workflow.md` |

---

## C. Flexibility vs Rigidity

### C1. Hard Gates in Current Code

- Coverage gate on `complete delta` (unless bypassed):
  - requirements in delta `applies_to.requirements` must be `verified` in parent spec coverage blocks.
- Requirement lifecycle statuses accepted by code:
  - `pending | in-progress | active | retired`
- Coverage statuses accepted by code:
  - `planned | in-progress | verified | failed | blocked`
- Change statuses accepted by code:
  - `draft | pending | in-progress | completed | deferred` (plus legacy alias `complete` normalization)

### C2. Flexible Areas in Current Code

- DR presence/content is not runtime-enforced.
- IP/phase presence is not runtime-enforced.
- Audit creation is optional and manual.
- Revision creation is optional/manual except completion-generated revisions for untracked requirements.
- Ceremony mode in `workflow.toml` is advisory today (loaded for guidance, not runtime gating).

### C3. Proposed Rigidity in Future Canonical-Lock Mode

The future switch should be able to require:

- audit/revision/spec-patch ordering before `complete delta`
- disallow or warn on `--allow-missing-plan`
- stricter handling of `--force` and `--skip-update-requirements`
- optional validation-level checks for canonical sequence compliance

---

## D. Requirement Locality and Lifecycle Support (Code-Truth)

### D1. Inline spec requirements (first-class)

- Extracted from SPEC/PROD markdown body FR/NF lines.
- Primary lifecycle source for registry sync.

### D2. Breakout requirement files under spec bundles (partial support)

- `create requirement` can scaffold requirement files under `specify/**/requirements/`.
- They are artifact-level documents, but not first-class requirement extraction sources in the main requirements sync path.

### D3. Backlog requirement metadata (indirect support)

- Backlog `related_requirements` can pre-populate delta requirement links when using `--from-backlog`.
- Backlog items are not lifecycle authority for requirement status transitions.

### D4. Coverage placement nuance

- Registry library can aggregate coverage from specs/deltas/plans/audits when those inputs are provided.
- Default sync/workspace paths do not include plan files.
- Delta completion coverage enforcement checks parent specs.

---

## E. Drift Findings (High-Impact)

1. **Phase scaffolding drift**
   - Some workflow narratives imply `phase-01.md` is auto-created by `create delta`.
   - Current code explicitly does not auto-create phases.

2. **Status enum drift in docs**
   - Historical docs still reference non-code statuses (`implemented`, `verified`, `in_progress`).
   - Code accepts hyphenated and different lifecycle sets.

3. **Archive vs closure drift**
   - “Archive” appears in high-level docs, but runtime closure is status + lifecycle + registry coherence.

4. **Coverage prerequisite discoverability drift**
   - The strongest runtime gate is easy to miss in top-level workflow docs.

5. **Ceremony enforcement perception drift**
   - Ceremony often read as enforcement; runtime behavior is permissive today.

---

## F. Surface Area for Future Canonical-Lock Switch (No Implementation in DE-038)

### F1. Switch Contract (Proposed)

- Location: `.spec-driver/workflow.toml`
- Name: **TBD in follow-up delta**
- Behavior:
  - default value keeps current permissive behavior
  - enabled value activates canonical sequence enforcement and stricter flag policy

### F2. Touchpoints to Wire in Follow-up Delta

- `create` command surfaces (`delta`, `phase`, revision/audit scaffolding expectations)
- `complete delta` sequencing and prerequisite checks
- `validate` command for sequence diagnostics
- agent workflow generation surfaces (`templates/agents/*`)
- policy for flag interactions (`--allow-missing-plan`, `--force`, `--skip-update-requirements`, `--skip-sync`)

### F3. Non-Goals in This Delta

- No runtime branching on switch
- No command behavior changes
- No schema changes

---

## G. Open Questions

1. What should the switch key be called in `workflow.toml`?
2. In lock mode, should non-canonical paths hard-fail or warn?
3. In lock mode, should `--force` be disallowed or policy-gated?
4. Should breakout requirement files become first-class lifecycle sources, or remain documentary artifacts?
5. Should plan coverage aggregation be part of default sync paths?

---

## Source Index

- `supekku/scripts/complete_delta.py`
- `supekku/scripts/lib/changes/coverage_check.py`
- `supekku/scripts/lib/changes/creation.py`
- `supekku/scripts/lib/requirements/lifecycle.py`
- `supekku/scripts/lib/requirements/registry.py`
- `supekku/scripts/lib/specs/registry.py`
- `supekku/scripts/lib/workspace.py`
- `supekku/cli/create.py`
- `supekku/cli/complete.py`
- `supekku/cli/sync.py`
- `docs/commands-workflow.md`
- `supekku/about/README.md`
- `supekku/about/lifecycle.md`
- `supekku/about/processes.md`
