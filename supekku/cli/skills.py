"""Skills management commands."""

from __future__ import annotations

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.skills.sync import sync_skills

app = typer.Typer(help="Skills management", no_args_is_help=True)


@app.command("sync")
def skills_sync() -> None:
  """Sync skills from package to agent target directories.

  Installs allowlisted skills to configured targets (e.g.
  `.claude/skills/`, `.agents/skills/`), prunes de-listed skills,
  and updates `.spec-driver/AGENTS.md`.
  """
  try:
    root = find_repo_root()
  except FileNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

  result = sync_skills(root)

  # Per-target summary
  for target_name, info in result["targets"].items():
    installed = info["installed"]
    pruned = info["pruned"]
    parts: list[str] = []
    if installed:
      parts.append(f"installed {len(installed)}")
    if pruned:
      parts.append(f"pruned {len(pruned)}")
    if parts:
      typer.echo(f"  {target_name}: {', '.join(parts)}")
    else:
      typer.echo(f"  {target_name}: up to date")

  # AGENTS.md summary
  if result["agents_md_changed"]:
    typer.echo(
      f"Wrote {result['written']} skills to .spec-driver/AGENTS.md",
    )
  else:
    typer.echo("AGENTS.md up to date")

  if result["warnings"]:
    for name in result["warnings"]:
      typer.echo(f"  Warning: '{name}' not found", err=True)

  raise typer.Exit(EXIT_SUCCESS)


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
