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
  format_change_with_context,
  format_phase_summary,
)
from .decision_formatters import format_decision_details
from .spec_formatters import format_package_list, format_spec_list_item

__all__ = [
  "format_change_list_item",
  "format_change_with_context",
  "format_decision_details",
  "format_package_list",
  "format_phase_summary",
  "format_spec_list_item",
]
