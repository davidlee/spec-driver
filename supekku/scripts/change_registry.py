#!/usr/bin/env python3
"""Generate registries for change artefacts (deltas, revisions, audits)."""

from __future__ import annotations

import argparse

from supekku.scripts.lib.change_registry import ChangeRegistry
from supekku.scripts.lib.cli_utils import add_root_argument

KINDS = ["delta", "revision", "audit"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
  """Parse command-line arguments for change registry generation.

  Args:
    argv: Optional list of command-line arguments.

  Returns:
    Parsed argument namespace.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--kind",
    choices=[*KINDS, "all"],
    default="all",
    help="Which registry to regenerate (default: all)",
  )
  add_root_argument(parser, "Repository root (auto-detected if not provided)")
  return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
  """Generate registries for change artefacts.

  Args:
    argv: Optional command-line arguments.

  Returns:
    Exit code: 0 on success.
  """
  args = parse_args(argv)
  kinds = KINDS if args.kind == "all" else [args.kind]
  for kind in kinds:
    registry = ChangeRegistry(root=args.root, kind=kind)
    registry.sync()
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
