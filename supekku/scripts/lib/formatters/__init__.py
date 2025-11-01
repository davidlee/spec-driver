"""Display formatting utilities for artifacts.

Pure formatting functions with no business logic.
Each formatter takes an artifact and returns a formatted string.

This package enforces separation of concerns:
- Formatters: artifact → string (display)
- Registries: persistence and loading
- CLI: args → registry → filter → format → output
"""

from .change_formatters import (
  format_change_list_item,
  format_change_list_json,
  format_change_list_table,
  format_change_with_context,
  format_phase_summary,
)
from .decision_formatters import (
  format_decision_details,
  format_decision_list_json,
  format_decision_list_table,
)
from .spec_formatters import (
  format_package_list,
  format_spec_list_item,
  format_spec_list_json,
  format_spec_list_table,
)
from .table_utils import (
  create_table,
  format_as_json,
  format_as_tsv,
  get_terminal_width,
  render_table,
)

__all__ = [
  "create_table",
  "format_as_json",
  "format_as_tsv",
  "format_change_list_item",
  "format_change_list_json",
  "format_change_list_table",
  "format_change_with_context",
  "format_decision_details",
  "format_decision_list_json",
  "format_decision_list_table",
  "format_package_list",
  "format_phase_summary",
  "format_spec_list_item",
  "format_spec_list_json",
  "format_spec_list_table",
  "get_terminal_width",
  "render_table",
]
