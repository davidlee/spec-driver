# Notes for DE-137

## 2026-05-18 — IP-137 + phase-01 drafted via /plan-phases

`/plan-phases` ran against the accepted DR-137 v3.1 baseline. Outputs:

- **IP-137** (`IP-137.md`) — five-phase execution plan with the full VT-CC-001..034 + VA-CC-001 catalogue mapped to phases via `supekku:verification.coverage@v1`. Phase shape:
  1. **IP-137-P01** — Schema & validation foundation (FieldMetadata.aliases / BlockMetadata.field_aliases / MetadataValidator strict-mode / ENUM_REGISTRY split / minimal REVISION+ADR metadata / normalize_field / closest_match)
  2. **IP-137-P02** — Template infrastructure + `dump_markdown_file` split (~33 callers) + admin regenerate-templates / validate templates CLI + one-time regeneration commit (F-42)
  3. **IP-137-P03** — `validate` Typer group + `schema enums` CLI + CLI vocabulary constants + ~8 live ripple sites + ISSUE-054 regression test
  4. **IP-137-P04** — `admin migrate` framework (`_protocol`/`_helpers`/`_folder` + orchestrator + lockfile + watermark + import-linter `Migrations isolation` contract) + workflow.toml schema + install fresh-vs-upgrade trigger
  5. **IP-137-P05** — Skill gates (5 files) + acceptance (`just check` + `lint-imports`) + PROD-004 coverage reconciliation + `complete delta DE-137`
- **Phase sheet** (`phases/phase-01.md`) — IP-137-P01 fully fleshed: 15 numbered tasks with design / files / testing / observations per task; entrance + exit criteria gated; VT coverage per task documented; risk table populated.

`spec-driver validate` post-write surfaces only the pre-existing 8 audit-gate warnings (unchanged baseline). No new validation errors.

Two decisions recorded directly in phase-01 §9:
- F-43 `DeprecationWarning` on re-export imports **deferred** to OQ-137-02 resolution (avoids noisy warnings during DE-138..142 implementation).
- `drift` registry gap filed as a backlog `ISSUE-NNN` during task 1.11 rather than fixed inline (keeps Category-B surface frozen for DE-137).

Ready for `/execute-phase` on IP-137-P01. Pre-flight task 1.1 (`grep -rn 'strict_unknown_keys|normalize_status|MetadataValidator\('` + DE-118 closure re-verify + DE-137 → `in-progress`) is the first action.

## 2026-05-18 — DR-137 v1 drafted; adversarial review returned ANOTHER REVIEW PASS

DR-137 was drafted via `/draft-design-revision` (10 clarifying questions Q1–Q10 resolved with user; foundation locked; sections §1–§12 written). Adversarial review (Opus sub-agent) returned 23 findings: **5 BLOCK**, **11 WARN**, **5 INFO**. Verdict: another review pass required before `/plan-phases`.

Dispositions below. Codes:
- **A** — accept; incorporate fix in DR-137 v2.
- **A-defer** — accept the finding but defer the fix to a follow-up (record in §8 Open Questions).
- **R** — reject with rationale.

