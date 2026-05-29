# Notes for DE-142

## Session 2026-05-29 (7) — P04 execution: group A (patterns) done; group B obstacle

### Done — group A (broaden + share ID patterns), TDD
- **NEW `blocks/id_patterns.py`** (NOT `blocks/metadata/patterns.py`). STD-003 resolution:
  callers (`revision_metadata.py`, `verification_metadata.py`) live at `blocks/` level;
  `blocks/metadata/` is the generic validation engine (domain-agnostic). ID regexes are
  domain-specific → `blocks/` level, alongside the `yaml_utils.py` precedent. Phase §6 STOP
  condition anticipated this ("follow STD-003").
  - `REQUIREMENT_ID_PATTERN = r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NF|NFR)-[A-Z0-9.-]+$"`
  - `SPEC_ID_PATTERN = r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*$"`
- **revision_metadata.py**: replaced 6 REQUIREMENT copies (was `^SPEC-\d{3}...(FR|NFR)...`) +
  3 SPEC copies (`^SPEC-\d{3}...`) with the shared constants. RE-/DE-/AUD- patterns untouched.
- **verification_metadata.py**: dropped its local `REQUIREMENT_ID_PATTERN` (`(SPEC|PROD)...(FR|NFR)`
  — missed NF/ISSUE) → imports the share. SUBJECT/VERIFICATION/PHASE patterns stay local.
- **VT-142-PATTERN-001** (`blocks/id_patterns_test.py`, 17 cases): accepts SPEC/PROD/ISSUE +
  FR/NF/NFR + dotted suffix + segmented container; rejects ADR, too-few-digits, bare-spec-as-req,
  requirement-form-as-spec, empty. No pre-existing test encoded the SPEC-only bug (grep clean).
- Evidence: `blocks/` suite 568 pass; targeted 91 pass; ruff/ty clean; pylint 10.00/10, 0 msgs.

### Group B OBSTACLE (must /consult before synthesis) — ADR in source_specs
DR §8 step 4 says synthesise `specs[]` from `source_specs ∪ destination_specs`. But the corpus
FM-only records carry **`source_specs: [ADR-007]`/`[ADR-008]`** (RE-035/034/033/031/032/029).
`SPEC_ID_PATTERN` deliberately excludes ADR (ADRs are decisions, not specs) → emitting
`spec_id: ADR-007` yields an INVALID synthesised block → the post-migrate `--strict` we're
chasing would fail. The P04 consult evidence ("no ADR refs") was about *requirements*, missed
`source_specs`. Also RE-028 is source≠dest both-real (PROD-011→PROD-002, looks like a move but
DEC-142-09 mandates `modify`). Need a focused decision on what `specs[]` is synthesised from.

### DEC-142-12 (consult, 2026-05-29) — synthesise `specs[]` from `destination_specs` only
User chose Opt 1 (recommended). Synthesised `specs[]` = one `{spec_id, action: updated}` per
`destination_specs` id; **`source_specs` dropped entirely** (it is origin data — consistent with
DEC-142-09's omit-origin; ADR-* sources have no valid block home; matches existing complete-delta
synthesis which emits dest-only `spec_id`). Differs from DR §8's literal "source ∪ dest union" on
exactly one record (RE-028 PROD-011 source dropped). `requirements[]` unchanged from plan: one
`modify` entry per FM requirement, `destination.spec` = requirement container, `kind` from FR/NF
token, no lifecycle/origin. **Updates DR §8 step 4.**

### Done — group B (v0_10_0_005 migration step), TDD
- **NEW `spec_driver/migrations/v0_10_0_005_revision_metadata/{__init__,migration,migration_test}.py`**
  mirroring v004. `RevisionMetadataStep(applies_to_kind="revision")`. `_transform`: cut
  `_CUT_KEYS = {lifecycle, aliases, auditers, source, source_specs, destination_specs, requirements}`;
  FM-only (no block) + scope present → synthesise `supekku:revision.change@v1` block:
  `specs[]` from `destination_specs` (DEC-142-12), `requirements[]` action=modify, kind from
  FR/NF token, `destination.spec` = requirement container, no lifecycle/origin (DEC-142-09);
  block-wins (no re-synth); idempotent; `drift_entries=[]` always (DEC-142-10). Isolation honoured
  (stdlib + `_helpers` + `_protocol` + pyyaml; frozen-local `_MARKER/_SCHEMA/_VERSION/_CUT_KEYS`).
  `applies_to` scans FM-only (split_frontmatter on head) so a migrated block's body `requirements:`
  doesn't false-positive. VT-142-MIGRATE-001..004 + edges = 24 pass.

