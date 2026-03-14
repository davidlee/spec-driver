# supekku.scripts.lib.requirements.registry

Requirements management and processing utilities.

## Constants

- `_REQUIREMENT_HEADING` - Matches dotted format only (NNN.MMM) — no overlap with spec bullet format.
- `_REQUIREMENT_LINE` - Optional tags in square brackets after category: **FR-001**(cat)[tag1, tag2]: Title
- `__all__`
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
- `__init__(self, registry_path) -> None`
- `_apply_audit_relations(self, audit_dirs) -> None`
- `_apply_coverage_blocks(self, spec_files, delta_files, plan_files, audit_files) -> None`: Apply verification coverage blocks to update requirement lifecycle.

Extracts coverage blocks from all artifact types, rebuilds coverage
fields from current sources (not accumulated), and derives status.

Coverage fields are cleared first so that removed coverage blocks
correctly result in empty evidence — the registry is a derived
projection (ADR-008 §5), not a persistent accumulator.

Terminal-status requirements (deprecated, superseded, retired) are
not overwritten by coverage-derived status.
- `_apply_delta_relations(self, delta_dirs, _repo_root) -> None`
- `_apply_revision_blocks(self, revision_dirs) -> None`
- `_apply_revision_relations(self, revision_dirs) -> None`
- `_apply_revision_requirement(self, payload) -> tuple[Tuple[int, int]]`
- `_apply_spec_relationships(self, spec_id, body) -> None`
- `_check_coverage_drift(self, req_id, entries) -> None`: Check for coverage drift and emit warnings.

Detects when the same requirement has conflicting coverage statuses
across different artifacts (spec vs IP vs audit).
- `_compute_status_from_coverage(self, entries) -> <BinOp>`: Compute requirement status from aggregated coverage entries.

Only entries with statuses in VALID_COVERAGE_STATUSES are considered.
Unknown statuses are silently ignored (warnings are emitted at the
ingestion boundary in _apply_coverage_blocks).

Applies precedence rules:
- ANY 'failed' or 'blocked' → in-progress (needs attention)
- ALL 'verified' → active
- ANY 'in-progress' → in-progress
- ALL 'planned' → pending
- MIXED → in-progress

Returns None if no entries or unable to determine.
- `_create_placeholder_record(self, uid, spec_id, payload) -> RequirementRecord`
- @staticmethod `_extract_coverage_entries(files, coverage_map) -> None`: Extract coverage entries from a set of artifact files into coverage_map.

Entries with unknown statuses are still recorded (for transparency in
coverage_entries) but a warning is emitted.  The downstream
_compute_status_from_coverage() independently filters unknown statuses
so they never influence derived requirement state.
- `_find_record_from_origin(self, payload) -> <BinOp>`
- `_iter_change_files(self, dirs, prefix) -> Iterator[Path]`
- `_iter_spec_files(self, spec_dirs) -> Iterator[Path]`
- `_load(self) -> None` - ------------------------------------------------------------------
- @staticmethod `_load_breakout_metadata(spec_path) -> dict[Tuple[str, dict[Tuple[str, Any]]]]`: Load metadata from breakout requirement files under a spec.

Scans ``spec_path.parent / "requirements"`` for ``*.md`` files and
extracts ``tags``, ``ext_id``, and ``ext_url`` from their frontmatter.

Returns:
  Mapping from qualified requirement ID (e.g. ``SPEC-100.FR-010``)
  to a dict of metadata fields.
- `_records_from_content(self, spec_id, _frontmatter, body, spec_path, repo_root) -> Iterator[RequirementRecord]`: Extract requirement records from spec body content.

Logs warnings if requirement-like lines are found but not extracted.
- `_records_from_frontmatter(self, spec_id, frontmatter, body, spec_path, repo_root) -> Iterator[RequirementRecord]`
- `_requirements_from_spec(self, spec_path, spec_id, repo_root) -> Iterator[RequirementRecord]`
- `_resolve_spec_path(self, spec_id, spec_registry) -> str`
- `_sync_backlog_requirements(self, backlog_registry, repo_root, seen, stats) -> None`: Extract and upsert requirements from backlog items.
- `_upsert_record(self, record, seen, stats, source_kind, source_type) -> None`: Merge-or-create a requirement record, tracking it in *seen*.

If *source_kind* or *source_type* are provided they are stamped on the
record **after** merge so the freshly-extracted provenance wins. - Deprecated alias — use sync() instead.
- `_validate_extraction(self, spec_registry, seen) -> None`: Validate extraction results and warn about potential issues.

Checks for specs with zero extracted requirements, which may indicate
format issues or extraction failures.

### SyncStats

Statistics tracking for synchronization operations.
