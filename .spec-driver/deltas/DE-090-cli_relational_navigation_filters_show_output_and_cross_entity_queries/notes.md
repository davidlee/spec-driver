# Notes for DE-090

## Phase 01 — P0 Bug Fixes (in progress)

### Completed

**P0-1: Relation type key fix** (`87cc7b7`)
- `_format_relations()` in `change_formatters.py` read `"kind"` but actual data uses `"type"` (confirmed via `Relation` dataclass, `list_relations()`, and creation code).
- All test fixtures in `change_formatters_test.py` also used `"kind"` — matching the bug. Fixed both.

**P0-2: Enrich show spec** (`0f3cd3e`)
- Added `_format_spec_relations()` — uses `spec.frontmatter.relations` (tuple of `Relation` objects with `.type`/`.target`).
- Added `_format_requirements_summary(fr_count, nf_count, other_count)` — pure function, counts passed by caller.
- `show_spec` in `show.py` loads `RequirementsRegistry`, counts by spec ID, passes to formatter.
- Existing mock specs in tests needed `spec.frontmatter.relations = ()` to avoid Mock truthiness issue.

**P0-3: Plan parse resilience** (`8b3aec0`)
- `extract_plan_overview()` raises `ValueError` on bad YAML — this escaped the `except Exception` around `load_markdown_file`.
- Wrapped the extract call in its own `try/except ValueError`, prints warning to stderr.
- Also added stderr warning for the existing frontmatter parse catch (was silently skipping).

### In progress

**P0-2b: Spec.to_dict() relations** — interrupted mid-task.
- `Spec` model already has a `.relations` property (line 53-60 in `models.py`) returning `list[dict]`.
- `to_dict()` (line 98-133) currently omits relations. Need to add `if self.relations: data["relations"] = self.relations`.
- Simple addition — no test written yet.

### Surprises / Adaptations

- `Spec.frontmatter` is `FrontmatterValidationResult` (frozen dataclass), not a dict. DR-090 initially assumed dict access — caught in adversarial review.
- Requirement kinds in registry are `"functional"` and `"non-functional"` (hyphenated), not `"non_functional"` (underscored). Had to handle both for safety.
- `Spec` model already has a `.relations` property that returns dicts — discovered during P0-2b. The formatter uses `spec.frontmatter.relations` (Relation objects) while `to_dict()` can use `self.relations` (dicts). Two valid access paths exist.

### Verification status

- `just lint` passes on all changed files
- All tests pass: `change_formatters_test.py` (54), `spec_formatters_test.py` (41), `discover_plans_test.py` (11), `show_test.py` (118)
- Full `just` not run since last change — next agent should run before declaring P01 complete.

### .spec-driver artefact status

- DR-090, IP-090, phase-01.md, DE-090 status change — all committed (`647508c`, `5388a71`, `99da3fa`, `7abc282`)
- notes.md — uncommitted (this update)

### Remaining for P01 close

1. Complete P0-2b (Spec.to_dict relations) — ~5 lines of code + test
2. Run `just` (full check)
3. Update phase-01 tracking, mark exit criteria
4. Hand off to Phase 02 (P1 filters)

### 2026-03-14 — Phase 03 complete

**Done**: All P2 tasks (3.0–3.4) implemented with tests.
- 3.0: Audit backfill — added `relations: [{type: documents, target: DE-xxx}]` to AUD-003–008 (6 audits; AUD-001/002 have no delta reference)
- 3.1: `show spec` reverse lookup counts — `_format_reverse_lookup_counts()` in spec_formatters; show.py loads ChangeRegistry per kind (delta/revision/audit), calls `find_related_to()`, passes counts. JSON includes `reverse_lookup_counts` dict.
- 3.2: `show spec --requirements` — `_format_requirements_list()` in spec_formatters; replaces count summary with full (uid, kind_label, title) list.
- 3.3: `show delta` reverse lookups — `_format_delta_reverse_lookups()` in change_formatters; show.py loads audit/revision registries, finds related. JSON includes `linked_audits`/`linked_revisions` arrays.
- 3.4: Backlog JSON consistency — `BacklogItem.to_dict()` always includes `linked_deltas: []` and `related_requirements: []`. Updated `format_backlog_list_json()` to use `to_dict()`. Updated show issue/problem/improvement/risk/backlog JSON to use `to_dict()`.

**Verification**: `just` passes — 3906 tests, ruff clean, pylint 9.72/10 (no new warnings).

**Findings**:
- `RequirementRecord` uses `.uid` not `.id` — caught during smoke test.
- AUD-001 (discovery audit) and AUD-002 (test audit) have no delta reference — only 6 of 8 audits needed backfill.
- `format_delta_details_json()` returns a JSON string, not a dict — had to parse/enrich/re-encode for delta reverse lookup JSON enrichment.

**Next**: Phase 04 — P3 domain collectors.

### 2026-03-14 — Phase 04 complete

**Done**: All P3 tasks (4.1–4.9) implemented with tests.
- 4.1: Added `domain_field` and `backlog_field` to `REFERENCE_SOURCES` in `core/relation_types.py`
- 4.2: `_collect_from_decision_fields()` — 11 list fields via shared `_collect_from_list_fields()` helper
- 4.3: `_collect_from_governance_fields()` — 9 fields (specs, requirements, deltas, standards, policies, related_policies, related_standards, supersedes, superseded_by)
- 4.4: `_collect_from_requirement_fields()` — 4 list fields + scalar `primary_spec`
- 4.5: `_collect_from_backlog_fields()` — `linked_deltas`, `related_requirements`, and `frontmatter["relations"]`
- 4.6: `_collect_from_domain_fields()` dispatcher chaining all 4 collectors
- 4.7: Wired into `collect_references()` as final collector
- 4.8: `list backlog --related-to` now uses `matches_related_to()` instead of raw frontmatter access
- 4.9: 87 tests covering all collectors, dispatcher, integration, and semantic separation

**Verification**: `pytest` passes — 3935 tests, ruff clean, pylint 10/10 on changed files.

**Findings**:
- `BacklogItem.relations` not a dataclass field — relations live in `frontmatter["relations"]` dict. `_collect_from_relations()` (getattr-based) misses them. Fixed by adding frontmatter relations handling to `_collect_from_backlog_fields()` with `source="relation"` to preserve semantic meaning.
- `supersedes`/`superseded_by` field names collide with `RELATION_TYPES` values. DR-090's semantic separation invariant (detail not in RELATION_TYPES) doesn't hold for these. Separation is enforced by `source` ("domain_field" vs "relation"), not detail uniqueness. Tests updated to reflect this reality.
- Extracted `_collect_from_list_fields(artifact, field_names, source)` shared helper to DRY the 3 typed model collectors (Decision, Governance, Requirement). All use getattr with defaults so non-matching models safely yield no hits.
- Governance collector has 9 fields (includes `policies`) not 8 as DR stated — StandardRecord has `policies` field that governance collector correctly captures.

**Commits**: `a624653` (phase sheet), `b5597c7` (implementation)

**Next**: Phase 05 — P4 reverse reference filtering.
