---
id: IP-137-P02
slug: "137-cross_cutting_metadata_schema_infrastructure_validation_templates_cli_migrate_orchestrator_de_136_child-phase-02"
name: IP-137 Phase 02 - Template infrastructure + emit split + first regeneration
created: "2026-05-18"
updated: "2026-05-18"
status: draft
kind: phase
plan: IP-137
delta: DE-137
---

# IP-137-P02 — Template infrastructure + emit split + first regeneration

## 1. Objective

Land the **template + emit infrastructure** that consumes the P01 metadata source-of-truth:

- New comment-preserving YAML emitter (`spec_driver/core/yaml_emit.py`) — stdlib-yaml plus a thin trailing-comment layer (~60 LOC target; OQ-137-01 gate at ≤~120 LOC).
- New template orchestration module (`spec_driver/orchestration/templates.py`) with `TEMPLATE_PLACEHOLDERS`, `render_frontmatter_for_kind(kind, data=None)`, `regenerate_template(kind, template_path)`, and `validate_templates(repo_root)`.
- Split `dump_markdown_file` into `dump_markdown_file_create(..., kind=)` and `dump_markdown_file_update(...)` per DEC-137-15 / F-1; remove the legacy entrypoint (no shim).
- Migrate every in-tree caller per the DR-137 §5.1 ripple table (11 create-path + 9 update-path production sites + the test ripple).
- Wire two CLI surfaces: `spec-driver admin regenerate-templates` and `spec-driver validate templates`, plus a `just validate-templates` target.
- Run one-time regeneration against `supekku/templates/*.md` and commit the templates with their new regenerable frontmatter.

No CLI for validate workspace/file (P03), no migrations (P04), no skill gates (P05).

## 2. Links & References

- **Delta**: DE-137
- **Design Revision Sections**:
  - DR-137 §5.1 (Deliverable Y — Template regeneration + comment-preserving emit; full ripple table)
  - DR-137 §3.1 outcomes 1, 5 (POL-001 single-emit-renderer; F-1 split)
  - DR-137 §11 (verification catalogue) — VT-CC-001, 002, 003, 004, 005, 006, 007, 024
  - DR-137 §7 (DEC-137-09 placeholder placement, DEC-137-15 split-without-shim, DEC-137-25 atomic write)
- **Specs / PRODs**: PROD-004 (FR-001), SPEC-114 (blocks/metadata), SPEC-116 (frontmatter_metadata), SPEC-125 (validation)
- **Support Docs**:
  - `supekku/scripts/lib/core/spec_utils.py:62` — current `dump_markdown_file` (split target)
  - `supekku/scripts/lib/core/frontmatter_writer.py` — current YAML dump path (`dump_frontmatter_yaml`)
  - `supekku/scripts/lib/core/frontmatter_metadata/` — per-kind `BlockMetadata` consumed by the renderer
  - `supekku/templates/*.md` — body-only Jinja templates today; gain regenerable frontmatter in this phase
  - `supekku/cli/main.py` — Typer wiring entrypoint for the new CLI modules
  - DEC-137-09, -15, -25 in DR-137 frontmatter
  - P01 hand-off note in `notes.md` — `FieldMetadata` shape locked; `normalize_field` available

## 3. Entrance Criteria

- [x] IP-137-P01 complete and committed (P01 phase sheet exit criteria satisfied)
- [x] `FieldMetadata.aliases` / `.tolerated_aliases` / `.field_aliases` available; per-kind metadata populated for delta/plan/phase/task status + relations field-aliases
- [x] DR-137 v3.1 accepted (ratified at P01 entrance); no design ambiguity outstanding for §5.1
- [ ] Local toolchain green at start: `just check` passes on the post-P01 `main` (re-verify so any regression in this phase is attributable)
- [ ] Pre-flight grep audit captured: list every `dump_markdown_file(...)` call site (production + tests) and tag each as `create` / `update` / `bypass` per DR-137 §5.1 table

## 4. Exit Criteria / Done When

