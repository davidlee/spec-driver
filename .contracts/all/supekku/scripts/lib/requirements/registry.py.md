# supekku.scripts.lib.requirements.registry

Requirements management and processing utilities.

## Constants

- `__all__` - Re-exports for backward compatibility

## Classes

### RequirementsRegistry

Registry for managing requirement records and lifecycle tracking.

#### Methods

- `collect(self) -> dict[Tuple[str, RequirementRecord]]`: Return all requirement records as a dictionary keyed by UID.
- `filter(self) -> list[RequirementRecord]`: Filter requirement records by multiple criteria (AND logic).
- `find(self, uid) -> <BinOp>`: Find a requirement record by its UID. - -- ADR-009 standard surface --------------------------------------------
- `find_by_verification_kind(self, kinds) -> list[RequirementRecord]`: Find requirements with coverage entries matching given kinds.
- `find_by_verification_status(self, statuses) -> list[RequirementRecord]`: Find requirements with coverage entries matching given statuses.
- `find_by_verified_by(self, artifact_pattern) -> list[RequirementRecord]`: Find requirements verified by specific artifact(s) using glob patterns.

Searches both verified_by and coverage_evidence fields.

- `iter(self) -> Iterator[RequirementRecord]`: Iterate over requirement records, optionally filtered by status.
- `move_requirement(self, uid, new_spec_id) -> str`: Move requirement to different spec, returning new UID. - ------------------------------------------------------------------
- `save(self) -> None`: Save requirements registry to YAML file.
- `search(self) -> list[RequirementRecord]`: Search requirements by query text and various filters. - ------------------------------------------------------------------
- `set_status(self, uid, status) -> None`: Set the status of a requirement.
- `sync(self, spec_dirs) -> SyncStats`: Sync requirements from specs, change artifacts, and backlog items. - ------------------------------------------------------------------
- `__init__(self, registry_path) -> None`
- `_load(self) -> None` - ------------------------------------------------------------------
