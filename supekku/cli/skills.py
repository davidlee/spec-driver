"""Skills management commands."""

from __future__ import annotations

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.skills.sync import sync_skills

app = typer.Typer(help="Skills management", no_args_is_help=True)


@app.command("sync")
def skills_sync() -> None:
  """Sync allowlisted skills to .spec-driver/AGENTS.md.

  Reads `.spec-driver/skills.allowlist`, reads skill metadata from
  `.agent/skills/*/SKILL.md`, and writes a managed AGENTS.md with
  only the allowlisted project skills exposed.
  """
  try:
    root = find_repo_root()
  except FileNotFoundError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

  result = sync_skills(root)

  if result["changed"]:
    typer.echo(
      f"Wrote {result['written']} skills to .spec-driver/AGENTS.md",
    )
  else:
    typer.echo("No changes (already up to date)")

  if result["warnings"]:
    for name in result["warnings"]:
      typer.echo(f"  Warning: '{name}' not found", err=True)

  raise typer.Exit(EXIT_SUCCESS)


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
