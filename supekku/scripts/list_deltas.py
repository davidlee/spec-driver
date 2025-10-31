#!/usr/bin/env python3
"""List deltas with optional filtering and status grouping.

Thin script layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

# pylint: disable=wrong-import-position
from supekku.scripts.lib.change_lifecycle import (  # type: ignore
  VALID_STATUSES,
  normalize_status,
)
from supekku.scripts.lib.change_registry import ChangeRegistry  # type: ignore
from supekku.scripts.lib.core.cli_utils import add_root_argument
from supekku.scripts.lib.formatters.change_formatters import (  # type: ignore
  format_change_list_item,
  format_change_with_context,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser(description=__doc__)
  add_root_argument(parser)
  parser.add_argument(
    "ids",
    nargs="*",
    help="Specific delta IDs to display (e.g., DE-002 DE-005)",
  )
  parser.add_argument(
    "--status",
    help=f"Filter by status. Valid statuses: {', '.join(sorted(VALID_STATUSES))}",
  )
  parser.add_argument(
    "--details",
    action="store_true",
    help="Show related specs, requirements, and phases from relationships metadata",
  )
  return parser.parse_args(argv)


def matches_filters(
  artifact,
  *,
  delta_ids: list[str] | None,
  status: str | None,
) -> bool:
  """Check if artifact matches the given filters."""
  if delta_ids and artifact.id not in delta_ids:
    return False
  # Normalize both statuses for comparison to handle variants
  # like "complete" vs "completed"
  return not (status and normalize_status(artifact.status) != normalize_status(status))


def main(argv: list[str] | None = None) -> int:
  """Main entry point for listing deltas."""
  args = parse_args(argv)
  root = args.root

  registry = ChangeRegistry(root=root, kind="delta")
  artifacts = list(registry.collect().values())

  # Filter artifacts
  delta_ids = [delta_id.strip().upper() for delta_id in args.ids] if args.ids else None
  status = (args.status or "").strip() or None

  filtered = [
    artifact
    for artifact in artifacts
    if matches_filters(artifact, delta_ids=delta_ids, status=status)
  ]

  # Group by status
  grouped: dict[str, list] = defaultdict(list)
  for artifact in filtered:
    grouped[artifact.status].append(artifact)

  # Sort statuses for consistent output
  sorted_statuses = sorted(grouped.keys())

  # Output grouped by status
  for status_key in sorted_statuses:
    deltas = sorted(grouped[status_key], key=lambda a: a.id)
    if not deltas:
      continue

    # Print deltas
    for delta in deltas:
      if args.details:
        print(format_change_with_context(delta))
      else:
        print(format_change_list_item(delta))

  return 0


if __name__ == "__main__":
  raise SystemExit(main())
