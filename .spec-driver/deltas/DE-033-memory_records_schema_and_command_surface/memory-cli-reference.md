# Memory CLI Reference

Reference for memory commands and frontmatter schema. Input for external skills authoring.

## Commands

### `create memory NAME`

Create a new memory record with the next available ID.

| Option | Short | Required | Description |
| --- | --- | --- | --- |
| `--type` | `-t` | yes | Memory type: `concept`, `fact`, `pattern`, `signpost`, `system`, `thread` |
| `--status` | `-s` | no | Initial status (default: `active`) |
| `--tag` | | no | Tag (repeatable) |
| `--summary` | | no | Brief summary |
| `--root` | | no | Repository root (auto-detected) |

Creates `memory/MEM-NNN-slugified_name.md` with frontmatter and body scaffold.

### `list memories`

List memory records with optional filtering and scope matching.

**Metadata pre-filters** (`--type`, `--status`, `--tag`) apply first with AND logic.
**Scope matching** (`--path`, `--command`, `--match-tag`) filters by context with OR logic.
Results are ordered deterministically: severity > weight > specificity > recency > id.

| Option | Short | Required | Description |
| --- | --- | --- | --- |
| `--status` | `-s` | no | Filter by status |
| `--type` | `-t` | no | Filter by memory type |
| `--tag` | | no | Filter by tag (metadata pre-filter) |
| `--path` | `-p` | no | Scope match: paths (repeatable) |
| `--command` | `-c` | no | Scope match: command string (token-prefix) |
| `--match-tag` | | no | Scope match: tags (repeatable, OR with path/command) |
| `--include-draft` | | no | Include draft memories |
| `--limit` | `-n` | no | Max results |
| `--regexp` | `-r` | no | Regex pattern on title/name/summary |
| `--case-insensitive` | `-i` | no | Case-insensitive regexp |
| `--format` | | no | Output format: `table` (default), `json`, `tsv` |
| `--json` | | no | Shorthand for `--format=json` |
| `--truncate` | | no | Truncate long fields to terminal width |
| `--root` | | no | Repository root (auto-detected) |

### `show memory MEMORY_ID`

Show detailed information about a specific memory record.

Accepts full ID (`MEM-001`) or numeric shorthand (`001`).

| Option | Short | Required | Description |
| --- | --- | --- | --- |
| `--json` | | no | Output as JSON |
| `--path` | | no | Output path only |
| `--raw` | | no | Output raw file content |
| `--root` | | no | Repository root (auto-detected) |

### `find memory PATTERN`

Find memory records matching an ID pattern.

Supports fnmatch patterns: `*` matches everything, `?` matches single char.
Accepts numeric-only IDs (e.g., `001` becomes `MEM-001`).

| Option | Short | Required | Description |
| --- | --- | --- | --- |
| `--root` | | no | Repository root (auto-detected) |

## Scope Matching Semantics

Scope matching filters memories by context relevance. Each memory record may declare scope criteria:

- **paths**: Exact path matches (strongest signal)
- **globs**: Filesystem glob patterns (e.g., `src/auth/**`)
- **commands**: Command string matching via token-prefix (e.g., scope `test auth` matches query `test auth:integration`)
- **languages**: Programming language tags (e.g., `py`, `ts`)
- **platforms**: Platform tags (e.g., `linux`, `mac`)

When `--path`, `--command`, or `--match-tag` are provided, only records whose scope matches at least one query are returned (OR across query types).

Records without scope are excluded from scope-filtered results.

## Ordering

Results are deterministically ordered by:

1. **Severity** — `critical` > `high` > `medium` > `low` > `none`/unset
2. **Weight** — higher weight first (tie-breaker within same severity)
3. **Specificity** — records with narrower scope rank higher
4. **Recency** — more recently updated first
5. **ID** — lexicographic (stable tie-breaker)

## Memory Frontmatter Reference

### Required Fields

| Field | Type | Values | Description |
| --- | --- | --- | --- |
| `id` | string | `MEM-NNN` | Unique identifier |
| `name` | string | | Human-readable title |
| `kind` | string | `memory` | Artifact kind (always `memory`) |
| `status` | enum | `draft`, `active`, `review`, `deprecated`, `superseded`, `obsolete`, `archived` | Lifecycle status |
| `memory_type` | enum | `concept`, `fact`, `pattern`, `signpost`, `system`, `thread` | Record categorisation |

### Optional Fields

| Field | Type | Description |
| --- | --- | --- |
| `created` | date | Creation date (YYYY-MM-DD) |
| `updated` | date | Last update date |
| `confidence` | enum | `low`, `medium`, `high` |
| `verified` | date | Last verified against reality |
| `review_by` | date | Next required review date |
| `summary` | string | Brief summary (1-2 sentences) |
| `tags` | list[string] | Classification tags |
| `owners` | list[string] | Responsible parties |
| `audience` | list[enum] | `human`, `agent` |
| `visibility` | list[enum] | `pre` (hook-driven), `on_demand` (manual) |
| `requires_reading` | list[string] | Pre-reading dependencies (paths or artifact IDs) |
| `relations` | list[object] | Cross-references: `{type, target, annotation}` |

### Nested Object Fields

**scope** — Context matching criteria:
```yaml
scope:
  paths: ["src/auth/cache.ts"]        # Exact path matches
  globs: ["src/auth/**"]              # Glob patterns
  commands: ["test auth:integration"] # Command-prefix matching
  languages: ["ts", "py"]            # Language tags
  platforms: ["linux"]                # Platform tags
```

**priority** — Ordering hints:
```yaml
priority:
  severity: none|low|medium|high|critical
  weight: 10  # Integer tie-breaker (higher = more prominent)
```

**provenance** — Source attribution:
```yaml
provenance:
  sources:
    - kind: adr|code|commit|design|doc|external|issue|pr|spec
      ref: specify/decisions/ADR-011-auth-flow.md
      note: Primary authority for auth flow
```

## Schema Inspection

```bash
# JSON Schema for validation
uv run spec-driver schema show frontmatter.memory --format json-schema

# YAML example with all fields
uv run spec-driver schema show frontmatter.memory --format yaml-example
```

## File Layout

Memory records are stored in `memory/` at the repository root:
```
memory/
  MEM-001-skinny_cli_pattern.md
  MEM-002-formatter_separation_of_concerns.md
```

Each file has YAML frontmatter (delimited by `---`) followed by a markdown body with `## Summary` and `## Context` sections.
