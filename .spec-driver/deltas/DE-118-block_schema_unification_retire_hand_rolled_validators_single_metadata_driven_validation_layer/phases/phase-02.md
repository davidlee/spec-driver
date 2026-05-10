---
id: IP-118-P02
slug: "118-block_schema_unification_retire_hand_rolled_validators_single_metadata_driven_validation_layer-phase-02"
name: IP-118 Phase 02
created: "2026-05-09"
updated: "2026-05-09"
status: draft
kind: phase
plan: IP-118
delta: DE-118
---

# Phase 02 — Foundations

## 1. Objective

Land the four DE-118-introduced mechanism changes plus the snapshot-compare harness. **No retirements** — every hand-rolled validator continues to run unchanged. Every change is additive and backwards-compatible (default flag values preserve current behaviour). Exit gate is `just check` green and `spec-driver validate` baseline-identical.

Concretely, P02 ships:

1. `FieldMetadata.additional_properties: FieldMetadata | None = None` — DEC-004 part 1; relaxed `__post_init__` so object type accepts `properties` OR `additional_properties`.
2. `MetadataValidator.__init__(metadata, *, strict_unknown_keys: bool = False)` — DEC-001 + DEC-004 part 2; object-type branch and top-level `validate(data)` extended per DR-118 §7 algorithm.
3. `BlockSchema.renderer: Callable[..., str] | None = None` — DEC-005 part 1; `get_parameters()` short-circuits to `{}` when None.
4. `_placeholder_renderer` retired — DEC-005 part 2; 7 workflow.* schemas re-register with `renderer=None`; `cli/schema.py:425–447` example fallback skips when None.
5. `supekku/scripts/lib/blocks/metadata/snapshot_compare.py` — DEC-007 dual-validate harness with `python -m … --root <path>` CLI.
6. VT additions for all of the above.

## 2. Links & References

- **Delta**: DE-118
- **Design Revision Sections**: DR-118 §3 (target outcomes), §4 ("Phase 1 — Foundations"), §7 DEC-001 / DEC-004 / DEC-005 / DEC-007 (algorithm + harness shape), §8 OQ-HARNESS-PLACEMENT / OQ-HARNESS-LIFECYCLE.
- **Specs / PRODs**: SPEC-114 (blocks/metadata; primary), SPEC-115 (changes/blocks; secondary), SPEC-116 (frontmatter_metadata; pattern reference).
- **Support Docs**:
  - P01 inventory at `../notes.md` (informs which loaders consume `MetadataValidator`).
  - DR-136 §11.1 (current-schema only — validator must not import `migrations/`).
  - STD-003 (utility module placement; relevant to OQ-HARNESS-PLACEMENT).

## 3. Entrance Criteria

- [x] IP-118-P01 complete (inventory + `validate-baseline.txt` committed at `c085d595`).
- [x] DR-118 §4 P02 design current — no edits since P01.
- [x] DE-118 status: in-progress; IP-118 status: in-progress.
- [x] No outstanding `/consult` thread on DE-118 design.

## 4. Exit Criteria / Done When

- [ ] `FieldMetadata.additional_properties` field landed; `__post_init__` accepts object type with `properties` OR `additional_properties` (or both).
- [ ] `MetadataValidator(metadata, strict_unknown_keys=True)` rejects unknown keys at every nested-object depth; `MetadataValidator(metadata)` (default) preserves loose behaviour bit-for-bit on the existing test corpus.
- [ ] `BlockSchema(renderer=None)` constructs; `get_parameters()` returns `{}`; `cli/schema.py` renderer fallback emits "no example available" (or equivalent) when `renderer is None` and prints no traceback.
- [ ] `_placeholder_renderer` deleted; 7 workflow.* schemas register with `renderer=None`; `phase_bridge_schema.py:13` no longer defines the function; `workflow_metadata.py:119` no longer imports it.
- [ ] `snapshot_compare.py` exists at `supekku/scripts/lib/blocks/metadata/snapshot_compare.py`; runnable via `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .`; harness output catalogued in `notes.md` under a P02 closure section. **Zero-disagreement gate moved to P02.5** per DR-118 §2 premise correction (six of seven hand-rolled validators are lax on extras; metadata declarations need fidelity widening before zero-disagreement is meaningful — that is P02.5 work, not P02 work). 18 malformed-YAML files logged separately as drift / backlog (informational only at P02 close).
- [ ] New unit tests added for: `additional_properties` semantics (5+ cases per DR-118 §5), `strict_unknown_keys` semantics (3+ cases), nested-object propagation (1+ case), renderer-Optional path (2 cases), harness self-tests (5 cases per DR-118 §5).
- [ ] `just check` passes (lint + tests).
- [ ] `uv run spec-driver validate` produces baseline-identical output (8 audit-gate warnings, modulo install-skew noise).
- [ ] OQ-HARNESS-PLACEMENT resolved (recorded in §9).
- [ ] No code changes outside the paths enumerated in DR-118 §4 "Phase 1 — Foundations" + new harness module + corresponding test files.

