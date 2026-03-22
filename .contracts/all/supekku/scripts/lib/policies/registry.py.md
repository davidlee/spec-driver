# supekku.scripts.lib.policies.registry

Policy registry management.

Provides PolicyRecord data model and PolicyRegistry for YAML-backed policy management.

## Constants

- `__all__`

## Classes

### PolicyRecord

Record representing a Policy with metadata.

#### Methods

- `to_dict(self, root) -> dict[Tuple[str, Any]]`: Convert to dictionary for YAML serialization.

Args:
    root: Repository root path for relativizing file paths

Returns:
    Dictionary representation suitable for YAML serialization

### PolicyRegistry

Registry for managing Policies.

#### Methods

- `collect(self) -> dict[Tuple[str, PolicyRecord]]`: Collect all policy files and parse them into PolicyRecords.
- `filter(self) -> list[PolicyRecord]`: Filter policies by various criteria.
- `find(self, policy_id) -> <BinOp>`: Find a specific policy by ID.
- `iter(self, status) -> Iterator[PolicyRecord]`: Iterate over policies, optionally filtered by status.
- @classmethod `load(cls, root) -> PolicyRegistry`: Load existing registry from YAML file.
- `parse_date(self, date_value) -> <BinOp>`: Parse date from various formats.
- `sync(self) -> None`: Sync registry by collecting policies and writing to YAML.
- `write(self, path) -> None`: Write registry to YAML file.
- `__init__(self) -> None`
- `_build_backlinks(self, policies) -> None`: Build backlinks from decisions that reference policies.

Per ADR-002, backlinks are computed at runtime from forward references,
not stored in frontmatter.

Args:
    policies: Dictionary of PolicyRecords to populate with backlinks
- `_parse_policy_file(self, policy_path) -> <BinOp>`: Parse an individual policy file into a PolicyRecord.
