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

- `find_by_verified_by(self, artifact_pattern) -> list[RequirementRecord]`: Find requirements verified by specific artifact(s) using glob patterns.

Searches both verified_by and coverage_evidence fields.

Args:
  artifact_pattern: Artifact ID or glob pattern (e.g., "VT-CLI-001" or "VT-*").
                    Returns empty list if None or empty string.

Returns:
  List of RequirementRecord objects verified by matching artifacts.
  Returns empty list if artifact_pattern is None, empty, or no matches found.
- `move_requirement(self, uid, new_spec_id) -> str`: Move requirement to different spec, returning new UID. - ------------------------------------------------------------------
- `save(self) -> None`: Save requirements registry to YAML file.
- `search(self) -> list[RequirementRecord]`: Search requirements by query text and various filters. - ------------------------------------------------------------------
- `set_status(self, uid, status) -> None`: Set the status of a requirement.
- `sync_from_specs(self, spec_dirs) -> SyncStats`: Sync requirements from specs and change artifacts, updating registry. - ------------------------------------------------------------------

### SyncStats

Statistics tracking for synchronization operations.