- [ ] `spec_driver/core/yaml_emit.py::emit_yaml_block(data, comments=None)` shipped — primitives, lists, nested dicts emit deterministically; top-level keys with simple-type values accept inline `# comment` trailing strings; ≤~120 LOC (OQ-137-01 gate).
- [ ] `spec_driver/orchestration/templates.py` shipped with `TEMPLATE_PLACEHOLDERS`, `render_frontmatter_for_kind(kind, data=None)`, `regenerate_template(kind, template_path) -> bool`, `validate_templates(repo_root) -> list[TemplateDrift]` (or equivalent). Renderer derives the comment map from `FRONTMATTER_METADATA_REGISTRY[kind]` (enum field ⇒ `# one of: …`; tolerated alias ⇒ sunset note). Aliases NOT shown in output.
- [ ] `dump_markdown_file` removed; `dump_markdown_file_create(path, frontmatter, body, *, kind)` and `dump_markdown_file_update(path, frontmatter, body)` shipped in `supekku/scripts/lib/core/spec_utils.py`. `_create` errors if `path` already exists; `_update` reads + preserves trailing `# ...` comments from the existing frontmatter region. Both atomic (temp + rename).
- [ ] All production create-path callers (11 sites from DR-137 §5.1) migrated to `_create(..., kind=<literal>)`.
- [ ] All production update-path callers (9 sites from DR-137 §5.1) migrated to `_update(...)`.
- [ ] All test callers migrated to whichever variant matches the system-under-test (≥12 sites; mechanical).
- [ ] `grep -rn 'dump_markdown_file\b' --include='*.py'` returns zero matches outside `_create` / `_update` definitions and intentional negative-assertion lines in tests (if any).
- [ ] `spec-driver admin regenerate-templates` Typer command shipped (`--dry-run` flag; optional positional `<kind>` filter) — wired into `supekku/cli/main.py`.
- [ ] `spec-driver validate templates` Typer command shipped — non-zero exit on drift, zero on clean — wired into `supekku/cli/main.py`.
- [ ] `justfile` carries `validate-templates` target invoking `uv run spec-driver validate templates`.
- [ ] `supekku/templates/*.md` regenerated once and committed — every template carries a leading `---` frontmatter block with kind-aware placeholders + enum-comment hints; bodies preserved verbatim (Jinja blocks intact).
- [ ] `just validate-templates` clean on the committed templates.
- [ ] VT coverage green: VT-CC-001, VT-CC-002, VT-CC-003, VT-CC-004, VT-CC-005, VT-CC-006, VT-CC-007, VT-CC-024.
- [ ] `just check` (test + ruff + format + pylint ratchet) clean.
- [ ] OQ-137-01 disposition recorded in notes.md: actual LOC count of `yaml_emit.py`; either confirm ≤~120 (keep stdlib path) or initiate ruamel.yaml swap.

## 5. Verification

- **Unit tests** (added or extended):
  - `tests/spec_driver/core/yaml_emit_test.py` — VT-CC-005 (primitives + containers; ~10 case table), VT-CC-006 (deterministic output across repeated invocations + sorted-key vs insertion-order semantics).
  - `tests/spec_driver/orchestration/templates_test.py` — VT-CC-001 (regenerated template carries enum-comment string for ≥1 field per kind), VT-CC-002 (regenerator idempotency: second invocation returns `False` / no diff), VT-CC-007 (malformed user template fails install loudly with path + parse error), VT-CC-024 (comment-map invariance: `data=None` vs `data=sample_fm` produces identical comment ordering + content).
  - `tests/spec_driver/presentation/cli/validate/templates_test.py` — VT-CC-003 (`validate templates` returns non-zero on metadata drift, zero on clean repo); use a fixture template tree under `tests/fixtures/de_137/templates/`.
  - `tests/supekku/scripts/lib/changes/<creation_test>.py` (or equivalent) — VT-CC-004 (artefact created via `spec-driver create <kind>` carries inline enum-comment hints in frontmatter).
  - `tests/supekku/scripts/lib/core/spec_utils_test.py` — `dump_markdown_file_create` (NEW path; error on existing path; comment-hints present for known kinds; atomicity smoke), `dump_markdown_file_update` (preserves existing trailing-comment map; idempotent round-trip).
- **Tooling / commands**:
  - `just test` — full suite, including the new VT files.
  - `just lint` — ruff zero warnings.
  - `just pylint-files <touched paths>` — no regression on touched files.
  - `just validate-templates` — gate on the committed `supekku/templates/*.md`.
  - `just check` — phase gate.
