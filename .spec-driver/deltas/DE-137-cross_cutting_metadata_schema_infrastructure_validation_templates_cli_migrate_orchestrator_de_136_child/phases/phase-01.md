---
id: IP-137-P01
slug: "137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child-phase-01"
name: IP-137 Phase 01 - Schema & validation foundation
created: "2026-05-18"
updated: "2026-05-18"
status: completed
kind: phase
plan: IP-137
delta: DE-137
---

# IP-137-P01 — Schema & validation foundation

## 1. Objective

Land the **metadata-as-source-of-truth** foundation: extend `FieldMetadata` and `BlockMetadata` with the two-axis alias mechanism (DEC-137-23 / F-30), populate per-kind alias matrices, retire the `strict_unknown_keys` constructor kwarg in favour of `MetadataValidator.validate(*, strict, accept_tolerated)`, add `ValidationError.fix_hint`/`fix_kind`, split `ENUM_REGISTRY` into a Category A derived view + Category B hardcoded view, add minimal `REVISION_`/`ADR_FRONTMATTER_METADATA` (status-only) so the derived view doesn't silently drop those enums, retire `normalize_status()` in favour of `normalize_field(kind, field, value)`, ship `closest_match()` did-you-mean utility, and convert `CHANGE_STATUSES`/`REQUIREMENT_STATUSES`/etc. into transition-window re-exports.

No CLI, no templates, no migrations — purely the schema + validator + enum source-of-truth layer that every subsequent phase consumes.

## 2. Links & References

- **Delta**: DE-137
- **Design Revision Sections**:
  - DR-137 §5.2 (Deliverable Z — strict validation, alias autocorrect, did-you-mean)
  - DR-137 §3.1 outcomes 1, 2
  - DR-137 §5.2 source-of-truth migration (split ENUM_REGISTRY)
  - DR-137 §11 (verification catalogue) — VT-CC-008, 009, 010, 011, 012, 013, 030, 034
- **Specs / PRODs**: PROD-004 (FR-002), SPEC-114 (blocks/metadata), SPEC-116 (frontmatter_metadata), SPEC-125 (validation)
- **Support Docs**:
  - `supekku/scripts/lib/blocks/metadata/schema.py` — `BlockMetadata`/`FieldMetadata` definitions
  - `supekku/scripts/lib/blocks/metadata/validator.py:60` — current `MetadataValidator(strict_unknown_keys=False)` baseline
  - `supekku/scripts/lib/core/frontmatter_metadata/` — per-kind `*_FRONTMATTER_METADATA` modules
  - `spec_driver/orchestration/enums.py` — current `ENUM_REGISTRY` (17 entries; F-17 split target)
  - `supekku/scripts/lib/changes/lifecycle.py` — `CHANGE_STATUSES`, `CANONICAL_STATUS_MAP`, `normalize_status()`
  - DEC-137-05, -14, -20, -23, -28 in DR-137 frontmatter

## 3. Entrance Criteria

- [x] DR-137 v3.1 accepted with edits (per notes.md 2026-05-18 entry)
- [x] IP-137 published with this phase referenced
- [x] DE-118 closed; `MetadataValidator(strict_unknown_keys=False)` opt-in baseline verified at `supekku/scripts/lib/blocks/metadata/validator.py:60`
- [x] DE-137 transitioned to `in-progress` before code edits begin
- [ ] Local toolchain green at start: `just check` passes against the current `main` so any regression from this phase is attributable

## 4. Exit Criteria / Done When

- [ ] `FieldMetadata` carries `aliases: Mapping[str, str] | None` + `tolerated_aliases: Mapping[str, ToleratedAlias] | None`; `BlockMetadata` carries `field_aliases: Mapping[str, str] | None`. New `ToleratedAlias` dataclass shipped.
- [ ] Per-kind alias matrix populated per DR-137 §5.2:
  - `delta.status`, `plan.status`, `phase.status`, `task.status` FieldMetadata.aliases cover the legacy values in the corpus-grounded matrix.
  - The shared relations-item `BlockMetadata.field_aliases = {"annotation": "nature"}`.
