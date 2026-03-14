# supekku.scripts.lib.backlog.models

Backlog item models and status vocabulary.

Per-kind status sets define accepted lifecycle values (DEC-057-02, DEC-057-08).
Validation is permissive: unknown values are warned, not rejected.

## Constants

- `logger`

## Functions

- `is_valid_status(kind, status) -> bool`: Check whether a status is in the accepted set for the given kind.

Returns True for known statuses, False for unknown. Logs a warning
for unknown values (permissive validation per DEC-057-08).

## Classes

### BacklogItem

Backlog item model representing issues, problems, improvements, and risks.

#### Methods

- `to_dict(self) -> dict[Tuple[str, Any]]`: Serialize to dict with consistent relational fields.

Always includes `linked_deltas` and `related_requirements` with `[]`
defaults, ensuring JSON parity between `list` and `show` output.
