#!/usr/bin/env python3
"""Create a breakout requirement file under a spec."""

from __future__ import annotations

import argparse

from supekku.scripts.lib.create_change import (
  create_requirement_breakout,  # type: ignore
)


def build_parser() -> argparse.ArgumentParser:
  """Build argument parser for requirement creation.

  Returns:
    Configured ArgumentParser instance.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("spec", help="Spec ID (e.g. SPEC-200)")
  parser.add_argument("requirement", help="Requirement code (e.g. FR-010)")
  parser.add_argument("title", help="Requirement title")
  parser.add_argument(
    "--kind",
    choices=["functional", "non-functional", "policy", "standard"],
    help="Requirement kind override",
  )
  return parser


def main(argv: list[str] | None = None) -> int:
  """Create a breakout requirement file under a spec.

  Args:
    argv: Optional command-line arguments.

  Returns:
    Exit code: 0 on success.
  """
  parser = build_parser()
  args = parser.parse_args(argv)
  create_requirement_breakout(
    args.spec,
    args.requirement,
    title=args.title,
    kind=args.kind,
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
