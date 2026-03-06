# Phase 8 Exploration Summary: Inline Link Parsing for Memory Records

## Overview
This document summarizes the codebase exploration for Phase 8 implementation: inline Obsidian-style `[[id]]` link parsing and resolution for memory artifacts. Phase 8 will implement the `obs-link-spec.md` proposal to support `[[memory-id|optional-label]]` syntax in memory record bodies.

---

## 1. ID Patterns & Validation Infrastructure

### Current ID Pattern Duplications (lines 349-378 in revision.py, lines 25-30 in verification.py)

**revision.py patterns:**
```python
_REQUIREMENT_ID = re.compile(r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$")
_SPEC_ID = re.compile(r"^SPEC-\d{3}(?:-[A-Z0-9]+)*$")
_REVISION_ID = re.compile(r"^RE-\d{3,}$")
_DELTA_ID = re.compile(r"^DE-\d{3,}$")
_AUDIT_ID = re.compile(r"^AUD-\d{3,}$")
_BACKLOG_ID = re.compile(r"^[A-Z]+-\d{3,}$")
```

**verification.py patterns:**
```python
_VERIFICATION_ID = re.compile(r"^V[TAH]-\d{3,}$")
_SUBJECT_ID = re.compile(r"^(SPEC|PROD|IP|AUD)-\d{3,}(?:-[A-Z0-9]+)*$")
_REQUIREMENT_ID = re.compile(
  r"^(SPEC|PROD)-\d{3,}(?:-[A-Z0-9]+)*\.(FR|NFR)-[A-Z0-9-]+$",
)
_PHASE_ID = re.compile(r"^IP-\d{3,}(?:-[A-Z0-9]+)*\.PHASE-\d{2}$")
```

**Challenge:** These patterns are duplicated across modules. For Phase 8 inline link resolution, we'll need memory ID patterns alongside these. Opportunity to consolidate in a central module later.

---

## 2. Memory ID Scheme (Phase 6 Complete)

### Canonical Form
`mem.<type>.<domain>.<subject>[.<purpose>]`

**Charset per segment:** `[a-z0-9]+(-[a-z0-9]+)*` (lowercase enforced on write)  
**Separators:** `.` (dot)  
**Segments:** 2–7 total (mem + 1–6 user segments), 3–6 recommended  
**Hyphens:** Allowed within segments but not leading/trailing

**Examples:**
- `mem.skill.prompting.style`
- `mem.system.auth.overview`
- `mem.pattern.cli.skinny`
- `mem.fact.http.default-timeout`

### Shorthand Support
Users can omit `mem.` prefix on input:
- Input: `system.auth.overview` → Normalized to: `mem.system.auth.overview`

### ID Validation Module
**Location:** `supekku/scripts/lib/memory/ids.py`

**Functions:**
- `validate_memory_id(raw: str) -> str` — returns canonical form or raises ValueError
- `normalize_memory_id(raw: str) -> str` — prepends `mem.` if missing, lowercases
- `extract_type_from_id(memory_id: str) -> str | None` — returns second segment (type hint)
- `filename_from_id(memory_id: str) -> str` — derives filename (e.g., `mem.pattern.cli.skinny.md`)

**Validation Regex:** `^mem\.[a-z0-9]+(-[a-z0-9]+)*(\.[a-z0-9]+(-[a-z0-9]+)*){1,5}$`

**Test coverage:** 35 tests in `ids_test.py` covering canonical, shorthand, rejection, lowercasing, hyphens.

---

## 3. Memory Model & Registry

### MemoryRecord Dataclass
**Location:** `supekku/scripts/lib/memory/models.py`

**Required Fields:**
- `id: str` — canonical memory ID
- `name: str` — display name
- `status: str` — artifact lifecycle status
- `memory_type: str` — enum: concept, fact, pattern, signpost, system, thread
- `path: str` — filesystem path to the markdown file

