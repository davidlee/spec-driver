---
id: IP-116-P03
slug: "116-registry_protocol_enforcement_and_governance_triplet_consolidation_adr_009-phase-03"
name: IP-116 Phase 2 — Policy + Standard registries + Workspace backlink hoist
created: "2026-06-02"
updated: "2026-06-02"
status: completed
kind: phase
plan: IP-116
delta: DE-116
---

# Phase 2 — Policy + Standard registries + Workspace backlink hoist

## 1. Objective

Collapse `PolicyRegistry` and `StandardRegistry` onto the `FrontmatterFileRegistry`
base, hoist backlink composition from registries to `Workspace._sync_governance`,
create legacy re-export shims, and prove correctness with a golden-YAML fixture
diff + shim-compat suite. **R (registry core + migration + backlink hoist) is
landable/committable here.**

## 2. Links & References

- **Delta**: DE-116 (scope §3, approach P2, verification §6).
- **Design Revision**: DR-116 §4 (base-class sketch, `_sync_governance` sketch, code-impact table).
- **Specs**: SPEC-126 (policies), SPEC-127 (standards).
- **Governance**: ADR-009 (registry API), ADR-002 (no backlinks in frontmatter), DEC-116-2
  (backlinks hoisted to Workspace), ER-3 (shim-compat suite).
- **Predecessor**: P1 (`phase-02.md`) — base class + DecisionRegistry done; Policy/Standard
  records already migrated.

## 3. Entrance Criteria

- [x] P1 complete — base + DecisionRegistry + shims committed green.
- [x] PolicyRecord and StandardRecord exist in `spec_driver/domain/records/`.
- [x] `uv run ty check` baseline green on DE-116 branch (331 diags).

## 4. Exit Criteria / Done When

- [ ] `spec_driver/domain/registries/policy.py` exists — `PolicyRegistry` subclass, pure
      (no relations import, no backlink building). `backlink_inputs = [("decisions", "policies")]`.
- [ ] `spec_driver/domain/registries/standard.py` exists — `StandardRegistry` subclass, pure.
      `backlink_inputs = [("decisions", "standards"), ("policies", "standards")]`.
- [ ] `supekku/scripts/lib/{policies,standards}/registry.py` are re-export shims.
- [ ] `Workspace._sync_governance(registry)` owns backlink composition via `build_backlinks_multi`;
      `sync_policies`/`sync_standards` delegate to it. Registries never import `domain.relations`.
- [ ] `spec_driver/orchestration/artifact_view.py` imports Policy/Standard registries from
      canonical paths.
- [ ] Golden-YAML fixture diff: before/after YAML byte-identical over a fixture corpus with
      known decision→policy and decision→standard cross-references (AR-2).
- [ ] Shim-compat suite on legacy paths green (ER-3).
- [ ] **Zero duplicated method bodies** across all 3 `domain/registries/{decision,policy,standard}.py`
      — grep for `def (collect|_parse_file|iter|find|write|sync)\b` in those files = 0.
- [ ] `uv run ty check` green; full gate sweep green.

## 5. Verification

