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
    # General semantic colors
    "info": "#00b8ff",  # sky blue
    "warning": "#d79921",  # yellow
    "danger": "#cc241d",  # red
    "success": "#8ec07c",  # green
    "emphasis": "#ff00c1",  # magenta
    # Artifact types
    "spec.id": "#00b8ff",  # sky blue
    "delta.id": "#d79921",  # yellow
    "requirement.id": "#9600ff",  # purple
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