**Optional Fields:**
- **Dates:** `created`, `updated`, `verified`, `review_by` (ISO-8601)
- **Scalars:** `confidence` (enum: low/medium/high), `summary` (string)
- **Lists:** `tags`, `owners`, `requires_reading`, `audience`, `visibility`, `relations`
- **Objects:** `scope`, `priority`, `provenance`

**Methods:**
- `from_frontmatter(path, fm) -> MemoryRecord` — constructs from parsed YAML dict
- `to_dict(root) -> dict` — serializes for YAML output, omits empty optionals, relativizes paths

**Notes:** No `links` field currently exists. Phase 8 will add:
- `links.out: list[LinkEntry]` — resolved outbound links from body
- `links.missing: list[str]` — unresolved link targets (optional, for warnings)

### MemoryRegistry
**Location:** `supekku/scripts/lib/memory/registry.py`

**Methods:**
- `collect() -> dict[str, MemoryRecord]` — globs `mem.*.md` files, parses frontmatter
- `find(memory_id) -> MemoryRecord | None` — lookup by ID
- `iter(status=None) -> Iterator[MemoryRecord]` — iterate with optional status filter
- `filter(memory_type=, status=, tag=) -> list[MemoryRecord]` — multi-criteria AND filter

**Discovery:** Globs `self.directory / "mem.*.md"` (configurable directory, defaults to `root / "memory"`)

**Frontmatter-first:** Uses frontmatter `id` as primary key; falls back to filename stem if missing.

---

## 4. Inline Link Spec (Phase 8 Design)

### obs-link-spec.md Summary
**Location:** `change/deltas/DE-033-memory_records_schema_and_command_surface/obs-link-spec.md`

**Proposal:**
1. **Syntax:** `[[id]]` or `[[id|Label]]` (Obsidian-style subset)
2. **Resolution on save:** Parse body → resolve to registry → update frontmatter `links.out`
3. **Frontmatter schema:**
   ```yaml
   links:
     out:
       - id: mem.system.auth-overview
         path: memory/system/auth-overview.md
         label: Auth overview
         kind: memory
     missing:
       - raw: "mem.system.nonexistent"
         found: 0
   ```
4. **Failure modes:** Missing → warn (non-fatal by default), ambiguous → warn, self-link → ignore/warn
5. **Rendering:** Do not rewrite body unless explicitly asked. Optional `mem render` for GitHub-friendly output.

### Resolution Rules (from id-spec.md §"Practical resolution rules")
Given token content `T`:
1. If `T` contains `|`, split: `target, label`
2. Normalize `target`:
   - Trim whitespace
   - If starts with `mem:`, strip scheme, ensure canonical `mem.` prefix
3. Attempt resolution:
   - Exact ID match in registry (fast path)
   - If matches `^[A-Z]{3,}-\d+$`, try exact (ADR/SPEC style)
   - If starts with `mem.` or contains `.`, try memory ID normalization + lookup
   - (Optional) slug/title alias lookup (warn on ambiguity)

### Design Constraints
**A) What is linkable?**
- At minimum: memory record IDs and other ADR/spec/requirement IDs
- Recommendation: prefer `id` as canonical identity (paths are derived)

**B) Update policy on save:**
- Recompute `links.out` from body (body = source of truth)
- Do NOT merge; overwrite deterministically to prevent "ghost links"

**C) Scope of Phase 8:**
- Parse `[[...]]` tokens (ignore code fences and inline backticks)
- Resolve to memory IDs and optionally other artifact IDs
- Write/update frontmatter `links.out` field
- Warn on missing/ambiguous targets (non-fatal)
- NO inverse link traversal (deferred to v1.1 graph index phase)
- NO automatic rewriting of body links (advisory only)

---

## 5. Frontmatter Metadata & Field Schema

### Memory Frontmatter Metadata
**Location:** `supekku/scripts/lib/core/frontmatter_metadata/memory.py`