| ID | Sev | Finding (one line) | Disposition | Action |
|---|---|---|---|---|
| F-1 | BLOCK | `dump_markdown_file(..., kind=)` ripple covers ~30 callers, not only `_creation.py`. Edit-path callers (frontmatter_writer, relations/manager, sync) may silently strip enum-comments. | **A** | Enumerate every caller in code_impacts; for non-creation callers, specify "preserve-comments-on-save" path (read existing comments → re-apply on dump). Or split into `dump_markdown_file_create(kind=...)` vs `dump_markdown_file_update(...)` (latter preserves existing). |
| F-2 | BLOCK | Layering contract gap: POL-003 names 5 layers; `spec_driver/migrations/` as "peer of orchestration" has no layer slot. Import-linter contract is `forbidden`-style, not `layers` extension. | **A** | Specify pyproject.toml diff: switch `root_package` → `root_packages = ["spec_driver", "supekku"]` and add explicit `forbidden` contract: `source_modules: spec_driver.migrations`, `forbidden_modules: spec_driver, supekku`, `allow: spec_driver.migrations._protocol`. |
| F-3 | BLOCK | DEC-137-11 rationale ("stable today ≠ stable forever in own code") proves too much — applies to `_protocol.py` itself. Real rationale is DR-136 §11.1 version-bridging. pyyaml is third-party, not stdlib. | **A** | Rewrite DEC-137-11 rationale: "schema-version-bridging steps must not pull current-schema knowledge." Explicitly list allowed deps: stdlib + `yaml` (pyyaml, pinned). Acknowledge vendoring cost (5 × ~20 LOC). |
| F-4 | BLOCK | Single watermark + multi-kind steps is broken under `--kind` filter. Watermark advances ambiguous; data loss risk if step touches multiple kinds. | **A** | Forbid multi-kind steps: `applies_to_kinds: tuple[str, ...]` becomes `applies_to_kind: str` (singular). Each step targets exactly one kind. Cross-kind concerns split into separate sequential steps. Simplifies dispatch + watermark; aligns with per-kind strict-flip story. |
| F-5 | WARN | "Fresh install ⇒ strict-on" heuristic uses workflow.toml presence; consumer deleting workflow.toml is silently reclassified. | **A** | Switch trigger: strict-on default applies only when **no `.spec-driver/` workspace** exists. Existing `.spec-driver/` ⇒ preserve absent toggles as tolerant. Surface prominent install-time message before any strict flip. |
| F-6 | BLOCK | Two emit paths (regenerator + dump_markdown_file with `kind=`) NOT actually aligned by `validate templates`. POL-001 violated. | **A** | Extract single `render_frontmatter_for_kind(kind, data) -> str` shared by both paths. Add VT-CC-024: regenerator-emit and creation-time-emit produce identical bytes for the same `(kind, data)`. |
| F-7 | WARN | `validate file <path>` "path:line:col" format largely a lie — `ValidationError` has no source positions. | **A** | Drop `:line:col`; format becomes `path: severity: dotted.field.path: message`. Parser-mid-error YAML cases (which DO carry mark.line/col) get the line/col surface; semantic errors get dotted-path only. Document explicitly. |
| F-8 | WARN | `validate workspace --kind` relation-traversal semantics fuzzy. | **A** | Specify: per-kind frontmatter validation = load-time filter (only matching artefacts loaded); relation traversal = full corpus loaded; warnings filtered to subject matching `<kind>`. Add VT-CC-025 covering sweep procedure (other kinds clean, target kind unmigrated ⇒ zero warnings). |
| F-9 | WARN | Re-export sunset undefined; `STATUS_COMPLETE = "complete"` legacy value lost. | **A** | Specify sunset: re-exports retired in named follow-up delta (DE-143 or post-DE-136-umbrella cleanup). Add `complete` to delta-status `FieldMetadata.aliases` (`"complete": "completed"`). Add parity VT-CC-013 covers this. |
| F-10 | WARN | VA-CC-002 (ISSUE-054 re-verify) gates nothing. | **A** | Convert to VT-CC-026: run original ISSUE-054 repro against `list deltas` post-DE-137; assert specific error format (no Rich traceback dump). Decouples ISSUE-054 closure from DR-137 scope. |
| F-11 | WARN | Typer group + `invoke_without_command=True` + default-dispatch with flags is unproven; doc'd workspace-flag flow unclear. | **A** | Decide: either (a) drop bare-`validate` dispatch and require explicit `validate workspace`, or (b) prove the pattern with a worked example showing `--strict` flow through callback. Recommend (a) — simpler. Update migration ripple count (now ~8 sites). |
| F-12 | WARN | Rewriting DR-136 in-line edits destroys audit trail. | **A** | Drop DR-136 self-reference rewrites from §5.4 migration ripple. Only touch `supekku/about/lifecycle.md`, `PROD-010.md`, `SPEC-110.md` examples. DR-136 stays untouched; §10 supersedes mechanism is the canonical reconciliation. |
| F-13 | WARN | Folder name `0.10.0_001_*` not a valid Python module name (starts with digit, contains dots). | **A** | Change format: `v<major>_<minor>_<patch>_<NNN>_<slug>/` (e.g. `v0_10_0_001_delta_blocks/`). Add named constant `MIGRATION_FOLDER_PATTERN: re.Pattern` and `parse_migration_folder(name) -> (Version, int, str)` with VT coverage. |
| F-14 | WARN | Partial-step-mid-walk recovery untested. | **A** | Add VT-CC-023: fixture where `step.apply()` raises mid-corpus; assert re-run reaches all files; final state matches "fully applied". |
| F-15 | INFO | `difflib.get_close_matches(cutoff=0.6)` fails the canonical "status 'live' → in-progress" example. | **A** | Spike: try `cutoff=0.4`; verify against the corpus (`live`, `complete`, `in_progres`, `pendng`, …); add VT-CC-010 cases for each canonical typo. If 0.4 has too many false positives, fall back to Levenshtein. |
| F-16 | WARN | POL-002: flag literals + subcommand names as magic strings. | **A** | Add §5.4.x "CLI vocabulary": named constants in `spec_driver/presentation/cli/constants.py` for every subcommand, flag, semver pattern, log-path template. Reference from Typer signatures. |
| F-17 | WARN | `ENUM_REGISTRY` has non-artefact-kind enums (verification.*, backlog.*, command.format, requirement.kind) — registry walk doesn't cover them. | **A** | Split: (a) artefact-frontmatter-derived (delta.status, spec.status, audit.status, …) via registry walk; (b) other (verification.*, backlog.*, drift.*, command.format) stays hardcoded or moves to its own per-block metadata. Document both branches in §5.2 source-of-truth migration. |
| F-18 | WARN | import-linter `root_package` is singular; can't forbid `spec_driver.migrations` from importing `supekku.*` without `root_packages` plural. | **A** | Covered by F-2 fix; ensure the pyproject diff is explicit. |
| F-19 | INFO | Phase aliases (`active`, `done`, `in_progress`) vs delta aliases — DR conflates. | **A** | §5.2: list aliases explicitly per (kind, field). Phase-only aliases stay on plan/phase FieldMetadata. Delta status aliases: `complete → completed` only. |
| F-20 | WARN | Per-migration vendoring violates POL-001 extraction threshold (≥3 copies ⇒ P1 finding). | **A** | Add `spec_driver/migrations/_helpers.py` (frozen alongside `_protocol.py`) with `split_frontmatter`, `atomic_write`, ~3 vendored functions migrations actually share. Plus explicit §7 trade-off note: POL-001 extraction-threshold exempt for migration subsystem (reason: capture-of-the-day discipline trumps reuse). |
| F-21 | INFO | Concurrent `admin migrate` invocations race on workflow.toml watermark. | **A** | §9.3 (recovery): document single-process assumption; add `.spec-driver/run/migrations/.lock` (PID lock); admin migrate prints clear error on detected lock. |
| F-22 | INFO | Template body preservation through regenerator unspecified; audit.md example block may be silently lost. | **A** | §5.1: regenerator emits only frontmatter section; body content (including example/Jinja blocks) preserved verbatim. Add VT-CC-002 sub-case: audit template's `{{ audit_verification_block }}` Jinja placeholder survives regeneration. |
| F-23 | INFO | Skill text insertion lacks automated VT. | **A** | Add VT-CC-027: post-DE-137, parse `supekku/skills/<skill>/SKILL.md` for the five named skills; assert the specific gate text is present per DR-136 §5.5. Or insert markers (`<!-- validate-gate -->`) for anchor-based assertion. |

