#!/usr/bin/env python3
"""Run pylint with json2 output and print a compact summary."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from supekku.scripts.lib.core.paths import get_run_dir
from supekku.scripts.lib.core.pylint_report import (
  load_pylint_json,
  render_pylint_summary,
  summarize_pylint_report,
)

DEFAULT_TARGETS = ["supekku"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
  """Parse command-line arguments for pylint reporting.

  Args:
    argv: Optional command-line arguments.

  Returns:
    Parsed arguments namespace.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "targets",
    nargs="*",
    help="Files or directories to lint (defaults to supekku)",
  )
  parser.add_argument(
    "--top",
    type=int,
    default=10,
    help="Maximum rows to show per summary section",
  )
  parser.add_argument(
    "--write-json",
    type=Path,
    help="Write full pylint json2 output to this file",
  )
  return parser.parse_args(argv)


def default_json_path(targets: list[str]) -> Path:
  """Choose a default output path for the lint report.

  Args:
    targets: Lint targets for the run.

  Returns:
    Path under .spec-driver/run/pylint/.
  """
  run_dir = get_run_dir() / "pylint"
  filename = "full.json" if targets == DEFAULT_TARGETS else "files.json"
  return run_dir / filename


def run_pylint(targets: list[str]) -> subprocess.CompletedProcess[str]:
  """Execute pylint with json2 output for the given targets.

  Args:
    targets: Files or directories to lint.

  Returns:
    Completed subprocess result.
  """
  command = [
    sys.executable,
    "-m",
    "pylint",
    *targets,
    "--output-format=json2",
    "--score=y",
  ]
  return subprocess.run(
    command,
    check=False,
    capture_output=True,
    text=True,
  )


def write_json_report(path: Path, raw: str) -> None:
  """Persist raw pylint json output to disk.

  Args:
    path: Output file path.
    raw: Raw json payload.
  """
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(raw, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
  """Run pylint and print a compact summary.

  Args:
    argv: Optional command-line arguments.

  Returns:
    Pylint subprocess exit code, or 1 if output parsing fails.
  """
  args = parse_args(argv)
  targets = args.targets or DEFAULT_TARGETS
  result = run_pylint(targets)

  if result.stderr.strip():
    print(result.stderr.strip(), file=sys.stderr)

  try:
    report = load_pylint_json(result.stdout)
  except ValueError as exc:
    print(f"Failed to parse pylint output: {exc}", file=sys.stderr)
    if result.stdout.strip():
      print(result.stdout.strip(), file=sys.stderr)
    return 1

  json_path = args.write_json or default_json_path(targets)
  write_json_report(json_path, result.stdout)

  summary = summarize_pylint_report(report)
  print(
    render_pylint_summary(
      summary,
      targets=targets,
      json_path=json_path,
      top_n=args.top,
    )
  )
  return result.returncode


if __name__ == "__main__":
  raise SystemExit(main())
