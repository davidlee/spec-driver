#!/usr/bin/env python3
"""CLI tool for managing decision (ADR) registry operations."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.cli_utils import add_root_argument  # type: ignore
from supekku.scripts.lib.decision_registry import DecisionRegistry  # type: ignore


def create_sync_parser(subparsers: argparse._SubParsersAction) -> None:
  """Create the sync command parser."""
  sync_parser = subparsers.add_parser(
    "sync",
    help="Sync decision registry from ADR files",
  )
  add_root_argument(sync_parser)


def create_list_parser(subparsers: argparse._SubParsersAction) -> None:
  """Create the list command parser."""
  list_parser = subparsers.add_parser(
    "list",
    help="List decisions with optional filtering",
  )
  add_root_argument(list_parser)
  list_parser.add_argument(
    "--status",
    help="Filter by status (accepted, draft, deprecated, etc.)",
  )
  list_parser.add_argument("--tag", help="Filter by tag")
  list_parser.add_argument("--spec", help="Filter by spec reference")
  list_parser.add_argument("--delta", help="Filter by delta reference")
  list_parser.add_argument("--requirement", help="Filter by requirement reference")
  list_parser.add_argument("--policy", help="Filter by policy reference")


def create_show_parser(subparsers: argparse._SubParsersAction) -> None:
  """Create the show command parser."""
  show_parser = subparsers.add_parser(
    "show",
    help="Show detailed information about a specific decision",
  )
  add_root_argument(show_parser)
  show_parser.add_argument("decision_id", help="Decision ID (e.g., ADR-001)")


def create_new_parser(subparsers: argparse._SubParsersAction) -> None:
  """Create the new command parser."""
  new_parser = subparsers.add_parser(
    "new",
    help="Create a new ADR with the next available ID",
  )
  add_root_argument(new_parser)
  new_parser.add_argument("title", help="Title for the new ADR")
  new_parser.add_argument(
    "--status",
    default="draft",
    help="Initial status (default: draft)",
  )
  new_parser.add_argument("--author", help="Author name")
  new_parser.add_argument("--author-email", help="Author email")


def handle_sync(args: argparse.Namespace) -> None:
  """Handle the sync command."""
  registry = DecisionRegistry(root=args.root)
  registry.sync_with_symlinks()


def handle_list(args: argparse.Namespace) -> None:
  """Handle the list command."""
  registry = DecisionRegistry(root=args.root)

  # Apply filters
  if any([args.tag, args.spec, args.delta, args.requirement, args.policy]):
    decisions = registry.filter(
      tag=args.tag,
      spec=args.spec,
      delta=args.delta,
      requirement=args.requirement,
      policy=args.policy,
    )
  else:
    decisions = list(registry.iter(status=args.status))

  if not decisions:
    return

  # Print header

  # Print decisions
  for decision in sorted(decisions, key=lambda d: d.id):
    # Truncate title if too long
    title = decision.title
    if len(title) > 40:
      title = title[:37] + "..."


def handle_show(args: argparse.Namespace) -> None:
  """Handle the show command."""
  registry = DecisionRegistry(root=args.root)
  decision = registry.find(args.decision_id)

  if not decision:
    sys.exit(1)

  # Print decision details

  if decision.created:
    pass
  if decision.decided:
    pass
  if decision.updated:
    pass
  if decision.reviewed:
    pass

  if decision.authors:
    pass
  if decision.owners:
    pass

  if decision.supersedes:
    pass
  if decision.superseded_by:
    pass

  if decision.specs:
    pass
  if decision.requirements:
    pass
  if decision.deltas:
    pass
  if decision.revisions:
    pass
  if decision.audits:
    pass

  if decision.related_decisions:
    pass
  if decision.related_policies:
    pass

  if decision.tags:
    pass

  if decision.backlinks:
    for _link_type, _refs in decision.backlinks.items():
      pass


def handle_new(args: argparse.Namespace) -> None:
  """Handle the new command."""
  registry = DecisionRegistry(root=args.root)

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
  title_slug = re.sub(r"[^a-zA-Z0-9]+", "-", args.title.lower()).strip("-")
  filename = f"{adr_id}-{title_slug}.md"

  # Create file path
  adr_path = registry.directory / filename

  # Check if file already exists
  if adr_path.exists():
    sys.exit(1)

  # Prepare frontmatter
  today = date.today().isoformat()
  frontmatter = {
    "id": adr_id,
    "title": f"{adr_id}: {args.title}",
    "status": args.status,
    "created": today,
    "updated": today,
    "reviewed": today,
  }

  # Add author info if provided
  if args.author or args.author_email:
    author = {}
    if args.author:
      author["name"] = args.author
    if args.author_email:
      author["contact"] = f"mailto:{args.author_email}"
    frontmatter["authors"] = [author]

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
  content = f"""# {adr_id}: {args.title}

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

  # Optionally sync registry
  registry.sync()


def main() -> None:
  """Main entry point."""
  parser = argparse.ArgumentParser(
    description="Manage decision (ADR) registry",
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )

  subparsers = parser.add_subparsers(dest="command", help="Available commands")

  create_sync_parser(subparsers)
  create_list_parser(subparsers)
  create_show_parser(subparsers)
  create_new_parser(subparsers)

  args = parser.parse_args()

  if not args.command:
    parser.print_help()
    sys.exit(1)

  try:
    if args.command == "sync":
      handle_sync(args)
    elif args.command == "list":
      handle_list(args)
    elif args.command == "show":
      handle_show(args)
    elif args.command == "new":
      handle_new(args)
  except (FileNotFoundError, ValueError, KeyError):
    sys.exit(1)


if __name__ == "__main__":
  main()