- **Evidence to capture** (in `notes.md`):
  - VT IDs + pass status table.
  - LOC count of `spec_driver/core/yaml_emit.py` (OQ-137-01 disposition).
  - Pre-migration `dump_markdown_file` callers audit (full list from task 2.1) + post-migration grep showing zero leftover refs.
  - Diff summary of regenerated `supekku/templates/*.md` (frontmatter inserted; bodies unchanged).

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - The relations-item `BlockMetadata` populated in P01 carries the comment map; `render_frontmatter_for_kind` only emits **top-level** key comments per DR-137 §5.1 (nested objects fall through to `yaml.safe_dump`). VT-CC-024 covers top-level comment-map shape; nested comment surface is out of scope for this phase.
  - `frontmatter_writer.dump_frontmatter_yaml` (current production emit path) is replaced by `emit_yaml_block` everywhere `dump_markdown_file_*` is called. Any **direct** callers of `dump_frontmatter_yaml` outside the dump helpers are flagged during task 2.1 audit and migrated explicitly or documented as out-of-scope.
  - Templates currently lack frontmatter (verified: `supekku/templates/delta.md` opens with `# {{ delta_id }} – {{ name }}`). `regenerate_template` therefore inserts a fresh `---` block at the top of every template in the one-time regeneration (task 2.13). Idempotency tests run *after* this insertion.
  - The DR-137 §5.1 ripple table is authoritative for production sites. Task 2.1 confirms zero new sites have been added since DR-137 v3.1 was ratified; any drift is reconciled before migration starts.
  - `kind=<literal>` strings used at create-path sites match `FRONTMATTER_METADATA_REGISTRY` keys exactly (`"delta"`, `"phase"`, `"audit"`, `"revision"`, `"plan"`, `"requirement"`, `"spec"`, `"spec_tests"`, `"memory"`, `"issue"` | `"improvement"` | `"risk"` | `"problem"`). Renderer raises `KeyError` (or a typed wrapper) on unknown kind — fail-loud per F-13 spirit.
- **STOP** when:
  - `yaml_emit.py` exceeds ~120 LOC or hits a stdlib-yaml edge case during VT-CC-005 implementation — OQ-137-01 triggers; **stop coding** and `/consult` for ruamel.yaml swap authorisation before continuing.
  - The dump_markdown_file ripple count diverges meaningfully from DR-137 §5.1 (e.g. >5 unaccounted-for sites surface) — reconcile via `/consult` before mass migration; the design may need an update.
  - Comment-map invariance (VT-CC-024) fails — the renderer's comment derivation depends on data shape unexpectedly; diagnose via golden-file diff. Do NOT paper over by branching the comment path on `data is None`.
  - One-time template regeneration produces a body-diff (not just frontmatter insertion) on any committed template — the regenerator is touching too much. Diagnose; do not commit corrupted templates.
  - `validate templates` is non-zero on the freshly regenerated committed templates — the renderer or the regenerator is non-idempotent. Block phase exit.
  - `just check` surfaces a pylint regression on a file this phase did not touch — confirm out-of-scope and leave per CLAUDE.md; do NOT silence.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID   | Description | Parallel? | Notes |
