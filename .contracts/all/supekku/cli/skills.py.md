# supekku.cli.skills

Skills management commands.

## Constants

- `app`

## Functions

- @app.command(sync) `skills_sync() -> None`: Sync skills from package to agent target directories.

Installs allowlisted skills to configured targets (e.g.
`.claude/skills/`, `.agents/skills/`), prunes de-listed skills,
and updates `.spec-driver/AGENTS.md`.
