"""Display formatting utilities for artifacts.

Pure formatting functions with no business logic.
Each formatter takes an artifact and returns a formatted string.

This package enforces separation of concerns:
- Formatters: artifact → string (display)
- Registries: persistence and loading
- CLI: args → registry → filter → format → output
"""

from .backlog_formatters import (
  format_backlog_details,
  format_backlog_list_json,
  format_backlog_list_table,
)
from .change_formatters import (
  format_change_list_item,
  format_change_list_json,
  format_change_list_table,
  format_change_with_context,
  format_delta_details_json,
  format_phase_summary,
)
from .decision_formatters import (
  format_decision_details,
  format_decision_list_json,
  format_decision_list_table,
)
from .requirement_formatters import (
  format_requirement_details,
  format_requirement_list_json,
  format_requirement_list_table,
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
  "format_backlog_details",
  "format_backlog_list_json",
  "format_backlog_list_table",
  "format_change_list_item",
  "format_change_list_json",
  "format_change_list_table",
  "format_change_with_context",
  "format_decision_details",
  "format_decision_list_json",
  "format_decision_list_table",
  "format_delta_details_json",
  "format_package_list",
  "format_phase_summary",
  "format_requirement_details",
  "format_requirement_list_json",
  "format_requirement_list_table",
  "format_spec_list_item",
  "format_spec_list_json",
  "format_spec_list_table",
  "get_terminal_width",
  "render_table",
]
