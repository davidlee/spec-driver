# supekku.scripts.lib.core.templates

Jinja2-based template loading and rendering utilities.

## Functions

- `extract_template_body(template_path) -> str`: Extract markdown body from template file after frontmatter.

This function maintains compatibility with the old template loading approach,
but now returns the raw template content (with Jinja2 placeholders intact)
rather than doing string replacement.

Args:
  template_path: Path to template file.

Returns:
  Extracted template content (body after frontmatter, with placeholders).

Raises:
  TemplateNotFoundError: If template file doesn't exist.
- `get_package_templates_dir() -> Path`: Get the package templates directory (built-in templates).

Returns:
  Path to package templates directory (supekku/templates/).
- `get_template_environment(repo_root) -> Environment`: Create and configure a Jinja2 environment for templates.

Uses a fallback strategy:
1. First tries user templates from .spec-driver/templates/
2. Falls back to package templates from supekku/templates/

A warning is issued when user templates directory doesn't exist.

Args:
  repo_root: Repository root path. If None, will auto-discover.

Returns:
  Configured Jinja2 Environment.
- `load_template(template_name, repo_root) -> Template`: Load a Jinja2 template by name.

Args:
  template_name: Name of template file (e.g., "ADR.md", "delta.md").
  repo_root: Repository root path. If None, will auto-discover.

Returns:
  Jinja2 Template object.

Raises:
  TemplateNotFoundError: If template file doesn't exist.
- `render_template(template_name, variables, repo_root) -> str`: Load and render a Jinja2 template with variables.

Args:
  template_name: Name of template file (e.g., "ADR.md", "delta.md").
  variables: Dictionary of template variables.
  repo_root: Repository root path. If None, will auto-discover.

Returns:
  Rendered template content.

Raises:
  TemplateNotFoundError: If template file doesn't exist.

## Classes

### TemplateNotFoundError

Raised when a template file cannot be found.

**Inherits from:** Exception
