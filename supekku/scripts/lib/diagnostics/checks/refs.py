"""Cross-reference consistency checks.

Delegates to WorkspaceValidator and translates ValidationIssue results
into DiagnosticResult entries.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from supekku.scripts.lib.diagnostics.models import DiagnosticResult
from supekku.scripts.lib.validation.validator import validate_workspace

if TYPE_CHECKING:
  from supekku.scripts.lib.workspace import Workspace

CATEGORY = "refs"

_LEVEL_TO_STATUS = {
  "error": "fail",
  "warning": "warn",
  "info": "pass",
}


def check_refs(ws: Workspace) -> list[DiagnosticResult]:
  """Check cross-reference consistency by delegating to WorkspaceValidator."""
  try:
    issues = validate_workspace(ws)
  except Exception as exc:  # noqa: BLE001
    return [
      DiagnosticResult(
        category=CATEGORY,
        name="validator",
        status="fail",
        message=f"Validation failed with error: {exc}",
        suggestion="Check workspace integrity; some artifacts may be malformed",
      ),
    ]

  if not issues:
    return [
      DiagnosticResult(
        category=CATEGORY,
        name="cross-references",
        status="pass",
        message="All cross-references resolve",
      ),
    ]

  return [
    DiagnosticResult(
      category=CATEGORY,
      name=issue.artifact,
      status=_LEVEL_TO_STATUS.get(issue.level, "warn"),
      message=issue.message,
    )
    for issue in issues
  ]
