# DE-096 Implementation Notes

## 2026-03-14 – Design exploration

### CompactDumper findings
- `yaml.safe_dump` with custom representer is idempotent and deterministic
- Flow-style heuristic: all scalars AND total rendered width < 80 chars → flow; otherwise block
- Empty lists emit as `[]` (flow) which matches project convention
- Relations (list-of-dicts) stay block-style — correct behaviour

### Date quoting
- Double-quoted `"2025-01-15"` → loaded as string → re-dumped as single-quoted `'2025-01-15'`
- Unquoted `2025-01-15` → loaded as `datetime.date` → re-dumped unquoted
- Both stable after normalisation; single-quote is canonical post-normalisation

### python-frontmatter library
- `load_markdown_file` uses `python-frontmatter`, not raw YAML split
- Correctly handles `---` horizontal rules in body (not confused with frontmatter delimiters)
- Returns `dict[str, Any]` — clean dict mutation surface

### Adversarial review findings
- `update_frontmatter_status` returns `bool` — callers check `False` for "no status field". Wrapper must preserve this.
- `FieldUpdateResult` return type — wrapper must compute updated/inserted from dict diff.
- Code-fenced YAML blocks in body: out of scope, body is passthrough via `load_markdown_file`/`dump_markdown_file` split.
- Client repo migration: existing client repos will get progressive reformatting on first edit. Needs a migration story — backlog item required before delta closure.

### Design decisions
- DEC-001: Full YAML round-trip (option B) — no hand-rolled parser
- DEC-002: CompactDumper heuristic — flow for short scalar lists, block for long/complex
- DEC-003: One-time normalisation commit as part of this delta
- DEC-004: `update_frontmatter(path, mutator)` as core primitive
- DEC-005: `updated` field bumped on every mutation
- DEC-006: Always reformat on write (option C) — normalisation commit eliminates transitional noise
- DEC-007: Body content including code-fenced blocks is passthrough — never touched by writer
- DEC-008: Client repo migration is out of scope for this delta — backlog item before closure