| ------ | ---- | --- | --- | --- |
| [ ] | 2.1  | Pre-flight grep audit of `dump_markdown_file` callers + reconcile against DR-137 §5.1 ripple table | [ ] | Authoritative input for 2.6/2.7/2.8 |
| [ ] | 2.2  | Implement `spec_driver/core/yaml_emit.py::emit_yaml_block` + tests (VT-CC-005, VT-CC-006) | [P] | OQ-137-01 watch ≤~120 LOC |
| [ ] | 2.3  | Implement `spec_driver/orchestration/templates.py::TEMPLATE_PLACEHOLDERS` + `render_frontmatter_for_kind(kind, data=None)` + tests (VT-CC-024) | [ ] | Depends on 2.2 |
| [ ] | 2.4  | Implement `regenerate_template(kind, path)` + `validate_templates(repo_root)` + tests (VT-CC-001, VT-CC-002, VT-CC-007) | [ ] | Atomic temp+rename; depends on 2.3 |
| [ ] | 2.5  | Split `dump_markdown_file` into `_create(..., kind=)` + `_update(...)`; add update-path comment extraction; delete legacy entrypoint | [ ] | `spec_utils.py`; depends on 2.3 |
| [ ] | 2.6  | Migrate 11 create-path production callers per DR-137 §5.1 table | [P] | Mechanical; group by file |
| [ ] | 2.7  | Migrate 9 update-path production callers per DR-137 §5.1 table | [P] | Mechanical |
| [ ] | 2.8  | Migrate test callers (≥12 sites) to matching variant | [P] | Drives test green during migration |
| [ ] | 2.9  | Confirm zero stale `dump_markdown_file(` references via grep | [ ] | Gate before CLI wiring |
| [ ] | 2.10 | Wire `spec-driver admin regenerate-templates` CLI (Typer module + main.py registration) | [ ] | `--dry-run`; positional `<kind>` filter |
| [ ] | 2.11 | Wire `spec-driver validate templates` CLI (Typer module + main.py registration) + VT-CC-003 test | [ ] | Non-zero on drift |
| [ ] | 2.12 | Add `just validate-templates` justfile target | [ ] | One-liner; ensures CI gate hookable |
| [ ] | 2.13 | One-time regeneration of `supekku/templates/*.md`; commit with frontmatter | [ ] | Bodies must remain byte-identical except inserted frontmatter |
| [ ] | 2.14 | Author VT-CC-004 (created artefact carries inline enum-comment hints) | [P] | Uses `spec-driver create` end-to-end |
| [ ] | 2.15 | `just check`; reconcile lint + pylint ratchet | [ ] | Phase gate |
| [ ] | 2.16 | Update `notes.md` + IP-137 progress; record OQ-137-01 disposition; commit phase | [ ] | `feat(DE-137): template emit infra + one-time regen (IP-137-P02)` |

### Task Details

- **2.1 Pre-flight grep audit**
  - **Design / Approach**: `rg -n 'dump_markdown_file\b' --type py` and `rg -n 'dump_frontmatter_yaml\b' --type py`. Tag each call site `create` / `update` / `bypass` per DR-137 §5.1 table. Reconcile against the table — flag any extra/missing sites. Capture output in `notes.md` as the authoritative ripple list.
  - **Files / Components**: read-only.
  - **Testing**: n/a.
  - **Observations & AI Notes**: confirms the migration surface before any code edit; protects against silent ripple drift since DR ratification.
  - **Commits / References**: audit committed with `chore(DE-137): pre-flight audit IP-137-P02` if a discrete commit makes sense; otherwise rolled into the first code commit.

- **2.2 `emit_yaml_block` implementation**
  - **Design / Approach**: New `spec_driver/core/yaml_emit.py`. Stdlib `yaml.safe_dump` for the data shell; thin trailing-comment layer that walks the emitted lines and appends `  # <comment>` to lines whose key matches the `comments` map (top-level scalars only — containers receive no trailing comment per DR-137 §5.1). Preserve dict insertion order. Strip the trailing `\n` that `safe_dump` adds and re-add it after comment injection to guarantee a single trailing newline.
  - **Files / Components**: NEW `spec_driver/core/yaml_emit.py`; NEW `tests/spec_driver/core/yaml_emit_test.py`.
  - **Testing**: VT-CC-005 — string, int, bool, None, list-of-strings, list-of-dicts, nested dict, empty dict, empty list, mixed; assert each emits well-formed YAML and that comments are appended to expected top-level keys. VT-CC-006 — same input emits byte-identical output across repeated invocations; insertion-order preserved.
  - **Observations & AI Notes**: OQ-137-01 watch — if the LOC count creeps past ~120, escalate via STOP. Watch for stdlib-yaml's tendency to fold long strings; we want `default_flow_style=False, sort_keys=False, allow_unicode=True`.
  - **Commits / References**: standalone commit acceptable; or bundle with 2.3.

