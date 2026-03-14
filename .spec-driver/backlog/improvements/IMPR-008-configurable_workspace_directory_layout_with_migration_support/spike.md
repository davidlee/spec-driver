# IMPR-008 Spike: workspace layout consolidation

## Brief

Estimate the work to consolidate workspace directories under `.spec-driver/`,
make layout configurable, and provide migration tooling.

## Questions to answer

1. **How many path references exist across code, tests, docs, and config?**
   DE-044 centralized constants but the _values_ still assume top-level dirs.
   Changing defaults means changing constants + verifying every caller.

2. **What reads `path:` fields from frontmatter/registry YAML?**
   Registry entries store relative paths. Moving dirs changes every stored path.
   How many entries? What tooling regenerates them vs requires manual update?

3. **What non-Python surfaces reference these paths?**
   `CLAUDE.md`, `AGENTS.md`, agent skills, hooks, boot files, glossary,
   memories, `.github/` — anything that hardcodes `specify/`, `change/`,
   `backlog/` outside Python code.

4. **Symlink feasibility** — do all target platforms (Linux, macOS, Windows/WSL)
   handle repo-internal symlinks cleanly with git? Any `.gitignore` gotchas?

5. **Config resolution order** — if `workflow.toml` `[dirs]` is present, do
   helpers read it at import time (cached) or per-call? Performance and
   testability implications.

6. **Migration scope** — what needs updating when dirs move?
   - Frontmatter `path:` fields
   - Registry YAML entries
   - Symlink status dirs (e.g. `decisions/accepted/`)
   - Cross-references in markdown (relative links between artifacts)
   - `.gitignore` patterns
   - Installer (creates initial directory structure + symlinks in `.spec-driver/`)
   - Existing `.spec-driver/` internal symlinks

7. **Dotdir discoverability** — moving human-authored content (specs, decisions,
   backlog) into `.spec-driver/` makes it invisible to `ls`. What's the concrete
   symlink strategy? Is it optional or required for usability? What does the
   installer need to create?

8. **Test fixture impact** — if paths become configurable, how do test fixtures
   that construct workspaces need to change? What's the strategy for testing
   both default and custom layouts?

## Approach

- Grep/count all path-dependent surfaces (code, YAML, markdown, config)
- Prototype `[dirs]` config resolution in `paths.py` (branch spike, not merged)
- List every file type that embeds workspace-relative paths
- Estimate delta count and rough size for each step

## Clarifications (from preflight)

- **`doc/` is out of scope** — steering convention, not a spec-driver dir
- **`kanban/` stays out** — per IMPR-008, intentionally external
- **Core motivation**: (a) installer footprint feels invasive for public use,
  (b) current folder structure has minor inconsistencies
- **Installer changes in scope** — current installer creates dirs + symlinks
  inside `.spec-driver/`; both need updating

## Findings

### Q1: Python path references

DE-044 did thorough work. **44 production files** properly import constants from
`core.paths`. Only **1 production file** (`sync/adapters/base.py:92`) retains a
hardcoded path check. **7 test files** use hardcoded mock paths (expected for
test data). Changing constant _values_ in `paths.py` would propagate cleanly
through production code with minimal verification.

### Q2: Registry `path:` fields

**309 entries** across 7 registry YAML files store `path:` fields as
repo-root-relative POSIX paths (e.g. `specify/decisions/ADR-001-...md`).
`backlog.yaml` (35 entries) uses ordering arrays without paths.

**All registries are auto-regenerated** during `spec-driver install` /
`spec-driver sync`. Each registry's `sync()` method scans disk, relativizes
paths via `Path.relative_to(root)`, and writes YAML. Safe to delete and
regenerate. CLI show/view/edit commands consume paths to resolve back to source
files.

**Impact**: Low. Changing directory layout + running sync regenerates all
registry paths automatically.

### Q3: Non-Python surfaces

~462 non-Python files reference workspace paths. Breakdown by category:

