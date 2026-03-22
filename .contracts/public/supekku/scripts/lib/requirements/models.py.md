# supekku.scripts.lib.requirements.models

Requirement data models and statistics tracking.

## Classes

### RequirementRecord

Record representing a requirement with lifecycle tracking.

#### Methods

- @classmethod `from_dict(cls, uid, data) -> RequirementRecord`: Create requirement record from dictionary.
- `merge(self, other) -> RequirementRecord`: Merge data from another record, preserving lifecycle fields.
- `to_dict(self) -> dict[Tuple[str, object]]`: Convert requirement record to dictionary for serialization.

### SyncStats

Statistics tracking for synchronization operations.
