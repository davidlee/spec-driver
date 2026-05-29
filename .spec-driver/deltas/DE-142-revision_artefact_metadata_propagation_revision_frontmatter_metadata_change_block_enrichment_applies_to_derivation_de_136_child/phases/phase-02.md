---
id: IP-142-P02
slug: "142-revision_artefact_metadata_propagation_revision_frontmatter_metadata_change_block_enrichment_applies_to_derivation_de_136_child-phase-02"
name: IP-142 Phase 02 — FM completion + applies_to derivation
created: "2026-05-29"
updated: "2026-05-29"
status: draft  # one of: completed | deferred | draft | in-progress | pending
kind: phase  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
plan: IP-142
delta: DE-142
---

# Phase 2 — FM completion + applies_to derivation

## 1. Objective

Bring revision frontmatter + scope derivation to delta/audit parity, **additively**:

1. Complete `REVISION_FRONTMATTER_METADATA` (DE-137 stub → full class).
2. Derive `applies_to` from the `supekku:revision.change@v1` block at load
   (`kind == "revision"`), never storing it (DEC-138-10).

Both moves are application-code only (DR-136 §11.1). No DE-118 block reshape,
no `@v2`, no migration (that is P04). Strict mode stays off for revisions until
the P04 flip — P02 changes the *class definition* and the *derivation*, neither
of which rejects legacy corpus keys in tolerant (default) mode.

## 2. Links & References

- **Delta**: DE-142
- **Design Revision Sections**: DR-142 §5 (FM completion), §6 (`applies_to`
  derivation), §13.2 (`applies_to.specs` composition — **resolved narrow, see §9**),
  §13.5 (FM-beside-block check — **resolved MINOR, see §9/§10**); DEC-142-05/06.
- **Specs / PRODs**: PROD-004.FR-001 (FM completion), PROD-004.FR-002 (derivation/strict).
- **Support Docs**:
  - `core/frontmatter_metadata/revision.py` (the DE-137 stub to complete)
  - `core/frontmatter_metadata/audit.py` (precedent — construction shape)
  - `core/frontmatter_metadata/base.py` (`BASE_FRONTMATTER_METADATA`: the field source)
  - `core/frontmatter_metadata/audit_test.py` (test precedent — `_BASE`/`_new_errors`)
  - `changes/artifacts.py` (`_derive_applies_to` :29; `load_change_artifact` :185)
  - `blocks/revision.py` (`extract_revision_blocks` — returns a **list**)
  - `blocks/metadata/validator.py` (:128-134 strict unknown-key check — generic)

## 3. Entrance Criteria

- [x] P01 complete (engine + block conditional rules shipped; suites green)
- [x] DR-142 §5/§6 approved; narrow decisions locked (DEC-CONSULT-01/02, user-approved 2026-05-29)
- [x] Owning delta DE-142 `in-progress`

## 4. Exit Criteria / Done When

- [ ] `REVISION_FRONTMATTER_METADATA` declares **narrow** field set: Base 7
      (status = revision enum + aliases) + `relations` (plain) + `tags` +
      `ext_id` + `ext_url`; no `revision_links` projection (DEC-142-06)
- [ ] `_derive_revision_applies_to` derives `specs` ← `sorted(set(block.specs[].spec_id))`,
      `requirements` ← `sorted(set(block.requirements[].requirement_id))`; multi-block union;
      block-first with FM-fallback only when no block
- [ ] `load_change_artifact` hooks the deriver for `kind == "revision"`; FM scope
      keys no longer read; `applies_to` runtime-only (never persisted)
- [ ] VT-142-FM-001/002 + VT-142-DERIVE-001/002 pass
- [ ] R-142-04 verified resolved with **zero** kind-specific check code (the generic
      `validator.py:128` strict check is armed for revision by the declared field set)
- [ ] Existing suites green (regression: `audit_test`, `artifacts_test`, `validator`);
      RE-042 still loads under tolerant mode
- [ ] `just lint` zero warnings; `just pylint-files` on touched files no new warnings

## 5. Verification

- Targeted (default terminal width): `core/frontmatter_metadata/revision_test.py`,
  `core/frontmatter_metadata/audit_test.py` (regression), `changes/artifacts_test.py`,
  `blocks/metadata/validator_test.py`.
- **VT-142-FM-001**: narrow FM accepts Base 7; +`relations` `[{type,target}]`;
  +`tags`; +`ext_id`/`ext_url`; +status alias canonicalises → `errors == []`.
- **VT-142-FM-002**: under strict, each cut key rejected as unknown. **NARROW set**:
  `source_specs`, `destination_specs`, `requirements`, `aliases`, `lifecycle`,
  `auditers`, `source`, `owners`, `summary`.
- **VT-142-DERIVE-001**: `_derive_revision_applies_to` → sorted-unique `specs` +
  `requirements`; block shadows FM; FM-fallback when no block; both-absent → `{}`;
  multi-block union. Plus one integration leg via `load_change_artifact` on an
  RE-042-shaped `tmp_path` fixture (proves the `kind=='revision'` hook fires).
