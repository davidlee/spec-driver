# Notes for DE-137

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

## New Agent Instructions (2026-05-18)

### Task card

- **Delta**: DE-137 — Cross-cutting metadata schema infrastructure: validation+templates+CLI+migrate orchestrator (DE-136 child).
- **Card path**: `.spec-driver/deltas/DE-137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child/`
- **DR**: `DR-137.md` (drafted; v1 returned ANOTHER REVIEW PASS from adversarial review).
- **Status**: DR-137 v1 written. v2 revision required before `/plan-phases` can run. No code touched.

### What's done

- `/draft-design-revision` ran to completion through "Adversarial review" step.
- 10 foundational design questions (Q1–Q10) resolved with user; foundation locked. See decisions DEC-137-01..DEC-137-14 in DR-137 frontmatter.
- DR-137 v1 written and committed-ready to the file (uncommitted at session end).
- Adversarial review (Opus sub-agent) produced 23 findings.
- All 23 findings dispositioned in this notes.md (see disposition table above) — **all accepted (A)**, no rejections.

### What's pending

1. **Revise DR-137 → v2** by applying the 23 dispositions above. Estimated 60–90 min focused work. Order suggestion: BLOCK first (F-1, F-2, F-3, F-4, F-6), then WARN, then INFO.
2. **Run a second adversarial-review pass** (same skill/process) on the revised DR.
3. If second-pass verdict is **ACCEPT** or **ACCEPT WITH EDITS**: integrate any final fixes, then transition to `/plan-phases` per `/draft-design-revision` step 8.
4. If second-pass verdict is **ANOTHER REVIEW PASS**: repeat the revise + review loop. If it loops > 2 more rounds without converging, `/consult` for a design-tension review.

### Required reading

- **DR-137 v1** — `.spec-driver/deltas/DE-137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child/DR-137.md` (the document being revised).
- **DE-137** — same folder, `DE-137.md` (the delta DR-137 implements).
- **DR-136** — `.spec-driver/deltas/DE-136-metadata_schema_consolidation_program_propagate_adr_010_across_artefacts_and_close_prod_004/DR-136.md` — canonical design reference; DR-137 §10 supersedes specific wording.
- **This notes.md** — disposition table is authoritative for what changes in v2.

### Related documents

- **IP-136** — `.spec-driver/deltas/DE-136-…/IP-136.md` — umbrella program plan; DE-137 is phase 2 ("Foundations"). DE-137 must close (alongside DE-118) before per-artefact propagation (DE-138..142) begins.
- **DE-118** — block validator unification; closed. DE-137 builds on `MetadataValidator.strict_unknown_keys` flag landed by DE-118 (verified opt-in default-off in `supekku/scripts/lib/blocks/metadata/validator.py:60`).
- **DE-138..142** — sibling per-artefact deltas, all `draft` status; consume DE-137 infrastructure. Do NOT pre-draft their DRs.

### Key files (for revision and verification)

- **DR-137**: `.spec-driver/deltas/DE-137-…/DR-137.md` (target of revision).
- **DE-137**: `.spec-driver/deltas/DE-137-…/DE-137.md` (may need small reconciliation after v2 — check §3 deliverables 6 references to `supekku/scripts/lib/migrations/` and update if F-2/F-3 changes the wording).
- **`MetadataValidator`**: `supekku/scripts/lib/blocks/metadata/validator.py` — DE-118-landed strict-flag baseline.
- **`FieldMetadata` / `BlockMetadata`**: `supekku/scripts/lib/blocks/metadata/schema.py` — DR-137 §5.2 extends.
- **Current `validate` CLI**: `supekku/cli/workspace.py:65` — DR-137 §5.4 replaces with Typer group.
- **`dump_markdown_file`**: `supekku/scripts/lib/core/spec_utils.py` — F-1 ripple (≥30 callers; enumerate).
- **`ENUM_REGISTRY`**: `spec_driver/orchestration/enums.py` — DR-137 §5.2 converts to derived view (F-17: not all entries are artefact-kind; split needed).
- **`pyproject.toml`**: F-2 / F-18 — need explicit `root_packages` plural + `forbidden` contract for migrations.
- **`workflow.toml`** + **DEFAULT_CONFIG**: `supekku/scripts/lib/core/config.py:17` — F-5 trigger change (workspace-existence, not workflow.toml presence).
- **Templates**: `supekku/templates/*.md` — F-22 body preservation note required.
- **Skills**: `supekku/skills/<execute-phase,close-change,audit-change,notes,update-delta-docs>/SKILL.md` — F-23 anchor markers may help.

