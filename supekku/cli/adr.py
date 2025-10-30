"""ADR (Architecture Decision Record) management commands."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
import yaml

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption

# Add parent to path for imports
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.decision_registry import DecisionRegistry

app = typer.Typer(help="ADR management commands")


@app.command("sync")
def sync(
  root: RootOption = None,
) -> None:
  """Sync decision registry from ADR files."""
  try:
    registry = DecisionRegistry(root=root)
    registry.sync_with_symlinks()
    typer.echo("ADR registry synchronized successfully")
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("list")
def list_decisions(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (accepted, draft, deprecated, etc.)",
    ),
  ] = None,
  tag: Annotated[
    str | None,
    typer.Option(
      "--tag",
      "-t",
      help="Filter by tag",
    ),
  ] = None,
  spec: Annotated[
    str | None,
    typer.Option(
      "--spec",
      help="Filter by spec reference",
    ),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option(
      "--delta",
      "-d",
      help="Filter by delta reference",
    ),
  ] = None,
  requirement: Annotated[
    str | None,
    typer.Option(
      "--requirement",
      "-r",
      help="Filter by requirement reference",
    ),
  ] = None,
  policy: Annotated[
    str | None,
    typer.Option(
      "--policy",
      "-p",
      help="Filter by policy reference",
    ),
  ] = None,
) -> None:
  """List decisions with optional filtering."""
  try:
    registry = DecisionRegistry(root=root)

    # Apply filters
    if any([tag, spec, delta, requirement, policy]):
      decisions = registry.filter(
        tag=tag,
        spec=spec,
        delta=delta,
        requirement=requirement,
        policy=policy,
      )
    else:
      decisions = list(registry.iter(status=status))

    if not decisions:
      raise typer.Exit(EXIT_SUCCESS)

    # Print decisions
    for decision in sorted(decisions, key=lambda d: d.id):
      updated_date = (
        decision.updated.strftime("%Y-%m-%d") if decision.updated else "N/A"
      )
      # Truncate title if too long
      title = decision.title
      if len(title) > 40:
        title = title[:37] + "..."

      typer.echo(f"{decision.id}\t{decision.status}\t{title}\t{updated_date}")

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("show")
def show(
  decision_id: Annotated[str, typer.Argument(help="Decision ID (e.g., ADR-001)")],
  root: RootOption = None,
) -> None:
  """Show detailed information about a specific decision."""
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


@app.command("new")
def new(
  title: Annotated[str, typer.Argument(help="Title for the new ADR")],
  root: RootOption = None,
  status: Annotated[
    str,
    typer.Option(
      "--status",
      "-s",
      help="Initial status (default: draft)",
    ),
  ] = "draft",
  author: Annotated[
    str | None,
    typer.Option(
      "--author",
      "-a",
      help="Author name",
    ),
  ] = None,
  author_email: Annotated[
    str | None,
    typer.Option(
      "--author-email",
      "-e",
      help="Author email",
    ),
  ] = None,
) -> None:
  """Create a new ADR with the next available ID."""
  try:
    registry = DecisionRegistry(root=root)

    # Find the next available ADR ID
    decisions = registry.collect()
    max_id = 0
    for decision_id in decisions:
      match = re.match(r"ADR-(\d+)", decision_id)
      if match:
        max_id = max(max_id, int(match.group(1)))

    next_id = max_id + 1
    adr_id = f"ADR-{next_id:03d}"

    # Create slug from title
    title_slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")
    filename = f"{adr_id}-{title_slug}.md"

    # Create file path
    adr_path = registry.directory / filename

    # Check if file already exists
    if adr_path.exists():
      typer.echo(f"Error: ADR file already exists: {adr_path}", err=True)
      raise typer.Exit(EXIT_FAILURE)

    # Prepare frontmatter
    today = date.today().isoformat()
    frontmatter = {
      "id": adr_id,
      "title": f"{adr_id}: {title}",
      "status": status,
      "created": today,
      "updated": today,
      "reviewed": today,
    }

    # Add author info if provided
    if author or author_email:
      author_info = {}
      if author:
        author_info["name"] = author
      if author_email:
        author_info["contact"] = f"mailto:{author_email}"
      frontmatter["authors"] = [author_info]

    # Add other empty fields for the new schema
    frontmatter.update(
      {
        "owners": [],
        "supersedes": [],
        "superseded_by": [],
        "policies": [],
        "specs": [],
        "requirements": [],
        "deltas": [],
        "revisions": [],
        "audits": [],
        "related_decisions": [],
        "related_policies": [],
        "tags": [],
        "summary": "",
      },
    )

    # Create content
    content = f"""# {adr_id}: {title}

## Context

**Brief** description of the problem or situation that requires a decision.

## Decision

The decision that was made and key reasoning.

## Consequences

### Positive
- Benefits of this decision

### Negative
- Trade-offs or downsides

### Neutral
- Other impacts to be aware of

## Verification
- Required test suites, monitoring, or audits ensuring compliance.

## References
- [Design artefact link]
- [External research]
"""

    # Write the file
    frontmatter_yaml = yaml.safe_dump(frontmatter, sort_keys=False)
    full_content = f"---\n{frontmatter_yaml}---\n\n{content}"

    # Ensure directory exists
    adr_path.parent.mkdir(parents=True, exist_ok=True)
    adr_path.write_text(full_content, encoding="utf-8")

    typer.echo(f"Created ADR: {adr_path}")

    # Optionally sync registry
    registry.sync()
    raise typer.Exit(EXIT_SUCCESS)

  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
