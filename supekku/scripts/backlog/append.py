#!/usr/bin/env python3
"""Append backlog entries to backlog/backlog.md if missing."""

from __future__ import annotations

from supekku.scripts.lib.backlog import append_backlog_summary


def main() -> None:
  """Append missing entries to backlog summary."""
  additions = append_backlog_summary()
  if additions:
    pass


if __name__ == "__main__":
  main()