## 5. Verification

- **Tests** (new, per DR-118 §5 verification matrix):
  - `supekku/scripts/lib/blocks/metadata/validator_test.py` — `additional_properties` and `strict_unknown_keys` cases. Existing test file extends.
  - `supekku/scripts/lib/blocks/metadata/schema_test.py` (or wherever FieldMetadata `__post_init__` is currently tested) — relaxed object-type post-init.
  - `supekku/scripts/lib/blocks/schema_registry_test.py` (new or extended) — `renderer=None` `get_parameters()` short-circuit.
  - `supekku/cli/schema_test.py` — example-fallback skip when `renderer is None`.
  - `supekku/scripts/lib/blocks/metadata/snapshot_compare_test.py` (new) — synthetic agreement, disagreement detection, missing-block, malformed-YAML, `--root` arg.
- **Tooling**:
  - `just check` — full project lint + test gate.
  - `uv run spec-driver validate` — diff against `validate-baseline.txt`.
  - `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` — must emit zero disagreements.
  - `just pylint-files <changed-files>` — confirm no new pylint regressions on touched files.
- **Evidence to capture**:
  - Final harness output (zero disagreements) pasted into `notes.md` under a P02 closure section.
  - Updated `validate-baseline.txt`? **No** — baseline is delta-scoped and only re-captured on intentional drift; P02 must hit the existing baseline.

## 6. Assumptions & STOP Conditions

### Assumptions

- The 7 workflow.* schemas register their renderer **exclusively** through `_placeholder_renderer`; no production code reaches in and calls `.renderer(...)` on them at runtime. Verified during P01 grep: only `cli/schema.py:438,440` invoke `schema.renderer(...)`, and only via the example-display path. **If P02 implementation surfaces another caller, escalate via `/consult`.**
- The DR-118 §7 DEC-004 algorithm (declared-property pass + unknown-key pass at every recursion depth) is implementable purely inside `_validate_field`'s object branch + a top-level pass in `validate(data)`. No deeper changes to `_validate_fields` required. (Confirmed by reading `validator.py:88-111`.)
- Existing block-validation tests use the `MetadataValidator(metadata)` no-flag construction. New `strict_unknown_keys=True` behaviour does not surface in pre-existing tests. **Must confirm at first test run.**
- The harness can rely on `BLOCK_SCHEMAS` registry for block-type discovery (registry mutations during dev are picked up automatically per DR-118 §5). It does **not** need to hard-code a list of 8 metadata declarations.

### STOP when

