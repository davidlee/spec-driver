"""Legacy re-export shim — see spec_driver.core.pylint_report."""

from spec_driver.core.pylint_report import (
  load_pylint_json,
  render_pylint_summary,
  summarize_pylint_report,
)

__all__ = ["load_pylint_json", "render_pylint_summary", "summarize_pylint_report"]
