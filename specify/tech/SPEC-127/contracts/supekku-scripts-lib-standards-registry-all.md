# supekku.scripts.lib.standards.registry

Standard registry management.

Provides StandardRecord data model and StandardRegistry for YAML-backed
standard management. Standards support draft, required, default, and
deprecated statuses.

## Constants

- `__all__`

## Classes

### StandardRecord

Record representing a Standard with metadata.

Standards differ from policies in status options:
- draft: Work in progress
- required: Must comply (like a policy)
- default: Recommended unless justified otherwise
- deprecated: No longer active

#### Methods

- `to_dict(self, root) -> dict[Tuple[str, Any]]`: Convert to dictionary for YAML serialization.

Args:
    root: Repository root path for relativizing file paths

Returns:
    Dictionary representation suitable for YAML serialization

### StandardRegistry

Registry for managing Standards.

#### Methods

- `collect(self) -> dict[Tuple[str, StandardRecord]]`: Collect all standard files and parse them into StandardRecords.
- `filter(self) -> list[StandardRecord]`: Filter standards by various criteria.
- `find(self, standard_id) -> <BinOp>`: Find a specific standard by ID.
- `iter(self, status) -> Iterator[StandardRecord]`: Iterate over standards, optionally filtered by status.
- @classmethod `load(cls, root) -> StandardRegistry`: Load existing registry from YAML file.
- `parse_date(self, date_value) -> <BinOp>`: Parse date from various formats.
- `sync(self) -> None`: Sync registry by collecting standards and writing to YAML.
- `write(self, path) -> None`: Write registry to YAML file.
- `__init__(self) -> None`
- `_parse_standard_file(self, standard_path) -> <BinOp>`: Parse an individual standard file into a StandardRecord.
