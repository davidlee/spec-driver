# supekku.scripts.lib.create_spec

Utilities for creating and managing specification files.

## Constants

- `__all__`

## Functions

- `build_frontmatter() -> MutableMapping[Tuple[str, object]]`
- `build_template_config(repo_root, spec_type) -> SpecTemplateConfig`
- `create_spec(spec_name, options) -> CreateSpecResult`
- `determine_next_identifier(base_dir, prefix) -> str`
- `extract_template_body(path) -> str`
- `find_repository_root(start) -> Path`
- `slugify(name) -> str`

## Classes

### CreateSpecOptions

Configuration options for creating specifications.

### CreateSpecResult

Result information from creating a specification.

#### Methods

- `to_json(self) -> str`

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
