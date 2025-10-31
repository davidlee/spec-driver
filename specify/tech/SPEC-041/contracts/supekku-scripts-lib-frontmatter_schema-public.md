# supekku.scripts.lib.frontmatter_schema

Schema definitions and validation for markdown file frontmatter.

## Functions

- `validate_frontmatter(frontmatter) -> FrontmatterValidationResult`

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
