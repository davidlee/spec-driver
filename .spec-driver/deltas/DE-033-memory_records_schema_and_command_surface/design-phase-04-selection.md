# Phase 4 Design: Selection & Filtering

**Delta**: DE-033 | **Requirement**: MEM-FR-003 | **Status**: implemented

## Overview

A pure-function selection module (`memory/selection.py`) providing deterministic
scope matching, filtering, and ordering for memory records. Integrates with the
existing CLI `list memories` command via new `--path` and `--command` options.

## Data

```python
@dataclass
class MatchContext:
  """Caller's current context for scope matching."""
  paths: list[str]       # Changed/target files (repo-relative, POSIX)
  command: str | None     # Command being run
  tags: list[str]         # Explicit tags for scope matching
```

## Functions

### `normalize_path(path: str, repo_root: Path) -> str`

Normalize to repo-relative, POSIX-style. No leading `./`, resolve `..`.

### `matches_scope(record, context) -> bool`

OR logic across match dimensions. A dimension only participates if the context
provides input for it (empty list / None = dimension inactive).

| Dimension  | Match rule                                                  | Notes                                                                                                                                      |
| ---------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Path exact | any `context.paths` == any `scope["paths"]`                 | Trailing `/` on scope entry = prefix match                                                                                                 |
| Path glob  | any `context.paths` matches any `scope["globs"]`            | Custom `_glob_match`/`_match_segments` with proper `**` globstar support (`PurePosixPath.full_match()` is Python 3.13+ only; venv is 3.12) |
| Command    | scope command tokens are a prefix of context command tokens | `shlex.split` both sides; all scope tokens must match corresponding context tokens exactly                                                 |
| Tag        | `set(context.tags) & set(record.tags)` non-empty            | Only if `context.tags` is non-empty                                                                                                        |

Records with no scope keys and no tags → `False` (reachable only by explicit ID).

#### Path semantics

- Both sides normalized: repo-relative, POSIX, no leading `./`
- `scope.paths` entries ending with `/` → prefix match (directory scope)
- `scope.paths` entries without trailing `/` → exact match
- `scope.globs` → matched via custom `_glob_match()` with segment-by-segment `fnmatch.fnmatchcase` (`PurePosixPath.full_match()` requires Python 3.13+)

#### Command semantics

Token-prefix matching via `shlex.split`:

- `scope: ["test"]` matches `"test auth --verbose"` (prefix)
- `scope: ["make lint"]` matches `"make lint --fix"` (prefix)
- `scope: ["test"]` does NOT match `"pytest"` (different token)
- `scope: ["build"]` does NOT match `"rebuild"` (different token)

### `scope_specificity(record, context) -> int`

Returns MAX specificity across matched dimensions:

| Score | Dimension                                   |
| ----- | ------------------------------------------- |
| 3     | Matched via `scope.paths` (exact or prefix) |
| 2     | Matched via `scope.globs`                   |
| 1     | Matched via `scope.commands`                |
| 0     | Matched via tags only / no context          |

### `sort_key(record, context=None, *, today=None) -> tuple`

5-level deterministic key per JAMMS §5.4:

| Level          | Source                               | Direction                 | Default    |
| -------------- | ------------------------------------ | ------------------------- | ---------- |
| 1. severity    | `priority.get("severity", "none")`   | critical=0 → none=4       | "none" → 4 |
| 2. weight      | `priority.get("weight", 0)`          | descending (negate)       | 0          |
| 3. specificity | `scope_specificity(record, context)` | descending (negate)       | 0          |
| 4. verified    | days since `record.verified`         | ascending (null → maxint) | maxint     |
| 5. id          | `record.id`                          | lexicographic             | —          |

### `is_surfaceable(record, context=None, *, include_draft, thread_recency_days, today) -> bool`

Returns `False` (excluded) when:

- `status ∈ {deprecated, superseded, obsolete}`
- `status == "draft"` and not `include_draft`
- `memory_type == "thread"` AND any of:
  - no context provided
  - not scope-matched to context
  - not verified within `thread_recency_days` of `today`

### `select(records, context=None, *, include_draft=False, thread_recency_days=14, limit=None, today=None) -> list[MemoryRecord]`

Composed pipeline:

1. Filter by `is_surfaceable()`
2. If context provided, further filter non-thread records by `matches_scope()`
   (threads already handled by `is_surfaceable`)
3. Sort by `sort_key()`
4. Apply `limit`

`today` defaults to `date.today()` at call time; injectable for deterministic tests.

## CLI integration

### New options on `list memories`

| Option             | Type                     | Purpose                                                         |
| ------------------ | ------------------------ | --------------------------------------------------------------- |
| `--path` / `-p`    | `list[str]` (repeatable) | Paths for scope matching                                        |
| `--command` / `-c` | `str`                    | Command string for scope matching                               |
| `--match-tag`      | `str` (repeatable)       | Tags for scope matching (distinct from `--tag` metadata filter) |
| `--include-draft`  | `bool`                   | Include draft memories                                          |
| `--limit`          | `int`                    | Cap output count                                                |

### Pipeline

```
registry.collect()
  → metadata pre-filter (--type, --status, --tag via registry.filter())
  → regexp filter (--regexp, existing)
  → build MatchContext from --path, --command, --match-tag
  → select() for scope matching + ordering + thread/draft handling
  → format + output
```

### Tag semantics (separated)

- `--tag`: metadata pre-filter (AND, existing behavior unchanged)
- `--match-tag`: scope matching dimension (OR with path/command)

## Edge cases

| Case                        | Behavior                                                                               |
| --------------------------- | -------------------------------------------------------------------------------------- |
| Empty scope `{}`            | No scope → matches only via tags/explicit ID                                           |
| `scope.globs: ["**"]`       | Matches all paths (universal/global memory)                                            |
| No context                  | All non-excluded records included; specificity=0; order by severity/weight/verified/id |
| Threads without context     | Excluded (context-dependent by nature)                                                 |
| Missing `priority.severity` | Default `"none"` (rank 4)                                                              |
| Missing `priority.weight`   | Default `0`                                                                            |
| Missing `record.verified`   | Sorted last (maxint days)                                                              |
| Unknown severity value      | Treated as `"none"`                                                                    |
| Missing `record.tags`       | Empty set (no tag matches)                                                             |
| Missing scope keys          | Empty list (dimension inactive)                                                        |

## Deferred

- `select_for_review()` — sort by overdue-ness for review queues (future phase)
- `scope.languages` / `scope.platforms` matching (future; fields exist in schema)
- Review-by overdue as sort dimension (future)

## Testing strategy (VT-MEM-SELECTION-001)

- `normalize_path`: edge cases (relative, absolute, `./`, `..`, trailing `/`)
- `matches_scope`: each dimension independently + OR composition + inactive dimensions
- `scope_specificity`: correct scoring for each match type
- `sort_key`: ordering stability across permutations; nullable field handling
- `is_surfaceable`: status exclusion matrix; thread recency logic with injected dates
- `select`: end-to-end pipeline with fixture records; determinism (same input → same output)
- CLI integration: `--path`, `--command`, `--match-tag` produce expected filtered/ordered output
