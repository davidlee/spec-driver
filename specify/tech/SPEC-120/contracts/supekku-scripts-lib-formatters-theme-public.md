# supekku.scripts.lib.formatters.theme

Rich theme configuration for spec-driver.

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

## Module Notes

- 8ec07c
- 458588
- d79921
- cc241d
- ff00c1 (max emphasis)
- 9600ff
- 00b8ff
- 3c3836
- 7c7876
- cecdcd

## Constants

- `SPEC_DRIVER_THEME` - Spec-driver application theme

## Functions

- `get_adr_status_style(status) -> str`: Get the style name for an ADR status.

Args:
  status: Status string (e.g., "accepted", "deprecated")

Returns:
  Style name from theme (e.g., "adr.status.accepted")
- `get_backlog_status_style(kind, status) -> str`: Get the style name for a backlog item status.

Args:
  kind: Backlog item kind (issue, problem, improvement, risk)
  status: Status string (e.g., "open", "captured")

Returns:
  Style name from theme (e.g., "backlog.issue.open")
- `get_change_status_style(status) -> str`: Get the style name for a change artifact status.

Args:
  status: Status string (e.g., "completed", "in-progress")

Returns:
  Style name from theme (e.g., "change.status.completed")
- `get_requirement_status_style(status) -> str`: Get the style name for a requirement status.

Args:
  status: Status string (e.g., "active", "pending")

Returns:
  Style name from theme (e.g., "requirement.status.active")
- `get_spec_status_style(status) -> str`: Get the style name for a spec status.

Args:
  status: Status string (e.g., "active", "draft")

Returns:
  Style name from theme (e.g., "spec.status.active")