**Schema Definition:** `MEMORY_FRONTMATTER_METADATA` extending base with memory-specific fields.

**Scope object structure (example):**
```yaml
scope:
  globs: ["src/auth/**", "packages/auth/**"]
  paths: ["src/auth.py"]
  commands: ["test auth:integration"]
  languages: ["py", "ts"]
  platforms: ["linux", "mac"]
```

**Priority object:**
```yaml
priority:
  severity: "high"  # enum: none, low, medium, high, critical
  weight: 10        # integer, tie-breaker
```

**Provenance object:**
```yaml
provenance:
  sources:
    - kind: "adr"     # enum: adr, code, commit, design, doc, external, issue, pr, spec
      ref: "path/or/url"
      note: "optional human note"
```

**Relations field (inherited from base):**
```yaml
relations:
  - type: "relates_to"
    target: "ADR-011"
    annotation: "optional"
```

**Current fields in MemoryRecord:** `scope`, `priority`, `provenance`, `relations` are all dict/list fields.  
**Phase 8 addition:** `links` (nested object with `out` and `missing` arrays).

---

## 6. Memory Formatters

### memory_formatters.py Structure
**Location:** `supekku/scripts/lib/formatters/memory_formatters.py`

**Detail View Functions:**
- `format_memory_details(record) -> str` — multi-line detail view
- `_format_dates(record) -> list[str]` — date fields
- `_format_scope(scope) -> list[str]` — scope dict as indented sub-lines
- `_format_priority(priority) -> list[str]` — priority dict
- `_format_provenance(provenance) -> list[str]` — provenance sources
- `_format_relations(relations) -> list[str]` — relations list

**List View Functions:**
- `format_memory_list_table(records, format_type="table", truncate=False) -> str`
- `format_memory_list_json(records) -> str`
- `_prepare_memory_row(record) -> list[str]` — single table row
- `_calculate_column_widths(terminal_width) -> dict[int, int]`

**Theme Integration:**
- `get_memory_status_style(status)` — returns Rich-style string for status styling
- Memory ID styled as `[memory.id]{id}[/memory.id]`
- Tags colored `[#d79921]{tags}[/#d79921]`

**Phase 8 addition:** New formatter function `_format_links(links) -> list[str]` to display resolved links in detail view.

---

## 7. CLI Structure & Command Integration

### Main Command Entry Point
**Location:** `supekku/cli/main.py`

**Verb-noun structure:**
- `create memory` (via `create.app`)
- `list memories` (via `list_module.app`)
- `show memory` (via `show.app`)
- `find memory` (via `find.app`)

### Create Command
**Location:** `supekku/cli/create.py`

**Signature:** `create memory <MEMORY_ID> --name <NAME> [--type TYPE] [--status STATUS] [--tag TAG] [--summary SUMMARY]`

**Creation flow:**
1. Parse user-supplied semantic memory ID
2. Normalize and validate ID
3. Build frontmatter dict with defaults
4. Create markdown file with template body
5. Write to `memory/<canonical_id>.md`

**Relevant modules:**
- `supekku/scripts/lib/memory/creation.py` — `create_memory()`, `build_memory_frontmatter()`
- `supekku/scripts/lib/memory/ids.py` — ID validation/normalization

### List Command
**Location:** `supekku/cli/list.py`

**Signature:** `list memories [--status STATUS] [--type TYPE] [--tag TAG] [--regexp PATTERN] [--path PATH] [--command CMD] [--match-tag TAG] [--format FORMAT] [--json] [--truncate]`

**Filtering pipeline:**
1. Registry pre-filter (--type, --status, --tag via `registry.filter()`)
2. Regexp filter (--regexp)
3. Build MatchContext from --path, --command, --match-tag
4. Selection/ordering via `select()` (scope matching + severity/weight sorting)
5. Format + output

