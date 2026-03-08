"""Lifecycle hygiene checks.

Detects in-progress deltas that have been stale beyond a configurable
threshold.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from supekku.scripts.lib.core.config import load_workflow_config
from supekku.scripts.lib.diagnostics.models import DiagnosticResult

if TYPE_CHECKING:
  from supekku.scripts.lib.workspace import Workspace

CATEGORY = "lifecycle"

DEFAULT_STALENESS_DAYS = 5


def check_lifecycle(ws: Workspace) -> list[DiagnosticResult]:
  """Check for stale in-progress deltas."""
  config = load_workflow_config(ws.root)
  staleness_days = config.get("doctor", {}).get(
    "staleness_days", DEFAULT_STALENESS_DAYS
  )

  try:
    deltas = ws.delta_registry.collect()
  except Exception as exc:  # noqa: BLE001
    return [
      DiagnosticResult(
        category=CATEGORY,
        name="delta-load",
        status="fail",
        message=f"Could not load deltas: {exc}",
      ),
    ]

  in_progress = {did: d for did, d in deltas.items() if d.status == "in-progress"}

  if not in_progress:
    return [
      DiagnosticResult(
        category=CATEGORY,
        name="stale-deltas",
        status="pass",
        message="No in-progress deltas",
      ),
    ]

  today = datetime.date.today()
  threshold = datetime.timedelta(days=staleness_days)
  results: list[DiagnosticResult] = []

  for did, delta in sorted(in_progress.items()):
    if not delta.updated:
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=did,
          status="warn",
          message=f"{did} is in-progress with no updated date",
          suggestion="Add an 'updated' date to the delta frontmatter",
        ),
      )
      continue

    try:
      updated = datetime.date.fromisoformat(delta.updated)
    except ValueError:
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=did,
          status="warn",
          message=f"{did} has unparseable updated date: {delta.updated}",
        ),
      )
      continue

    age = today - updated
    if age > threshold:
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=did,
          status="warn",
          message=(
            f"{did} in-progress for {age.days} days (threshold: {staleness_days})"
          ),
          suggestion=f"Review {did} — complete, update, or park it",
        ),
      )
    else:
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=did,
          status="pass",
          message=f"{did} in-progress, updated {age.days} days ago",
        ),
      )

  return results