### DEC-142-13 (consult, 2026-05-29) — fix two pre-existing orchestrator bugs in `migrate.py`
Discovered at the dry-run: `admin migrate revision --dry-run` reported "would touch 0" though 40
records need cutting. Root cause = TWO defects in `presentation/cli/admin/migrate.py`:
1. **`_kind_files` kind-matcher didn't strip a trailing `# comment`** → records stamped
   `kind: revision  # one of: ...` (RE-041, RE-042) were invisible to the sweep → they'd keep FM
   keys and **fail strict after the flip**. Fixed: `value.split("#",1)[0].strip().strip("'\"")`.
   (Latent for ALL kinds; prior delta/spec/prod/audit sweeps may have silently skipped commented
   records too — watermark is past them so not auto-re-run. Out of DE-142 scope; candidate issue.)
2. **dry-run touch-count summed `results`** (empty during dry-run) **instead of `previews`** →
   always printed 0. Fixed: sum `previews`. Cosmetic but made dry-run useless for VA evidence.
User approved fixing both (recommended) over hand-fixing 2 records. Tests: `TestKindFiles` (2) +
`TestDryRunCount` (CLI-level, asserts "would touch 1"). Full migrations + admin suites: 201 pass.
ruff/format clean; pylint 0 new (import-outside-toplevel are pre-existing deferred imports); ty 5
pre-existing tomlkit `Item` false-positives (lines 180/538-540, untouched).

### Group C — NOT verify-only; `create revision` was emitting legacy FM (DEC-142-14/15)
The phase assumed the template+creation were already narrow+block-canonical. WRONG: the
`revision.md` template IS narrow, but `create_revision` (`changes/revision_creation.py`) ignored
the `{{ revision_change_block }}` placeholder AND injected hand-rolled FM keys (aliases/
source_specs/destination_specs/requirements) → a freshly-created revision FAILED strict.
- **DEC-142-14 (consult)**: fix `create_revision` to emit narrow FM + render the canonical block
  via the existing `blocks/revision.render_revision_change_block` (specs from destination,
  requirements as `modify`, DEC-142-09/12). Live `create revision` now validates `--strict` clean.
  Also dropped the dead `--source`/`source_specs` (no block home under modify-only; separable from
  consolidation — approved block design carries no source). Fixed stale test-fixture template
  (`creation_test._make_repo` revision.md lacked the placeholder).
- **DEC-142-15 (consult)**: `create_completion_revision` (complete-delta path) appends its OWN
  richer lifecycle-bearing block → would DOUBLE with create_revision's new block. User: consolidate
  to a single block author is right BUT defer to after handover. NOW: add `render_change_block: bool
  = True` to create_revision; completion passes `False` (keeps its rich block as sole author, zero
  output change). Consolidation (create_revision = single canonical renderer, drop completion's
  `_render_revision_change_block`) filed as **ISSUE-062**.
- **Cleanup**: removed stray `RE-044-test_revision` (this-session machine junk per events.jsonl
  `eb74cb09`; `create revision "Test Revision"` with legacy shape, never tracked — would have
  corrupted the group-D sweep). Not recreated by any test (only `--help` is invoked in-tree).

## Session 2026-05-29 (6) — P04 consult (migration design locked)

P04 is the consult gate, not a mechanical phase. Ran a 4-agent read-only evidence
workflow (`de-142-p04-consult-evidence`) to ground the open decisions, then consulted.
**The evidence corrected the handover's central claim** and reshaped DR §8.

### Evidence (verified against current code/corpus, supersedes some recon claims)
- **Block ID patterns are NOT uniformly "SPEC-only".** Each field carries a
  kind-appropriate regex. The killer is `requirements[].requirement_id`
  (`revision_metadata.py:206`): `^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$`
  (+ 6 sibling copies at :99/:109/:119/:129/:275 and `destination.requirement_id`).
- **97 legitimate refs across ~24 records violate it** on two axes: (1) container
  prefix `PROD-*`/`ISSUE-*` (first-class spec-likes), not `SPEC-`; (2) requirement
  token `NF-` (and dotted suffix `FR-016.001`), not `(FR|NFR)`. **99 `NF-`
  requirements exist repo-wide** vs 437 `FR-` — `NF` is canonical, never matched.
- **Handover's `r".+"` delta-block claim was WRONG.** `DELTA_RELATIONSHIPS_METADATA`
  declares **NO** ID patterns (type=string only). The `r".+"` lives in
  `delta.context_inputs`/`risk_register` (different blocks). So the closest sibling
  runs pattern-free.
- **A partial canonical constant already exists, unused here:**
  `verification_metadata.py:22` `REQUIREMENT_ID_PATTERN = ^(SPEC|PROD)-\d{3,}...(FR|NFR)...`.
  Revision hardcodes SPEC-only ×7 (POL-001 dup). Even this constant misses `NF`/`ISSUE`.
- **`lifecycle` + `lifecycle.status` are both `required=False`** (`:297`,`:302`).
- **Zero corpus blocks use `action: move`** — 27 blocks are all `modify` (the
  `updated` counts are the separate `specs[].action` enum). FM-only records carry
  `source_specs == destination_specs` (in-place) or dest-only. So DR §8's
  synthesise-as-`move` is unimplementable (move requires `origin`, which nothing has).
