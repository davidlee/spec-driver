#!/usr/bin/env python3
"""Create backlog artefact (issue/problem/improvement) with next sequential ID."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.backlog import create_backlog_entry


def main() -> None:
  """Create new backlog entry with specified kind and name."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("kind", choices=["issue", "problem", "improvement", "risk"])
  parser.add_argument("name")
  args = parser.parse_args()
  create_backlog_entry(args.kind, args.name)


if __name__ == "__main__":
  main()