- [ ] Minimal `REVISION_FRONTMATTER_METADATA` and `ADR_FRONTMATTER_METADATA` (status-field only) registered in `FRONTMATTER_METADATA_REGISTRY` so derived `ENUM_REGISTRY` view covers `revision.status` and `adr.status`. Full schemas remain DE-142 / future-delta scope.
- [ ] `MetadataValidator.__init__(metadata)` only (no `strict_unknown_keys` kwarg); `.validate(data, *, strict: bool = False, accept_tolerated: bool = True)` returns `list[ValidationError]`; two-pass (field-NAME rename then per-field dispatch). F-54 collision case returns `error`-severity diagnostic without merging.
- [ ] `ValidationError` carries optional `fix_hint: str | None` + `fix_kind: Literal["rename_key", "rewrite_value"] | None`.
- [ ] All in-tree `MetadataValidator(...)` construction sites stop passing `strict_unknown_keys`; callers that need strictness pass `strict=True` to `.validate()`.
- [ ] `spec_driver/core/string_utils.py::closest_match(value, candidates) -> str | None` shipped (~5 LOC, stdlib `difflib`).
- [ ] `supekku/scripts/lib/blocks/metadata/aliases.py::normalize_field(kind, field, value) -> str` shipped; `changes/lifecycle.py::normalize_status` removed (no shim per DEC-137-14 / -23 spirit; callers migrate).
- [ ] `ENUM_REGISTRY` split: Category A entries become a registry-walking `_kind_status(kind)` derived view; Category B entries stay hardcoded (drift.status, command.format, requirement.kind, spec.kind, backlog.status, improvement.status, verification.kind).
- [ ] `CHANGE_STATUSES`/`REQUIREMENT_STATUSES`/`SPEC_STATUSES`/`POLICY_STATUSES`/`STANDARD_STATUSES`/`MEMORY_STATUSES`/`BACKLOG_BASE_STATUSES`/`RISK_STATUSES`/etc. become transition-window re-exports from per-kind metadata; `CANONICAL_STATUS_MAP` migrates to `FieldMetadata.aliases`. Each re-export module emits a `# OQ-137-02 sunset` comment.
- [ ] VT coverage green: VT-CC-008, VT-CC-009, VT-CC-010, VT-CC-011, VT-CC-012, VT-CC-013, VT-CC-030, VT-CC-034.
- [ ] `just check` (test + ruff + format + pylint ratchet) clean.

## 5. Verification

- **Unit tests** (added or extended):
  - `tests/spec_driver/core/string_utils_test.py` — VT-CC-010 (canonical typos at cutoff 0.6; semantic alternatives return None).
  - `tests/supekku/scripts/lib/blocks/metadata/schema_test.py` — `ToleratedAlias` dataclass + `FieldMetadata.aliases` / `tolerated_aliases` + `BlockMetadata.field_aliases` round-trip.
  - `tests/supekku/scripts/lib/blocks/metadata/validator_test.py` — VT-CC-008, 011, 030, 034 (two-pass behaviour; collision; strict/tolerant branches; fix_hint/fix_kind population).
  - `tests/supekku/scripts/lib/blocks/metadata/aliases_test.py` — `normalize_field` parity + missing-kind/missing-field fallthrough.
  - `tests/supekku/scripts/lib/changes/lifecycle_test.py` — VT-CC-013 normalize_status / normalize_field parity over every value in legacy `CANONICAL_STATUS_MAP` including `'complete' → 'completed'`.
  - `tests/spec_driver/orchestration/enums_test.py` — VT-CC-012 pre-split-vs-post-split parity (Category A derived view emits the same sorted lists as the pre-split hardcoded lambdas).
  - `tests/supekku/scripts/lib/blocks/metadata/validator_test.py` — VT-CC-009 tolerated-alias surface (accept on default; reject under `--no-tolerated-aliases`; `--fix` ignores).
- **Tooling / commands**:
  - `just test` — full suite.
  - `just lint` — ruff zero warnings.
  - `just pylint-files <paths>` — touched files; do not regress the ratchet.
  - `just check` — gate before declaring exit criteria.
