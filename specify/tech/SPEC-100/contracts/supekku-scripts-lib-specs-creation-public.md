# supekku.scripts.lib.specs.creation

Utilities for creating and managing specification files.

## Functions

- `build_frontmatter() -> MutableMapping[Tuple[str, object]]`: Build YAML frontmatter dictionary for spec file.

Args:
  spec_id: Unique spec identifier.
  slug: URL-friendly slug.
  name: Human-readable spec name.
  kind: Spec kind/type.
  created: Creation date (ISO format).

Returns:
  Frontmatter dictionary.
- `build_template_config(repo_root, spec_type) -> SpecTemplateConfig`: Build template configuration for the specified spec type.

Args:
  repo_root: Repository root path.
  spec_type: Type of spec ("tech" or "product").

Returns:
  SpecTemplateConfig with paths and settings.

Raises:
  SpecCreationError: If spec type is not supported.
- `create_spec(spec_name, options) -> CreateSpecResult`: Create a new spec, generating necessary files from templates.
- `determine_next_identifier(base_dir, prefix) -> str`: Determine next sequential spec identifier.

Args:
  base_dir: Directory containing existing specs.
  prefix: Identifier prefix (e.g., "SPEC", "PROD").

Returns:
  Next available identifier (e.g., "SPEC-042").
- `extract_template_body(path) -> str`: Extract markdown body from template file.

Args:
  path: Path to template file.

Returns:
  Extracted markdown content.

Raises:
  TemplateNotFoundError: If template file doesn't exist.
- `find_repository_root(start) -> Path`: Find repository root by searching for .git or spec-driver templates.

Args:
  start: Path to start searching from.

Returns:
  Repository root path.

Raises:
  RepositoryRootNotFoundError: If repository root cannot be found.
- `slugify(name) -> str`: Convert name to URL-friendly slug.

Args:
  name: Human-readable name.

Returns:
  Lowercase slug with hyphens.

## Classes

### CreateSpecOptions

Configuration options for creating specifications.

### CreateSpecResult

Result information from creating a specification.

#### Methods

- `to_json(self) -> str`: Serialize result to JSON format.

Returns:
  JSON string representation of the result.

### RepositoryRootNotFoundError

Raised when the repository root cannot be located.

**Inherits from:** SpecCreationError

### SpecCreationError

Raised when creation fails due to invalid configuration.

**Inherits from:** RuntimeError

### SpecTemplateConfig

Configuration for specification template processing.

### TemplateNotFoundError

Raised when a specification template cannot be found.

**Inherits from:** SpecCreationError
