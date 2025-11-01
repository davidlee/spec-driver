# supekku.scripts.lib.core.frontmatter_schema

Schema definitions and validation for markdown file frontmatter.

## Constants

- `__all__`

## Functions

- `_ensure_str_list(payload, field) -> list[str]`
- `_normalize_relations(payload) -> tuple[Tuple[list[dict[Tuple[str, Any]]], tuple[Tuple[Relation, Ellipsis]]]]`
- `_parse_iso_date(value) -> date`
- `_require_str(payload, field) -> str`
- `validate_frontmatter(frontmatter) -> FrontmatterValidationResult`: Validate frontmatter against schema, optionally checking for specific kind.

## Classes

### FrontmatterValidationError

Raised when frontmatter metadata fails schema validation.

**Inherits from:** ValueError

### FrontmatterValidationResult

Result of validating frontmatter against schema requirements.

#### Methods

- `dict(self) -> Mapping[Tuple[str, Any]]`: Return the validated frontmatter as an immutable mapping.

### Relation

Represents a relationship between specifications or changes.
