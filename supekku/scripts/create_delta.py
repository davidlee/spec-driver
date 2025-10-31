#!/usr/bin/env python3
"""Create a Delta bundle with optional plan scaffolding."""

from __future__ import annotations

import argparse

from supekku.scripts.lib.changes.creation import create_delta  # type: ignore


def build_parser() -> argparse.ArgumentParser:
  """Build argument parser for delta creation.

  Returns:
    Configured ArgumentParser instance.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("name", help="Delta title")
  parser.add_argument(
    "--spec",
    dest="specs",
    action="append",
    help="Spec ID impacted (repeatable)",
  )
  parser.add_argument(
    "--requirement",
    dest="requirements",
    action="append",
    help="Requirement ID impacted (repeatable)",
  )
  parser.add_argument(
    "--allow-missing-plan",
    action="store_true",
    help="Skip implementation plan and phase scaffolding",
  )
  return parser


def main(argv: list[str] | None = None) -> int:
  """Create a Delta bundle with optional plan scaffolding.

  Args:
    argv: Optional command-line arguments.

  Returns:
    Exit code: 0 on success.
  """
  parser = build_parser()
  args = parser.parse_args(argv)
  result = create_delta(
    args.name,
    specs=args.specs,
    requirements=args.requirements,
    allow_missing_plan=args.allow_missing_plan,
  )
  for _extra in result.extras:
    pass
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