- Any pre-existing test fails with default `strict_unknown_keys=False` after the validator change. Indicates the algorithm has not preserved loose behaviour. Escalate via `/consult`; do not proceed.
- ~~The harness reports a disagreement against this repo's `.spec-driver/` corpus before any retirement has shipped~~ — **TRIGGERED 2026-05-09**. Resolved via `/consult`: DR-118 §2 premise (uniform hand-rolled rejection) was wrong; six of seven hand-rolled validators are lax on extras. Resolution: insert IP-118-P02.5 (declaration fidelity) between P02 and P03; harness gate moves to P02.5 close. P02 closes with disagreements catalogued, not zero.
- A workflow.* renderer call site is found outside `cli/schema.py:438,440` — DR-118 §7 DEC-005's "no observable behaviour change" assumption breaks. Escalate.
- `additional_properties` validator integration touches `_validate_fields` instead of staying scoped to `_validate_field` — design assumption violated; confirm before proceeding.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 2.1 | `FieldMetadata.additional_properties` + relaxed `__post_init__` | no (foundation) | DEC-004 part 1 |
| [ ] | 2.2 | `MetadataValidator.strict_unknown_keys` flag + `_validate_field` object-branch extension + top-level unknown-key pass | no (depends on 2.1) | DEC-001 + DEC-004 part 2 |
| [ ] | 2.3 | VT for additional_properties + strict_unknown_keys + nested propagation | yes (after 2.2) | red/green TDD: write before 2.1/2.2 land |
| [ ] | 2.4 | `BlockSchema.renderer` Optional + `get_parameters()` None guard | yes (independent of 2.1–2.3) | DEC-005 part 1 |
| [ ] | 2.5 | Retire `_placeholder_renderer`; register 7 workflow.* with `renderer=None`; `cli/schema.py:425-447` None-guard | no (depends on 2.4) | DEC-005 part 2 |
| [ ] | 2.6 | VT for renderer-Optional + cli/schema.py fallback | yes (after 2.5) | small tests; pair with 2.5 |
| [ ] | 2.7 | `snapshot_compare.py` harness + module entrypoint + self-tests | yes (after 2.4 — registry-aware) | DEC-007; runs as `python -m …` |
| [ ] | 2.8 | Final gate: `just check`, harness against `.spec-driver/`, baseline-diff, commit | no (closure) | one closing commit (or 2 if 2.1–2.3 and 2.4–2.7 split naturally) |

### Task Details

- **2.1 `FieldMetadata.additional_properties` + relaxed `__post_init__`**
  - **Design / Approach**: Add `additional_properties: FieldMetadata | None = None` to the dataclass. Relax `__post_init__` line "object type requires properties": accept when `self.properties` truthy **or** `self.additional_properties is not None`. Update docstring.
  - **Files / Components**: `supekku/scripts/lib/blocks/metadata/schema.py`.
  - **Testing**: extend `schema_test.py` (or wherever `FieldMetadata.__post_init__` is currently tested — locate first) — three cases: object with `properties` only (existing behaviour), object with `additional_properties` only (new — must not raise), object with both (must not raise).
  - **Observations & AI Notes**: DR-118 §7 DEC-004 narrative is canonical. Watch for downstream consumers that destructure `FieldMetadata(...)` positionally — `additional_properties` is keyword-only in practice but the dataclass accepts positional. Adding it after `default_value` (currently last) keeps existing positional callers safe.
  - **Commits / References**: stage with 2.2; single commit "feat(DE-118): FieldMetadata.additional_properties + MetadataValidator.strict_unknown_keys".

- **2.2 `MetadataValidator.strict_unknown_keys` flag + algorithm extension**
  - **Design / Approach**:
    - `__init__(self, metadata: BlockMetadata, *, strict_unknown_keys: bool = False)`.
    - Top-level `validate(data)` adds an unknown-key pass after `_validate_fields(data, self.metadata.fields, "")`: for each key in `data` not in `self.metadata.fields`, append `ValidationError(path=key, message="unknown key")` when `strict_unknown_keys=True`. (No `additional_properties` at top level — DEC-004 explicitly punts on top-level dynamic-key blocks.)
    - `_validate_field` object branch (currently lines 184–196) replaced with the DR-118 §7 DEC-004 algorithm: declared-property pass → unknown-key pass; per-key route to `field_meta.additional_properties` validation when set, else strict-rejection when `self.strict_unknown_keys`.
  - **Files / Components**: `supekku/scripts/lib/blocks/metadata/validator.py`.
  - **Testing**: see 2.3.
  - **Observations & AI Notes**: `strict_unknown_keys` lives on the instance — recursion through `_validate_field` carries the flag automatically (calls `self._validate_field(...)`). Confirm via the propagation test (2.3).
  - **Commits / References**: same commit as 2.1.

