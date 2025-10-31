#!/usr/bin/env python3
"""CLI tool for managing decision (ADR) registry operations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.cli_utils import add_root_argument  # type: ignore
from supekku.scripts.lib.decision_creation import (  # type: ignore
  ADRAlreadyExistsError,
  ADRCreationOptions,
  create_adr,
)
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
  try:
    registry = DecisionRegistry(root=args.root)
    options = ADRCreationOptions(
      title=args.title,
      status=args.status,
      author=args.author if hasattr(args, "author") else None,
      author_email=args.author_email if hasattr(args, "author_email") else None,
    )

    result = create_adr(registry, options, sync_registry=True)
    print(f"Created ADR: {result.path}")
  except ADRAlreadyExistsError:
    sys.exit(1)


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
