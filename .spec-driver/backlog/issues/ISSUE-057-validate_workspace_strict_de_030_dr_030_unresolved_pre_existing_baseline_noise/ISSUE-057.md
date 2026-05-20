---
id: ISSUE-057
slug: validate_workspace_strict_de_030_dr_030_unresolved_pre_existing_baseline_noise
name: "validate workspace strict: DE-030 → DR-030 unresolved (pre-existing baseline noise)"
created: "2026-05-20"
updated: "2026-05-20"
status: open  # one of: in-progress | open | resolved | triaged
kind: issue  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
categories: []
severity: p3
impact: systemic
---

# validate workspace strict: DE-030 → DR-030 unresolved (pre-existing baseline noise)

## Summary

`uv run spec-driver validate workspace --kind delta --strict` surfaces one persistent `error`-level diagnostic against DE-030:

```
Issue: ValidationIssue(level='error', message="References unresolved artifact 'DR-030' (via relation.introduces)", artifact='DE-030')
```

Under tolerant mode the same diagnostic emits as `warning` (validator promotes severity under strict). This is pre-existing baseline noise — present at IP-138-P01 close, P03 close, and IP-138-P04 entrance. Not introduced by DE-138 work.

## Surface

- DE-030 (`.spec-driver/deltas/DE-030-unit_vs_assembly_spec_classification/DE-030.md`) declares relation `introduces: DR-030`.
- DR-030 (`.spec-driver/deltas/DE-030-unit_vs_assembly_spec_classification/DR-030.md`) exists on disk with frontmatter `id: DR-030`, `kind: design_revision`, `delta_ref: DE-030`, `relations: [{type: implements, target: DE-030}]`. Status `draft`.
- Validator still reports `DR-030` as "unresolved" — registry-resolution does not find the artefact despite presence + correct frontmatter.

## Root-cause hypothesis (unverified)

Design revisions co-located inside delta directories may not be picked up by the relation resolver, OR the resolver expects DR-* in `.spec-driver/revisions/` (where `RE-*` lives) rather than under the owning delta dir. DR-138 + sibling DR-* files all live under their parent delta dir without surfacing this error — needs verification.

## DE-138 P04 carve-out

Acknowledged as pre-existing baseline noise in DR-138 §11.4 + §10.5 (amended at IP-138-P04 task 4.1):

- Pre-flip baseline: `validate workspace --kind delta --strict` = exit 1 (1× DR-030 error + 7× sibling-draft audit-gate warnings promoted).
- Post-flip gate: tolerates this exact baseline; new errors beyond it fail the gate.
- Strict-flip is verification-bearing for delta block schemas + cut-key enforcement (DR-138 §5/§6), not for cross-artefact relation resolution (this issue's scope).

## Resolution path

1. Investigate registry-resolution scope — confirm whether design_revisions inside delta dirs are loaded.
2. If load-order / discovery bug: one-line registry fix.
3. If by-design (DR-* must live in `.spec-driver/revisions/`): either move DR-* files or extend resolver to walk delta dirs.
4. Once resolved: DE-138 P04 baseline carve-out (DR-138 §11.4) can be tightened back to "only sibling-draft audit-gate warnings remain."

## Owner / Due

- **Owner**: TBD (likely supekku registry/validation maintainer).
- **Due**: open; no DE-138 close blocker — see carve-out above.
- **Consumed by**: post-DE-138 sweep of validate-workspace baseline; not the DE-136 P04 umbrella audit (that audit's scope is DR-138 §9.5 verification-asymmetry — see F-138-24 / separate issue).

## Cross-references

- DR-138 §11.4 (post-flip gate baseline carve-out — amended IP-138-P04).
- DR-138 §10.5 (acceptance gate "0 errors beyond documented baseline").
- IP-138-P04 phase sheet §6 (STOP carve-out).
- DE-030, DR-030 (the offending pair).