- **VT-golden-registry-yaml**: before/after YAML diff empty over fixture corpus (AR-2 safety net).
- **VT-shim-compat**: dedicated tests on legacy import paths prove shims are drop-in (ER-3).
- **VA-ty-protocol-conformance**: `uv run ty check` — all 3 registries satisfy `RegistryProtocol`.
- **VA-no-relations gate**: `rg "domain\.relations" spec_driver/domain/registries` = 0.
- **VA-core-import gate**: `rg "supekku\.scripts\.lib\.core" spec_driver/domain/registries` = 0.
- **VA-internal-consumer gate**: no `spec_driver/**` (non-shim) imports policy/standard from `supekku.*`.
- **VA-zero-duplication**: grep for inherited method defs in domain/registries/*.py = 0.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - The live governance corpus has **zero backlinks** (AR-2 confirmed) — golden-YAML fixture test
    must use a synthetic fixture corpus with cross-references.
  - `Workspace._registry_for(category)` dispatch needs a small mapping dict (category string →
    registry property). Per AR-4 this is magic strings — tracked as minor follow-up.
  - `PolicyRegistry.filter` drops `standard` kw-only arg (unlike Decision which has `policy`+`standard`).
  - `StandardRegistry.filter` drops `standard` kw-only arg (has `policy` only).
- **STOP when**:
  - Golden-YAML fixture diff is non-empty → backlink hoist changed output; revert and investigate (R1).
  - Shim breakage in legacy consumers → STOP, restore original module, confirm scope.

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x]    | 2.1 | Create `spec_driver/domain/registries/policy.py` — PolicyRegistry onto base | [P] | `_build_record`, `_artifact_dir`, `filter`, `backlink_inputs` |
| [x]    | 2.2 | Create `spec_driver/domain/registries/standard.py` — StandardRegistry onto base | [P] | same pattern |
| [x]    | 2.3 | Shim `supekku/scripts/lib/policies/registry.py` and `standards/registry.py` | [P] | re-export from canonical |
| [x]    | 2.4 | Check/shim `supekku/scripts/lib/{policies,standards}/__init__.py` | [P] | already import from registry modules |
| [x]    | 2.5 | Hoist backlink composition to `Workspace._sync_governance` | [ ] | DR §4 sketch |
| [x]    | 2.6 | Migrate `artifact_view.py` Policy/Standard imports to canonical | [ ] | 2 lines |
| [x]    | 2.7 | Golden-YAML fixture test (VT-golden-registry-yaml) | [ ] | 4/4 pass |
| [x]    | 2.8 | Shim-compat suite (VT-shim-compat) | [ ] | 18/18 pass |
| [x]    | 2.9 | Full gate sweep + test suite green | [ ] | 36/36 pass; all VAs green |

### Task Details

- **2.1 PolicyRegistry onto base**
  - **Approach**: Same pattern as DecisionRegistry in P1. Subclass `FrontmatterFileRegistry[PolicyRecord]`.
    Class attrs: `_prefix = "POL"`, `_yaml_root_key = "policies"`,
    `backlink_inputs = [("decisions", "policies")]`.
    Defines: `_artifact_dir` → `get_policies_dir`, `_build_record` → `PolicyRecord(...)`,
    `filter(self, *, tag, spec, delta, requirement, standard)` → calls `_filter`.
    No `_resolve_status` override (base default is correct: `fm['status']` or `'draft'`).
  - **Testing**: shim-compat suite + policy-specific tests in P2.8.

- **2.2 StandardRegistry onto base**
  - **Approach**: Same. `_prefix = "STD"`, `_yaml_root_key = "standards"`,
    `backlink_inputs = [("decisions", "standards"), ("policies", "standards")]`.
    `filter(self, *, tag, spec, delta, requirement, policy)` → calls `_filter`.
    No `_resolve_status` override.
  - **Testing**: shim-compat + standard-specific tests.

- **2.5 Workspace backlink hoist**
  - **Approach**: Per DR §4 sketch. Add private `_sync_governance(self, registry)`:
    ```python
    def _sync_governance(self, registry):
      records = registry.collect()
      groups = [([(r.id, getattr(r, field)) for r in self._registry_for(cat).collect().values()], cat)
                for cat, field in registry.backlink_inputs]
      if groups:
        build_backlinks_multi(records, groups)
      registry.write(records=records)
    ```
    `_registry_for(category: str)` maps `"decisions"` → `self.decisions`, etc.
    `sync_policies` → `self._sync_governance(self.policies)`.
    `sync_standards` → `self._sync_governance(self.standards)`.
    `sync_decisions` unchanged (no backlinks on ADR).

- **2.7 Golden-YAML fixture test**
  - **Approach**: Create a minimal fixture corpus in a temp dir with ADR files that reference
    POL/STD, POL files that reference STD. Generate YAML with old registries → save. Generate
    with new registries + Workspace backlink hoist → compare byte-for-byte. Must match exactly.
  - **Files**: `spec_driver/domain/registries/test_golden_yaml.py`.

- **2.8 Shim-compat suite**
  - **Approach**: Test that legacy imports work and produce correct types:
    ```python
    from supekku.scripts.lib.policies.registry import PolicyRegistry, PolicyRecord
    from supekku.scripts.lib.standards.registry import StandardRegistry, StandardRecord
    from spec_driver.domain.registries.frontmatter import RegistryProtocol
    assert isinstance(PolicyRegistry(), RegistryProtocol)
    assert isinstance(StandardRegistry(), RegistryProtocol)
    ```
  - **Files**: `spec_driver/domain/registries/test_shim_compat.py`.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| R1 — Backlink hoist changes YAML output | Golden fixture diff as gating VT; revert on non-empty | open |
| Shim breakage in legacy consumers | Dedicated shim-compat suite (ER-3); if fails, restore and investigate | open |

## 9. Decisions & Outcomes

- `2026-06-02` — Phase authored. Policy/Standard follow same collapse pattern as Decision (P1).
  Backlink hoist per DR §4 `_sync_governance` sketch.

## 10. Findings / Research Notes

- `PolicyRegistry.filter` kw-only args: tag, spec, delta, requirement, standard (5 — no "policy" arg).
- `StandardRegistry.filter` kw-only args: tag, spec, delta, requirement, policy (5 — no "standard" arg).
- Both `PolicyRegistry` and `StandardRegistry` have `_build_backlinks` that lazily import
  `build_backlinks`/`build_backlinks_multi` from `domain.relations` — this is the upward edge
  being hoisted.
- Policy has `ext_id`, `ext_url` fields in `_build_record`; Standard has `policies`, `ext_id`,
  `ext_url`.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] IP-116 progress updated (P2 ticked)
- [ ] Hand-off notes to P3 (creation unification)