- **DEC-05 confirmed**: `write_drift_ledger`/`_next_drift_id` are bespoke to
  `migrations/spec_requirements/migration.py:346`, called only by `migrate_requirements.py`.
  Generic `admin migrate` orchestrator captures `StepResult.drift_entries` but **never
  writes DL files** (only a per-run log). Mechanism architecturally incomplete.

### User decisions (consult, 2026-05-29) — all 4 ratified
- **DEC-CONSULT-04 → BROADEN to shared patterns.** Hoist/extend two shared constants
  and reuse across revision + verification blocks (POL-001, kills the dup + the latent
  NF bug):
  - `REQUIREMENT_ID_PATTERN = ^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NF|NFR)-[A-Z0-9.-]+$`
  - `SPEC_ID_PATTERN = ^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*$` (for `specs[].spec_id`,
    `destination.spec`, `destination.additional_specs[]`).
  - `RE-`/`DE-`/`AUD-` patterns (`metadata.revision`, `lifecycle.introduced_by/
    implemented_by/verified_by`) stay — they're correct.
  - F-F-safe: pure relaxation (no previously-valid block becomes invalid; not a `@v2`).
  - Rationale beats narrow/strict default: narrow here = MASSIVE real lossage (97 legit
    records) → the standing rule itself points to loosening.
- **DEC-CONSULT-03 → DISSOLVED. Synthesise `action: modify`, OMIT `lifecycle`.** No
  `unknown` value, no touching shared `REQUIREMENT_STATUSES` (3-5 consumers), R-142-02
  leak gone. **Supersedes approved DEC-142-04's `unknown` tolerated_alias** (ratified).
- **DEC-CONSULT-05 → NO auto-drift in this migration. Backlog the gap = ISSUE-061.**
  Broadened patterns + faithful modify-synthesis is a lossless reformat, not
  spec-vs-reality divergence → no drift entries warranted. Residual strict errors
  (expected ~0) dispositioned manually. Don't build the orchestrator drift helper
  speculatively in DE-142 (write-less / YAGNI).
- **DEC-CONSULT-07 → manual `[validation.strict].revision = true` AFTER
  VA-142-CORPUS-001 disposition**, decoupled from the migrate run (DR-136 §11.2 order).

### DR §8 corrections (ratified — see DR-142 §8/§12/§13 updates this session)
1. Synthesis action `move` → **`modify`**; `origin` from source_specs → **dropped**;
   `lifecycle.status: unknown` → **lifecycle omitted**.
2. Per-record drift emission → **removed** (no synthesis drift; manual residual).
3. Add pattern-broadening as work item (was implicit/absent).

### Done (planning) — phase-04 authored + committed
- Consult outcomes recorded (DR-142 §8/§12/§13, IP-142 §4/§8, this notes session) — commit `d576d446`.
- ISSUE-061 filed (orchestrator drift-write gap, DEC-142-10) — commit `d576d446`.
- `phases/phase-04.md` authored (10 tasks, 4 groups, TDD) + validated clean — commit `abe80b42`.
- Two more verified facts captured for execution: (1) `supekku/templates/revision.md` is
  ALREADY narrow (base FM + `{{ revision_change_block }}`) → template work is verify-only;
  (2) migration steps auto-discover by folder (`_discover_steps` iterates `migrations/`) →
  creating `v0_10_0_005_revision_metadata/` registers it, no `_registry` edit.

### What's next
- **`/execute-phase` for IP-142-P04** (TDD per phase-04 §7). Groups A→D in order:
  A broaden+hoist ID patterns (shared `blocks/metadata/patterns.py`, reuse in
  revision+verification); B `v0_10_0_005` migration step (mirror v004, isolation strict,
  no drift); C template verify; D sweep + manual strict flip. **STOP + /consult** if the
  post-migrate `--strict` shows residual NOT explained by the broadened patterns (§6).

## Session 2026-05-29 (5) — P03 executed (list revisions enrichment)

### Done (TDD)
- **Domain** `changes/revision_check.py` (NEW): `RevisionChangeSummary(sources,
  destinations, requirements)` + cell methods + `revision_change_summary(artifact)`.
  sources ← `requirements[].origin[].ref` (kind=spec); destinations ←
  `requirements[].destination.spec`; requirements ← `requirement_id`. Sorted+deduped,
  tolerant load, multi-block union. Mirrors `audit_check.AuditFindingsSummary`.
- **Columns** `REVISION_COLUMNS` (ID, Name, Status, Source, Destination, Requirements).
- **Formatter** `format_revision_list_row/json/table` (`change_formatters.py`). Strips
  `"Spec Revision - "` name prefix. **Adaptive Source-hide** (DEC-CONSULT-06, user-approved):
  Source column dropped in the TABLE view when no revision has an origin; TSV + JSON keep
  the full schema. `RevisionChangeSummary` imported top-level (no cycle → cleaner than the
  audit inner-import mirror).
