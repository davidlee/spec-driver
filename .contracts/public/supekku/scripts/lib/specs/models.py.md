# supekku.scripts.lib.specs.models

Data models for specifications and related entities.

## Classes

### Spec

In-memory representation of a specification artefact.

#### Methods

- @property `c4_level(self) -> str`: Return the C4 architecture level (e.g. 'code', 'component', or '').
- @property `category(self) -> str`: Return the taxonomy category (e.g. 'unit', 'assembly', or '').
- @property `ext_id(self) -> str`: Return external system identifier (e.g. 'JIRA-1234').
- @property `ext_url(self) -> str`: Return external system URL.
- @property `informed_by(self) -> list[str]`: Return list of ADR IDs that inform this spec.
- @property `kind(self) -> str`: Return the kind/type of this spec (e.g., 'spec', 'prod').
- @property `name(self) -> str`: Return human-readable name for this spec.
- @property `packages(self) -> list[str]`: Return list of package paths associated with this spec.
- @property `relations(self) -> list[dict[Tuple[str, Any]]]`: Return list of relation dicts from frontmatter.
- @property `slug(self) -> str`: Return URL-friendly slug for this spec.
- @property `status(self) -> str`: Return the status of this spec (e.g., 'draft', 'active').
- @property `tags(self) -> list[str]`: Return list of tags for this spec.
- `to_dict(self, root) -> dict[Tuple[str, <BinOp>]]`: Convert to dictionary for JSON serialization.

Args:
root: Repository root path for relativizing file paths

Returns:
Dictionary representation suitable for JSON serialization
