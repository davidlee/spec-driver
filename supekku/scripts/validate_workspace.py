#!/usr/bin/env python3
"""Validate workspace metadata and relationships."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.backlog import find_repo_root
from supekku.scripts.lib.cli_utils import add_root_argument
from supekku.scripts.lib.validator import validate_workspace  # type: ignore
from supekku.scripts.lib.workspace import Workspace  # type: ignore


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__)
  add_root_argument(parser, "Repository root (auto-detected if not provided)")
  parser.add_argument(
    "--sync",
    action="store_true",
    help="Synchronise registries before validation",
  )
  parser.add_argument(
    "--strict",
    action="store_true",
    help="Enable strict validation (warn about deprecated ADR references)",
  )
  return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
  args = parse_args(argv)
  ws = (
    Workspace(find_repo_root(args.root))
    if hasattr(args, "root")
    else Workspace.from_cwd()
  )
  if args.sync:
    ws.reload_specs()
    ws.sync_change_registries()
    ws.sync_requirements()

  issues = validate_workspace(ws, strict=args.strict)
  if not issues:
    return 0

  for _issue in issues:
    pass
  return 1


def get_repo_root(start: Path) -> Path:
  return find_repo_root(start)


if __name__ == "__main__":
  raise SystemExit(main())