- **CLI** `list_revisions` wired thin: `{r.id: revision_change_summary(r)}` +
  `format_revision_list_table` (replaced generic `format_change_list_table`). Filters kept.

### User decision this session
- **DEC-CONSULT-06 → adaptive Source column** (not fixed 6-col, not dropped). User asked
  "can we cheaply hide it if no non-nil values?" — yes (~mirrors `show_external` pattern).

### Verification
- VT-142-LIST-001/002/003/004 + adaptive-hide: 82 targeted pass. Live `list revisions`:
  Source HIDDEN (corpus has zero origins), Destination/Requirements populated; `--json`
  stable schema. Regression (cli/list + changes + formatters): 770 passed, only the 2
  pre-existing width-wrap delta-list failures. ruff/ty clean; pylint net **+1** (one
  `too-complex` on `format_revision_list_table`, McCabe 12 == its `format_audit_list_table`
  sibling — faithful mirror; no new message types). Phase-03 validated + `completed`;
  IP §6 VT-142-LIST-* → verified, §9 P03 checked.

### Housekeeping
- Stray untracked telemetry dirs (`.spec-driver/deltas/.spec-driver/run/` + the DE-142
  bundle one) **deleted** (user-approved) → `show_test::test_path_and_json_mutually_exclusive`
  now passes (pre-existing failures: 3 → 2, both width-wrap). Underlying CWD-resolution bug
  filed as **ISSUE-060**.

### Future DRY (noted, not done)
- `format_revision_list_table` + `format_audit_list_table` share an identical row-cell
  styling loop (id/status markup). Extracting `_styled_change_cell` would drop both below
  the `too-complex` threshold. Out of P03 scope (touches audit).

---

## Session 2026-05-29 (4) — P02 executed (FM completion + applies_to derivation)

### Done (TDD red→green→refactor)
- **FM class** (`core/frontmatter_metadata/revision.py`): completed the DE-137 stub to
  the NARROW shape via explicit BASE key-picks (id,name,slug,kind,status,created,
  updated,relations,tags,ext_id,ext_url) — NOT a `**BASE` splat (which would re-admit
  the universal-cut keys). `status` enum-replaced; docstring de-stubbed; 2 examples.