### Summary

All 23 findings dispositioned **A** (accept). No rejections. Most BLOCK fixes are concrete edits or expanded enumeration; the most substantive is F-4 (forbid multi-kind steps — simplifies the migration framework materially).

Estimated revision effort: **~90 min focused** to incorporate all fixes; ~60 min minimum if INFO findings deferred to v3.

Recommended next actions:
1. Revise DR-137 → v2 with all 23 dispositions applied.
2. Run second adversarial review pass.
3. If verdict ACCEPT or ACCEPT WITH EDITS → proceed to `/plan-phases`.

### Inherited scope-notes (carried from DE-137 §3)

- **F-B** (relations key naming): resolved → `nature` canonical, `annotation` permanent alias. Locked in DEC-137-05.
- **F-E** (Phase 2 entrance check on DE-118): verified satisfied — `MetadataValidator(strict_unknown_keys: bool = False)` is opt-in flag, not unconditional. Confirmed in `supekku/scripts/lib/blocks/metadata/validator.py:60`.

### Audit reviewer raw output

Reviewer agent ID: `a9da5e032c8ca4704` (general-purpose, opus model). Full finding text and verdict preserved in this turn's transcript.

---

## 2026-05-18 — DR-137 v3.1 — third-pass review accepted with edits

Third adversarial pass returned **ACCEPT WITH EDITS** (13 findings F-49..F-61: 0 BLOCK, 4 WARN, 9 INFO). The two must-fix WARN findings (F-54 collision data-loss, F-58/F-61 missing §10 reconciliations) plus a small set of cheap edits applied as v3.1:

