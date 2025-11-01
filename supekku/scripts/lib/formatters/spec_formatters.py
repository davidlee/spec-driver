"""Specification (SPEC/PROD) display formatters.

Pure formatting functions with no business logic.
Formatters take Spec objects and return formatted strings for display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.table_utils import (
  add_row_with_truncation,
  calculate_column_widths,
  create_table,
  format_as_json,
  format_as_tsv,
  get_terminal_width,
  render_table,
)

if TYPE_CHECKING:
  from collections.abc import Sequence
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
  spec: Spec,
  *,
  include_path: bool = False,
  include_packages: bool = False,
  root: Path | None = None,
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


def format_spec_list_table(
  specs: Sequence[Spec],
  format_type: str = "table",
  no_truncate: bool = False,
  include_packages: bool = False,
) -> str:
  """Format specs as table, JSON, or TSV.

  Args:
    specs: List of Spec objects to format
    format_type: Output format (table|json|tsv)
    no_truncate: If True, don't truncate long fields
    include_packages: Include package list in output

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_spec_list_json(specs)

  if format_type == "tsv":
    rows = []
    for spec in specs:
      row = [spec.id, spec.slug]
      if include_packages:
        row.append(format_package_list(spec.packages))
      rows.append(row)
    return format_as_tsv(rows)

  # table format
  columns = ["ID", "Slug"]
  if include_packages:
    columns.append("Packages")

  table = create_table(columns=columns, title="Specifications")

  terminal_width = get_terminal_width()
  num_cols = len(columns)
  max_widths = calculate_column_widths(terminal_width, num_columns=num_cols)

  for spec in specs:
    row_data = [spec.id, spec.slug]
    if include_packages:
      row_data.append(format_package_list(spec.packages))

    add_row_with_truncation(
      table,
      row_data,
      max_widths=max_widths if not no_truncate else None,
    )

  return render_table(table)


def format_spec_list_json(specs: Sequence[Spec]) -> str:
  """Format specs as JSON array.

  Args:
    specs: List of Spec objects

  Returns:
    JSON string with structure: {"items": [...]}
  """
  items = []
  for spec in specs:
    item = {
      "id": spec.id,
      "slug": spec.slug,
      "name": spec.name,
      "packages": spec.packages if spec.packages else [],
    }
    items.append(item)

  return format_as_json(items)
