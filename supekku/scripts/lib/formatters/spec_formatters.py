"""Specification (SPEC/PROD) display formatters.

Pure formatting functions with no business logic.
Formatters take Spec objects and return formatted strings for display.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from pathlib import Path

  from supekku.scripts.lib.specs.models import Spec


def format_package_list(packages: list[str]) -> str:
  """Format list of packages as comma-separated string.

  Args:
    packages: List of package paths

  Returns:
    Comma-separated string of packages
  """
  return ",".join(packages)


def format_spec_list_item(
  spec: "Spec",
  *,
  include_path: bool = False,
  include_packages: bool = False,
  root: "Path | None" = None,
) -> str:
  """Format spec as tab-separated list item with optional columns.

  Args:
    spec: Specification object to format
    include_path: Include file path instead of slug (default: False)
    include_packages: Include package list (default: False)
    root: Repository root for relative path calculation (required if include_path=True)

  Returns:
    Tab-separated string: "{id}\\t{slug|path}[\\t{packages}]"
  """
  line = spec.id

  if include_path:
    if root is None:
      msg = "root parameter required when include_path=True"
      raise ValueError(msg)
    try:
      rel = spec.path.relative_to(root)
    except ValueError:
      rel = spec.path
    line += f"\t{rel.as_posix()}"
  else:
    line += f"\t{spec.slug}"

  if include_packages:
    pkg_list = format_package_list(spec.packages)
    line += f"\t{pkg_list}"

  return line