- **2.3 `render_frontmatter_for_kind` + `TEMPLATE_PLACEHOLDERS`**
  - **Design / Approach**: NEW `spec_driver/orchestration/templates.py`. Define `TEMPLATE_PLACEHOLDERS: Mapping[str, Mapping[str, str]]` per DR-137 §5.1 (one entry per kind covering required-with-no-default fields: `id`, `slug`, `name`, `created`, `updated`). `render_frontmatter_for_kind(kind, data=None)` → resolve `BlockMetadata` from `FRONTMATTER_METADATA_REGISTRY[kind]`; build the comment map from `FieldMetadata.enum_values` (`# one of: a | b | c`) and `tolerated_aliases` (`# tolerated until <sunset>: ...` per entry) — note aliases are NOT shown (validator-side concern). When `data=None`, emit placeholder values from `TEMPLATE_PLACEHOLDERS[kind]` falling back to `FieldMetadata.default_value` for optional fields. When `data` is provided, emit those values. Delegate emit to `emit_yaml_block`.
  - **Files / Components**: NEW `spec_driver/orchestration/templates.py`; NEW `tests/spec_driver/orchestration/templates_test.py`.
  - **Testing**: VT-CC-024 — for every kind, build the comment map with `data=None` and again with `data=<sample fm>`; assert the dicts are byte-equal (same keys, same ordering, same comment strings). Golden-file outputs (one per kind) for placeholder-mode output shape.
  - **Observations & AI Notes**: `TEMPLATE_PLACEHOLDERS` lives in `orchestration/`, not `BlockMetadata` (DEC-137-09; keeps `BlockMetadata` pure data). The renderer is the **single** comment-emitting surface; both `regenerate_template` and `dump_markdown_file_create` route through it (POL-001).
  - **Commits / References**: bundles with 2.4.

- **2.4 `regenerate_template` + `validate_templates`**
  - **Design / Approach**: `regenerate_template(kind, template_path) -> bool` reads the existing file; locates the closing `---` (if any) of an existing frontmatter block; replaces only the frontmatter region with the output of `render_frontmatter_for_kind(kind, data=None)`; preserves the body verbatim (Jinja blocks, prose, headings). If no frontmatter block exists, inserts one at the top. Atomic (temp + rename). Returns `True` iff bytes changed. `validate_templates(repo_root)` walks `repo_root/supekku/templates/` (or the configured templates dir), calls `regenerate_template` in dry-run mode (compare proposed bytes to current), returns a list of `TemplateDrift` records (path, kind, unified diff). Empty list ⇒ clean.
  - **Files / Components**: same `templates.py`; tests file as above.
  - **Testing**: VT-CC-001 — render every kind, assert ≥1 enum-comment string present in the output. VT-CC-002 — call `regenerate_template` twice on the same file; second call returns `False` and bytes unchanged. VT-CC-007 — fixture template with malformed YAML frontmatter ⇒ `regenerate_template` raises a typed error containing the path + parse-error message (no Rich traceback; resolves F-13).
  - **Observations & AI Notes**: atomic write uses `Path.write_text` via a temp file in the same directory then `os.replace` (DEC-137-25). Body preservation MUST be byte-exact — write a regression test asserting `body_after == body_before` for a template with an intact body.
  - **Commits / References**: bundles with 2.3.

- **2.5 `dump_markdown_file` split**
  - **Design / Approach**: In `supekku/scripts/lib/core/spec_utils.py`:
    - Add `dump_markdown_file_create(path, frontmatter, body, *, kind)` — raise `FileExistsError` if `path.exists()`; call `render_frontmatter_for_kind(kind, data=frontmatter)`; combine with body; atomic write.
    - Add `dump_markdown_file_update(path, frontmatter, body)` — read existing file head; lex trailing `# ...` comments per top-level key with a focused regex (capture map `{key: comment_text}`); call `emit_yaml_block(frontmatter, comments=<extracted map>)`; combine with body; atomic write.
    - Delete the original `dump_markdown_file` once 2.6/2.7/2.8 land (no shim).
  - **Files / Components**: `supekku/scripts/lib/core/spec_utils.py`; tests in `tests/supekku/scripts/lib/spec_utils_test.py` (or co-located).
  - **Testing**: `_create` round-trip per kind (frontmatter + body parse-back equal to input); `_create` raises on pre-existing path; `_update` preserves comments on a fixture with `key: value  # legacy hint` entries; `_update` idempotent (second write byte-identical when data unchanged).
  - **Observations & AI Notes**: comment-extraction regex pattern: `^(?P<key>[A-Za-z_][\w-]*):\s*.*?(?:\s+#\s*(?P<comment>.*?))?\s*$` — handle only single-line scalar values; comments on container-keyed lines (e.g. `aliases:`) tracked as "associated with previous key" if necessary, but a clean MVP attaches comments only to scalar lines. Bypasses: `regenerate_template`, `validate --fix` (P03), migrations (P04) — these use lower-level utilities.
  - **Commits / References**: bundles with 2.6/2.7/2.8 (single mass-migration commit acceptable, or staged per directory).

