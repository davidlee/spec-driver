# supekku.scripts.lib.requirements.sync

Requirement synchronization — change artifact relations and record upsert.

## Constants

- `logger`

## Functions

- `_apply_audit_relations(records, audit_dirs) -> None`: Apply audit relation entries to requirement records.
- `_apply_delta_relations(records, delta_dirs, _repo_root) -> None`: Apply delta relationship blocks to requirement records.
- `_apply_revision_blocks(records, revision_dirs) -> None`: Apply structured revision blocks to requirement records.
- `_apply_revision_relations(records, revision_dirs) -> None`: Apply revision relation entries to requirement records.
- `_apply_revision_requirement(records, payload) -> tuple[Tuple[int, int]]`: Apply a single revision requirement entry to records.
- `_apply_spec_relationships(records, spec_id, body) -> None`: Apply spec relationship blocks to requirement records.
- `_create_placeholder_record(records, uid, spec_id, payload) -> RequirementRecord`: Create a placeholder requirement record from revision data.
- `_find_record_from_origin(records, payload) -> <BinOp>`: Find a record from revision origin references.
- `_iter_change_files(dirs, prefix) -> Iterator[Path]`: Yield change artifact markdown files matching a prefix.
- `_iter_spec_files(spec_dirs) -> Iterator[Path]`: Yield spec markdown files from spec directories.
- `_resolve_spec_path(spec_id, spec_registry) -> str`: Resolve a spec ID to its relative file path.
- `_sync_backlog_requirements(records, backlog_registry, repo_root, seen, stats) -> None`: Extract and upsert requirements from backlog items.
- `_upsert_record(records, record, seen, stats, source_kind, source_type) -> None`: Merge-or-create a requirement record, tracking it in _seen_.

If _source_kind_ or _source_type_ are provided they are stamped on the
record **after** merge so the freshly-extracted provenance wins.
