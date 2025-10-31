#!/usr/bin/env python3
"""Create a Spec Revision bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.create_change import create_revision  # type: ignore


def build_parser() -> argparse.ArgumentParser:
  """Build argument parser for revision creation.

  Returns:
    Configured ArgumentParser instance.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("name", help="Revision title (summary)")
  parser.add_argument(
    "--source",
    dest="source_specs",
    action="append",
    help="Source spec ID (repeatable)",
  )
  parser.add_argument(
    "--destination",
    dest="destination_specs",
    action="append",
    help="Destination spec ID (repeatable)",
  )
  parser.add_argument(
    "--requirement",
    dest="requirements",
    action="append",
    help="Requirement ID affected (repeatable)",
  )
  return parser


def main(argv: list[str] | None = None) -> int:
  """Create a Spec Revision bundle.

  Args:
    argv: Optional command-line arguments.

  Returns:
    Exit code: 0 on success.
  """
  parser = build_parser()
  args = parser.parse_args(argv)
  create_revision(
    args.name,
    source_specs=args.source_specs,
    destination_specs=args.destination_specs,
    requirements=args.requirements,
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