**Relevant modules:**
- `supekku/scripts/lib/memory/selection.py` — `select()`, `matches_scope()`, `sort_key()`
- `supekku/scripts/lib/formatters/memory_formatters.py` — formatting dispatch

### Show Command
**Location:** `supekku/cli/show.py`

**Signature:** `show memory <MEMORY_ID> [--json] [--path] [--raw]`

**Details view:**
- Accepts shorthand (omitted `mem.` prefix) and canonical IDs
- Normalizes via `normalize_memory_id()` (adds `mem.` prefix if missing)
- Looks up in registry and displays formatted details
- Optional JSON, path-only, or raw file content output

### Find Command
**Location:** `supekku/cli/find.py`

**Signature:** `find memory <PATTERN>`

**Pattern matching:**
- Globs memory IDs using `fnmatch` (e.g., `mem.pattern.*`)
- Returns matching records with formatted output

### Common Utilities
**Location:** `supekku/cli/common.py`

**Relevant functions:**
- `normalize_id(kind, id_string) -> str` — shorthand normalization
- `ARTIFACT_PREFIXES` dict — removed `"memory"` entry in Phase 6 (memory IDs are not numeric shorthand)

---

## 8. Test Patterns & Conventions

### Memory Module Tests

**Location:** `supekku/scripts/lib/memory/`

- `ids_test.py` — 35 tests for ID validation, normalization, extraction
- `models_test.py` — ~100 tests for MemoryRecord construction, serialization, date parsing
- `registry_test.py` — ~21 tests for discovery, parsing, filtering
- `selection_test.py` — 73 tests for scope matching, specificity, ordering, surfaceability
- `creation_test.py` — 13 tests for creation logic

**CLI Tests:**

**Location:** `supekku/cli/memory_test.py`

- ~35+ integration tests covering `create memory`, `list memories`, `show memory`, `find memory`
- Fixture helper: `_write_memory_file()` — inline YAML construction, no separate fixture files

**Formatter Tests:**

**Location:** `supekku/scripts/lib/formatters/memory_formatters_test.py` (not yet created; Phase 5 added formatters without dedicated tests)

### Test Conventions
- **Inline fixtures:** YAML dicts/strings in test code, no separate fixture files
- **TDD-first:** Tests written before implementation
- **Deterministic:** Same input → same output; no RNG or external dependencies
- **Full coverage:** Edge cases, rejection paths, optional fields

---

## 9. Workspace Facade & Registry Access

### Workspace Class
**Location:** `supekku/scripts/lib/workspace.py`

**Current registries exposed:**
- `specs: SpecRegistry`
- `requirements: RequirementsRegistry`
- `decisions: DecisionRegistry`
- `delta_registry: ChangeRegistry` (for deltas)
- `revision_registry: ChangeRegistry` (for revisions)
- `audit_registry: ChangeRegistry` (for audits)

**Phase 8 addition:** May need to add `memory_registry: MemoryRegistry` for central access if the inline link parser needs cross-registry lookups. Current memory registry is accessed ad-hoc in CLI commands.

---

## 10. Core Utilities: spec_utils & file I/O

### spec_utils Module
**Location:** `supekku/scripts/lib/core/spec_utils.py`

**Key functions:**
- `load_markdown_file(path) -> tuple[dict, str]` — parses frontmatter and body
  - Returns: `(frontmatter_dict, body_string)`
  - Body is lstrip'd of leading newlines; trailing newline preserved if present in original
- `dump_markdown_file(path, frontmatter, body) -> None` — writes YAML frontmatter + body
  - Format: `---\n{yaml}\n---\n\n{body}`
  - Frontmatter YAML is stripped, body is lstrip'd and trailing newline added if missing

**Integration with Python frontmatter library:**
- Uses `python-frontmatter` package to parse/serialize markdown with YAML frontmatter
- Safe YAML serialization via `yaml.safe_dump()`

**Phase 8 usage:** Will use these to read memory body, parse `[[...]]` tokens, and write updated frontmatter with `links.out` field.