| Category                                                  | Count | Migration                                 |
| --------------------------------------------------------- | ----- | ----------------------------------------- |
| Content files (specs, deltas, backlog items)              | ~357  | paths embedded in content, not structural |
| Memory files                                              | ~66   | paths in content + cross-references       |
| Registry YAML                                             | 8     | auto-regenerated (see Q2)                 |
| Agent instructions (CLAUDE.md, AGENTS.md, boot, glossary) | 11    | manual update                             |
| Skill definitions (19 skills × 3 locations)               | 57    | manual update or templated                |
| Templates                                                 | ~11   | manual update                             |
| Config (pyproject.toml, settings.json)                    | 2     | manual review                             |
| CI (.github/)                                             | 1     | manual update                             |

**Key insight**: The ~357 content files embed paths as references to other
artifacts (e.g. `specify/decisions/ADR-001-...`). These are _prose references_,
not structural. A migration tool could sed-replace them, but they'd also work
as-is if old paths redirect (symlinks). The actionable surface is ~90 files.

### Q4: Symlink feasibility

**Current symlinks in repo**:

- `.spec-driver/about → ../supekku/about` (config)
- `.spec-driver/templates → ../supekku/templates` (config)
- `.contracts/{api,implementation}` (view aliases)
- `specify/{product,tech}/by-{slug,package,language,category,c4-level}/` (navigation index)
- `specify/tech/SPEC-XXX/contracts/` (compat mirror → `.contracts/`)

**Platform**: Standard `Path.symlink_to()` — works on Linux/macOS natively,
WSL with config. Git stores symlinks as mode `120000`. No `.gitignore`
complications found.

**Symlink builders** (`SpecIndexBuilder`, `ContractMirrorTreeBuilder`) use
relative path calculations with depth arithmetic. Moving `specify/` would
require recalculating relative targets, but the builders are designed to rebuild
from scratch — the code is resilient.

### Q5: Config resolution

**Current state**: `paths.py` constants are module-level literals. No config
integration. `config.py` has `load_workflow_config()` that reads
`.spec-driver/workflow.toml` with `tomllib`, deep-merges over `DEFAULT_CONFIG`,
and returns a dict. No `[dirs]` section exists yet.

**Architecture choice needed**: The `get_*_dir()` helpers are called throughout
the codebase. Making them config-aware requires either:

- **(a) Lazy config read**: Each helper reads config on first call, caches result.
  Simple but adds a `repo_root` dependency to config resolution (chicken-and-egg
  with `find_repo_root()`).
- **(b) Explicit config injection**: Pass config dict through call chain. Cleaner
  but invasive — 44 files import these helpers.
- **(c) Module-level init**: Call `init_paths(config)` once at startup to set
  module state. Testable with setup/teardown. Minimal caller changes.

Option (c) is probably the pragmatic choice.

### Q6: Migration scope

Full list of surfaces requiring update when dirs move:

| Surface                      | Count             | Mechanism                                     |
| ---------------------------- | ----------------- | --------------------------------------------- |
| `paths.py` constant values   | 4                 | change string values                          |
| Registry YAML `path:` fields | 309 entries       | auto-regenerated by sync                      |
| Installer directory creation | 16 dirs           | update `initialize_workspace()`               |
| Installer symlinks           | 2 config symlinks | update targets                                |
| Spec index symlinks          | ~100+ generated   | auto-rebuilt by `SpecIndexBuilder`            |
| Contract mirror symlinks     | ~50+ generated    | auto-rebuilt by `ContractMirrorTreeBuilder`   |
| Agent instructions           | 11 files          | manual edit                                   |
| Skill definitions            | 57 files (19×3)   | manual or re-sync                             |
| Templates                    | ~11 files         | manual edit                                   |
| Memories                     | ~66 files         | content references, best-effort sed           |
| Content cross-references     | ~357 files        | optional sed, or leave with redirect symlinks |
| CI config                    | 1 file            | manual edit                                   |
| `.gitignore`                 | review            | patterns may reference old paths              |

### Q7: Dotdir discoverability

**Theoretical concern, not a practical one**: `ls` won't show `.spec-driver/`
contents by default. However, `.spec-driver/` and `.contracts/` are already
dotdirs in daily use without friction. The pattern is established. Agents have
no trouble finding dotdirs — if anything they over-discover `.spec-driver/`,
preferring to browse it directly rather than using CLI commands.