- **2.6 Create-path caller migration**
  - **Design / Approach**: Mechanical replacement per DR-137 §5.1 table:
    - `supekku/scripts/lib/changes/delta_creation.py:105,141` — `kind="delta"` (both sites; second is the phase-N sheet written during scaffolding — confirm `kind="phase"` if the second site writes a phase, not a delta).
    - `supekku/scripts/lib/changes/phase_creation.py:486` — `kind="phase"`.
    - `supekku/scripts/lib/changes/audit_creation.py:96` — `kind="audit"`.
    - `supekku/scripts/lib/changes/revision_creation.py:92` — `kind="revision"`.
    - `supekku/scripts/lib/changes/creation.py:95` — `kind="plan"`.
    - `supekku/scripts/lib/changes/creation.py:245` — `kind="requirement"` (call site hardcodes the kind in the frontmatter dict; lift to explicit kwarg).
    - `supekku/scripts/lib/specs/creation.py:169` — `kind="spec"` (covers PROD via the kind argument; confirm site passes the right literal — possibly `kind=spec_kind` where `spec_kind` is "spec" or "prod_spec").
    - `supekku/scripts/lib/specs/creation.py:188` — `kind="spec_tests"`.
    - `supekku/cli/resolve.py:284` — `kind="memory"`.
    - `supekku/scripts/lib/backlog/registry.py:397` — `kind=<caller-provided>` (issue/improvement/risk/problem; caller already passes the discriminator).
  - **Files / Components**: each file above.
  - **Testing**: existing creation tests must continue to pass; new artefacts created during the test suite carry inline enum-comments (VT-CC-004 verifies one end-to-end).
  - **Observations & AI Notes**: line numbers are DR-ratification-era; re-verify with task 2.1 grep before editing. The `creation.py:245` and `backlog/registry.py:397` callers are the two that already had `kind` in the frontmatter dict — lift the discriminator to the kwarg.
  - **Commits / References**: bundles with 2.5.

- **2.7 Update-path caller migration**
  - **Design / Approach**: Mechanical replacement per DR-137 §5.1 table:
    - `supekku/scripts/lib/core/frontmatter_writer.py:138,176,226` — three rewrite paths (status flip, generic write, frontmatter-only update).
    - `spec_driver/domain/relations/manager.py:105,142` — relations manager add/remove paths.
    - `supekku/cli/compact.py:74` — compaction rewrite.
    - `supekku/scripts/sync_specs.py:140,160,184` — three spec-rewrite paths.
    - `scripts/normalise_frontmatter.py:35` — one-off normaliser.
  - **Files / Components**: each file above.
  - **Testing**: existing update-path tests must pass; comment-preservation regression test added for a representative update site (e.g. frontmatter_writer status flip on a file with inline enum comments).
  - **Observations & AI Notes**: re-verify line numbers via task 2.1 grep.
  - **Commits / References**: bundles with 2.5.

- **2.8 Test caller migration**
  - **Design / Approach**: For each test file currently calling `dump_markdown_file(...)`, migrate to the variant matching the system-under-test. Tests for `*_creation.py` modules typically need `_create`; tests for relations/sync/writer typically need `_update`. Where a test is using `dump_markdown_file` as a fixture-builder (creating a starter artefact for the test), prefer `_create` to keep the kind discriminator explicit.
  - **Files / Components**: `tests/supekku/scripts/lib/` subdirectories (changes, requirements, relations, specs, validation, core); `tests/spec_driver/orchestration/`; CLI tests.
  - **Testing**: the migrations themselves are the testing — once all call sites migrate, the legacy entrypoint deletion (task 2.9) cannot regress hidden references.
  - **Observations & AI Notes**: 12+ ripple sites; bulk-edit acceptable. Use `rg -l dump_markdown_file --type py` post-edit to confirm zero leftovers in tests.
  - **Commits / References**: bundles with 2.5.

- **2.9 Confirm zero stale references**
  - **Design / Approach**: `rg -n 'dump_markdown_file\b' --type py`. Acceptable matches: the `_create` and `_update` definitions; explicit negative-test lines (if any test asserts the legacy name is gone). All other matches must be migrated. Delete the legacy `dump_markdown_file(...)` function from `spec_utils.py`.
  - **Files / Components**: `supekku/scripts/lib/core/spec_utils.py` (delete legacy fn).
  - **Testing**: `just test` must pass after deletion — proves no hidden caller.
  - **Observations & AI Notes**: this is the F-1 "no shim" gate; do not leave a backwards-compatibility wrapper.
  - **Commits / References**: gate task — bundles with 2.5.

