"""Tests for Jinja2 template loading and rendering utilities."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from supekku.scripts.lib.core.templates import (
  TemplateNotFoundError,
  extract_template_body,
  get_template_environment,
  load_template,
  render_template,
)


@pytest.fixture
def mock_templates_dir(tmp_path: Path) -> Path:
  """Create a temporary templates directory with test templates."""
  templates_dir = tmp_path / "templates"
  templates_dir.mkdir()

  # Create a simple template
  simple_template = templates_dir / "simple.md"
  simple_template.write_text("Hello {{ name }}!", encoding="utf-8")

  # Create a template with frontmatter
  frontmatter_template = templates_dir / "with_frontmatter.md"
  frontmatter_template.write_text(
    "---\ntitle: Test\n---\n\nContent: {{ content }}",
    encoding="utf-8",
  )

  # Create a complex template
  complex_template = templates_dir / "complex.md"
  complex_template.write_text(
    "# {{ title }}\n\n{% if description %}{{ description }}{% endif %}\n",
    encoding="utf-8",
  )

  return templates_dir


@patch("supekku.scripts.lib.core.templates.get_templates_dir")
def test_get_template_environment(
  mock_get_templates_dir: MagicMock,
  mock_templates_dir: Path,
) -> None:
  """Test creating a Jinja2 environment."""
  mock_get_templates_dir.return_value = mock_templates_dir

  env = get_template_environment()

  assert env is not None
  assert not env.autoescape
  assert env.keep_trailing_newline


@patch("supekku.scripts.lib.core.templates.get_templates_dir")
def test_load_template_simple(
  mock_get_templates_dir: MagicMock,
  mock_templates_dir: Path,
) -> None:
  """Test loading a simple template."""
  mock_get_templates_dir.return_value = mock_templates_dir

  template = load_template("simple.md")

  assert template is not None
  assert template.name == "simple.md"


@patch("supekku.scripts.lib.core.templates.get_templates_dir")
def test_load_template_not_found(
  mock_get_templates_dir: MagicMock,
  mock_templates_dir: Path,
) -> None:
  """Test loading a non-existent template raises error."""
  mock_get_templates_dir.return_value = mock_templates_dir

  with pytest.raises(
    TemplateNotFoundError,
    match="Template not found.*nonexistent.md",
  ):
    load_template("nonexistent.md")


@patch("supekku.scripts.lib.core.templates.get_templates_dir")
def test_render_template_simple(
  mock_get_templates_dir: MagicMock,
  mock_templates_dir: Path,
) -> None:
  """Test rendering a simple template."""
  mock_get_templates_dir.return_value = mock_templates_dir

  result = render_template("simple.md", {"name": "World"})

  assert result == "Hello World!"


@patch("supekku.scripts.lib.core.templates.get_templates_dir")
def test_render_template_complex(
  mock_get_templates_dir: MagicMock,
  mock_templates_dir: Path,
) -> None:
  """Test rendering a complex template with conditionals."""
  mock_get_templates_dir.return_value = mock_templates_dir

  # With description
  result = render_template(
    "complex.md",
    {"title": "Test Title", "description": "Test Description"},
  )
  assert result == "# Test Title\n\nTest Description\n"

  # Without description
  result = render_template(
    "complex.md",
    {"title": "Test Title"},
  )
  assert result == "# Test Title\n\n\n"


def test_extract_template_body_with_frontmatter(tmp_path: Path) -> None:
  """Test extracting body from template with frontmatter."""
  template_path = tmp_path / "template.md"
  template_path.write_text(
    "---\ntitle: Test\n---\n\nBody content {{ var }}",
    encoding="utf-8",
  )

  body = extract_template_body(template_path)

  assert body == "Body content {{ var }}"


def test_extract_template_body_without_frontmatter(tmp_path: Path) -> None:
  """Test extracting body from template without frontmatter."""
  template_path = tmp_path / "template.md"
  template_path.write_text("Body content {{ var }}", encoding="utf-8")

  body = extract_template_body(template_path)

  assert body == "Body content {{ var }}"


def test_extract_template_body_not_found(tmp_path: Path) -> None:
  """Test extracting body from non-existent template raises error."""
  template_path = tmp_path / "nonexistent.md"

  with pytest.raises(
    TemplateNotFoundError,
    match="Template not found.*nonexistent.md",
  ):
    extract_template_body(template_path)


def test_extract_template_body_preserves_placeholders(tmp_path: Path) -> None:
  """Test that extract_template_body preserves Jinja2 placeholders."""
  template_path = tmp_path / "template.md"
  content = "---\nid: test\n---\n\n# {{ title }}\n\n{{ description }}"
  template_path.write_text(content, encoding="utf-8")

  body = extract_template_body(template_path)

  assert "{{ title }}" in body
  assert "{{ description }}" in body
