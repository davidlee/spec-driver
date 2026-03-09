# supekku.scripts.lib.policies.creation

Policy creation utilities.

## Functions

- `build_policy_frontmatter(policy_id, title, status, author, author_email) -> dict`: Build frontmatter dictionary for policy.

Args:
  policy_id: Policy identifier (e.g., "POL-001").
  title: Human-readable title.
  status: Status value (e.g., "draft", "required", "deprecated").
  author: Optional author name.
  author_email: Optional author email.

Returns:
  Dictionary containing policy frontmatter.
- `create_policy(registry, options) -> PolicyCreationResult`: Create a new policy with the next available ID.

Args:
  registry: Policy registry for finding next ID and storing policy.
  options: Policy creation options (title, status, author, etc.).
  sync_registry: Whether to sync the registry after creation.

Returns:
  PolicyCreationResult with ID, path, and filename.

Raises:
  PolicyAlreadyExistsError: If policy file already exists at computed path.
- `create_title_slug(title) -> str`: Create URL-friendly slug from title.

Args:
  title: Human-readable title.

Returns:
  Lowercase slug with hyphens.
- `generate_next_policy_id(registry) -> str`: Generate the next available policy ID.

Args:
  registry: Policy registry to scan for existing IDs.

Returns:
  Next available policy ID (e.g., "POL-001").

## Classes

### PolicyAlreadyExistsError

Raised when attempting to create a policy file that already exists.

**Inherits from:** Exception

### PolicyCreationOptions

Options for creating a new policy.

### PolicyCreationResult

Result of creating a new policy.
