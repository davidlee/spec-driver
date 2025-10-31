# supekku.scripts.lib.spec_utils

Utilities for working with specification files and frontmatter.

## Functions

- `append_unique(values, item) -> bool`: Append item to list if not already present, return True if added.
- `dump_markdown_file(path, frontmatter, body) -> None`: Write frontmatter and content to a markdown file.
- `ensure_list_entry(frontmatter, key) -> list[Any]`: Ensure a frontmatter key contains a list value.
- `load_markdown_file(path) -> tuple[Tuple[dict[Tuple[str, Any]], str]]`: Load markdown file and extract frontmatter and content.
- `load_validated_markdown_file(path) -> tuple[Tuple[FrontmatterValidationResult, str]]`: Load a markdown file and validate its frontmatter against the schema.

Raises FrontmatterValidationError if validation fails.