- **Evidence to capture**: VT IDs and pass status into `notes.md`; pylint diff (paths only); ENUM_REGISTRY pre/post snapshot showing identical sorted lists per Category A key (for VT-CC-012 audit trail).

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `FRONTMATTER_METADATA_REGISTRY` is the canonical entrypoint to per-kind metadata at runtime; adding `revision` and `adr` entries there is sufficient to wire `revision.status` / `adr.status` into the derived view (verified in §5.2 walk).
  - `CANONICAL_STATUS_MAP` is the complete legacy alias inventory for change-status; the corpus grep in DR-137 §5.2 confirmed no extra values lurk in `.spec-driver/`.
  - Removing `strict_unknown_keys=` from `MetadataValidator.__init__` has a small in-tree ripple (mostly `validation/validator.py` + tests); confirm with a `grep -rn 'strict_unknown_keys'` audit before refactor.
  - Plan/phase/task share `PLAN_FRONTMATTER_METADATA`; populating aliases once on the shared `status` `FieldMetadata` covers all three kinds (per DR-137 §5.2 note).
- **STOP** when:
  - A populated FieldMetadata.aliases entry conflicts with an existing in-corpus value (e.g. a SPEC currently using `status: 'complete'` would silently flip under loader-default tolerant normalisation — confirm intent before merging). Run `validate workspace` post-change as a sanity check.
  - The retired `strict_unknown_keys=` parameter has consumers passing positionally (rare but possible) — fix-forward by reading errors and refactoring callers explicitly.
  - `ENUM_REGISTRY` parity (VT-CC-012) fails: the derived view returns a different set than the legacy lambda for any Category A key. Diagnose with side-by-side dump; do NOT paper over by hardcoding the missing values.
  - Test count or coverage drops on touched files (`just pylint-report` regression) — investigate before continuing.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | --- | --- | --- |
| [x] | 1.1 | Pre-flight grep audit + DE-137 status transition | [ ] | Audit in notes.md 2026-05-18 entry |
| [x] | 1.2 | `closest_match()` utility (`spec_driver/core/string_utils.py`) | [ ] | VT-CC-010 green (13 cases) |
| [x] | 1.3 | Extend schema dataclasses: `ToleratedAlias`, `FieldMetadata.aliases` + `.tolerated_aliases`, `BlockMetadata.field_aliases` | [ ] | Plus `FieldMetadata.field_aliases` (DR-extension; see notes) |
| [x] | 1.4 | Populate per-kind FieldMetadata.aliases matrix (delta/plan/phase/task status) + relations field_aliases | [P] | Extended to cover audit + revision (DR-extension; see notes) |
| [x] | 1.5 | Add minimal `REVISION_FRONTMATTER_METADATA` + `ADR_FRONTMATTER_METADATA` (status-only) and wire into `FRONTMATTER_METADATA_REGISTRY` | [P] | Both wired |
| [x] | 1.6 | Refactor `MetadataValidator`: retire `strict_unknown_keys` ctor kwarg; add `validate(*, strict, accept_tolerated)`; two-pass with F-54 collision branch | [ ] | Report-only design (no in-place mutation; see notes) |
| [x] | 1.7 | Migrate `MetadataValidator(...)` call sites to drop `strict_unknown_keys=`; pass `strict=` to `.validate()` | [ ] | 5 production + 8 test sites |
| [x] | 1.8 | Add `ValidationError.fix_hint` + `.fix_kind`; populate in 1.6 paths | [ ] | Plus `severity` field |
| [x] | 1.9 | Implement `normalize_field(kind, field, value)` in new `blocks/metadata/aliases.py`; retire `normalize_status()` | [ ] | VT-CC-013 parity green (9 matrix cases + case/whitespace) |
| [x] | 1.10 | Migrate `CANONICAL_STATUS_MAP` data into `FieldMetadata.aliases`; remove the map from `changes/lifecycle.py` | [ ] | Callers migrated to `normalize_field` |
| [x] | 1.11 | Split `ENUM_REGISTRY`: Category A becomes registry-walking `_kind_status(kind)`; Category B stays hardcoded | [ ] | VT-CC-012 parity green (22 paths); ISSUE-055 filed for drift gap |
| [x] | 1.12 | Convert lifecycle status constants to transition re-exports + sunset comment | [ ] | 8 modules: CHANGE/REQUIREMENT/SPEC/POLICY/STANDARD/MEMORY/BACKLOG_BASE+RISK/VERIFICATION/ADR |
| [x] | 1.13 | Author tests: VT-CC-008, 009, 010, 011, 012, 013, 030, 034 | [P] | All 8 VTs covered; see §5 evidence |
| [x] | 1.14 | Run `just check`; reconcile lint + pylint ratchet | [ ] | 4982 tests pass; ruff clean; pylint 9.69 (baseline 9.69; -8 messages) |
| [x] | 1.15 | Update notes.md + IP-137 progress checkbox; commit `feat(DE-137): land metadata aliases + strict validator (IP-137-P01)` | [ ] | This task |

