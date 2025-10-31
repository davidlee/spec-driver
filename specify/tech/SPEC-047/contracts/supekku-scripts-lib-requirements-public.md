# supekku.scripts.lib.requirements

Requirements management and processing utilities.

## Classes

### RequirementRecord

Record representing a requirement with lifecycle tracking.

#### Methods

- @classmethod `from_dict(cls, uid, data) -> RequirementRecord`
- `merge(self, other) -> RequirementRecord`: Merge data from another record, preserving lifecycle fields.
- `to_dict(self) -> dict[Tuple[str, object]]`

### RequirementsRegistry

Registry for managing requirement records and lifecycle tracking.

#### Methods

- `move_requirement(self, uid, new_spec_id) -> str` - ------------------------------------------------------------------
- `save(self) -> None`
- `search(self) -> list[RequirementRecord]` - ------------------------------------------------------------------
- `set_status(self, uid, status) -> None`
- `sync_from_specs(self, spec_dirs) -> SyncStats` - ------------------------------------------------------------------

### SyncStats

Statistics tracking for synchronization operations.