- **2.10 `admin regenerate-templates` CLI**
  - **Design / Approach**: NEW `spec_driver/presentation/cli/admin/regenerate_templates.py` (Typer subcommand). Arguments: optional positional `kind: str | None`; flag `--dry-run / --no-dry-run` (default `False`). Behaviour: walks templates dir; for each kind matching (or all), call `regenerate_template`; report changed paths (and unified diff if `--dry-run`). Exit code 0 on no-op-or-success; non-zero on error. Wire into `supekku/cli/main.py` under the `admin` group.
  - **Files / Components**: NEW CLI module; `supekku/cli/main.py`.
  - **Testing**: CliRunner smoke — `regenerate-templates --dry-run` on the committed templates returns exit 0 and zero "would change" lines (idempotent).
  - **Observations & AI Notes**: respect STD-001 (Typer + Rich for output). Use a Rich table for the per-path summary.
  - **Commits / References**: bundles with 2.11.

- **2.11 `validate templates` CLI + VT-CC-003**
  - **Design / Approach**: NEW `spec_driver/presentation/cli/validate/templates.py` (Typer subcommand under a new `validate` Typer group — minimal group skeleton lands here; P03 fleshes out `validate workspace` / `validate file`). Calls `validate_templates(repo_root)`; prints any drift records; exit 1 if non-empty, exit 0 if empty. Wire into `supekku/cli/main.py`. Bare `validate` is left as P03's concern; for this phase `validate templates` is the only registered subcommand.
  - **Files / Components**: NEW CLI module + group skeleton; `supekku/cli/main.py`.
  - **Testing**: VT-CC-003 — CliRunner on a fixture template tree with hand-introduced drift ⇒ exit non-zero, drift listed; clean tree ⇒ exit 0.
  - **Observations & AI Notes**: do NOT pre-implement `validate workspace` / `validate file` here — those are P03 deliverables and would conflate scope. Keep the group skeleton small.
  - **Commits / References**: bundles with 2.10.

- **2.12 `just validate-templates` target**
  - **Design / Approach**: Add a one-line recipe to `justfile`: `validate-templates: uv run spec-driver validate templates`. Keep the existing `just check` pipeline unchanged in this phase — `validate-templates` is invocable but not yet promoted into `check` (decide promotion in P03 once the full `validate` group lands).
  - **Files / Components**: `justfile`.
  - **Testing**: `just validate-templates` runs cleanly post-2.13.
  - **Observations & AI Notes**: keeps the CI surface discoverable without forcing `just check` to depend on a still-evolving CLI group.
  - **Commits / References**: bundles with 2.10/2.11.

- **2.13 One-time template regeneration**
  - **Design / Approach**: Run `uv run spec-driver admin regenerate-templates --dry-run` first; review diff carefully (bodies MUST be untouched except for frontmatter insertion). Then `uv run spec-driver admin regenerate-templates` (full apply). `git diff -- supekku/templates/` — confirm every changed file is `+++` frontmatter only. Commit templates as a discrete commit `chore(DE-137): regenerate templates with frontmatter (IP-137-P02)`.
  - **Files / Components**: `supekku/templates/*.md`.
  - **Testing**: `just validate-templates` (post-regen) ⇒ clean. `just test` continues to pass (any test loading a template still works because bodies are preserved).
  - **Observations & AI Notes**: any template with an unexpected body diff signals a regenerator bug — STOP and diagnose before committing. Templates with no frontmatter today get an inserted block; templates with existing partial frontmatter (none in current corpus, but be defensive) get a full rewrite.
  - **Commits / References**: discrete commit.

- **2.14 VT-CC-004 — created artefact carries enum-comment hints**
  - **Design / Approach**: End-to-end test: invoke `spec-driver create delta "test"` (or equivalent per-kind creation) under CliRunner in a tmp workspace; read the resulting file; assert ≥1 enum-comment string present in the frontmatter region (e.g. `# one of: draft | in-progress | completed | abandoned` adjacent to the `status:` key).
  - **Files / Components**: NEW (or extend) `tests/supekku/cli/create_*_test.py`.
  - **Testing**: this is the test.
  - **Observations & AI Notes**: this VT proves the create-path migration (2.6) actually routes through `render_frontmatter_for_kind`. Without it, a silent regression where `_create` falls back to comment-less emit goes undetected.
  - **Commits / References**: bundles with 2.5/2.6.

