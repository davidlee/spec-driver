"""Rich theme configuration for spec-driver.

Centralizes color and style definitions for consistent CLI output.

Color Palette:
- Green:      #8ec07c
- Blue:       #458588
- Yellow:     #d79921
- Red:        #cc241d
- Magenta:    #ff00c1 (max emphasis)
- Purple:     #9600ff
- Sky Blue:   #00b8ff
- Dark Grey:  #3c3836
- Mid Grey:   #7c7876
- Light Grey: #cecdcd
"""

from __future__ import annotations

from rich.theme import Theme

# Spec-driver application theme
SPEC_DRIVER_THEME = Theme(
  {
    # ADR status colors
    "adr.status.accepted": "#8ec07c",  # green
    "adr.status.rejected": "#cc241d",  # red
    "adr.status.deprecated": "#cc241d",  # red
    "adr.status.revision-required": "#9600ff",  # purple
    "adr.status.proposed": "#d79921",  # yellow
    "adr.status.draft": "#7c7876",  # mid grey
    # ADR display
    "adr.id": "#458588",  # blue
    # Change artifact status colors
    "change.status.completed": "#8ec07c",  # green
    "change.status.complete": "#8ec07c",  # green (legacy)
    "change.status.in-progress": "#d79921",  # yellow
    "change.status.pending": "#00b8ff",  # sky blue
    "change.status.draft": "#7c7876",  # mid grey
    "change.status.deferred": "#cc241d",  # red
    # Spec status colors
    "spec.status.active": "#8ec07c",  # green
    "spec.status.live": "#8ec07c",  # green
    "spec.status.draft": "#cecdcd",  # light grey
    "spec.status.stub": "#7c7876",  # mid grey
    "spec.status.deprecated": "#cc241d",  # red
    "spec.status.archived": "#3c3836",  # dark grey
    # Requirement status colors
    "requirement.status.live": "#8ec07c",  # green
    "requirement.status.implemented": "#8ec07c",  # green
    "requirement.status.verified": "#00ff00 bold",  # hot lime green
    "requirement.status.in-progress": "#d79921",  # yellow
    "requirement.status.pending": "#00b8ff",  # sky blue
    "requirement.status.retired": "#cc241d",  # red
    # Backlog item status colors (issue)
    "backlog.issue.open": "#cc241d",  # red
    "backlog.issue.in-progress": "#d79921",  # yellow
    "backlog.issue.resolved": "#8ec07c",  # green
    "backlog.issue.closed": "#7c7876",  # mid grey
    # Backlog item status colors (problem)
    "backlog.problem.captured": "#d79921",  # yellow
    "backlog.problem.analyzed": "#00b8ff",  # sky blue
    "backlog.problem.addressed": "#8ec07c",  # green
    # Backlog item status colors (improvement)
    "backlog.improvement.idea": "#00b8ff",  # sky blue
    "backlog.improvement.planned": "#d79921",  # yellow
    "backlog.improvement.implemented": "#8ec07c",  # green
    # Backlog item status colors (risk)
    "backlog.risk.suspected": "#d79921",  # yellow
    "backlog.risk.confirmed": "#cc241d",  # red
    "backlog.risk.mitigated": "#8ec07c",  # green
    # General semantic colors
    "info": "#00b8ff",  # sky blue
    "warning": "#d79921",  # yellow
    "danger": "#cc241d",  # red
    "success": "#8ec07c",  # green
    "emphasis": "#ff00c1",  # magenta
    # Artifact types
    "spec.id": "#00b8ff",  # sky blue
    "change.id": "#d79921",  # yellow
    "requirement.id": "#9600ff",  # purple
    "backlog.id": "#ff00c1",  # magenta
    # UI elements
    "table.border": "#7c7876",  # mid grey
  }
)


def get_adr_status_style(status: str) -> str:
  """Get the style name for an ADR status.

  Args:
    status: Status string (e.g., "accepted", "deprecated")

  Returns:
    Style name from theme (e.g., "adr.status.accepted")
  """
  status_lower = status.lower().replace(" ", "-")
  return f"adr.status.{status_lower}"


def get_change_status_style(status: str) -> str:
  """Get the style name for a change artifact status.

  Args:
    status: Status string (e.g., "completed", "in-progress")

  Returns:
    Style name from theme (e.g., "change.status.completed")
  """
  status_lower = status.lower().replace(" ", "-")
  return f"change.status.{status_lower}"


def get_spec_status_style(status: str) -> str:
  """Get the style name for a spec status.

  Args:
    status: Status string (e.g., "active", "draft")

  Returns:
    Style name from theme (e.g., "spec.status.active")
  """
  status_lower = status.lower().replace(" ", "-")
  return f"spec.status.{status_lower}"


def get_requirement_status_style(status: str) -> str:
  """Get the style name for a requirement status.

  Args:
    status: Status string (e.g., "live", "pending")

  Returns:
    Style name from theme (e.g., "requirement.status.live")
  """
  status_lower = status.lower().replace(" ", "-")
  return f"requirement.status.{status_lower}"


def get_backlog_status_style(kind: str, status: str) -> str:
  """Get the style name for a backlog item status.

  Args:
    kind: Backlog item kind (issue, problem, improvement, risk)
    status: Status string (e.g., "open", "captured")

  Returns:
    Style name from theme (e.g., "backlog.issue.open")
  """
  kind_lower = kind.lower()
  status_lower = status.lower().replace(" ", "-")
  return f"backlog.{kind_lower}.{status_lower}"
