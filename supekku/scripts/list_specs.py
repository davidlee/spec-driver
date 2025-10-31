#!/usr/bin/env python3
"""List SPEC/PROD artefacts with optional substring filtering.

Thin script layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

# pylint: disable=wrong-import-position
from supekku.scripts.lib.core.cli_utils import add_root_argument
from supekku.scripts.lib.formatters.spec_formatters import (  # type: ignore
  format_spec_list_item,
)
from supekku.scripts.lib.spec_registry import SpecRegistry  # type: ignore


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
  """Parse command-line arguments for spec listing.

  Args:
    argv: Optional list of command-line arguments.

  Returns:
    Parsed argument namespace.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  add_root_argument(parser)
  parser.add_argument(
    "--kind",
    choices=["tech", "product", "all"],
    default="all",
    help="Restrict to tech specs, product specs, or both",
  )
  parser.add_argument(
    "--filter",
    dest="substring",
    help="Substring to match against spec ID, slug, or name (case-insensitive)",
  )
  parser.add_argument(
    "--package",
    dest="package_filter",
    help="Substring to match against declared package paths",
  )
  parser.add_argument(
    "--package-path",
    dest="package_path",
    help=(
      "Exact package path to resolve via by-package index "
      "(e.g. internal/infrastructure/git)"
    ),
  )
  parser.add_argument(
    "--for-path",
    nargs="?",
    const=".",
    metavar="PATH",
    default=None,
    help=(
      "Filter specs whose packages include PATH "
      "(defaults to the current working directory)"
    ),
  )
  parser.add_argument(
    "--paths",
    action="store_true",
    help="Include relative file paths in the output",
  )
  parser.add_argument(
    "--packages",
    action="store_true",
    help="Include package list in the output",
  )
  return parser.parse_args(argv)


def normalise_kind(requested: str, spec_id: str) -> bool:
  """Check if spec ID matches the requested kind filter.

  Args:
    requested: Kind filter ("all", "tech", or "product").
    spec_id: Spec identifier to check.

  Returns:
    True if spec matches the filter, False otherwise.
  """
  if requested == "all":
    return True
  if requested == "tech":
    return spec_id.startswith("SPEC-")
  if requested == "product":
    return spec_id.startswith("PROD-")
  return True


def main(argv: list[str] | None = None) -> int:
  """List SPEC/PROD artifacts with filtering and formatting options.

  Args:
    argv: Optional command-line arguments.

  Returns:
    Exit code: 0 on success.
  """
  args = parse_args(argv)
  registry = SpecRegistry(args.root)
  substring = (args.substring or "").strip().lower()

  spec_root = registry.root / "specify" / "tech"
  package_index_root = spec_root / "by-package"

  package_filters: list[str] = []
  package_exact: set[str] = set()

  if args.package_filter:
    package_filters.append(args.package_filter.strip().lower())

  def resolve_package_path(package_path: str) -> None:
    """Resolve package path to spec ID via by-package index."""
    node = package_index_root / Path(package_path) / "spec"
    if node.exists():
      try:
        target = node.resolve()
        package_exact.add(target.name)
      except OSError:
        pass

  if args.package_path:
    resolve_package_path(args.package_path.strip())

  if args.for_path is not None:
    raw_path = args.for_path
    base = Path.cwd() if raw_path == "." else Path(raw_path)
    if not base.is_absolute():
      base = (Path.cwd() / base).resolve()
    try:
      relative = base.relative_to(package_index_root)
      resolve_package_path(str(relative))
    except ValueError:
      try:
        relative = base.relative_to(registry.root)
        package_filters.append(relative.as_posix().lower())
      except ValueError:
        package_filters.append(base.as_posix().lower())

  specs = registry.all_specs()
  if substring:
    specs = [
      spec
      for spec in specs
      if substring in spec.id.lower()
      or substring in spec.slug.lower()
      or substring in spec.name.lower()
    ]

  if package_exact:
    specs = [spec for spec in specs if spec.id in package_exact]

  if package_filters:
    specs = [
      spec
      for spec in specs
      if spec.packages
      and any(
        any(filter_value in pkg.lower() for pkg in spec.packages)
        for filter_value in package_filters
      )
    ]

  specs.sort(key=lambda spec: spec.id)

  for spec in specs:
    if not normalise_kind(args.kind, spec.id):
      continue
    line = format_spec_list_item(
      spec,
      include_path=args.paths,
      include_packages=args.packages,
      root=registry.root,
    )
    print(line)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