### Task Details

- **1.1 Pre-flight grep audit + DE-137 status transition**
  - **Design / Approach**: `rg -n 'strict_unknown_keys|normalize_status|MetadataValidator\(' --type py` (record output in notes.md). Confirm DE-118 closed (`spec-driver list deltas --id DE-118`). Transition DE-137 to `in-progress` via `spec-driver` lifecycle command.
  - **Files / Components**: read-only.
  - **Testing**: n/a.
  - **Observations & AI Notes**: produces the authoritative ripple list for tasks 1.6 / 1.7.
  - **Commits / References**: status transition committed separately (`chore(DE-137): start IP-137-P01`).

- **1.2 `closest_match()` utility**
  - **Design / Approach**: ~5 LOC wrapping `difflib.get_close_matches(value, candidates, n=1, cutoff=0.6)`. Return `None` for empty / single-char inputs to avoid spurious matches. Pure function.
  - **Files / Components**: NEW `spec_driver/core/string_utils.py`; NEW `tests/spec_driver/core/string_utils_test.py`.
  - **Testing**: VT-CC-010 — canonical typos table from DR-137 §5.2 (`'complete'`, `'pendng'`, `'in_progres'`, `'defered'`, `'draaft'`) each surface expected match; `'live'`, `'active'`, `'done'`, `'wip'`, `''`, `'a'` return None.
  - **Observations & AI Notes**: cutoff=0.6 confirmed in DR-137 spike (DEC-137-20). Empty/single-char short-circuit prevents `'a' → 'audit'` style false positives.
  - **Commits / References**: bundleable with task 1.13 or standalone.

- **1.3 Schema dataclass extensions**
  - **Design / Approach**: in `supekku/scripts/lib/blocks/metadata/schema.py`, add `@dataclass(frozen=True) class ToleratedAlias` with `canonical`, `sunset_after`, `rationale` fields. Extend `FieldMetadata` with `aliases: Mapping[str, str] | None = None` and `tolerated_aliases: Mapping[str, ToleratedAlias] | None = None`. Extend `BlockMetadata` with `field_aliases: Mapping[str, str] | None = None`. All default `None`.
  - **Files / Components**: `supekku/scripts/lib/blocks/metadata/schema.py`, schema test extension.
  - **Testing**: VT round-trip — construct each variant via `dataclasses.replace`; assert field defaults; assert mutability semantics (Mapping accepts dict/MappingProxyType).
  - **Observations & AI Notes**: `tolerated_aliases` values are `ToleratedAlias` instances (not raw strings) so the sunset metadata travels with the alias.
  - **Commits / References**: blocks 1.4, 1.5, 1.6.

- **1.4 Per-kind alias matrix population**
  - **Design / Approach**: For each per-kind metadata module under `supekku/scripts/lib/core/frontmatter_metadata/`, populate the relevant `status` `FieldMetadata` with `aliases=` per DR-137 §5.2 corpus matrix:
    - `delta.status` aliases: `{"complete": "completed", "active": "in-progress", "done": "completed", "in_progress": "in-progress"}`
    - `plan.status`, `phase.status`, `task.status` (shared `PLAN_FRONTMATTER_METADATA`) aliases: `{"active": "in-progress", "done": "completed", "in_progress": "in-progress"}`
    - spec/audit/revision/design_revision: empty (reserved for DE-139/141/142)
  - For the shared **relations-item** `BlockMetadata` (used by delta, spec, audit, revision, design_revision, plan, phase), set `field_aliases = {"annotation": "nature"}`. Locate via `grep -rn 'relations' supekku/scripts/lib/core/frontmatter_metadata/`.
  - **Files / Components**: per-kind frontmatter_metadata modules; relations-block metadata module.
  - **Testing**: VT-CC-013 covers value normalisation parity. Add a focused test asserting `FRONTMATTER_METADATA_REGISTRY["delta"].fields["status"].aliases["complete"] == "completed"`.
  - **Observations & AI Notes**: `tolerated_aliases` stays empty in DE-137 (DR-137 §5.2 matrix); these are added by DE-138..142 as they migrate.
  - **Commits / References**: parallelisable across per-kind files.

