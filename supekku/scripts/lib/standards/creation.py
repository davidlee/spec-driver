"""Standard creation utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml
from jinja2 import Template

from supekku.scripts.lib.core.paths import get_templates_dir
from supekku.scripts.lib.core.templates import extract_template_body
from supekku.scripts.lib.standards.registry import StandardRegistry


@dataclass
class StandardCreationOptions:
  """Options for creating a new standard."""

  title: str
  status: str = "draft"
  author: str | None = None
  author_email: str | None = None


@dataclass
class StandardCreationResult:
  """Result of creating a new standard."""

  standard_id: str
  path: Path
  filename: str


class StandardAlreadyExistsError(Exception):
  """Raised when attempting to create a standard file that already exists."""


def generate_next_standard_id(registry: StandardRegistry) -> str:
  """Generate the next available standard ID.

  Args:
    registry: Standard registry to scan for existing IDs.

  Returns:
    Next available standard ID (e.g., "STD-001").
  """
  standards = registry.collect()
  max_id = 0
  for standard_id in standards:
    match = re.match(r"STD-(\d+)", standard_id)
    if match:
      max_id = max(max_id, int(match.group(1)))

  next_id = max_id + 1
  return f"STD-{next_id:03d}"


def create_title_slug(title: str) -> str:
  """Create URL-friendly slug from title.

  Args:
    title: Human-readable title.

  Returns:
    Lowercase slug with hyphens.
  """
  return re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")


def build_standard_frontmatter(
  standard_id: str,
  title: str,
  status: str,
  author: str | None = None,
  author_email: str | None = None,
) -> dict:
  """Build frontmatter dictionary for standard.

  Args:
    standard_id: Standard identifier (e.g., "STD-001").
    title: Human-readable title.
    status: Status value (e.g., "draft", "required", "default", "deprecated").
    author: Optional author name.
    author_email: Optional author email.

  Returns:
    Dictionary containing standard frontmatter.
  """
  today = date.today().isoformat()
  frontmatter = {
    "id": standard_id,
    "title": f"{standard_id}: {title}",
    "status": status,
    "created": today,
    "updated": today,
    "reviewed": today,
  }

  # Add author to owners if provided
  if author:
    frontmatter["owners"] = [author]
  else:
    frontmatter["owners"] = []

  # Add other empty fields for the schema
  frontmatter.update(
    {
      "supersedes": [],
      "superseded_by": [],
      "policies": [],
      "specs": [],
      "requirements": [],
      "deltas": [],
      "related_policies": [],
      "related_standards": [],
      "tags": [],
      "summary": "",
    },
  )

  return frontmatter


def create_standard(
  registry: StandardRegistry,
  options: StandardCreationOptions,
  *,
  sync_registry: bool = True,
) -> StandardCreationResult:
  """Create a new standard with the next available ID.

  Args:
    registry: Standard registry for finding next ID and storing standard.
    options: Standard creation options (title, status, author, etc.).
    sync_registry: Whether to sync the registry after creation.

  Returns:
    StandardCreationResult with ID, path, and filename.

  Raises:
    StandardAlreadyExistsError: If standard file already exists at computed path.
  """
  # Generate next ID
  standard_id = generate_next_standard_id(registry)

  # Create filename
  title_slug = create_title_slug(options.title)
  filename = f"{standard_id}-{title_slug}.md"
  standard_path = registry.directory / filename

  # Check if file already exists
  if standard_path.exists():
    msg = f"Standard file already exists: {standard_path}"
    raise StandardAlreadyExistsError(msg)

  # Build frontmatter
  frontmatter = build_standard_frontmatter(
    standard_id,
    options.title,
    options.status,
    options.author,
    options.author_email,
  )

  # Load template body and render with Jinja2
  template_path = get_templates_dir(registry.root) / "standard-template.md"
  template_body = extract_template_body(template_path)
  template = Template(template_body)
  content = template.render(standard_id=standard_id, title=options.title)

  # Write file
  frontmatter_yaml = yaml.safe_dump(frontmatter, sort_keys=False)
  full_content = f"---\n{frontmatter_yaml}---\n\n{content}"

  standard_path.parent.mkdir(parents=True, exist_ok=True)
  standard_path.write_text(full_content, encoding="utf-8")

  # Sync registry if requested
  if sync_registry:
    registry.sync()

  return StandardCreationResult(
    standard_id=standard_id,
    path=standard_path,
    filename=filename,
  )


__all__ = [
  "StandardCreationOptions",
  "StandardCreationResult",
  "StandardAlreadyExistsError",
  "generate_next_standard_id",
  "create_title_slug",
  "build_standard_frontmatter",
  "create_standard",
]