- **`kind` enum pinned to `["revision"]`** — surfaced at RED: the shared BASE `kind`
  enum OMITS `revision` (lists `design_revision`, not RE-* `revision`). Latent
  pre-existing bug (never tripped — revision strict validation isn't on). Fixed
  locally (no shared-BASE widening). Left the BASE omission as an observation.
- **applies_to deriver** (`changes/artifacts.py`): `_derive_revision_applies_to(blocks,
  frontmatter)` — unions `specs[].spec_id` / `requirements[].requirement_id` across all
  blocks (`extract_revision_blocks` returns a list), `sorted(set())`, block-first /
  FM-fallback, per-block `parse()` tolerant skip. Hooked `elif kind == "revision":` in
  `load_change_artifact`. Kept local (POL-001 — 2 call sites, different block shapes).
- **R-142-04 confirmed MINOR**: no kind-specific check code; the generic
  `validator.py:128` declared-fields unknown-key check is armed for revision by the
  narrow field set alone. VT-142-DERIVE-002 proves it (strict error / strict=False ok).
- **Tests**: `revision_test.py` (FM-001/002 + DERIVE-002); 8 deriver cases + RE-050
  integration leg in `artifacts_test.py` (DERIVE-001). 37 targeted + 9 subtests pass.

### Verification evidence
- Full `pytest supekku`: **5244 passed, 4 skipped**; only the **3 known pre-existing
  failures** (2 width-wrap `ListDeltasMalformedFrontmatterTest`; 1 stray-telemetry
  `show_test::test_path_and_json_mutually_exclusive`). Zero new.
- ruff check/format + ty clean on touched files; whole-repo `ruff check` passes.
  pylint **net-improved**: `use-implicit-booleaness-not-comparison` 4→0 (fixed my 2 +
  4 pre-existing); zero new message types. `load_change_artifact`'s pre-existing
  `too-complex`/`too-many-*` (present at HEAD) nudged by the 1-line `elif`, count
  unchanged — left as pre-existing observation.
- `validate file phase-02.md`: clean. Phase-02 → `completed`. IP §6 coverage
  VT-142-FM-001/002 + DERIVE-001/002 → `verified`; IP §9 P02 checked.

### Handoff → P03 (list enrichment)
- Reuse `_rev_block(data)` fixture helper (artifacts_test.py) + RE-042/RE-040 corpus.
- The source/destination SPLIT (origin vs `destination.spec`) is recomputed in
  `changes/revision_check.py` (NEW), NOT read from `applies_to` (which is the deduped
  union). `RevisionChangeBlock.parse()` is on-demand.
- **Open UX consult (DEC-CONSULT-06)**: `list revisions` columns — Source is empty for
  all 42 current records. Bring the rendered mockup before wiring the formatter.
- P03 work is parallelisable (domain summary / column_defs / formatter / CLI / 4 list
  tests) → candidate for a small implementation workflow.

### Deferred (unchanged)
- P04 block-pattern + `unknown`-enum decisions (DEC-CONSULT-03/04), drift-write
  mechanism (05), flip timing (07), stray-dir deletion (08) — bring at P03/P04.

---

## Session 2026-05-29 (3) — recon workflow + P02 planning + consult

### Done
- **Recon workflow** (`de-142-recon`, 6 agents, read-only): mapped P02-P04 code
  reality vs DR-142 and surfaced an 8-item decision register. Key outcomes:
  - **R-142-04 resolved MINOR** (was flagged ARCH): the FM-beside-block strict
    check needs NO bespoke/kind-specific code. `validator.py:128-134` is a generic
    declared-fields unknown-key check; revision is already registered
    (`__init__.py:52`); `get_strict_map` reads `[validation.strict].revision`
    generically. P02 verifies via VT-142-DERIVE-002, adds no check code.
  - **Corpus FM survey (42 revisions)**: only
    `id,name,slug,kind,status,created,updated,relations,aliases,destination_specs,
    requirements,source_specs` present. **None** carry
    `lifecycle/auditers/source/owners/summary` → narrow FM shape is **lossless**.
  - **P04 corpus issue (deferred)**: the `revision.change@v1` block patterns are
    SPEC-only (`^SPEC-\d{3}`) while the sibling **delta** block uses `pattern=r".+"`.
    Corpus pervasively references `PROD-*` (first-class spec), `ADR-*`, `ISSUE-*`,
    `NF-`. Strict would drift-track ~38/42 legit records, and a dest-only synthesised
    `move` trips P01's origin+destination rule (RE-030). DR §8's synthesis is partly
    unimplementable as written → needs a pattern decision at P04 (DEC-CONSULT-03/04).
  - Baseline: targeted suite 1298 passed/0 failed @ default width. The "3 failures"
    split: `show_test` mutually-exclusive is the stray-telemetry dir; the two
    `ListDeltasMalformedFrontmatterTest` are terminal-width wrap artifacts. Suite is
    width-brittle BOTH ways.

### User decisions this session (consult)
- **DEC-CONSULT-01 → NARROW FM shape** (zero corpus lossage). Declared set = DR §5
  table exactly: Base 7 + relations + tags + ext_id + ext_url; omit
  lifecycle/auditers/source/owners/summary.
- **DEC-CONSULT-02 → NARROW applies_to.specs** (DR §6): `specs` from
  `block.specs[].spec_id` only; source/dest split recomputed in P03, not folded in.
- **P04 decisions (03/04 patterns+`unknown`, 05 drift-write, 06 list UX, 07 flip
  timing, 08 stray-dir delete) DEFERRED** — bring researched proposals at P03/P04.
- User interaction preference captured to memory `user-decision-density-preference`:
  unpack consequential decisions with example YAML; lean narrow/strict unless real
  data shows lossage; no dense multi-question batches.

### Done (planning)
- `phases/phase-02.md` authored (6 tasks, ~4 files, TDD). P01 wrap-up handoff closed.

### What's next
- **`/execute-phase` for IP-142-P02** (TDD per phase-02 §7). Inline (small, sequential
  TDD) — reserve workflow orchestration for P03 (parallel: domain/columns/formatter/CLI/tests)
  and P04. Then plan P03, then consult+plan P04.

---

## Session 2026-05-29 — reconciliation + DR + planning

### Done
- **DR-136 §10.2/§10.5 erratum** (commit `45b756a1`): the canonical placement
  table sketched a *flat* `changes:` block that contradicted DE-118's shipped
  rich `metadata`/`specs`/`requirements` schema AND its own F-F scope-note
  ("additive enrichment, not redefinition"). Corrected in place to the shipped
  shape + field-mapping. Recorded in DE-136 phase-03 §9. Routed via /consult,
  user-approved erratum path (not a formal umbrella RE — DR-136 still draft,
  binding intent unchanged).
- **DR-142 authored + validated + internally adversarially reviewed** (commit
  `760d4984`). 7 work items, all grounded in current code reality. DE-142
  reconciled (scope/touchpoints/verification/OQs/risk register).
- **IP-142 + phase-01 sheet** (commit `b5363f73`). 4-phase plan; P01 ready.

### Key design facts (load-bearing — verified in code, not assumed)
- `supekku:revision.change@v1` is **DE-118's rich schema** (`blocks/revision_metadata.py`):
  top-level `metadata`/`specs`/`requirements`; `requirements[].action` enum
  (`introduce|modify|move|retire`) **already exists**. DE-142 is **additive only**
  (F-F) — NO `@v2`, NO block reshape.
- `REVISION_FRONTMATTER_METADATA` already exists as a **DE-137 stub** (Base +
  status only). DE-142 *completes* it (Base 7 + relations + tags + ext_id/ext_url).
- `ConditionalRule` (`blocks/metadata/schema.py`) is **top-level only** —
  `_validate_conditional_rules` does dot-path dict traversal, cannot reach
  `requirements[].action`. DE-142 P01 extends `FieldMetadata` with object-scoped
  `conditional_rules` applied in `_validate_object` (DEC-142-02). Only
  `test_engine.py` uses top-level rules today → low refactor blast radius.
- `applies_to` is **derived, never stored** (DEC-138-10 no-competing-truths);
  precedent `_derive_applies_to` in `changes/artifacts.py:29`. Revisions load via
  `ChangeRegistry(kind="revision")`.
- Migration folder is **`v0_10_0_005_revision_metadata`** (follows
  `v0_10_0_004_audit_findings`), NOT DR-136's ordinal "v06" (DEC-142-07,
  precedent DEC-141-05).
