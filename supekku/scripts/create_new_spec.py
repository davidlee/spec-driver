#!/usr/bin/env python3
"""Create a new SPEC or PROD document bundle from templates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

# pylint: disable=wrong-import-position
from supekku.scripts.lib.create_spec import (  # type: ignore
  CreateSpecOptions,
  SpecCreationError,
  create_spec,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
  """Parse command-line arguments for spec creation.

  Args:
    argv: List of command-line arguments.

  Returns:
    Parsed argument namespace with spec_name joined as a single string.

  Raises:
    SystemExit: If spec_name is not provided.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "spec_name",
    nargs=argparse.REMAINDER,
    help="Name of the spec to create",
  )
  parser.add_argument(
    "--type",
    choices=["tech", "product"],
    default="tech",
    help="Spec type (tech or product)",
  )
  parser.add_argument(
    "--json",
    action="store_true",
    help="Emit machine-readable JSON output",
  )
  parser.add_argument(
    "--no-testing",
    dest="testing",
    action="store_false",
    help="Skip companion testing guide (tech specs only)",
  )
  parser.set_defaults(testing=True)

  args = parser.parse_args(argv)
  if not args.spec_name:
    parser.error("spec name is required")
  args.spec_name = " ".join(args.spec_name).strip()
  return args


def main(argv: list[str] | None = None) -> int:
  """Create a new SPEC or PROD document bundle.

  Args:
    argv: Optional command-line arguments. Defaults to sys.argv[1:].

  Returns:
    Exit code: 0 on success, 1 on error.
  """
  namespace = parse_args(argv or sys.argv[1:])
  options = CreateSpecOptions(
    spec_type=namespace.type,
    include_testing=namespace.testing,
    emit_json=namespace.json,
  )

  try:
    result = create_spec(namespace.spec_name, options)
  except SpecCreationError:
    return 1

  if options.emit_json or result.test_path:
    pass

  return 0


if __name__ == "__main__":
  raise SystemExit(main())
