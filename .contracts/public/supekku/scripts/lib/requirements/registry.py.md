# supekku.scripts.lib.requirements.registry

Requirements management and processing utilities.

## Constants

- `logger`

## Classes

### RequirementRecord

Record representing a requirement with lifecycle tracking.

#### Methods

- @classmethod `from_dict(cls, uid, data) -> RequirementRecord`: Create requirement record from dictionary.
- `merge(self, other) -> RequirementRecord`: Merge data from another record, preserving lifecycle fields.
- `to_dict(self) -> dict[Tuple[str, object]]`: Convert requirement record to dictionary for serialization.

### RequirementsRegistry

Registry for managing requirement records and lifecycle tracking.

#### Methods

- `collect(self) -> dict[Tuple[str, RequirementRecord]]`: Return all requirement records as a dictionary keyed by UID.

Returns:
  Copy of the internal records dictionary.
- `filter(self) -> list[RequirementRecord]`: Filter requirement records by multiple criteria (AND logic).

Args:
  status: Filter by status field.
  spec: Filter by spec membership (primary or secondary).
  kind: Filter by kind (functional/non-functional).
  tag: Filter by tag membership.

Returns:
  List of matching RequirementRecords.
- `find(self, uid) -> <BinOp>`: Find a requirement record by its UID.

Returns:
  RequirementRecord or None if not found. - -- ADR-009 standard surface --------------------------------------------
- `find_by_verification_kind(self, kinds) -> list[RequirementRecord]`: Find requirements with coverage entries matching given kinds.

A requirement matches if ANY of its coverage_entries has a kind
in the provided list (OR logic).

Args:
  kinds: List of verification kinds (VT, VA, VH) to match.
         Returns empty list if empty.

Returns:
  Sorted list of matching RequirementRecord objects.
- `find_by_verification_status(self, statuses) -> list[RequirementRecord]`: Find requirements with coverage entries matching given statuses.

A requirement matches if ANY of its coverage_entries has a status
in the provided list (OR logic).

Args:
  statuses: List of verification statuses to match.
            Returns empty list if empty.

Returns:
  Sorted list of matching RequirementRecord objects.
- `find_by_verified_by(self, artifact_pattern) -> list[RequirementRecord]`: Find requirements verified by specific artifact(s) using glob patterns.

Searches both verified_by and coverage_evidence fields.

Args:
  artifact_pattern: Artifact ID or glob pattern (e.g., "VT-CLI-001" or "VT-*").
                    Returns empty list if None or empty string.

Returns:
  List of RequirementRecord objects verified by matching artifacts.
  Returns empty list if artifact_pattern is None, empty, or no matches found.
- `iter(self) -> Iterator[RequirementRecord]`: Iterate over requirement records, optionally filtered by status.

Args:
  status: If provided, yield only records with this status.

Yields:
  RequirementRecord instances.
- `move_requirement(self, uid, new_spec_id) -> str`: Move requirement to different spec, returning new UID. - ------------------------------------------------------------------
- `save(self) -> None`: Save requirements registry to YAML file.
- `search(self) -> list[RequirementRecord]`: Search requirements by query text and various filters. - ------------------------------------------------------------------
- `set_status(self, uid, status) -> None`: Set the status of a requirement.
- `sync(self, spec_dirs) -> SyncStats`: Sync requirements from specs, change artifacts, and backlog items. - ------------------------------------------------------------------

### SyncStats

Statistics tracking for synchronization operations.
