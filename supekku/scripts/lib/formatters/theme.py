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

from rich.style import Style
from rich.text import Text
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
    # Policy status colors
    "policy.status.draft": "#7c7876",  # mid grey
    "policy.status.active": "#8ec07c",  # green
    "policy.status.deprecated": "#cc241d",  # red
    # Policy display
    "policy.id": "#458588",  # blue
    # Standard status colors
    "standard.status.draft": "#7c7876",  # mid grey
    "standard.status.required": "#8ec07c",  # green
    "standard.status.default": "#00b8ff",  # sky blue
    "standard.status.deprecated": "#cc241d",  # red
    # Standard display
    "standard.id": "#458588",  # blue
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
    "requirement.status.active": "#8ec07c",  # green
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
    # Drift ledger status colors
    "drift.status.open": "#d79921",  # yellow
    "drift.status.closed": "#7c7876",  # mid grey
    # Drift entry status colors
    "drift.entry.open": "#cc241d",  # red
    "drift.entry.triaged": "#d79921",  # yellow
    "drift.entry.adjudicated": "#00b8ff",  # sky blue
    "drift.entry.resolved": "#8ec07c",  # green
    "drift.entry.deferred": "#7c7876",  # mid grey
    "drift.entry.dismissed": "#3c3836",  # dark grey
    "drift.entry.superseded": "#3c3836",  # dark grey
    # Drift display
    "drift.id": "#ff00c1",  # magenta
    # Memory status colors
    "memory.status.active": "#8ec07c",  # green
    "memory.status.draft": "#7c7876",  # mid grey
    "memory.status.review": "#d79921",  # yellow
    "memory.status.archived": "#3c3836",  # dark grey
    "memory.status.deprecated": "#cc241d",  # red
    "memory.status.superseded": "#cc241d",  # red
    "memory.status.obsolete": "#cc241d",  # red
    # Memory display
    "memory.id": "#458588",  # blue
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
    "requirement.category": "#458588",  # blue
    "backlog.id": "#ff00c1",  # magenta
    # Artifact group colours (DEC-053-11, type selector grouping)
    "artifact.group.governance": "#458588",  # blue
    "artifact.group.change": "#d79921",  # yellow
    "artifact.group.domain": "#00b8ff",  # sky blue
    "artifact.group.operational": "#8ec07c",  # green
    # Track view (DE-054)
    "track.timestamp": "#7c7876",  # mid grey
    "track.cmd": "#cecdcd",  # light grey
    "track.artifact": "#00b8ff",  # sky blue
    "track.status.ok": "#8ec07c",  # green
    "track.status.error": "#cc241d",  # red
    "track.session.0": "#458588",  # blue
    "track.session.1": "#d79921",  # yellow
    "track.session.2": "#8ec07c",  # green
    "track.session.3": "#9600ff",  # purple
    "track.session.4": "#00b8ff",  # sky blue
    "track.session.5": "#ff00c1",  # magenta
    "track.session.6": "#cc241d",  # red
    "track.session.7": "#cecdcd",  # light grey
    # UI elements
    "table.border": "#7c7876",  # mid grey
  }
)


def resolve_style(name: str) -> Style | None:
  """Resolve a theme style name to a Rich Style object.

  Args:
    name: Style name from the theme (e.g., "adr.status.accepted")

  Returns:
    Resolved Style object, or None if the name is not in the theme.
  """
  return SPEC_DRIVER_THEME.styles.get(name)


def styled_text(value: str, style_name: str) -> Text:
  """Create a Rich Text object with a resolved theme style.

  Args:
    value: The text content.
    style_name: Style name from the theme (e.g., "spec.id").

  Returns:
    Text object with the style applied. Unstyled if style_name is not found.
  """
  text = Text(value)
  style = resolve_style(style_name)
  if style:
    text.stylize(style)
  return text


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
    status: Status string (e.g., "active", "pending")

  Returns:
    Style name from theme (e.g., "requirement.status.active")
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


def get_policy_status_style(status: str) -> str:
  """Get the style name for a policy status.

  Args:
    status: Status string (e.g., "active", "draft")

  Returns:
    Style name from theme (e.g., "policy.status.active")
  """
  status_lower = status.lower().replace(" ", "-")
  return f"policy.status.{status_lower}"


def get_standard_status_style(status: str) -> str:
  """Get the style name for a standard status.

  Args:
    status: Status string (e.g., "required", "default")

  Returns:
    Style name from theme (e.g., "standard.status.required")
  """
  status_lower = status.lower().replace(" ", "-")
  return f"standard.status.{status_lower}"


def get_drift_status_style(status: str) -> str:
  """Get the style name for a drift ledger status.

  Args:
    status: Status string (e.g., "open", "closed")

  Returns:
    Style name from theme (e.g., "drift.status.open")
  """
  status_lower = status.lower().replace(" ", "-")
  return f"drift.status.{status_lower}"


def get_drift_entry_status_style(status: str) -> str:
  """Get the style name for a drift entry status.

  Args:
    status: Status string (e.g., "open", "triaged", "resolved")

  Returns:
    Style name from theme (e.g., "drift.entry.resolved")
  """
  status_lower = status.lower().replace(" ", "-")
  return f"drift.entry.{status_lower}"


def get_memory_status_style(status: str) -> str:
  """Get the style name for a memory status.

  Args:
    status: Status string (e.g., "active", "draft")

  Returns:
    Style name from theme (e.g., "memory.status.active")
  """
  status_lower = status.lower().replace(" ", "-")
  return f"memory.status.{status_lower}"