- `list revisions` lives in **`cli/list/reviews.py`** (same file as audits).

### What's next
- **`/execute-phase` for IP-142-P01** (engine + block conditional rules). Move
  DE-142 to `in-progress` at start. TDD per phase-01 §7 tasks 1.1–1.6.
- Then P02 (FM + applies_to), P03 (list), P04 (migration + sweep + strict flip).
- **Audit deferred to DE-136 umbrella close** (VA-DE136-CLOSE-001), per
  DE-139/DE-141 sibling precedent.
- After DE-142 closes + `[validation.strict].revision = true`: DE-136 P03 tasks
  3.9–3.11 (flip confirm, baseline check, phase wrap), then P04 umbrella close.

### Memory to capture once P01 lands (not yet — design only)
- "Object-level `FieldMetadata.conditional_rules` enable per-array-item
  validation" — capture as a metadata-engine capability memory after it's real.
  → **landed**; memory `mem.pattern.spec-driver.field-conditional-rules` written.

---

## Session 2026-05-29 — P01 executed (engine + block conditional rules)

### Done
- `FieldMetadata.conditional_rules` (additive, default `[]`) — `schema.py`.
- `_validate_conditional_rules` → `_apply_conditional_rules(obj, rules, path_prefix)`
  (`validator.py`). Top-level `validate()` passes `prefix=""` (no leading dot);
  `_validate_object` passes `field_path` → array-item errors read
  `requirements[2].origin`.
- Extracted `_validate_additional_keys` from `_validate_object` (the rule-call
  pushed McCabe 10→11; extraction restores it). Behaviour-identical.
- `requirements[]` item declares 3 `ConditionalRule`s: move→{origin,destination},
  introduce→{destination}, modify→{destination}; retire/`specs[]` unconstrained.
- Tests: `ObjectScopedConditionalRuleTest` (test_engine.py, ENGINE-001/002/003);
  `RequirementActionConditionalRuleTest` (new file
  `revision_metadata_conditional_test.py`, BLOCK-001/002/003). 121 targeted pass.

### Verification evidence
- Full `pytest supekku`: **5229 passed, 4 skipped**. **3 pre-existing failures**
  (`cli/list_test.py::ListDeltasMalformedFrontmatterTest` ×2,
  `cli/show_test.py::ShowPathFlagTest::test_path_and_json_mutually_exclusive`) —
  reproduce on clean HEAD with this work stashed; caused by stray untracked
  `.spec-driver/deltas/.spec-driver/run` telemetry polluting CLI discovery. Not P01.
- ruff/ruff-format/ty clean; pylint no new message types (validator matches HEAD
  baseline after the extraction).

### Residual → P02+
- **JSON-schema gap**: `metadata_to_json_schema` emits `allOf` only from
  `BlockMetadata.conditional_rules`; per-item `FieldMetadata.conditional_rules`
  are NOT projected to JSON Schema. Runtime validation correct; doc/schema parity
  deferred. Flag if JSON-schema consumers need the if/then.

### Handoff → P02 (FM completion + applies_to derivation)
- R-142-04 still open: confirm FM-beside-block strict check generalises to
  `kind:revision` (may be delta-keyed).
- `applies_to.specs` dedup/order to finalise (DR-142 §13.2 / §7.1 split).
- F-F additive-only; DEC-138-10 derive-don't-store; DR-136 §11.1 engine/migration
  boundary still hold.

---

## New Agent Instructions

