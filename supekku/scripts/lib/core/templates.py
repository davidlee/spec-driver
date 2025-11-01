"""Jinja2-based template loading and rendering utilities."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from .paths import get_templates_dir


class TemplateNotFoundError(Exception):
  """Raised when a template file cannot be found."""


def get_template_environment(repo_root: Path | None = None) -> Environment:
  """Create and configure a Jinja2 environment for templates.

  Args:
    repo_root: Repository root path. If None, will auto-discover.

  Returns:
    Configured Jinja2 Environment.
  """
  templates_dir = get_templates_dir(repo_root)
  return Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=False,  # Markdown templates don't need autoescaping
    keep_trailing_newline=True,
  )


def load_template(
  template_name: str,
  repo_root: Path | None = None,
) -> Template:
  """Load a Jinja2 template by name.

  Args:
    template_name: Name of template file (e.g., "ADR.md", "delta.md").
    repo_root: Repository root path. If None, will auto-discover.

  Returns:
    Jinja2 Template object.

  Raises:
    TemplateNotFoundError: If template file doesn't exist.
  """
  env = get_template_environment(repo_root)
  try:
    return env.get_template(template_name)
  except TemplateNotFound as e:
    templates_dir = get_templates_dir(repo_root)
    msg = f"Template not found: {templates_dir / template_name}"
    raise TemplateNotFoundError(msg) from e


def render_template(
  template_name: str,
  variables: dict,
  repo_root: Path | None = None,
) -> str:
  """Load and render a Jinja2 template with variables.

  Args:
    template_name: Name of template file (e.g., "ADR.md", "delta.md").
    variables: Dictionary of template variables.
    repo_root: Repository root path. If None, will auto-discover.

  Returns:
    Rendered template content.

  Raises:
    TemplateNotFoundError: If template file doesn't exist.
  """
  template = load_template(template_name, repo_root)
  return template.render(**variables)


def extract_template_body(template_path: Path) -> str:
  """Extract markdown body from template file after frontmatter.

  This function maintains compatibility with the old template loading approach,
  but now returns the raw template content (with Jinja2 placeholders intact)
  rather than doing string replacement.

  Args:
    template_path: Path to template file.

  Returns:
    Extracted template content (body after frontmatter, with placeholders).

  Raises:
    TemplateNotFoundError: If template file doesn't exist.
  """
  if not template_path.exists():
    msg = f"Template not found: {template_path}"
    raise TemplateNotFoundError(msg)

  content = template_path.read_text(encoding="utf-8")

  # If template has frontmatter, extract body after it
  if content.startswith("---"):
    parts = content.split("---", 2)
    return parts[2].lstrip("\n") if len(parts) >= 3 else content

  return content


__all__ = [
  "TemplateNotFoundError",
  "extract_template_body",
  "get_template_environment",
  "load_template",
  "render_template",
]
