# DE-031 Implementation Brief (for Opus)

## Goal

Generate config-tailored, token-cheap agent guidance modules under `.spec-driver/agents/` so skills (especially `/boot`)
can `@reference` them instead of hardcoding paths or dynamically parsing config.

Target outputs (installer-owned, overwriteable):

- `.spec-driver/agents/exec.md`
- `.spec-driver/agents/workflow.md`
- `.spec-driver/agents/glossary.md`
- `.spec-driver/agents/policy.md`

Source inputs:

- `.spec-driver/workflow.toml` (switchboard)
- `.spec-driver/doctrine.md` (escape hatch; small bespoke text)

## Where to implement

- `supekku/scripts/install.py`: after workspace init, render templates into `.spec-driver/agents/`
- `supekku/templates/`: add Jinja2 templates for each module (suggest: `agents/exec.md`, `agents/workflow.md`, etc.)
- TOML parsing: use stdlib `tomllib` (py3.11+) or a tiny dependency-free parser if required

## Design constraints

- Generated docs MUST omit disabled primitives (token conservation).
- Keep each module short and composable; avoid putting “everything” in `workflow.md`.
- Installer may overwrite `.spec-driver/agents/**` on every run.

## Planned: derived template context (phase 2+)

The glossary and other templates need to conditionally render based on which
primitives are active. Workflow.toml doesn't model this directly — it has
`cards.enabled`, `contracts.enabled`, etc. but nothing for specs, deltas,
requirements, verification, backlog.

Rather than littering templates with compound Jinja conditionals, add a
`build_template_context(config) -> dict` function that derives higher-level
flags from the raw config:

- `has_specs`, `has_deltas`, `has_requirements`, `has_backlog`, `has_verification`, etc.
- Cross-cutting: "requirements appear if specs OR backlog enabled"
- Templates get a flat, pre-computed context — `{% if ctx.has_requirements %}`

This keeps workflow.toml lean, derivation logic testable in Python, and
templates maintainable.

## Suggested test strategy

- Add unit tests for “render from config” using a temp repo root:
  1. write `.spec-driver/workflow.toml` with known paths/toggles
  2. run `initialize_workspace(tmp_root, auto_yes=True)`
  3. assert the four files exist and contain expected substitutions (e.g. `kanban/{...}`, `doc/artefacts`, `.contracts`)
  4. assert disabled primitives are absent from `glossary.md` / `policy.md`