### Task card
- **This delta**: `.spec-driver/deltas/DE-142-revision_artefact_metadata_propagation_revision_frontmatter_metadata_change_block_enrichment_applies_to_derivation_de_136_child/`
- **Parent (umbrella)**: `.spec-driver/deltas/DE-136-metadata_schema_consolidation_program_propagate_adr_010_across_artefacts_and_close_prod_004/` (DE-142 is the last per-artefact child; tracked in DE-136 phase-03 task 3.8)
- **Status**: DE-142 `in-progress`. **P01/P02/P03 COMPLETE** (`44c54f58`, `084e8616`, `34b470de`).
  **P04 CONSULTED + PLANNED, NOT YET EXECUTED** (`d576d446` decisions, `abe80b42` phase sheet).

### Next activity — **`/execute-phase` for IP-142-P04** (NOT consult — that's done)
The consult gate is closed: DEC-142-08..11 ratified (DR-142 §8/§12, session 6 above).
`phases/phase-04.md` is authored, validated, committed. **Route `/using-spec-driver` →
`/execute-phase`** and implement P04 §7 tasks TDD, groups A→D in order:
- **A — broaden ID patterns** (application code, ships first): new shared
  `blocks/metadata/patterns.py` (confirm vs STD-003) with
  `REQUIREMENT_ID_PATTERN = r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NF|NFR)-[A-Z0-9.-]+$"`
  + `SPEC_ID_PATTERN = r"^(SPEC|PROD|ISSUE)-\d{3,}(?:-[A-Z0-9]+)*$"`; reuse across
  revision_metadata.py (7 hardcoded copies) + verification_metadata.py (drop its local dup,
  fix the `NF` gap). VT-142-PATTERN-001.
- **B — migration step** `v0_10_0_005_revision_metadata/` (mirror v004; isolation DEC-138-12:
  stdlib + `_helpers` + `_protocol` + pyyaml only, frozen-local block constants). Cut keys
  `{lifecycle, aliases, auditers, source, source_specs, destination_specs, requirements}`;
  FM-only → synthesise `modify` block (kind from FR/NF token, destination.spec = requirement
  container, **omit lifecycle/origin**); block-wins; idempotent; **`drift_entries=[]` always**.
  VT-142-MIGRATE-001..004.
- **C — template** verify-only (`supekku/templates/revision.md` already narrow + block-canonical).
- **D — sweep** (DR §8.1 order) → VA-142-CORPUS-001 (expect strict clean) → **manual**
  `[validation.strict].revision = true` in `workflow.toml` (DEC-142-11).
- **STOP + /consult** if post-migrate `--strict` shows residual NOT explained by the broadened
  patterns (e.g. a genuine `modify` missing `destination`) — see phase-04 §6.

### Corpus facts (verified session 6 — supersede earlier recon claims)
- 42 revisions: 27 carry a `supekku:revision.change` block, 15 FM-only (need synth).
- ALL carry hand-rolled `aliases` + most carry `source_specs`/`destination_specs`/`requirements`
  → cut by migration. ZERO carry `lifecycle/auditers/source/owners/summary`.
- **ZERO `move` blocks** — all 27 are `action: modify` (`updated` counts = the separate
  `specs[].action` enum). FM-only records are in-place (`source==destination`, e.g. RE-015
  PROD-014) or dest-only (RE-040 → SPEC-122). So synthesise `modify`, never `move`.
- **97 requirement_id violators across ~24 records** vs the OLD SPEC-only regex: `PROD-*` (17
  families), `ISSUE-016`, `SPEC-110/122`; `NF-` token (99 NF reqs repo-wide vs 437 FR). These
  are LEGITIMATE, not drift — fixed by broadening (group A), not drift-tracking.
- `lifecycle` + `lifecycle.status` are both `required=False` → synthesis omits lifecycle.
- (Earlier recon's "`ADR-*`", "~38/42", "RE-030 dest-only move", "DL-075/drift per record" are
  SUPERSEDED — no `ADR-*` requirement refs; no `move`; no synthesis drift; ISSUE-061 owns the gap.)

### After P04 closes
- `[validation.strict].revision = true` in `workflow.toml`; then DE-136 P03 tasks 3.9–3.11
  (flip confirm, baseline) → DE-136 P04 umbrella close. Audit deferred to DE-136 umbrella
  (VA-DE136-CLOSE-001). DE-142 has no standalone audit.

### Required reading (in order) — for P04 execution
1. `phases/phase-04.md` (the runsheet — tasks, VT specs, STOP conditions, findings)
2. `DR-142.md` §8 + §8.0/§8.1 (migration logic + pattern broadening + flip sequence), §12 (DEC-142-08..11)
3. `IP-142.md` §4 (P04 row), §6 (test plan), §8 (resolved decisions)
4. DR-136 §11.1 (engine/migration boundary — load-bearing for isolation) + §11.2 (sweep order)
5. notes.md session 6 (this file, above — evidence + decisions) + memory `user-decision-density-preference`
   (only if a NEW decision arises — the planned ones are settled)