- F-54: validator pseudo-code now refuses to silently merge when both alias and canonical keys present; emits `error`-severity diagnostic; `--fix` declines. New VT-CC-034.
- F-58: new §10 reconciliation point 11 covering minimal REVISION/ADR metadata scope advance.
- F-61: new §10 reconciliation point 12 covering the field_aliases/aliases alias-mechanism split (DEC-137-23).
- F-49: corrected `creation.py:245` row in ripple table (`requirement`, not branched `design_revision/design_change`).
- F-50: added explicit `BaseMigrationStep` concrete helper class to `_protocol.py` listing (Protocol can't carry default impls).
- F-51: fixed dangling "see §10 reconciliation point 11" cross-reference in §5.2 matrix (now resolves correctly post-F-58).
- F-52: corrected §10 point 2 DEC citation (DEC-137-13 was wrong; just F-13).
- F-55: lockfile uuid rationale rewritten — it's a log-correlation anchor, not a PID-reuse mitigator.
- F-59: DE-137 §7 risk row updated to match v3 VT-CC-024 wording (comment-map invariance, not byte-identical).
- F-60: DE-137 §3 outcome 2 refreshed to describe the F-30 alias split.

Findings declined for v3.1 (filed as paper cuts to land alongside IP-137 drafting per the reviewer's own guidance): F-53 asymmetric tolerated_field_aliases (rationale: field renames are rare and migration-paired, no real demand); F-56 narrowing of `complete` from CHANGE_STATUSES (already covered by tolerant-on-read; the matrix is explicit enough); F-57 lockfile content format constant (acceptable adjacency to lock acquire code).

Verdict for v3.1: ready for `/plan-phases`. Reviewer's strengths note: "the import-linter prototype is genuinely verified ... the F-32 Typer exit code is mechanically correct ... the F-30 schema split is conceptually crisp ... the doc's adversarial-review process is working as designed."

## 2026-05-18 — DR-137 v3 written; third adversarial review pending

Second-pass adversarial review returned ANOTHER REVIEW PASS — 3 BLOCK + 11 WARN + 11 INFO findings (F-24..F-48). User dispositioned all BLOCKS as A and accepted my F-30 design (BlockMetadata.field_aliases + FieldMetadata.aliases split).

v2→v3 highlights:
- **F-24** (BLOCK): `dump_markdown_file` ripple table rebuilt from actual `grep` of the tree. 11 create-path + 9 update-path + 1 bypass + ~12 tests ≈ 33 sites. Wrong path corrected (`spec_driver/domain/relations/manager.py` not `changes/relations/manager.py`). Real callers added: `backlog/registry.py`, `cli/resolve.py`, `cli/compact.py`, `sync_specs.py`, `scripts/normalise_frontmatter.py`. Comment-preservation algorithm in `_update` spelled out (frontmatter head re-read + lex trailing comments + re-emit).
- **F-25** (BLOCK): import-linter contract prototyped against installed import-linter 2.11. Working diff: keep `root_package = "spec_driver"` (singular); add `include_external_packages = true`; enumerate forbidden modules explicitly (each `spec_driver.<layer>` + `supekku`); no `allow` field (which doesn't exist), no `ignore_imports` whitelist needed (frozen sidecars simply absent from the forbidden list). Prototype confirmed contract correctly catches both `spec_driver.core.X` and `supekku.*` imports from migration steps.
- **F-30** (BLOCK): split alias mechanism. `BlockMetadata.field_aliases: Mapping[str, str]` for field-NAME (parse-time key rename); `FieldMetadata.aliases: Mapping[str, str]` for field-VALUE (post-dispatch value normalisation). `ValidationError.fix_kind ∈ {rename_key, rewrite_value}` for `--fix` dispatch. Diagnostics rewritten (`relations[0].annotation: field name 'annotation' is an alias for 'nature'`); per-kind matrix split into field_aliases (relations block) + per-FieldMetadata aliases (per-kind status); VT-CC-008 scoped to field-NAME; new VT-CC-030 for field-VALUE.

WARN fixes inline (F-26..F-48): kind-validation at migrate-discovery (VT-CC-031); plan/phase/task sibling-folder dispatch (DEC-137-25); two-layer dispatch contract for `applies_to_kind` + `applies_to(path)` with default base class; uniform exit-code contract (VT-CC-032); `validate file` non-artefact handling; rewrite VT-CC-024 to test comment-map invariance (not byte-identical, which was impossible); VT-CC-019 covers mixed-state idempotency; lockfile liveness cross-platform (POSIX kill -0 + uuid for PID-reuse, Windows skips staleness); frozen-forever ≠ bug-frozen (DEC-137-26); REVISION + ADR minimal metadata added (DEC-137-28); workflow.toml unknown-kind warning (VT-CC-033); DEC-137-21 trade-off acknowledged for linkifier UX; F-42 first-regeneration commit-pairing note; OQ-137-03 filed for future JSON output mode.

Decisions added: DEC-137-23..28. VTs added: VT-CC-030..033. OQ-137-03 filed.

Reviewer's verdict was ANOTHER REVIEW PASS; goal of v3 is to reach ACCEPT or ACCEPT WITH EDITS on a third pass. If a fourth pass surfaces another BLOCK round, /consult is the next move.

## 2026-05-18 — DR-137 v2 written; second adversarial review pending

DR-137 revised to v2. All 23 dispositions from the §"DR-137 v1 drafted" table applied. User-confirmed pause points before locking:
- **F-1** resolved via option (a): split `dump_markdown_file` into `*_create(kind=)` (emit comments) and `*_update()` (preserve existing comments). Old function removed; every caller migrates explicitly. Ripple table at §5.1.
- **F-11** resolved via option (a): drop bare-`validate` default-dispatch (reverses Q2 A1). Bare `spec-driver validate` prints help.

F-15 difflib spike executed before locking: at cutoff=0.6, all canonical typos (`'complete'`, `'pendng'`, `'in_progres'`, `'defered'`, `'draaft'`) match expected canonical. Semantic alternatives (`'live'`, `'active'`, `'done'`, `'wip'`) don't match at any practical cutoff without sweeping in false positives. Conclusion: keep cutoff=0.6; semantic alternatives belong in `FieldMetadata.aliases`, not did-you-mean. Recorded as DEC-137-20.

Other v1→v2 highlights:
- New decisions: DEC-137-15..22 (F-1, F-4, F-11, F-5, F-20, F-15, F-7, F-21 resolutions).
- New OQ-137-02 (re-export sunset target delta TBD).
- §5.6 gained verbatim pyproject diff for F-2 import-linter contract (`root_packages` plural; explicit forbidden contract on `spec_driver.migrations`).
- §5.6 gained `_helpers.py` (vendored bytes-level shared helpers, F-20) and `_folder.py` (parser, F-13).
- §5.6 gained lockfile (F-21) and explicit mid-walk recovery procedure + VT-CC-023 (F-14).
- Folder name shape: `v<M>_<m>_<p>_<NNN>_<slug>/` — valid Python identifier (F-13).
- `MigrationStep.applies_to_kinds: tuple[str,...]` ⇒ `applies_to_kind: str` (singular). Multi-kind steps forbidden (F-4; DEC-137-16).
- Strict-on-default trigger keyed to `.spec-driver/` workspace absence at install time, not workflow.toml presence (F-5).
- §5.4 gained CLI vocabulary constants module (F-16; POL-002).
- §5.5 gained anchor-comment markers around skill inserts (F-23) + VT-CC-027.
- §10 Supersedes grew to 10 entries; §10.1 enumerates *live* document edits (DR-136 stays frozen, F-12).
- Verification catalogue grew to VT-CC-001..029 + VA-CC-001 (VA-CC-002 retired in favour of VT-CC-026).
- DE-137.md reconciled: §3 deliverables, §5 system touchpoints, §7 risks (ruamel.yaml → custom yaml_emit + 3 new risks for F-1/F-4/F-9), §8 open decisions resolved or refiled as OQ-137-02.

Internal end-to-end review post-v2 caught one local inconsistency: §5.2 enum-violation example used `'live'` as did-you-mean input, contradicting DEC-137-20. Replaced with `'in_progres'` (typo example) and kept `'live'` as the "no did-you-mean candidate" example to document the spike result inline.

**Final file count**: DR-137 ≈ 1207 lines (was 889). DE-137 unchanged shape but refreshed deliverable/risk/decisions wording.

Ready for second adversarial-review pass.

## New Agent Instructions (2026-05-18, refreshed post `/plan-phases`)

### Task card

- **Delta**: DE-137 — Cross-cutting metadata schema infrastructure: validation+templates+CLI+migrate orchestrator (DE-136 child).
- **Card path**: `.spec-driver/deltas/DE-137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child/`
- **DR**: `DR-137.md` v3.1 — **ACCEPT WITH EDITS** verdict applied (third adversarial pass complete; ready for plan/execute).
- **IP**: `IP-137.md` — five-phase plan drafted via `/plan-phases`; verification coverage block enumerates VT-CC-001..034 + VA-CC-001 mapped to phases.
- **Active phase**: `phases/phase-01.md` — IP-137-P01 *Schema & validation foundation*, status `draft`, 15 tasks specified.
- **Delta status**: `draft`. Next agent transitions to `in-progress` as task 1.1 of IP-137-P01.

### What's done

- `/draft-design-revision` completed across 3 adversarial-review passes. DR-137 v1 → v2 → v3 → v3.1 (latest). All 61 review findings (F-1..F-61) dispositioned. Decisions DEC-137-01..28 locked. Open questions OQ-137-01..03 carried forward.
- `/plan-phases` produced IP-137 (5 phases) + Phase 01 sheet (15 tasks).
- `spec-driver validate` shows no new validation issues attributable to planning artefacts (only the pre-existing 8 audit-gate warnings).

### What's pending

1. **Execute IP-137-P01** via `/execute-phase` against `phases/phase-01.md`. First task (1.1) is a read-only pre-flight grep audit + DE-137 lifecycle transition.
2. After IP-137-P01 exit criteria met: create `phases/phase-02.md` (template infrastructure + `dump_markdown_file` split).
3. After IP-137-P02 exit criteria met: create `phases/phase-03.md` (validate Typer group + schema enums CLI + ripple).
4. After IP-137-P03 exit criteria met: create `phases/phase-04.md` (migrate framework + workflow.toml + import-linter).
5. After IP-137-P04 exit criteria met: create `phases/phase-05.md` (skill gates + acceptance + closure).
6. `/audit-change` → `/close-change` to finish.

### Required reading

- **DR-137** — `.spec-driver/deltas/DE-137-…/DR-137.md` (v3.1; the canonical design). Specifically §5 per-deliverable detail and §11 verification catalogue.
- **DE-137** — same folder, `DE-137.md` (delta scope; deliverables enumerated).
- **IP-137** — same folder, `IP-137.md` (phase map + verification coverage block).
- **phases/phase-01.md** — concrete task list and exit gates for the next phase to execute.
- **This notes.md** — adversarial-review disposition history (F-1..F-61) is the audit trail; current state at top of file.

### Related documents

- **DR-136** — `.spec-driver/deltas/DE-136-metadata_schema_consolidation_program_propagate_adr_010_across_artefacts_and_close_prod_004/DR-136.md` — canonical design reference; DR-137 §10 enumerates supersedes.
- **IP-136** — same DE-136 folder — umbrella plan; DE-137 is Phase 2 ("Foundations"). DE-137 must close before per-artefact propagation (DE-138..142) begins.
- **DE-118** — block-validator unification; closed. Provides the `MetadataValidator(strict_unknown_keys=False)` opt-in baseline. Verified at `supekku/scripts/lib/blocks/metadata/validator.py:60`.
- **DE-138..142** — sibling per-artefact deltas, all `draft`. They consume DE-137 infrastructure. **Do NOT pre-draft their DRs.**

### Key files (touchpoints for IP-137-P01)

- **Schema dataclasses**: `supekku/scripts/lib/blocks/metadata/schema.py` — `FieldMetadata` + `BlockMetadata` (tasks 1.3, 1.8).
- **Validator**: `supekku/scripts/lib/blocks/metadata/validator.py:60` — `MetadataValidator` refactor target (tasks 1.6, 1.7).
- **Validation entrypoint**: `supekku/scripts/lib/validation/validator.py` — primary caller surface for the `strict_unknown_keys` kwarg removal (task 1.7).
- **Per-kind metadata**: `supekku/scripts/lib/core/frontmatter_metadata/` — populate aliases here (task 1.4); add `revision.py` + `adr.py` (task 1.5).
- **Lifecycle constants**: `supekku/scripts/lib/changes/lifecycle.py` — `CHANGE_STATUSES`, `CANONICAL_STATUS_MAP`, `normalize_status` (tasks 1.9, 1.10, 1.12).
- **`ENUM_REGISTRY`**: `spec_driver/orchestration/enums.py` — Category A/B split (task 1.11).
- **NEW**: `spec_driver/core/string_utils.py` (task 1.2 — `closest_match`).
- **NEW**: `supekku/scripts/lib/blocks/metadata/aliases.py` (task 1.9 — `normalize_field`).
- **Tests under**: `tests/spec_driver/core/`, `tests/supekku/scripts/lib/blocks/metadata/`, `tests/supekku/scripts/lib/changes/`, `tests/spec_driver/orchestration/`.

### Key files (later phases — for context only)

- `supekku/scripts/lib/core/spec_utils.py` — `dump_markdown_file` split (IP-137-P02; ~33 ripple sites enumerated in DR-137 §5.1).
- `spec_driver/core/yaml_emit.py` (NEW; IP-137-P02; ~60 LOC custom emitter, OQ-137-01).
- `spec_driver/orchestration/templates.py` (NEW; IP-137-P02; `render_frontmatter_for_kind` shared).
- `supekku/templates/*.md` (IP-137-P02; one-time regeneration after templates.py lands — F-42).
- `supekku/cli/workspace.py:65` + new `spec_driver/presentation/cli/{validate,schema,admin}/` (IP-137-P03).
- `spec_driver/migrations/{_protocol,_helpers,_folder}.py` (NEW; IP-137-P04; frozen sidecars).
- `pyproject.toml` (IP-137-P04; import-linter `Migrations isolation` forbidden contract — verbatim diff in DR-137 §5.6).
- `supekku/scripts/lib/core/config.py:17` + `DEFAULT_CONFIG` (IP-137-P04; workflow.toml schema additions).
- `supekku/skills/<execute-phase,close-change,audit-change,notes,update-delta-docs>/SKILL.md` (IP-137-P05; verbatim text + anchor markers).

### Relevant memories

Use `/retrieving-memory` for any unfamiliar concept. Likely useful:

- `mem.signpost.spec-driver.overview` — orientation.
- `mem.concept.spec-driver.delta`, `.spec-driver.plan`, `.spec-driver.revision` — entity primitives.
- `mem.fact.spec-driver.status-enums` — status enum locations.
- `mem.pattern.spec-driver.delta-completion` — closure gates.
- `mem.pattern.validation.warning-triage` — `validate` warning categories.

### Relevant doctrines

All loaded into the boot context already:

- **ADR-010** — placement heuristic (frontmatter / blocks / prose; never duplicate).
- **ADR-011** — Workspace as canonical registry-access surface.
- **POL-001** — single source of truth (load-bearing throughout DE-137; metadata is canonical for enums + aliases).
- **POL-002** — no magic strings/numbers (load-bearing for IP-137-P03 CLI constants module).
- **POL-003** — module boundaries (load-bearing for IP-137-P04 migrations isolation).
- **STD-001** — Typer/Rich (IP-137-P03 validate/schema CLIs).
- **STD-003** — utility module placement (yaml_emit, string_utils).
- **STD-004** — script lifecycle (orphan prevention).

### Important user instructions / decisions

- **Migrations are self-contained scripts** like database migrations — capture-of-the-day; minimal external deps; the three frozen sidecars (`_protocol`, `_helpers`, `_folder`) are the only shared surface (DEC-137-11 / DEC-137-19 / DEC-137-26).
- **Multi-kind migration steps forbidden** (DEC-137-16). DE-138..142 cannot ship a single cross-kind step; cross-kind concerns split into ordered per-kind ordinals.
- **Bare `spec-driver validate` prints help** (DEC-137-17). Reverses an earlier Q2 A1 leaning; user confirmed during v2 dispositions.
- **`dump_markdown_file` split into `_create(..., kind=)` + `_update(...)`** (DEC-137-15); no shim. Every caller migrates explicitly.
- **Fresh-install strict-mode trigger keyed to `.spec-driver/` workspace absence** (DEC-137-18), NOT `workflow.toml` presence.
- **F-43 DeprecationWarning on transition re-exports deferred** to OQ-137-02 resolution — explicitly noted in phase-01 §9 to prevent noisy import-time warnings during DE-138..142 work.
- **`drift` registry gap filed as backlog ISSUE during IP-137-P01 task 1.11**, not fixed inline. Same for `improvement` / `backlog` umbrella entries (Category B).

### Unresolved tensions / open questions

- **OQ-137-01** — Custom `yaml_emit` (~60 LOC, stdlib yaml only) vs ruamel.yaml. Gate: if implementation exceeds ~120 LOC or hits stdlib-yaml edge cases at IP-137-P02, swap to ruamel.
- **OQ-137-02** — Sunset target delta for transition-window re-exports (`CHANGE_STATUSES`, etc.). Resolve at DE-136 umbrella close; downgrade to "next major spec-driver version" if no follow-up delta exists.
- **OQ-137-03** — Structured JSON diagnostic output mode. Out of DE-137 scope; file follow-up at close if CI consumer demand surfaces.
- No active design tensions awaiting resolution before code begins — DR-137 v3.1 ACCEPT WITH EDITS verdict cleared the bar.

### Commit-state guidance

- **No code touched yet**. Only `.spec-driver/**` changes pending from this session:
  - `M  .spec-driver/deltas/DE-137-…/notes.md` (this update)
  - `??  .spec-driver/deltas/DE-137-…/IP-137.md` (new — five-phase plan)
  - `??  .spec-driver/deltas/DE-137-…/phases/phase-01.md` (new — IP-137-P01 sheet)
- **Recommend committing these now before code work starts**, per project doctrine (frequent small `.spec-driver/**` commits; keep worktree clean). Suggested commit: `docs(DE-137): plan IP-137 + draft phase-01 sheet`.
- During IP-137-P01 execution: commit pre-flight audit results to notes.md first, then code changes per task. The phase wrap-up commit goes out as `feat(DE-137): land metadata aliases + strict validator (IP-137-P01)`.
- `.vscode/` is untracked at session start — not part of this delta; ignore.

### Other advice for next agent

- **The phase sheet is authoritative.** Each task in `phases/phase-01.md` §7 has design / files / testing / observations spelled out. Follow it rather than re-deriving from DR-137 §5.2.
- **Task 1.1 first.** The grep audit produces the authoritative list of `MetadataValidator(...)` and `normalize_status` consumers; tasks 1.6 / 1.7 / 1.9 / 1.10 depend on it. Don't skip.
- **Capture pre-split `ENUM_REGISTRY` snapshot before task 1.11** — VT-CC-012 needs the equality assertion against the *prior* lambda outputs, not a freshly-computed reference.
- **DE-137 status transition to `in-progress` is part of task 1.1**, not implicit. The `/execute-phase` skill should handle this; if it doesn't, run `uv run spec-driver` lifecycle command explicitly.
- **`.spec-driver/` workspace persistence**: running `spec-driver` against this repo will warn about install version mismatch (`workflow.toml has 0.9.2, running 0.9.3`). Non-blocking but expected; do not "fix" by running `spec-driver install` mid-session unless the user authorises (would update workflow.toml shape).
- If a phase's exit criteria can't be cleanly met (e.g. a VT genuinely fails on an unforeseen issue), `/consult` rather than relaxing the criteria.

