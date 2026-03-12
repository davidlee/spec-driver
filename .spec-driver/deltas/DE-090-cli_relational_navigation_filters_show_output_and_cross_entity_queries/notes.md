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
