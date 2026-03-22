# supekku.scripts.lib.decisions.registry

Decision (ADR) registry management and processing utilities.

## Classes

### DecisionRecord

Record representing an Architecture Decision Record with metadata.

#### Methods

- `to_dict(self, root) -> dict[Tuple[str, Any]]`: Convert to dictionary for YAML serialization.

Args:
    root: Repository root path for relativizing file paths

Returns:
    Dictionary representation suitable for YAML serialization

### DecisionRegistry

Registry for managing Architecture Decision Records.

#### Methods

- `collect(self) -> dict[Tuple[str, DecisionRecord]]`: Collect all ADR files and parse them into DecisionRecords.
- `filter(self) -> list[DecisionRecord]`: Filter decisions by various criteria.
- `find(self, decision_id) -> <BinOp>`: Find a specific decision by ID.
- `iter(self, status) -> Iterator[DecisionRecord]`: Iterate over decisions, optionally filtered by status.
- @classmethod `load(cls, root) -> DecisionRegistry`: Load existing registry from YAML file.
- `parse_date(self, date_value) -> <BinOp>`: Parse date from various formats.
- `rebuild_status_symlinks(self) -> None`: Rebuild all status-based symlink directories.
- `sync(self) -> None`: Sync registry by collecting decisions and writing to YAML. - If in future we need to show "referenced by" on decisions, add logic here.
- `sync_with_symlinks(self) -> None`: Sync registry and rebuild symlinks in one operation.
- `write(self, path) -> None`: Write registry to YAML file.