- **2.3 VT for additional_properties + strict_unknown_keys**
  - **Design / Approach**: Red/green TDD — write tests FIRST, then 2.1 and 2.2 land them green. Cases (per DR-118 §5):
    - `additional_properties`: `properties` only (existing); `additional_properties` only; both; neither + strict → reject extra; neither + lax (default) → accept extra; nested `additional_properties` propagation through recursion.
    - `strict_unknown_keys`: top-level extra key rejected when True; accepted when False (default); top-level extra key with `additional_properties` set on the field metadata? — N/A for DE-118 (DEC-004 punts top-level dynamic).
    - Nested propagation: `level1.level2.unknown_key` rejected when `strict_unknown_keys=True` at constructor; `_SESSION_ENTRY`-shaped recursion case (synthetic, since live data is absent — see notes.md §2).
  - **Files / Components**: `supekku/scripts/lib/blocks/metadata/validator_test.py` (extend).
  - **Testing**: tests are the deliverable.
  - **Observations & AI Notes**: keep test names descriptive — these become the durable contract for DEC-004 semantics. Future drift will be caught here.
  - **Commits / References**: same commit as 2.1/2.2.

- **2.4 `BlockSchema.renderer` Optional + `get_parameters()` None guard**
  - **Design / Approach**: change type annotation to `Callable[..., str] | None`; default `None`. `get_parameters()` first line: `if self.renderer is None: return {}`. Update docstring.
  - **Files / Components**: `supekku/scripts/lib/blocks/schema_registry.py:14-49`.
  - **Testing**: see 2.6.
  - **Observations & AI Notes**: positional-arg callers of `BlockSchema(...)` exist (e.g. each `register_block_schema(..., BlockSchema(name=..., marker=..., version=..., renderer=..., description=..., metadata=...))`). All current sites pass `renderer=` positionally or as a keyword — adding `Optional` with a default doesn't break them. **But** dataclass field order matters: `renderer` is currently the 4th positional field. Default cannot precede non-default field. Currently field order is `name, marker, version, renderer, description, metadata`; `description` has no default but comes after; making `renderer` default-bearing requires either reordering (breaking change) or making `description` also default. Option: keep position, add default `= None`, **and** ensure `description` either also gets a default (`= ""`) or stays required keyword-only. Inspect all `BlockSchema(...)` call sites in 2.5 and decide before landing.
  - **Commits / References**: stage with 2.5; single commit "feat(DE-118): BlockSchema.renderer Optional; retire _placeholder_renderer".