---

## 11. Key Design Patterns & Principles

### Separation of Concerns (SRP)
- **Domain packages** (`memory/`) — ID validation, models, registry, selection, creation
- **Formatters** (`formatters/`) — pure display functions, no business logic
- **CLI** (`cli/`) — thin orchestration: args → registry → filter → format → output
- **Core utilities** (`core/`) — shared infrastructure

### Pure Functions Over Stateful Objects
- Prefer `(input) -> output` instead of stateful transformations
- Example: `matches_scope(record, context) -> bool`, `sort_key(record, context) -> tuple`
- Enables deterministic testing and composition

### Frontmatter-First with Registry Fallback
- Frontmatter `id` is authoritative; filename is derived
- Registry `collect()` uses glob discovery; parsing uses frontmatter-first ID resolution
- Path changes are cheap if ID is canonical

### Deterministic Ordering
- Multi-level sort keys for predictable output
- Severity, weight, specificity, verification date, ID (lexicographic)
- Enables repeatable filtering and ranking

---

## 12. Implementation Roadmap for Phase 8

### Task 8.1: Link Parser Module
**Responsibility:** Extract `[[...]]` tokens from markdown body

**Design:**
- Input: markdown body string
- Output: list of `LinkToken` namedtuple/dataclass with `raw`, `target`, `label`
- Ignore tokens inside:
  - Fenced code blocks (`` ``` ` ``)
  - Inline backticks (`` ` ``)
  - HTML comments (`<!-- -->`)

**Algorithm:**
- State machine: track fenced block state, inline code state
- When in normal mode, capture `[[...]]` matches
- When in fenced/code mode, skip matches

**Test strategy:**
- Basic token extraction (`[[id]]`, `[[id|label]]`)
- Edge cases: empty brackets, nested brackets, escaped brackets
- Ignoring tokens in code blocks, inline code, comments
- Whitespace handling

### Task 8.2: Link Resolver Module
**Responsibility:** Map link tokens to memory (and optionally other artifact) IDs

**Design:**
- Input: `LinkToken` list, `MemoryRegistry`, optional other registries
- Output: list of `ResolvedLink` with `target_id`, `path`, `label`, `kind`, `resolved_to` (id/slug/error)
- Also output: list of `UnresolvedLink` (missing targets)

**Resolution order (per id-spec.md §11):**
1. Exact ID match in memory registry (fast)
2. If matches `^[A-Z]{3,}-\d+$`, try exact (ADR/SPEC style)
3. If starts with `mem.` or contains `.`, normalize and retry memory registry
4. (Optional) slug/title alias lookup (warn on ambiguity)

**Identifier recognition:**
- Memory IDs: `mem\.` prefix or dot-separated (e.g., `system.auth.overview`)
- ADR/SPEC IDs: `[A-Z]{3,}-\d+` (e.g., `ADR-012`, `SPEC-123`)
- Backlog IDs: similar pattern

**Test strategy:**
- Valid memory links (canonical, shorthand, with/without scheme prefix `mem:`)
- Valid ADR/SPEC links
- Missing targets → `UnresolvedLink` entry
- Ambiguous slug/title matches → warning output

### Task 8.3: Link Writer (Frontmatter Update)
**Responsibility:** Update memory record frontmatter with resolved links

**Design:**
- Input: `MemoryRecord`, `list[ResolvedLink]`, `list[UnresolvedLink]`
- Output: updated frontmatter dict with `links` field

**Frontmatter structure:**
```yaml
links:
  out:
    - id: mem.system.auth-overview
      path: memory/system/auth-overview.md
      label: Auth overview
      kind: memory
  missing:
    - raw: "mem.system.nonexistent"
      found: 0
```

**Update strategy:**
- Write `links.out` deterministically sorted by `id` to reduce diff noise
- Optionally track `links.missing` for warnings
- DO NOT merge; overwrite on every save

**Test strategy:**
- Single link, multiple links, no links
- Deterministic ordering (same input → same output)
- Empty/null handling

### Task 8.4: Memory Edit/Save Hook
**Responsibility:** Integrate parser + resolver + writer into memory save/edit workflow

**Design:**
- New function: `parse_and_resolve_links(memory_file_path, memory_registry, other_registries=None) -> (links_out, links_missing)`
- Integrate into:
  - `mem edit` command (on save)
  - `mem fmt` command (if implemented)
  - `mem save` command (if implemented)

**CLI integration:**
- Add `--links` / `--no-links` flag to `create memory` and edit commands (default: auto-resolve)
- Add `--strict` flag for CI (fail on missing/ambiguous targets)

**Test strategy:**
- End-to-end: parse body → resolve → update frontmatter
- Real memory files with inline links
- Determinism: same file content → same links output

### Task 8.5: Formatter Update
**Responsibility:** Display resolved links in memory detail view

**Design:**
- New formatter: `_format_links(links_dict) -> list[str]`
- Displays `links.out` entries as:
  ```
  Links:
    mem.system.auth-overview → Auth overview (memory/system/auth-overview.md)
    ADR-012 → Architecture Decision (...)
  ```
- Optionally display missing links with warning badge

**Test strategy:**
- Formatting with no links, single link, multiple links
- Link truncation in table view (if applicable)

### Task 8.6: Tests & Verification
**Responsibility:** Comprehensive test coverage for all link parsing logic

**Test files to create/update:**
- `supekku/scripts/lib/memory/links_parser_test.py` — token extraction, code fence handling
- `supekku/scripts/lib/memory/links_resolver_test.py` — registry lookup, identifier recognition
- `supekku/scripts/lib/memory/links_writer_test.py` — frontmatter update, determinism
- `supekku/cli/memory_test.py` — end-to-end with real memory files (extend existing tests)

**Lint & Quality:**
- `just lint` (ruff) — zero warnings
- `just pylint` — no new regressions
- `just test` — all suites passing

---

## 13. Key Files & Absolute Paths

### Domain Logic
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/ids.py` — ID validation
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/models.py` — MemoryRecord model
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/registry.py` — MemoryRegistry discovery
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/selection.py` — filtering/ordering
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/creation.py` — creation logic

### CLI Commands
- `/home/david/dev/spec-driver/supekku/cli/main.py` — main app entry
- `/home/david/dev/spec-driver/supekku/cli/create.py` — `create memory`
- `/home/david/dev/spec-driver/supekku/cli/list.py` — `list memories`
- `/home/david/dev/spec-driver/supekku/cli/show.py` — `show memory`
- `/home/david/dev/spec-driver/supekku/cli/find.py` — `find memory`
- `/home/david/dev/spec-driver/supekku/cli/common.py` — `normalize_id()`, `ARTIFACT_PREFIXES`

### Formatters
- `/home/david/dev/spec-driver/supekku/scripts/lib/formatters/memory_formatters.py` — detail/list formatting

### Metadata & Schema
- `/home/david/dev/spec-driver/supekku/scripts/lib/core/frontmatter_metadata/memory.py` — frontmatter schema
- `/home/david/dev/spec-driver/supekku/scripts/lib/blocks/metadata/__init__.py` — metadata framework

### Core Utilities
- `/home/david/dev/spec-driver/supekku/scripts/lib/core/spec_utils.py` — markdown file I/O
- `/home/david/dev/spec-driver/supekku/scripts/lib/workspace.py` — registry facade

### Tests
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/ids_test.py` — ID tests (35 tests)
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/models_test.py` — model tests (~100 tests)
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/registry_test.py` — registry tests (21 tests)
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/selection_test.py` — selection tests (73 tests)
- `/home/david/dev/spec-driver/supekku/scripts/lib/memory/creation_test.py` — creation tests (13 tests)
- `/home/david/dev/spec-driver/supekku/cli/memory_test.py` — CLI integration tests (35+ tests)

### Design Documents
- `/home/david/dev/spec-driver/change/deltas/DE-033-memory_records_schema_and_command_surface/obs-link-spec.md` — inline link design
- `/home/david/dev/spec-driver/change/deltas/DE-033-memory_records_schema_and_command_surface/id-spec.md` — memory ID scheme
- `/home/david/dev/spec-driver/change/deltas/DE-033-memory_records_schema_and_command_surface/IP-033.md` — implementation plan
- `/home/david/dev/spec-driver/change/deltas/DE-033-memory_records_schema_and_command_surface/DR-033.md` — design revision
- `/home/david/dev/spec-driver/change/deltas/DE-033-memory_records_schema_and_command_surface/phases/phase-06.md` — completed Phase 6 sheet

---

## 14. Critical Implementation Notes

### Parser Design Recommendation
**State Machine Approach:**
```
States: NORMAL, IN_CODE_FENCE, IN_INLINE_CODE, IN_COMMENT
Transitions:
  NORMAL → IN_CODE_FENCE (on ``` or ~~~)
  NORMAL → IN_INLINE_CODE (on `)
  NORMAL → IN_COMMENT (on <!--)
  NORMAL + [[...]] → capture token
  Exit fence/code/comment → return to NORMAL
```

**Edge Cases to Handle:**
- Code fence delimiters (``` or ~~~) with language specifiers (```python)
- Inline code spanning multiple tokens (rare in practice)
- Escaped brackets (\[\[)
- Nested/malformed brackets

### Resolver Design Recommendation
**Order matters for performance:**
1. **Fast path:** Exact ID match in memory registry (O(1) dict lookup)
2. **Slow path:** Slug/title alias lookup (O(n) linear scan)

**Identifier heuristics:**
- If starts with `mem.` → treat as memory ID
- If matches `^[A-Z]{3,}-\d+$` → treat as primitive ID (ADR/SPEC)
- If contains `.` → likely memory ID shorthand → add `mem.` prefix

### Writer Design Recommendation
**Deterministic sorting:**
```python
links_out = sorted(resolved_links, key=lambda x: x['id'])
```

**Avoid ghost links:**
- Always overwrite `links.out` from current body parse, never merge with previous
- Track missing separately for warnings

### MemoryRecord Extension
**Minimal change to models.py:**
```python
@dataclass
class MemoryRecord:
  ...existing fields...
  
  # Phase 8: inline link resolution
  links: dict[str, Any] = field(default_factory=dict)  # {"out": [...], "missing": [...]}
```

**Alternative (more explicit):**
```python
@dataclass
class LinkEntry:
  id: str
  path: str
  label: str | None
  kind: str

@dataclass
class MemoryRecord:
  ...existing fields...
  links_out: list[LinkEntry] = field(default_factory=list)
  links_missing: list[str] = field(default_factory=list)
```

Recommend the first approach (nested dict) to match existing `scope`, `priority`, `provenance` pattern.

---

## 15. Testing Strategy Summary

### Unit Test Layers
1. **Parser tests** — token extraction, code fence handling
2. **Resolver tests** — registry lookup, heuristics
3. **Writer tests** — frontmatter update, determinism
4. **Formatter tests** — link display in detail view

### Integration Tests
- End-to-end: create memory → edit body with links → save → verify links.out

### CLI Tests
- `create memory` with inline links (pre-populated body or edit)
- `show memory` displays resolved links
- `list memories` (future: filter by linked targets)

### Determinism Tests
- Parse → resolve → serialize → parse again → compare (idempotency)
- Same body content → same links.out ordering (no randomness)

### Edge Cases
- Empty body, no links → empty links.out
- Missing targets → links.missing entries
- Ambiguous slug matches → warning + unresolved
- Self-links → special handling (ignore or warn)
- Cycles → acceptable (graph structure is fine)
- Code blocks with `[[...]]` → should not parse

---

## 16. Success Criteria for Phase 8

### Completion Checklist
- [ ] Parser module (`links_parser.py`) with state machine for code fence/inline code handling
- [ ] Resolver module (`links_resolver.py`) with multi-strategy ID lookup
- [ ] Writer module (`links_writer.py`) with deterministic frontmatter updates
- [ ] MemoryRecord extension with `links` field
- [ ] Formatter update to display links in detail view
- [ ] CLI integration (optional `--links`/`--strict` flags)
- [ ] Comprehensive test coverage (parser, resolver, writer, formatter, CLI)
- [ ] All tests passing (`just test` → 100%)
- [ ] Lint clean (`just lint` → zero warnings)
- [ ] No pylint regressions
- [ ] Updated schema examples if `links` field added to memory frontmatter metadata
- [ ] Real memory records created/edited with inline links for demonstration

### Expected Test Count
- Parser: ~30 tests
- Resolver: ~25 tests
- Writer: ~15 tests
- Formatter: ~10 tests
- CLI integration: ~15 tests
- **Total new:** ~95 tests

### Current Test Count
- Memory module + CLI: ~1984 tests (from Phase 6)
- **Expected after Phase 8:** ~2080 tests

---

## 17. Deferred to Future Phases

### v1.1 + (Post-Phase 8)
- **Graph index:** Full inverse relation traversal across all artifact types
- **Automatic link rewriting:** Optional `mem render` or `--normalize-links` flag
- **Bidirectional traversal:** "Show memories linked to this spec" (reverse lookups)
- **Link validation in CI:** Strict mode checking all memory files for broken links
- **Slug/title aliases:** Full implementation with ambiguity detection
- **Cross-artifact link filtering:** `list memories --linked-to SPEC-001`

### Per obs-link-spec.md
- Do not rewrite inline `[[...]]` tokens unless user explicitly enables `--normalize-links`
- Advisory link handling in v1 (informational, no blocking behavior)
- Missing links warn but don't fail (unless `--strict` on CI)

---

## 18. Key Observations & Design Insights

### Duplication of ID Patterns
Existing ID patterns in `revision.py` and `verification.py` offer an opportunity to consolidate ID validation into a central module (future refactor). Phase 8 will add memory ID patterns; a follow-up cleanup could extract all patterns into `core/id_patterns.py`.

### Metadata Framework is Extensible
The `blocks/metadata/` framework provides a clean pattern for defining new artifact schemas. Adding `links` field to `MemoryRecord` frontmatter can extend the existing `MEMORY_FRONTMATTER_METADATA` schema.

### Pure Functions Enable Composition
The existing `selection.py` module demonstrates how pure functions (`matches_scope()`, `sort_key()`, `is_surfaceable()`) compose into complex behavior. Link parsing should follow the same pattern: parser → resolver → writer.

### Determinism is Critical
Memory filtering/ordering relies on deterministic tie-breaker logic (severity, weight, specificity, verified date, ID). Link parsing must also be deterministic (same input → same links.out, same ordering every time). This enables reliable testing and predictable CLI behavior.

### Frontmatter-First Design
The registry uses frontmatter `id` as the primary key; filesystem paths are derived and changeable. This makes link resolution ID-centric rather than path-centric, improving stability under file moves/renames.

---

## Conclusion

Phase 8 (Inline Link Parsing) will complete the memory artifact feature set by enabling authors to reference other memory records and specs using Obsidian-style `[[id]]` syntax. The implementation should follow established spec-driver patterns:
- Pure functions in domain modules
- Thin CLI orchestration
- Metadata-driven schema validation
- Comprehensive deterministic testing
- No competing truths (links are advisory pointers to canonical artifacts)

The obs-link-spec and id-spec documents provide clear guidance on syntax, resolution, and failure modes. The existing memory domain (models, registry, selection, creation) provides a solid foundation for extending with link functionality.