### Relevant memories

Use `/retrieving-memory` for any unfamiliar concept. Likely useful:

- `mem.signpost.spec-driver.overview` — orientation.
- `mem.concept.spec-driver.delta`, `.spec-driver.revision`, `.spec-driver.plan` — entity primitives.
- `mem.fact.spec-driver.status-enums` — status enum locations.
- `mem.pattern.spec-driver.delta-completion` — closure gates.
- `mem.pattern.validation.warning-triage` — `validate` warning categories.

### Relevant doctrines

All loaded into the boot context already:

- **ADR-010** — placement heuristic (frontmatter / blocks / prose; never duplicate).
- **ADR-011** — Workspace as canonical registry-access surface.
- **POL-001** — single source of truth (load-bearing for F-6 fix).
- **POL-002** — no magic strings/numbers (load-bearing for F-16 fix).
- **POL-003** — five-layer architecture (load-bearing for F-2 layering question).
- **STD-001** — Typer/Rich (relevant to F-11).
- **STD-003** — utility module placement.

### Important user instructions / decisions

- **Migrations are self-contained scripts** like database migrations — capture-of-the-day; minimal external deps; `_protocol.py` is the only shared file (user-stated, key constraint).
- **Migrations naming uses spec-driver semver** for linearised sequence (user proposal).
- **F-1 in disposition table**: user has not seen this finding yet. The fix may benefit from a quick confirm-with-user before implementation if the agent's chosen path (split into create vs update variants vs preserve-comments-on-save) is non-obvious.
- **F-11 disposition** suggests dropping bare-`validate` dispatch. User originally approved A1 in Q2 conversation (named `validate workspace` peers with backwards-compatible bare `validate` dispatch). Dropping bare `validate` is a small UX regression on the path the user originally approved. **Confirm with user before locking** if reverting that decision — could go either way.

### Unresolved tensions

- **F-4 multi-kind migrations**: disposition forbids them. This is a simplification, but means the upcoming per-artefact deltas DE-138..142 cannot ship a single migration touching two artefact kinds. If DR-136 §6–§10 anticipates any multi-kind migration, that's a contradiction worth surfacing. Spot-check at v2 revision time.
- **F-9 re-export sunset**: needs a named delta as the sunset target. If no follow-up delta exists, propose one or weaken sunset to "next major spec-driver version."

### Commit-state guidance

- **No code touched** yet. Only `.spec-driver/**` changes pending.
- Modified files at session end: `.spec-driver/deltas/DE-137-…/DR-137.md`, `.spec-driver/deltas/DE-137-…/notes.md`.
- **Recommend committing these now before v2 revision starts**, per project doctrine (frequent small commits of `.spec-driver/**`, keep worktree clean). Suggested message: `docs(DE-137): draft DR-137 + adversarial review dispositions`.
- After v2 revision: separate commit `docs(DE-137): revise DR-137 v2 incorporating adversarial review fixes`.
- After second-pass review acceptance: separate commit `docs(DE-137): finalise DR-137 (review accepted)`.

### Other advice for next agent

- The disposition table above is the authoritative work list. Don't re-derive findings; apply dispositions directly.
- Keep DR-137 §10 (Supersedes) growing as v2 fixes generate new DR-136 reconciliations. Especially F-3, F-4 add fresh reconciliations.
- When applying F-2 (pyproject diff), produce a real diff or at minimum a verbatim block — not prose ("we'll add a forbidden contract"). The reviewer flagged that for v1.
- F-15 (difflib cutoff): the disposition says "spike with cutoff=0.4" — actually try it in Python before committing. The reviewer ran `SequenceMatcher.ratio('live', 'in-progress') = 0.4` — at cutoff=0.4 it passes. Verify in a REPL with the canonical examples before finalising.
- After v2 is written, **read it back end-to-end** before spawning the second-pass reviewer — easy to miss a section.