- **2.5 Retire `_placeholder_renderer`; rewire 7 workflow.* schemas; `cli/schema.py` None-guard**
  - **Design / Approach**:
    - Delete `_placeholder_renderer` from `phase_bridge_schema.py:13` and the export.
    - In `workflow_metadata.py`: drop the `_placeholder_renderer` import (line 119); change the `_WORKFLOW_SCHEMAS` registration loop (line 165–183) to pass `renderer=None`.
    - In `cli/schema.py:425-447`: at the top of the renderer-fallback block, `if schema.renderer is None: console.print("[yellow]No example renderer available for this schema.[/yellow]"); return`. (Keep the metadata-first short-circuit at line 425 unchanged — it's already the dominant path for these schemas.)
  - **Files / Components**: `supekku/scripts/lib/blocks/phase_bridge_schema.py`, `supekku/scripts/lib/blocks/workflow_metadata.py`, `supekku/cli/schema.py`.
  - **Testing**: see 2.6.
  - **Observations & AI Notes**: pre-deletion grep `rg "_placeholder_renderer" supekku/` to confirm only the 2 sites + 1 self-definition (already done in P01 follow-up; refresh before delete).
  - **Commits / References**: same commit as 2.4.

- **2.6 VT for renderer-Optional + cli/schema.py fallback**
  - **Design / Approach**:
    - In `schema_registry_test.py` (extend or create): `BlockSchema(renderer=None).get_parameters() == {}`.
    - In `cli/schema_test.py`: invoking `show_schema` against a `renderer=None` schema does not raise; emits the documented "no example available" message (or whatever 2.5 settles on).
  - **Files / Components**: `supekku/scripts/lib/blocks/schema_registry_test.py` (extend), `supekku/cli/schema_test.py` (extend).
  - **Testing**: tests are the deliverable.
  - **Commits / References**: same commit as 2.4/2.5.

- **2.7 Snapshot-compare harness**
  - **Design / Approach**:
    - New module `supekku/scripts/lib/blocks/metadata/snapshot_compare.py`. CLI entrypoint via `if __name__ == "__main__":` + `argparse` → invocable as `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root <path>`.
    - Algorithm: walk `<root>/.spec-driver/` for `*.md` files; for each file, scan for known block markers (use `BLOCK_SCHEMAS` to enumerate); for each found block, dual-validate: hand-rolled validator (where one exists at this point in the migration — P02 has all 7 still active) **and** `MetadataValidator(BLOCK_SCHEMAS[type].metadata, strict_unknown_keys=True)`. Compare verdict-level (errors empty vs non-empty). Disagreements → exit non-zero with diff output.
    - Key design decision: for blocks whose hand-rolled validator takes ID kwargs (`delta_id`, `spec_id`), the harness must extract the parent ID from frontmatter (filename or `id:` field) and pass it. Sketched in notes.md §3.2 inventory — implementer reuses extractor pattern.
    - Self-tests in sibling `snapshot_compare_test.py`: synthetic agreement (handcrafted block + matching metadata both accept), disagreement (block that hand-rolled accepts but metadata rejects, e.g. unknown extra key with `strict_unknown_keys=True`), missing-block file (file with no marker → silently skip), malformed YAML (file with marker but invalid YAML → recorded as a separate failure category, not a "disagreement"), `--root` arg (run against a synthetic fixture directory, not just `.`).
  - **Files / Components**: new `supekku/scripts/lib/blocks/metadata/snapshot_compare.py`, new `supekku/scripts/lib/blocks/metadata/snapshot_compare_test.py`. **No** edits to existing modules.
  - **Testing**: harness self-tests + the gate "harness emits zero disagreements against this repo's `.spec-driver/`" at 2.8.
  - **Observations & AI Notes**:
    - **OQ-HARNESS-PLACEMENT resolution** — keep at `supekku/scripts/lib/blocks/metadata/`. STD-003 (utility module placement) targets cross-cutting utility sprawl across `core/` and `utils/`; this harness has heavy domain coupling (imports BlockMetadata, BLOCK_SCHEMAS, MetadataValidator) and is dev-tooling, not production. P04 review may flip this — relocation is a single `git mv` if so.
    - **OQ-HARNESS-LIFECYCLE** — defer to P04 per DR-118 §8. P02 ships the harness; P04 settles ownership / re-run trigger. P02 documentation in the module docstring should explicitly note "manual run only as of DE-118 P02; lifecycle owner TBD in P04".
    - Use existing block extractors (`extract_revision_blocks`, `extract_relationships`, etc.) where they exist; reach into `BLOCK_SCHEMAS` for schemas that don't have a dedicated extractor (workflow.*) — those are loaded via the metadata pipeline already.
  - **Commits / References**: separate commit "feat(DE-118): snapshot-compare harness for block-validator dual-validation".

- **2.8 Final gate + commit**
  - **Design / Approach**: run `just check`, `python -m supekku.scripts.lib.blocks.metadata.snapshot_compare --root .` (must report 0 disagreements), and `uv run spec-driver validate` (must equal `validate-baseline.txt`). Commit closes the phase.
  - **Files / Components**: `notes.md` updated with P02 closure section + harness output paste; phase-02 sheet ticked through; IP-118.md progress flag updated.
  - **Testing**: this is the gate — green = phase passes.
  - **Observations & AI Notes**: if any of the gates fail, the failing task remains open and the commit does not land. Per /execute-phase step 11, keep verification status fields current as code progresses.
  - **Commits / References**: closing commit "chore(DE-118): close IP-118-P02 — foundations landed".

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| **R-P02-1** Top-level unknown-key pass forgotten — DEC-004 algorithm only enforced inside `_validate_field` object branch, leaving block-level extras silently accepted. | Test in 2.3 for top-level extra key; explicit task split in 2.2 covering both top-level `validate(data)` and nested `_validate_field`. | open |
| **R-P02-2** Default-arg field order in `BlockSchema` dataclass blocks `renderer: ... \| None = None` because `description` (no default) follows. | Documented in 2.4 design; decide reorder vs default-on-`description` before 2.5 lands. | open |
| **R-P02-3** A workflow.* renderer call site exists outside `cli/schema.py:438,440` and would AttributeError when `renderer=None`. | P01 grep covered this; refresh in 2.5 before delete. STOP-condition documented (§6). | open |
| **R-P02-4** Snapshot harness scope creep — temptation to make it a general validation framework. | Keep tightly bounded: dual-validate today's 7 hand-rolled vs metadata; no validator-discovery DSL, no config file. P04 owns lifecycle (`OQ-HARNESS-LIFECYCLE`). | open |
| **R-P02-5** `__post_init__` relaxation accidentally allows a malformed `FieldMetadata(type="object")` (neither `properties` nor `additional_properties`) to construct. | Keep the validation: object type requires `properties` OR `additional_properties` (logical OR); reject when both are absent/empty. Test 2.3 covers the negative case. | open |
| **R-P02-6** `strict_unknown_keys` propagation through `additional_properties` recursion: when `additional_properties=<shape>`, unknown keys *match* the additional shape but inside that shape, nested `strict_unknown_keys` should still apply. | Algorithm in DR-118 §7 DEC-004 makes this implicit (recursion uses `self._validate_field`, which carries `self.strict_unknown_keys`). Test in 2.3 with a nested case. | open |

## 9. Decisions & Outcomes

- `2026-05-09` — **OQ-HARNESS-PLACEMENT resolved**: harness lives at `supekku/scripts/lib/blocks/metadata/snapshot_compare.py`, not `core/`. Rationale: heavy domain coupling (imports `BlockMetadata`, `BLOCK_SCHEMAS`, `MetadataValidator`) makes `core/` placement semantically wrong; STD-003 targets cross-cutting utility sprawl, not domain-coupled dev tooling; harness is dev-only, not production. P04 audit may revisit — relocation is a single `git mv`.
- `2026-05-09` — **`renderer=None` representation**: `BlockSchema.renderer` becomes `Optional` with `None` default; the `get_parameters()` short-circuit returns `{}`. Alternative considered: keep mandatory and pass an explicit `_NoRenderer` sentinel — rejected as more surface for no benefit.
- `2026-05-09` — **Top-level `additional_properties` punted**: DEC-004 explicitly does **not** add `additional_properties` to `BlockMetadata`. Rationale: no current schema needs top-level dynamic keys; ADR-009 argues against speculative structure. P02 implements `strict_unknown_keys` top-level rejection only.

## 10. Findings / Research Notes

P01 inventory (`../notes.md`) confirms:
- 7 hand-rolled validator classes are still wired into production parse paths during P02; harness has both sides to dual-validate against.
- Only `cli/schema.py:438,440` calls `schema.renderer(...)` at runtime — safe for Optional with a None guard.
- 2 parallel-test gaps for P03 (`relationships_metadata_test.py`, `tracking_metadata_test.py`); not P02 work.

P02 design touches `metadata/schema.py`, `metadata/validator.py`, `schema_registry.py`, `phase_bridge_schema.py`, `workflow_metadata.py`, `cli/schema.py`, plus 2 new files (`snapshot_compare.py` + test). All paths match DR-118 §4 "Phase 1 — Foundations" exactly.

Surface area: ~6 modules edited, ~2 new modules, ~50–80 new test cases. Mechanism-only — no semantic changes for existing call sites (default flag values preserve current behaviour). Verdict-equivalence verified by harness run against repo at 2.8.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied (all items in §4).
- [ ] Verification evidence stored (harness output appended to `../notes.md`; `just check` log not stored — passes/fails determined at run).
- [ ] Spec/Delta/Plan updated: IP-118 progress flag for P02 ticked; phase-02 sheet status `draft` → `completed`; OQ-HARNESS-PLACEMENT marked resolved in DR-118 (or noted in notes.md if DR-118 amend is heavy).
- [ ] Hand-off note to IP-118-P03 in `../notes.md` final paragraph: "P02 foundations landed; mechanism in place. P03 may begin per DR-118 §4 ordering (VerificationCoverageValidator first)."
