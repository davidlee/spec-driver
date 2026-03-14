---
id: IMPR-008
name: Configurable workspace directory layout with migration support
created: "2026-03-06"
updated: "2026-03-06"
status: resolved
kind: improvement
resolved_by: DE-049
tags: [architecture, install, usability]
relations:
  - type: follows-from
    target: DE-044
  - type: addresses
    target: PROB-003
---

# Configurable workspace directory layout with migration support

## Context

DE-044 centralized all workspace directory names as constants in `core/paths.py`.
The current defaults scatter four top-level directories across the repo root:

```
repo/
  .spec-driver/     # internal config + registry
  specify/          # specs, decisions, policies, standards
    tech/
    product/
    decisions/
    policies/
    standards/
  change/           # deltas, revisions, audits
    deltas/
    revisions/
    audits/
  backlog/          # issues, problems, improvements, risks
  memory/           # agent memories
```

Five directories at repo root, four spec-driver-specific. The two grouping
directories (`specify/`, `change/`) add nesting without adding much meaning —
`decisions/` isn't more discoverable under `specify/` than it would be directly
under `.spec-driver/`.

## Opportunity

### Option A: Flatten into `.spec-driver/` (preferred)

Eliminate the intermediate grouping directories entirely. Everything lives
directly under `.spec-driver/`:

```
.spec-driver/
  config/
    templates/
    workflow.toml
    doctrine.md
  contracts/
  decisions/
  policies/
  standards/
  product/
  tech/
  backlog/
    backlog.md
    risks/
    problems/
    improvements/
    issues/
  memory/
  audits/
  deltas/
  revisions/
```

Benefits:

- **Single top-level footprint** — zero repo root pollution
- **Flatter** — no `specify/decisions/` indirection; `decisions/` is self-evident
- **Config separation** — `config/` groups tooling config (templates, workflow,
  doctrine) away from content directories
- **Clearer ownership** — everything spec-driver creates lives under `.spec-driver/`

Trade-offs:

- More siblings at the `.spec-driver/` level (mitigated by clear naming)
- `config/` is new grouping — current `workflow.toml`, `doctrine.md`, and
  `templates/` live directly in `.spec-driver/`; this moves them one level down
- Breaking change for existing workspaces — requires migration

### Option B: Nest current structure under `.spec-driver/`

Keep `specify/` and `change/` grouping but move under `.spec-driver/`:

```
.spec-driver/
  specify/
  change/
  backlog/
  memory/
  registry/
  templates/
```

Benefits:

- Single footprint, minimal conceptual change
- Smaller migration (just move dirs down one level)

Trade-offs:

- Retains the `specify/decisions/` indirection
- Deeper paths for daily browsing

### Make layout configurable via `workflow.toml`

Regardless of default layout chosen:

```toml
[dirs]
tech = "tech"               # relative to .spec-driver/
decisions = "decisions"
deltas = "deltas"
backlog = "backlog"
memory = "memory"
# ...
```

The constants in `paths.py` already isolate all path construction.
A future delta wraps those constants in config resolution — helpers read
`workflow.toml` `[dirs]` if present, falling back to defaults.

### Migration assistance

`spec-driver migrate` (or `install --migrate`) should:

- Detect the old layout (top-level `specify/`, `change/`, etc.)
- Show a diff of proposed moves
- Move directories, update internal path references (registry `path:` fields,
  frontmatter paths)
- Optionally write explicit `[dirs]` config to preserve old layout for users
  who prefer it

## Considerations

- **Kanban stays at repo root** — `kanban/` is intentionally outside
  `.spec-driver/`. It's a lightweight operational tool, not a spec-driver
  artifact. Users may use it independently or replace it with their own
  task system. The `.spec-driver/` boundary is for spec-driven artifacts.
- **Convenience symlinks from project root** — the installer could offer to
  create symlinks from conventional project-root locations into `.spec-driver/`,
  e.g. `docs/ -> .spec-driver/tech/`, `contracts/ -> .spec-driver/contracts/`.
  The exact conventions are TBD but the intent is: content that collaborators
  or CI commonly browse gets a short top-level path, while canonical storage
  stays consolidated. Symlinks are optional, convention-driven, and should be
  configurable (possibly via a `[symlinks]` section in `workflow.toml`).
- **Backward compatibility**: if top-level dirs exist and no `[dirs]` config,
  assume legacy layout and warn — don't break.
- **Git history**: directory moves create large diffs. Best done at a natural
  break point or as part of a version bump.
- **ADR candidate**: the default layout change is architectural and should go
  through ADR process before implementation.
- **`registry/`**: already lives under `.spec-driver/` — unaffected by either option.

## Progress

- ADR-006 accepted: Option A (flatten under `.spec-driver/`) with backward-compat symlinks
- DE-044: centralised path constants in `core/paths.py` — completed
- DE-048: `[dirs]` config resolution via `workflow.toml` — completed
- DE-049: flattened layout under `.spec-driver/`, backward-compat symlinks — completed
- IMPR-009 (TUI dashboard) consumes `paths.py` getters and inherits
  configurability for free

## Suggested approach

1. ~~ADR to decide between Option A (flatten) vs Option B (nest) vs status quo~~ — done (ADR-006)
2. ~~Delta: add `[dirs]` config resolution in `paths.py` helpers (non-breaking)~~ — done (DE-048)
3. ~~Delta: change default for new installs (per ADR)~~ — done (DE-049)
4. Delta: `spec-driver migrate` for existing workspaces — deferred (YAGNI at current adoption)
