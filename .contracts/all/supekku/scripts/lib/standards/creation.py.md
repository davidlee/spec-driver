# supekku.scripts.lib.standards.creation

Standard creation utilities.

## Constants

- `__all__`

## Functions

- `build_standard_frontmatter(standard_id, title, status, author, author_email) -> dict`: Build frontmatter dictionary for standard.

Args:
  standard_id: Standard identifier (e.g., "STD-001").
  title: Human-readable title.
  status: Status value (e.g., "draft", "required", "default", "deprecated").
  author: Optional author name.
  author_email: Optional author email.

Returns:
  Dictionary containing standard frontmatter.
- `create_standard(registry, options) -> StandardCreationResult`: Create a new standard with the next available ID.

Args:
  registry: Standard registry for finding next ID and storing standard.
  options: Standard creation options (title, status, author, etc.).
  sync_registry: Whether to sync the registry after creation.

Returns:
  StandardCreationResult with ID, path, and filename.

Raises:
  StandardAlreadyExistsError: If standard file already exists at computed path.
- `create_title_slug(title) -> str`: Create URL-friendly slug from title.

Args:
  title: Human-readable title.

Returns:
  Lowercase slug with hyphens.
- `generate_next_standard_id(registry) -> str`: Generate the next available standard ID.

Args:
  registry: Standard registry to scan for existing IDs.

Returns:
  Next available standard ID (e.g., "STD-001").

## Classes

### StandardAlreadyExistsError

Raised when attempting to create a standard file that already exists.

**Inherits from:** Exception

### StandardCreationOptions

Options for creating a new standard.

### StandardCreationResult

Result of creating a new standard.