- **1.5 Minimal REVISION + ADR metadata**
  - **Design / Approach**: NEW `supekku/scripts/lib/core/frontmatter_metadata/revision.py` and `.../adr.py`, each defining a `BlockMetadata` instance with a `status` `FieldMetadata` populated from the current `REVISION_STATUSES` / `ADR_STATUSES` literal (read at session start). Wire into `FRONTMATTER_METADATA_REGISTRY` under keys `revision` and `adr`. Full schemas remain DE-142 / future-delta scope — only `status` ships in DE-137.
  - **Files / Components**: NEW per-kind modules; `FRONTMATTER_METADATA_REGISTRY` source.
  - **Testing**: VT-CC-012 — assert `_kind_status("revision")()` returns sorted `REVISION_STATUSES`; same for `adr`.
  - **Observations & AI Notes**: DEC-137-28 / F-58 — without this, the Category-A derived view returns `[]` for `revision.status` / `adr.status` after task 1.11, silently breaking a previously valid enum.
  - **Commits / References**: parallelisable with 1.4.

- **1.6 `MetadataValidator` refactor**
  - **Design / Approach**: Per DR-137 §5.2 pseudo-code. Drop the `strict_unknown_keys` kwarg from `__init__`. Implement two-pass `.validate(data, *, strict=False, accept_tolerated=True)`:
    1. **Pass 1** — apply `metadata.field_aliases`: if `alias_key in data`, check for canonical collision (F-54 → error severity + abort fix); else rename; if `strict`, emit warning + `fix_kind="rename_key"` + `fix_hint=canonical_key`.
    2. **Pass 2** — per-field validation: unknown-key check (under `strict`); enum check with did-you-mean (via `closest_match`); `FieldMetadata.aliases` value normalisation with `strict`→warning + `fix_kind="rewrite_value"`; `tolerated_aliases` accepted under default, rejected under `accept_tolerated=False`.
  - **Files / Components**: `supekku/scripts/lib/blocks/metadata/validator.py`; `ValidationError` dataclass.
  - **Testing**: VT-CC-008 (field-NAME alias rename → warning + fix_kind/fix_hint); VT-CC-011 (unknown-key strict vs tolerant); VT-CC-030 (field-VALUE alias rewrite → warning + fix_kind/fix_hint); VT-CC-034 (collision: both keys present → error severity, no merge, fix declined); VT-CC-009 (tolerated alias accepted on default, rejected under `accept_tolerated=False`).
  - **Observations & AI Notes**: existing `validator.py:548` `--fix` codepath (phase-status auto-repair) consumes `fix_hint` after this lands; that integration is part of IP-137-P03 (CLI). Keep the in-memory diagnostic surface complete here.
  - **Commits / References**: bundle with 1.7 + 1.8.

- **1.7 Caller migration for `strict_unknown_keys` kwarg removal**
  - **Design / Approach**: mechanical refactor of every `MetadataValidator(metadata, strict_unknown_keys=…)` site to `MetadataValidator(metadata)` + downstream `.validate(..., strict=<that bool>)`. From task 1.1 audit, the live ripple is small (predominantly `supekku/scripts/lib/validation/validator.py` plus tests).
  - **Files / Components**: per task-1.1 audit output.
  - **Testing**: existing validator tests must continue to pass (red→green at each call-site update).
  - **Observations & AI Notes**: positional callers (rare) caught by ruff `unexpected-keyword-argument` — fix-forward, do NOT add a back-compat kwarg.
  - **Commits / References**: bundle with 1.6.

- **1.8 `ValidationError` extensions**
  - **Design / Approach**: Add `fix_hint: str | None = None` and `fix_kind: Literal["rename_key", "rewrite_value"] | None = None` to `ValidationError`. Existing call sites that build `ValidationError(...)` continue to work because new fields default. Populate from task 1.6 paths only.
  - **Files / Components**: `ValidationError` dataclass (in `validator.py` or wherever currently defined).
  - **Testing**: covered by VT-CC-008 + VT-CC-030 assertions on diagnostic shape.
  - **Observations & AI Notes**: `fix_kind` typed as a `Literal` for static checks; consumer dispatch in IP-137-P03 `--fix` uses `match` statement.
  - **Commits / References**: bundle with 1.6.

