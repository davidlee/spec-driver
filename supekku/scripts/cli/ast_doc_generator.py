#!/usr/bin/env python3
"""CLI wrapper for the Python AST documentation generator.

Provides backward compatibility with the original CLI interface while
using the new modular library API underneath.
"""

import argparse
import sys
from pathlib import Path

from supekku.scripts.lib.docs.python import VariantSpec, generate_docs


def create_parser() -> argparse.ArgumentParser:
  """Create argument parser matching original CLI interface."""
  parser = argparse.ArgumentParser(
    description="Generate deterministic Python documentation from AST",
  )

  parser.add_argument(
    "path",
    type=Path,
    help="Path to Python file or package directory to document",
  )

  parser.add_argument(
    "--type",
    choices=["public", "all", "tests"],
    default="public",
    help="Documentation type: public (default), all, or tests",
  )

  parser.add_argument(
    "--check",
    action="store_true",
    help="Check mode: verify docs are up to date (exit 1 if not)",
  )

  parser.add_argument(
    "--output-dir",
    type=Path,
    default=Path("supekku/docs/deterministic"),
    help="Output directory for generated docs",
  )

  parser.add_argument(
    "--cache-dir",
    type=Path,
    help="Custom cache directory (default: platform-specific)",
  )

  parser.add_argument("--no-cache", action="store_true", help="Disable caching")

  parser.add_argument(
    "--cache-stats",
    action="store_true",
    help="Show cache performance statistics",
  )

  return parser


def _handle_error_result(_result) -> int:
  """Handle error result and return error count."""
  return 1


def _handle_check_result(result) -> int:
  """Handle check mode result and return error count."""
  if result.status == "unchanged":
    return 0

  return 1


def _handle_normal_result(result) -> tuple:
  """Handle normal result and return (created, changed, unchanged) counts."""
  {
    "created": "+",
    "changed": "~",
    "unchanged": "=",
  }[result.status]

  counts = {"created": 0, "changed": 0, "unchanged": 0}
  counts[result.status] = 1
  return counts["created"], counts["changed"], counts["unchanged"]


def _print_summary(
  results: list,
  created_count: int,
  changed_count: int,
  unchanged_count: int,
) -> None:
  """Print summary if not in check mode."""
  if not results or any(hasattr(r, "check") and r.check for r in results):
    return

  len(results)
  summary_parts = []
  if created_count:
    summary_parts.append(f"{created_count} created")
  if changed_count:
    summary_parts.append(f"{changed_count} changed")
  if unchanged_count:
    summary_parts.append(f"{unchanged_count} unchanged")

  ", ".join(summary_parts)


def format_status_output(results: list) -> None:
  """Format and display status output for results."""
  created_count = 0
  changed_count = 0
  unchanged_count = 0
  error_count = 0

  for result in results:
    if result.status == "error":
      error_count += _handle_error_result(result)
    elif hasattr(result, "check") and result.check:
      error_count += _handle_check_result(result)
    else:
      created, changed, unchanged = _handle_normal_result(result)
      created_count += created
      changed_count += changed
      unchanged_count += unchanged

  _print_summary(results, created_count, changed_count, unchanged_count)

  if error_count > 0:
    sys.exit(1)


def main() -> None:
  """Main CLI entry point."""
  parser = create_parser()
  args = parser.parse_args()

  # Convert CLI args to library API params
  variant_spec = {
    "public": VariantSpec.public(),
    "all": VariantSpec.all_symbols(),
    "tests": VariantSpec.tests(),
  }[args.type]

  cache_dir = None if args.no_cache else args.cache_dir

  try:
    # Generate docs using library API
    results = generate_docs(
      unit=args.path,
      variants=[variant_spec],
      check=args.check,
      output_root=args.output_dir,
      cache_dir=cache_dir,
      base_path=args.path.parent if args.path.is_file() else args.path,
    )

    # Process results and show output
    format_status_output(results)

  except FileNotFoundError:
    sys.exit(1)
  except PermissionError:
    sys.exit(1)
  except ValueError:
    sys.exit(1)


if __name__ == "__main__":
  main()
