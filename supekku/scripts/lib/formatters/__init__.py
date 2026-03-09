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
from .card_formatters import (
  format_card_details,
  format_card_list_json,
  format_card_list_table,
)
from .cell_helpers import (
  format_date_cell,
  format_tags_cell,
)
from .change_formatters import (
  format_change_list_item,
  format_change_list_json,
  format_change_list_table,
  format_change_with_context,
  format_delta_details_json,
  format_phase_summary,
  format_plan_list_table,
)
from .decision_formatters import (
  format_decision_details,
  format_decision_list_json,
  format_decision_list_table,
)
from .drift_formatters import (
  format_drift_details,
  format_drift_details_json,
  format_drift_list_table,
)
from .memory_formatters import (
  format_memory_details,
  format_memory_list_json,
  format_memory_list_table,
)
from .policy_formatters import (
  format_policy_details,
  format_policy_list_json,
  format_policy_list_table,
)
from .relation_formatters import (
  format_refs_count,
  format_refs_tsv,
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
from .standard_formatters import (
  format_standard_details,
  format_standard_list_json,
  format_standard_list_table,
)
from .table_utils import (
  create_table,
  format_as_json,
  format_as_tsv,
  get_terminal_width,
  render_table,
)

__all__ = [
  "format_date_cell",
  "format_tags_cell",
  "create_table",
  "format_as_json",
  "format_as_tsv",
  "format_backlog_details",
  "format_backlog_list_json",
  "format_backlog_list_table",
  "format_card_details",
  "format_card_list_json",
  "format_card_list_table",
  "format_change_list_item",
  "format_change_list_json",
  "format_change_list_table",
  "format_change_with_context",
  "format_decision_details",
  "format_decision_list_json",
  "format_decision_list_table",
  "format_memory_details",
  "format_memory_list_json",
  "format_memory_list_table",
  "format_delta_details_json",
  "format_drift_details",
  "format_drift_details_json",
  "format_drift_list_table",
  "format_package_list",
  "format_phase_summary",
  "format_refs_count",
  "format_refs_tsv",
  "format_plan_list_table",
  "format_policy_details",
  "format_policy_list_json",
  "format_policy_list_table",
  "format_requirement_details",
  "format_requirement_list_json",
  "format_requirement_list_table",
  "format_spec_list_item",
  "format_spec_list_json",
  "format_spec_list_table",
  "format_standard_details",
  "format_standard_list_json",
  "format_standard_list_table",
  "get_terminal_width",
  "render_table",
]