- **1.9 `normalize_field` + retirement of `normalize_status`**
  - **Design / Approach**: NEW `supekku/scripts/lib/blocks/metadata/aliases.py` exporting `normalize_field(kind: str, field: str, value: str) -> str`. Reads `FRONTMATTER_METADATA_REGISTRY[kind].fields[field]` and applies `.aliases.get(value, value)`. Returns `value` unchanged if metadata or alias map absent. Tolerated aliases also normalised at this layer (read-time tolerance is the default; strict gating happens in the validator).
  - **Files / Components**: NEW module + test; remove `normalize_status` from `supekku/scripts/lib/changes/lifecycle.py` and migrate its (small) caller surface.
  - **Testing**: VT-CC-013 — parametric assertion that the new function returns the same canonical as legacy `normalize_status` for every legacy value (`complete → completed`, plus the `active`/`done`/`in_progress` trio) when invoked as `normalize_field("delta", "status", value)`.
  - **Observations & AI Notes**: per DEC-137-23, fail-soft (return unchanged) keeps loaders tolerant; strictness is the validator's concern.
  - **Commits / References**: depends on 1.4 alias data.

- **1.10 `CANONICAL_STATUS_MAP` migration**
  - **Design / Approach**: The legacy hardcoded `CANONICAL_STATUS_MAP` becomes the FieldMetadata.aliases entries from task 1.4. Delete the map and any imports of it; the per-kind metadata is now the source. Audit `changes/lifecycle.py` for `CANONICAL_STATUS_MAP` consumers; replace each with a `normalize_field("delta", "status", value)` call.
  - **Files / Components**: `changes/lifecycle.py` + downstream callers (likely formatter or registry).
  - **Testing**: VT-CC-013 parity (above).
  - **Observations & AI Notes**: ensure delete-don't-shim discipline — DEC-137-15 spirit applies (clear migration, no back-compat layer).
  - **Commits / References**: bundle with 1.9.

- **1.11 `ENUM_REGISTRY` split**
  - **Design / Approach**: In `spec_driver/orchestration/enums.py`, replace the Category A hardcoded lambdas with the `_kind_status(kind)` factory per DR-137 §5.2 step 3. Keep Category B entries (`drift.status`, `command.format`, `requirement.kind`, `spec.kind`, `backlog.status`, `improvement.status`, `verification.kind`) as-is — they stay hardcoded. File a backlog `ISSUE-` (via `spec-driver create issue`) for the `drift` registry gap (DR-137 §5.2 Category B note); do NOT inline-fix in this phase.
  - **Files / Components**: `spec_driver/orchestration/enums.py`; backlog `ISSUE-NNN` (drift gap).
  - **Testing**: VT-CC-012 — for every Category A key, derived view returns sorted list equal to the pre-split lambda's result (capture pre-split snapshot before code change, assert equality after).
  - **Observations & AI Notes**: depends on task 1.5 minimal revision/adr metadata; without it, `revision.status` returns `[]` and VT-CC-012 fails for that key.
  - **Commits / References**: gate task — verify VT-CC-012 green before moving on.

- **1.12 Lifecycle-constant transition re-exports**
  - **Design / Approach**: For each currently-hardcoded status constant in `supekku/scripts/lib/changes/lifecycle.py`, `supekku/scripts/lib/requirements/...`, etc., replace the literal definition with a derivation from the per-kind metadata, e.g.:
    ```python
    CHANGE_STATUSES: frozenset[str] = frozenset(
      DELTA_FRONTMATTER_METADATA.fields["status"].enum_values
    )
    ```
    Add a `# OQ-137-02 sunset` comment to each re-export so the future cleanup delta can `grep` for them. Add a `DeprecationWarning` on import (F-43 disposition) is **out of scope for IP-137-P01** — defer to umbrella close to avoid noisy import-time warnings during DE-138..142 work.
  - **Files / Components**: `changes/lifecycle.py`, `requirements/<status_module>.py` (locate by grep), any other module currently hardcoding status sets.
  - **Testing**: existing tests asserting set membership continue to pass (derivation is equivalent).
  - **Observations & AI Notes**: F-43 DeprecationWarning explicitly deferred to OQ-137-02 resolution; recording here so reviewers don't expect it.
  - **Commits / References**: bundle with 1.10.

