# supekku.scripts.lib.decisions.creation

Shared logic for creating architecture decision records (ADRs).

## Constants

- `ADR_TEMPLATE` - ADR template content

## Functions

- `build_adr_frontmatter(adr_id, title, status, author, author_email) -> dict`: Build frontmatter dictionary for ADR.

Args:
  adr_id: ADR identifier (e.g., "ADR-001").
  title: Human-readable title.
  status: Status value (e.g., "draft", "accepted").
  author: Optional author name.
  author_email: Optional author email.

Returns:
  Dictionary containing ADR frontmatter.
- `create_adr(registry, options) -> ADRCreationResult`: Create a new ADR with the next available ID.

Args:
  registry: Decision registry for finding next ID and storing ADR.
  options: ADR creation options (title, status, author, etc.).
  sync_registry: Whether to sync the registry after creation.

Returns:
  ADRCreationResult with ID, path, and filename.

Raises:
  ADRAlreadyExistsError: If ADR file already exists at computed path.
- `create_title_slug(title) -> str`: Create URL-friendly slug from title.

Args:
  title: Human-readable title.

Returns:
  Lowercase slug with hyphens.
- `generate_next_adr_id(registry) -> str`: Generate the next available ADR ID.

Args:
  registry: Decision registry to scan for existing IDs.

Returns:
  Next available ADR ID (e.g., "ADR-042").

## Classes

### ADRAlreadyExistsError

Raised when attempting to create an ADR file that already exists.

**Inherits from:** Exception

### ADRCreationOptions

Options for creating a new ADR.

### ADRCreationResult

Result of creating a new ADR.