- **2.15 Acceptance gate**
  - **Design / Approach**: `just check`. Address every failure (test, ruff, format, pylint ratchet). For pylint, regression on touched files blocks per CLAUDE.md. Out-of-scope regressions left as-is (do not silence).
  - **Files / Components**: as needed.
  - **Testing**: this is the verification gate.
  - **Observations & AI Notes**: any new ruff or pylint findings on `yaml_emit.py` / `templates.py` are this phase's responsibility; resolve before exit.
  - **Commits / References**: cleanups separate from the feature commits where practical.

- **2.16 Phase wrap-up**
  - **Design / Approach**: Update `notes.md` with VT pass table, `yaml_emit.py` LOC count (OQ-137-01 disposition: keep stdlib or escalate), pre- vs post-migration grep evidence. Check IP-137 §9 progress box for P02. Commit phase work as `feat(DE-137): template emit infra + one-time regen (IP-137-P02)` (or staged commits if migration was bundled separately). Hand-off note for P03: `validate templates` group skeleton landed; P03 extends with `workspace` / `file` peers.
  - **Files / Components**: `notes.md`, `IP-137.md`, `phases/phase-02.md`.
  - **Testing**: n/a (paperwork).
  - **Observations & AI Notes**: phase-03 sheet is **not** scaffolded in this phase — P03's entrance criteria include "P02 complete", and `/plan-phases` runs at P02 close.
  - **Commits / References**: final phase commit.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| `yaml_emit.py` blows past ~120 LOC chasing stdlib-yaml edge cases | OQ-137-01 STOP condition; ruamel.yaml swap on consult; bounded by clear-cut feature scope (top-level scalar comments only) | open |
| Comment-extraction regex on update-path misses an edge case (e.g. multi-line scalars, block-styled values) | MVP scope is single-line scalars; document as "tolerated until DE-138..142 surface a counter-example"; VT covers happy path | open |
| Mass migration of ~33 callers introduces silent kind mismatches (e.g. `kind="delta"` at a phase-write site) | DR-137 §5.1 table per-row review; VT-CC-004 catches end-to-end mismatches via comment-string assertions | open |
| `regenerate_template` strips Jinja blocks from bodies (regex-overreach) | Body-preservation regression test on the first commit; manual diff review at task 2.13 before committing | open |
| Test ripple (~12+ sites) misses a fixture-builder caller that doesn't run in default test mode | `rg -n 'dump_markdown_file\b' --type py` post-migration is the gate; deletion of the legacy fn triggers ImportError if any caller slips through | open |
| `validate templates` CI gate fires false positives on the committed templates (regenerator non-idempotent) | VT-CC-002 catches in tests; `just validate-templates` post-2.13 is the final gate before commit | open |
| New `validate` Typer group skeleton conflicts with P03 expectations | Keep skeleton minimal (group + single `templates` subcommand); P03 extends without restructuring; coordinate via notes hand-off | open |

## 9. Decisions & Outcomes

- `2026-05-18` — P02 sheet drafted at IP-137 plan-phases handoff. No new decisions yet; the phase rides on DR-137 v3.1 decisions DEC-137-09, -15, -25 verbatim.

## 10. Findings / Research Notes

- Pre-flight grep (task 2.1) output to be captured here.
- OQ-137-01 disposition recorded here at task 2.15 (LOC count + decision).
- Any unexpected `dump_markdown_file` caller surfaced during 2.6/2.7/2.8 recorded inline.

## 11. Wrap-up Checklist

- [ ] Exit criteria (all bullets in §4) satisfied
- [ ] Verification evidence stored in `notes.md` (VT pass status; `yaml_emit.py` LOC; pre/post grep of `dump_markdown_file` callers; template diff summary)
- [ ] IP-137 §9 progress box for P02 checked
- [ ] OQ-137-01 disposition recorded (keep stdlib emit or escalate to ruamel.yaml)
- [ ] Hand-off note in `notes.md` summarising any new constraints for IP-137-P03 (e.g. `validate` Typer group skeleton location; comment-extraction limitations to be aware of when implementing `--fix` consumers)