Consolidation also creates an opportunity to separate user-serviceable config
from spec-driver-managed internals. `.spec-driver/config/` would hold
`workflow.toml`, `doctrine.md`, templates, and other lifecycle config files
that users edit. Managed internals (`agents/`, `hooks/`, `registry/`) stay
at `.spec-driver/` level. Currently these are mixed together.

**Mitigation options**:

1. **Convenience symlinks from repo root** — installer creates e.g.
   `specs/ → .spec-driver/tech/`, `decisions/ → .spec-driver/decisions/`.
   Configurable via `[symlinks]` in workflow.toml. Optional but recommended.
2. **Shell alias** — `alias sd='ls .spec-driver/'`. Fragile, not portable.
3. **CLI browse command** — `spec-driver browse`. Already partially exists.

Option 1 is the only viable approach. The installer would need a new step to
create/manage convenience symlinks, and a `[symlinks]` config section to let
users choose which ones they want.

**Key distinction from status quo**: Even with convenience symlinks, the
consolidation has real structural benefits over today's layout:

- **Atomic git operations**: `git add .spec-driver` rolls up all spec-driver
  changes in one go, instead of `git add change/ specify/ .spec-driver/` etc.
- **User-owned symlinks**: Because spec-driver internally resolves everything
  through `.spec-driver/`, convenience symlinks are purely cosmetic. Users can
  freely rename, rearrange, or delete them without affecting spec-driver's
  functioning. Today's top-level dirs are load-bearing.

### Q8: Test fixture impact

**Current patterns**: 7 `RepoTestCase` files + many pytest files use path
constants. All use `SPECS_DIR`, `CHANGES_DIR` etc. from `core.paths` (not raw
strings). ~52 test files total reference these constants.

**If paths become configurable via option (c) from Q5**:

- Tests call `init_paths(config)` in setUp/fixture with default config →
  existing tests unchanged
- New tests for custom layouts: call `init_paths(custom_config)` in setUp
- `monkeypatch` works for pytest-style tests
- `RepoTestCase` needs a `tearDown` that resets paths to defaults

**Estimate**: Moderate — add init/reset calls to test base class, write a small
set of custom-layout tests. Most existing tests need no changes.

## Estimates

### Suggested delta decomposition

| Delta                                | Scope                                                                                                                                                                                                              | Size | Risk |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | ---- |
| **DE-A: ADR for default layout**     | ADR-004: decide Option A (flatten). Documents canonical paths for new content, aids agent/user discoverability of new structure.                                                                                   | S    | Low  |
| **DE-B: `[dirs]` config resolution** | Add `[dirs]` to workflow.toml, wire into `paths.py` helpers via `init_paths(config)` at startup. Non-breaking — defaults match current layout.                                                                     | M    | Low  |
| **DE-C: New defaults + installer**   | Update constant defaults per ADR. Update installer to create dirs under `.spec-driver/`, create `config/` grouping.                                                                                                | M    | Low  |
| **DE-E: Backward-compat symlinks**   | Installer creates `specify/`, `change/`, `backlog/` symlinks at repo root pointing into `.spec-driver/`. De-risks C — existing cross-references, agent instructions, and memories keep working without mass edits. | S    | Low  |

**Deferred**:

- **Migration tooling** (detect old layout, move dirs, update references):
  YAGNI at current adoption (16 stars). Symlinks from E buy time. Build if/when
  users need it.
- **Content cross-reference cleanup** (~357 files with embedded old paths):
  symlinks keep them working. Sed-replace if/when it proves problematic.

**Total estimated effort**: 4 deltas — 1S + 2M + 1S. Risk is low across the
board because E ensures backward compatibility.

**Dependency chain**: A → B → C + E (C and E can be one delta or parallel).

### Open questions

1. ~~Dotdir discoverability~~ — resolved: not a practical concern.
2. ~~Content cross-references~~ — resolved: symlinks keep old paths working,
   sed-replace deferred until problematic.
3. Should PROB-003 status be updated to reflect DE-044 completion?
4. Should C and E be one delta or two? Leaning one — the symlinks are integral
   to the layout change, not an independent feature.
