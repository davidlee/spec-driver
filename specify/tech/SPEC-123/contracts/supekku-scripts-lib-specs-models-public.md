# supekku.scripts.lib.specs.models

Data models for specifications and related entities.

## Classes

### Spec

In-memory representation of a specification artefact.

#### Methods

- @property `kind(self) -> str`: Return the kind/type of this spec (e.g., 'spec', 'prod').
- @property `name(self) -> str`: Return human-readable name for this spec.
- @property `packages(self) -> list[str]`: Return list of package paths associated with this spec.
- @property `slug(self) -> str`: Return URL-friendly slug for this spec.
- @property `status(self) -> str`: Return the status of this spec (e.g., 'draft', 'active').
- `to_dict(self, root) -> dict[Tuple[str, <BinOp>]]`: Convert to dictionary for JSON serialization.

Args:
    root: Repository root path for relativizing file paths

Returns:
    Dictionary representation suitable for JSON serialization
