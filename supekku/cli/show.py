"""Show commands for displaying detailed information about artifacts."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption

# Add parent to path for imports
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.decision_registry import DecisionRegistry

app = typer.Typer(help="Show detailed artifact information")


@app.command("adr")
def show_adr(
  decision_id: Annotated[str, typer.Argument(help="Decision ID (e.g., ADR-001)")],
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific decision/ADR."""
  try:
    registry = DecisionRegistry(root=root)
    decision = registry.find(decision_id)

    if not decision:
      typer.echo(f"Error: Decision not found: {decision_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    # Print decision details
    typer.echo(f"ID: {decision.id}")
    typer.echo(f"Title: {decision.title}")
    typer.echo(f"Status: {decision.status}")

    if decision.created:
      typer.echo(f"Created: {decision.created}")
    if decision.decided:
      typer.echo(f"Decided: {decision.decided}")
    if decision.updated:
      typer.echo(f"Updated: {decision.updated}")
    if decision.reviewed:
      typer.echo(f"Reviewed: {decision.reviewed}")

    if decision.authors:
      typer.echo(f"Authors: {', '.join(str(a) for a in decision.authors)}")
    if decision.owners:
      typer.echo(f"Owners: {', '.join(str(o) for o in decision.owners)}")

    if decision.supersedes:
      typer.echo(f"Supersedes: {', '.join(decision.supersedes)}")
    if decision.superseded_by:
      typer.echo(f"Superseded by: {', '.join(decision.superseded_by)}")

    if decision.specs:
      typer.echo(f"Related specs: {', '.join(decision.specs)}")
    if decision.requirements:
      typer.echo(f"Requirements: {', '.join(decision.requirements)}")
    if decision.deltas:
      typer.echo(f"Deltas: {', '.join(decision.deltas)}")
    if decision.revisions:
      typer.echo(f"Revisions: {', '.join(decision.revisions)}")
    if decision.audits:
      typer.echo(f"Audits: {', '.join(decision.audits)}")

    if decision.related_decisions:
      typer.echo(f"Related decisions: {', '.join(decision.related_decisions)}")
    if decision.related_policies:
      typer.echo(f"Related policies: {', '.join(decision.related_policies)}")

    if decision.tags:
      typer.echo(f"Tags: {', '.join(decision.tags)}")

    if decision.backlinks:
      typer.echo("\nBacklinks:")
      for link_type, refs in decision.backlinks.items():
        typer.echo(f"  {link_type}: {', '.join(refs)}")

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
