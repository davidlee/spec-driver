#!/usr/bin/env python3
"""Create a breakout requirement file under a spec."""

from __future__ import annotations

import argparse

from supekku.scripts.lib.changes.creation import (
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
  parser.add_argument(
    "--tags",
    help="Comma-separated discovery tags",
  )
  parser.add_argument(
    "--ext-id",
    dest="ext_id",
    help="External system identifier (e.g. JIRA-1234)",
  )
  parser.add_argument(
    "--ext-url",
    dest="ext_url",
    help="URL to external resource",
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
  tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
  create_requirement_breakout(
    args.spec,
    args.requirement,
    title=args.title,
    kind=args.kind,
    tags=tags,
    ext_id=args.ext_id,
    ext_url=args.ext_url,
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
