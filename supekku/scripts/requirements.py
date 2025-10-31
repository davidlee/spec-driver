#!/usr/bin/env python3
"""Manage requirements registry: sync, list, search, and update status."""

from __future__ import annotations

import argparse
from pathlib import Path

from supekku.scripts.lib.core.paths import get_registry_dir  # type: ignore
from supekku.scripts.lib.requirements import (  # type: ignore
  VALID_STATUSES,
  RequirementsRegistry,
)
from supekku.scripts.lib.specs.registry import SpecRegistry  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = get_registry_dir(ROOT) / "requirements.yaml"
DEFAULT_SPEC_DIRS = [ROOT / "specify" / "tech", ROOT / "specify" / "product"]
DEFAULT_DELTA_DIRS = [ROOT / "change" / "deltas"]
DEFAULT_REVISION_DIRS = [ROOT / "change" / "revisions"]
DEFAULT_AUDIT_DIRS = [ROOT / "change" / "audits"]


def build_parser() -> argparse.ArgumentParser:
  """Build argument parser for requirements registry management.

  Returns:
    Configured ArgumentParser with subcommands.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  subparsers = parser.add_subparsers(dest="command", required=True)

  sync_parser = subparsers.add_parser(
    "sync",
    help="Synchronise requirements registry",
  )
  sync_parser.add_argument(
    "--spec-dir",
    dest="spec_dirs",
    action="append",
    help=(
      "Additional spec directory to scan "
      "(defaults include specify/tech and specify/product)"
    ),
  )

  list_parser = subparsers.add_parser("list", help="List requirements")
  list_parser.add_argument("--query", help="Substring to match")
  list_parser.add_argument(
    "--status",
    choices=sorted(VALID_STATUSES),
    help="Filter by lifecycle status",
  )
  list_parser.add_argument("--spec", help="Filter by primary spec or containing spec")
  list_parser.add_argument(
    "--implemented-by",
    dest="implemented_by",
    help="Filter by implementing delta ID",
  )
  list_parser.add_argument(
    "--introduced-by",
    dest="introduced_by",
    help="Filter by revision ID that introduced the requirement",
  )
  list_parser.add_argument(
    "--verified-by",
    dest="verified_by",
    help="Filter by audit ID verifying the requirement",
  )

  move_parser = subparsers.add_parser(
    "move",
    help="Move a requirement to a new primary spec",
  )
  move_parser.add_argument("uid", help="Requirement UID (e.g. SPEC-002.FR-001)")
  move_parser.add_argument("target_spec", help="Target spec ID")
  move_parser.add_argument(
    "--introduced-by",
    dest="introduced_by",
    help="Revision ID introducing the requirement in the new spec",
  )

  show_parser = subparsers.add_parser(
    "show",
    help="Show full record for a requirement",
  )
  show_parser.add_argument("uid", help="Requirement UID (e.g. SPEC-002.FR-001)")

  status_parser = subparsers.add_parser(
    "set-status",
    help="Update lifecycle status for a requirement",
  )
  status_parser.add_argument("uid", help="Requirement UID")
  status_parser.add_argument("status", choices=sorted(VALID_STATUSES))

  return parser


def main(argv: list[str] | None = None) -> int:
  """Manage requirements registry: sync, list, search, and update status.

  Args:
    argv: Optional command-line arguments.

  Returns:
    Exit code: 0 on success, 1 on error.
  """
  parser = build_parser()
  args = parser.parse_args(argv)

  registry = RequirementsRegistry(REGISTRY_PATH)
  spec_registry = SpecRegistry(ROOT)

  if args.command == "sync":
    spec_dirs = DEFAULT_SPEC_DIRS.copy()
    if args.spec_dirs:
      spec_dirs.extend(Path(d) for d in args.spec_dirs)
    registry.sync_from_specs(
      spec_dirs,
      spec_registry=spec_registry,
      delta_dirs=DEFAULT_DELTA_DIRS,
      revision_dirs=DEFAULT_REVISION_DIRS,
      audit_dirs=DEFAULT_AUDIT_DIRS,
    )
    registry.save()
    return 0

  if args.command == "move":
    try:
      registry.move_requirement(
        args.uid,
        args.target_spec,
        spec_registry=spec_registry,
        introduced_by=args.introduced_by,
      )
    except Exception:  # pylint: disable=broad-except
      return 1
    registry.save()
    return 0

  if args.command == "list":
    results = registry.search(
      query=args.query,
      status=args.status,
      spec=args.spec,
      implemented_by=args.implemented_by,
      introduced_by=args.introduced_by,
      verified_by=args.verified_by,
    )
    for record in results:
      details = f"{record.uid}\t{record.status}\t{record.title}"
      if record.primary_spec:
        details += f" (primary: {record.primary_spec})"
    return 0

  if args.command == "show":
    record = registry.records.get(args.uid)
    if not record:
      return 1
    registry.save()
    return 0

  if args.command == "set-status":
    registry.set_status(args.uid, args.status)
    registry.save()
    return 0

  parser.error("Unknown command")
  return 1


if __name__ == "__main__":
  raise SystemExit(main())