### Key files (code, verified — for P04)
- `spec_driver/migrations/v0_10_0_004_audit_findings/{migration,migration_test}.py` — the step to MIRROR
- `spec_driver/migrations/_protocol.py` (`BaseMigrationStep`/`StepPreview`/`StepResult`),
  `_helpers.py` (`atomic_write`, `split_frontmatter`) — the only allowed imports (+ stdlib/yaml)
- `spec_driver/presentation/cli/admin/migrate.py` — `_discover_steps` (folder-based; no registry edit)
- `supekku/scripts/lib/blocks/revision_metadata.py` — 7 hardcoded SPEC-only regexes (:74/:99/:109/:119/:129/:206/:269/:275/:289) to replace
- `supekku/scripts/lib/blocks/verification_metadata.py:22` — `REQUIREMENT_ID_PATTERN` (the dup to fix+share)
- `supekku/scripts/lib/core/git.py:12` — `SHA_HEX_PATTERN` (domain-local placement precedent, STD-003)
- `supekku/templates/revision.md` — already narrow (verify only)
- Real fixtures: `RE-042` (block + modify + destination), `RE-015` (FM-only, source==dest=PROD-014),
  `RE-040` (FM-only, dest-only SPEC-122 + requirements)

### Relevant memories
- `mem.pattern.validation.per-kind-block-wiring`, `mem.pattern.spec-driver.block-class-data-taxonomy`,
  `mem.pattern.spec-driver.metadata-validator-strictness` (block/validator patterns)
- `user-decision-density-preference` (Claude Code auto-memory — consult style; only if new decisions)
- Candidate NEW memory after P04 lands: "revision.change ID patterns broadened to shared
  `(SPEC|PROD|ISSUE)`+`(FR|NF|NFR)` constants" (capture once real, per the once-it-lands rule)
- (run `/retrieving-memory` at execute start)

### Relevant doctrines
- **F-F (load-bearing)**: additive over DE-118; no block redefinition, no `@v2`. Pattern broadening
  is a pure RELAXATION (no previously-valid block becomes invalid) → F-F-safe, not a redefinition.
- **DEC-138-12 (load-bearing for P04 group B)**: migration steps import ONLY stdlib + `_helpers` +
  `_protocol` + pyyaml — NO `supekku.*`, NO validation/registries/cli. Frozen-local block constants.
- **DR-136 §11.1**: metadata engine = application code (current-schema); migration = legacy-aware.
  The broadened patterns are APPLICATION code (group A); the step does NOT import them.
- **DEC-138-10**: `applies_to` derived, never stored.
- POL-001 (max reuse — the shared pattern constants); STD-003 (utility/pattern placement);
  POL-003 (formatters); STD-002 (lint/pylint); ADR-008 (intent vs observed — referential integrity
  is an audit/registry concern, NOT a block-schema regex; rationale for broadening over strictness).

### User decisions (P04 consult, 2026-05-29) — all ratified, see DR-142 §12
- **DEC-142-08**: broaden ID patterns to shared constants (chose "broaden", not "remove" or "drift-track").
- **DEC-142-09**: synthesise `action: modify` + omit `lifecycle` (no `unknown`; supersedes DEC-142-04).
- **DEC-142-10**: no automated migration drift; orchestrator gap → ISSUE-061 (out of scope).
- **DEC-142-11**: manual `workflow.toml` strict flip after VA-142-CORPUS-001 disposition.
- Standing style (memory `user-decision-density-preference`): one focused decision at a time, example
  YAML, lean narrow/strict UNLESS the corpus shows real lossage (here it did → broaden).

### Loose ends / unresolved (assess during P04)
- R-142-01/02/04 are RESOLVED/DISSOLVED (DR-142 §13): no `move` blocks; lifecycle omitted; FM-beside-block
  check generalised in P02. The one live risk: post-migrate residual strict errors NOT explained by
  broadening (e.g. a genuinely malformed existing block) → STOP + /consult (phase-04 §6), do not mass-drift.
- Shared-pattern home: phase proposes `blocks/metadata/patterns.py` — CONFIRM against STD-003 at execute start.
- JSON-schema gap (P01 residual): per-item `FieldMetadata.conditional_rules` not projected to JSON Schema.
  Runtime correct; flag only if a JSON-schema consumer needs the if/then. Not P04 scope.

### Commit-state guidance
- Worktree CLEAN re: this work. P04-consult artefacts committed: `d576d446` (DR/IP/notes + ISSUE-061),
  `abe80b42` (phase-04). Earlier: `45b756a1`/`760d4984`/`b5363f73` + P01–P03 feat commits.
- Pre-existing unrelated changes (NOT mine, DO NOT commit): `.gitignore`, `flake.lock`, `flake.nix`
  (modified), `.vscode/` (untracked).
- This continuation's notes update is uncommitted — commit it before/with the first P04 work.
- Repo doctrine: prefer frequent small `.spec-driver/**` commits; code + `.spec-driver` may commit
  together or separately. For P04: commit group A (patterns+tests), then B (migration step+tests),
  then the swept corpus + flip, as logical units.