- **VT-142-DERIVE-002**: FM carrying `applies_to`/`source_specs`/etc. *beside* a
  block → strict ValidationError on the offending key; **same data tolerated under
  `strict=False`** (proves it is the strict-flip gate, DEC-138-10 transition window).
- Evidence: test run output appended to §10.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - Narrow = DR §5 table exactly: Base 7 + `relations` + `tags` + `ext_id` + `ext_url`.
    `owners`/`summary`/`lifecycle`/`auditers`/`source` are **omitted** from the
    declared field set (zero corpus uses them — verified 2026-05-29 — so narrow is
    lossless here).
  - The generic strict unknown-key check (`validator.py:128-134`) already covers
    `kind:revision` once the field set omits the scope keys (R-142-04 resolved MINOR).
  - `extract_revision_blocks` returns a **list** → the deriver must union across all
    blocks, not copy delta's single-block path.
  - P02 introduces **no strict default** → legacy corpus keys keep loading under
    tolerant mode until P04.
- **STOP when**:
  - Completing the class rejects RE-042 (or any corpus revision) under **tolerant**
    mode → a strict default leaked; do not flip strict here.
  - The deriver needs to read requirement-level destination/origin to satisfy
    `applies_to.specs` → that is the *wide* §13.2 reading we rejected; re-confirm
    before widening.
  - R-142-04 turns out to need a kind-specific check path (it should not) → `/consult`
    before adding one; that would contradict the resolved MINOR verdict.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | ----------- | --------- | ----- |
| [ ] | 2.1 | Write `revision_test.py` FIRST (RED): VT-142-FM-001 valid cases + VT-142-FM-002 cut-key (narrow set) + VT-142-DERIVE-002 strict/tolerant legs | [ ] | mirror `audit_test.py:20-34`; cut-key set as one module constant |
| [ ] | 2.2 | Complete `REVISION_FRONTMATTER_METADATA` (narrow, explicit key picks from BASE; status enum replace; drop stub docstring; add examples — declared-valid fields ONLY) | [ ] | GREEN FM-001/002/DERIVE-002; additive, no block touch |
| [ ] | 2.3 | Add `_derive_revision_applies_to(blocks, frontmatter)` (narrow; sorted(set); multi-block union; block-first/FM-fallback) | [ ] | RED first via DERIVE-001 matrix; do NOT generalise `_derive_applies_to` |
| [ ] | 2.4 | Hook `elif kind == "revision":` in `load_change_artifact` (try/except ValueError like delta) | [ ] | applies_to runtime-only; no `_derive_revision_link_relations` (delta-only) |
| [ ] | 2.5 | DERIVE-001 integration leg: RE-042-shaped `tmp_path` fixture through `load_change_artifact` | [P] | block shadows FM scope keys |
| [ ] | 2.6 | Verify `__init__.py` needs no change; lint + targeted suites green; RE-042 tolerant-load check; pin terminal width on any wrapped/truncated assertion | [ ] | width-brittle suite (see §10) |

### Task Details

- **2.1 Tests first (RED)**
  - **Design / Approach**: mirror `audit_test.AuditFrontmatterValidationTest` —
    `_BASE` = 7 required fields (`id=RE-001`, `kind=revision`, `status=draft`,
    ISO `created`/`updated`); `_new_errors(data)` = `[str(e) for e in
    MetadataValidator(REVISION_FRONTMATTER_METADATA).validate(data, strict=True)]`.
    FM-001 asserts `errors == []` for the valid variants (optionally dual-validate
    against legacy `validate_frontmatter` as `audit_test` does). FM-002 iterates the
    **narrow** cut-key constant asserting each appears in a strict "unknown key"
    error. DERIVE-002 adds the `strict=False` tolerance leg on the same data.
  - **Files**: `core/frontmatter_metadata/revision_test.py` (NEW).
  - **Footgun**: do NOT copy `audit.py:301`'s example verbatim — it includes a cut
    key (`findings`); FM examples are illustrative, not class-validated. Keep
    revision examples to declared-valid fields only.

- **2.2 Complete the FM class (narrow)**
  - **Design / Approach**: keep `version=1`,
    `schema_id="supekku.frontmatter.revision"`. Build `fields` by **explicit picks**
    from `BASE_FRONTMATTER_METADATA.fields` (`id,name,slug,kind,created,updated,
    relations,tags,ext_id,ext_url`) + `status` via `replace(..., type="enum",
    pattern=None, enum_values=REVISION_STATUS_ENUM_VALUES,
    aliases=REVISION_STATUS_ALIASES)` (already correct at revision.py:33-39). Do
    **not** `**BASE...fields` splat (that would re-admit `lifecycle/auditers/source/
    owners/summary`). Update docstring (drop "stub / DE-142 scope"). Add `examples`
    (minimal RE-001 + one richer with relations/tags/ext_id).
  - **Files**: `core/frontmatter_metadata/revision.py`.