- **1.13 Test authoring**
  - **Design / Approach**: Author VT files per the §5 inventory. Pair each VT with the production task it covers (parallelisable). Use existing test conventions in `tests/supekku/scripts/lib/blocks/metadata/` and `tests/spec_driver/`.
  - **Files / Components**: new test files (see §5 list).
  - **Testing**: this *is* the testing.
  - **Observations & AI Notes**: VT-CC-012 needs a pre-change snapshot — capture before task 1.11 lands.
  - **Commits / References**: each VT can land with its production task; bundle tail VTs (12, 13) at phase close.

- **1.14 Acceptance gate (`just check`)**
  - **Design / Approach**: run `just check`. Address every failure (test, ruff, pylint ratchet, format). For pylint, regression on touched files is treated as a blocker per CLAUDE.md.
  - **Files / Components**: as needed.
  - **Testing**: this is the verification gate.
  - **Observations & AI Notes**: if pylint surfaces pre-existing warnings on files this phase didn't touch, do NOT silence — confirm out-of-scope and leave; CLAUDE.md is explicit.
  - **Commits / References**: any cleanups separate from the feature commits.

- **1.15 Phase wrap-up**
  - **Design / Approach**: Update `notes.md` with VT status + ENUM_REGISTRY snapshot evidence. Check the IP-137 `Progress Tracking` box for P01. Commit phase work as `feat(DE-137): land metadata aliases + strict validator (IP-137-P01)`.
  - **Files / Components**: `notes.md`, `IP-137.md`, `phases/phase-01.md`.
  - **Testing**: n/a (paperwork).
  - **Observations & AI Notes**: hand off to IP-137-P02 by creating `phases/phase-02.md` only after this phase's exit criteria are met.
  - **Commits / References**: final phase commit.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| `strict_unknown_keys=` kwarg has positional callers — mechanical refactor misses them | Use ruff `unexpected-keyword-argument` + `just test` to catch; do NOT add back-compat shim | open |
| `FieldMetadata.aliases` populated for `delta.status` silently rewrites in-corpus values on read | Default-tolerant loader path preserves observable behaviour; the alias is a no-op for already-canonical values; run `validate workspace` post-1.4 to confirm no surprise warnings | open |
| `ENUM_REGISTRY` parity fails because Category B keys aren't separated cleanly | DR-137 §5.2 explicitly enumerates Category A vs B; task 1.11 implements only Category A as derived; Category B stays untouched | open |
| `revision.status` / `adr.status` minimal metadata diverges from the canonical status literal currently in use | Source the enum from the existing `REVISION_STATUSES` / `ADR_STATUSES` constants verbatim (task 1.5) so VT-CC-012 trivially passes | open |
| `CANONICAL_STATUS_MAP` consumers depend on the map's identity (e.g. iteration order) | Grep for direct references before removal (task 1.10); migrate each to `normalize_field` explicitly | open |

## 9. Decisions & Outcomes

- `2026-05-18` — Defer F-43 `DeprecationWarning` on re-export imports to OQ-137-02 resolution (post-umbrella cleanup), to avoid noisy warnings during DE-138..142 implementation. Recorded in task 1.12.
- `2026-05-18` — File backlog ISSUE for `drift` registry gap during task 1.11 rather than inline-fix; keeps Category-B surface frozen for this delta.

## 10. Findings / Research Notes

- Pre-flight grep (task 1.1) output captured in `notes.md` once executed.
- Pre-split `ENUM_REGISTRY` snapshot (for VT-CC-012 parity audit) saved alongside task 1.11 commit.
- Any unexpected `strict_unknown_keys=True` consumer surfaced during task 1.7 recorded inline here.

## 11. Wrap-up Checklist

- [x] Exit criteria (all bullets in §4) satisfied
- [x] Verification evidence stored in `notes.md` (VT pass status; ENUM_REGISTRY parity snapshot; grep audit output)
- [x] IP-137 §9 progress box for P01 checked
- [x] Hand-off note in `notes.md` summarising any new constraints for IP-137-P02 (e.g. confirmed yaml_emit dependency surface, FieldMetadata shape locked)
