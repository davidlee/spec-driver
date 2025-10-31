# supekku.scripts.lib.requirements

Requirements management and processing utilities.

## Constants

- `_REQUIREMENT_LINE`
- `__all__`

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
- `__init__(self, registry_path) -> None`
- `_apply_audit_relations(self, audit_dirs) -> None`
- `_apply_delta_relations(self, delta_dirs, repo_root) -> None`
- `_apply_revision_blocks(self, revision_dirs) -> None`
- `_apply_revision_relations(self, revision_dirs) -> None`
- `_apply_revision_requirement(self, payload) -> tuple[Tuple[int, int]]`
- `_apply_spec_relationships(self, spec_id, body) -> None`
- `_create_placeholder_record(self, uid, spec_id, payload) -> RequirementRecord`
- `_find_record_from_origin(self, payload) -> <BinOp>`
- `_iter_change_files(self, dirs, prefix) -> Iterator[Path]`
- `_iter_spec_files(self, spec_dirs) -> Iterator[Path]`
- `_load(self) -> None` - ------------------------------------------------------------------
- `_records_from_content(self, spec_id, frontmatter, body, spec_path, repo_root) -> Iterator[RequirementRecord]`
- `_records_from_frontmatter(self, spec_id, frontmatter, body, spec_path, repo_root) -> Iterator[RequirementRecord]`
- `_requirements_from_spec(self, spec_path, spec_id, repo_root) -> Iterator[RequirementRecord]`
- `_resolve_spec_path(self, spec_id, spec_registry) -> str`

### SyncStats

Statistics tracking for synchronization operations.