- **2.3 / 2.4 / 2.5 applies_to derivation + hook**
  - **Design / Approach**: `_derive_revision_applies_to(blocks, frontmatter)` mirrors
    `_derive_applies_to` (artifacts.py:29-65) but unions over the block **list**:
    `specs = sorted({b.parse()['specs'][i]['spec_id'] ...})`, `requirements =
    sorted({... requirement_id ...})`. Block-first; FM-fallback only when no block
    (transition window). In `load_change_artifact`, add `elif kind == "revision":`
    beside the delta branch (artifacts.py:185), wrapping extraction in
    `try/except ValueError`. FM `source_specs/destination_specs/requirements` no
    longer read for revisions. **No** `_derive_revision_link_relations` projection
    (DEC-142-06 — that is delta-only).
  - **Files**: `changes/artifacts.py`, `changes/artifacts_test.py`.

- **2.6 Verify + lint**
  - **Files**: `core/frontmatter_metadata/__init__.py` (verify only — registry maps
    revision→class at :52, export at :84), `revision.py`, `revision_test.py`,
    `artifacts.py`, `artifacts_test.py`.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Class completion leaks a strict default → rejects corpus under tolerant mode | RE-042 tolerant-load assertion in 2.6; validator only rejects under `strict=True` (validator.py:128) | design |
| Deriver copies delta's single-block path, drops multi-block specs | DERIVE-001 multi-block union case; `extract_revision_blocks` returns a list (verified) | design |
| Width-brittle suite masks/falses a failure | Run targeted tests at default width; pin `COLUMNS` or assert width-independent substrings on any wrapped/truncated output (§10) | design |
| Premature generalisation of `_derive_applies_to` | Keep the revision deriver local (2 call sites, different block shapes — POL-001/no-premature-abstraction) | design |

## 9. Decisions & Outcomes

- `2026-05-29` — **DEC-CONSULT-01 (narrow FM shape)**, user-approved. Declared field
  set = DR §5 table exactly (Base 7 + relations + tags + ext_id + ext_url); omit
  lifecycle/auditers/source/owners/summary. **Zero corpus lossage** — verified none
  of the 42 revisions carry those keys. VT-142-FM-002 asserts the full narrow cut set.
- `2026-05-29` — **DEC-CONSULT-02 (narrow applies_to.specs)**, user-approved. Per
  DR §6: `specs` from `block.specs[].spec_id` only; the source/destination split the
  list columns (P03) need is recomputed independently, not folded into derived scope.
  Deterministic `sorted(set(...))` both keys.
- `2026-05-29` — **R-142-04 resolved MINOR** (recon-verified). The FM-beside-block
  strict check needs **no** bespoke/kind-specific code: `validator.py:128-134` is a
  generic declared-fields unknown-key check, revision is already registered
  (`__init__.py:52`), and `get_strict_map` reads `[validation.strict].revision`
  generically. VT-142-DERIVE-002 verifies this rather than any new code path.

## 10. Findings / Research Notes

- **Corpus FM survey (42 revisions, 2026-05-29)**: top-level keys present =
  `id,name,slug,kind,status,created,updated,relations,aliases,destination_specs(40),
  requirements(34),source_specs(12)`. **None** carry
  `lifecycle/auditers/source/owners/summary` → narrow is lossless.
- **Baseline (read-only, recon-confirmed)**: targeted suite 1298 passed / 0 failed at
  default width. The "3 pre-existing failures" decompose: `show_test.py::
  test_path_and_json_mutually_exclusive` is caused by a stray untracked
  `.spec-driver/deltas/.spec-driver/` telemetry dir (DEC-CONSULT-08, deletion pending
  user OK); the two `ListDeltasMalformedFrontmatterTest` failures are **terminal-width
  wrap artifacts** (pass at `COLUMNS=400`), not telemetry. The suite is brittle in
  **both** directions (narrow breaks `list_test` wrap asserts; wide breaks formatter
  truncation asserts). None touch P02 unit suites.
- **Block patterns (P04 preview, NOT this phase)**: the `supekku:revision.change@v1`
  block patterns are SPEC-only (`^SPEC-\d{3}...`) while the sibling **delta** block
  uses `pattern=r".+"`. The revision corpus pervasively references `PROD-*` (a
  first-class spec), `ADR-*`, `ISSUE-*`, `NF-`. Strict would drift-track ~38/42
  legitimately-structured records. This is a **genuine P04 decision** (DEC-CONSULT-03/04),
  deferred — bring a concrete pattern proposal + before/after YAML when planning P04.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored (§10)
- [ ] DR-142/IP-142 updated if approach shifted
- [ ] Hand-off note to P03 (list enrichment — needs the derived summary + RE-042 fixture)
