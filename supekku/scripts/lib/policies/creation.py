"""Policy creation utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml
from jinja2 import Template

from supekku.scripts.lib.core.paths import get_templates_dir
from supekku.scripts.lib.core.templates import extract_template_body
from supekku.scripts.lib.policies.registry import PolicyRegistry


@dataclass
class PolicyCreationOptions:
  """Options for creating a new policy."""

  title: str
  status: str = "draft"
  author: str | None = None
  author_email: str | None = None


@dataclass
class PolicyCreationResult:
  """Result of creating a new policy."""

  policy_id: str
  path: Path
  filename: str


class PolicyAlreadyExistsError(Exception):
  """Raised when attempting to create a policy file that already exists."""


def generate_next_policy_id(registry: PolicyRegistry) -> str:
  """Generate the next available policy ID.

  Args:
    registry: Policy registry to scan for existing IDs.

  Returns:
    Next available policy ID (e.g., "POL-001").
  """
  policies = registry.collect()
  max_id = 0
  for policy_id in policies:
    match = re.match(r"POL-(\d+)", policy_id)
    if match:
      max_id = max(max_id, int(match.group(1)))

  next_id = max_id + 1
  return f"POL-{next_id:03d}"


def create_title_slug(title: str) -> str:
  """Create URL-friendly slug from title.

  Args:
    title: Human-readable title.

  Returns:
    Lowercase slug with hyphens.
  """
  return re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")


def build_policy_frontmatter(
  policy_id: str,
  title: str,
  status: str,
  author: str | None = None,
  author_email: str | None = None,
) -> dict:
  """Build frontmatter dictionary for policy.

  Args:
    policy_id: Policy identifier (e.g., "POL-001").
    title: Human-readable title.
    status: Status value (e.g., "draft", "required", "deprecated").
    author: Optional author name.
    author_email: Optional author email.

  Returns:
    Dictionary containing policy frontmatter.
  """
  today = date.today().isoformat()
  frontmatter = {
    "id": policy_id,
    "title": f"{policy_id}: {title}",
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
      "standards": [],
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


def create_policy(
  registry: PolicyRegistry,
  options: PolicyCreationOptions,
  *,
  sync_registry: bool = True,
) -> PolicyCreationResult:
  """Create a new policy with the next available ID.

  Args:
    registry: Policy registry for finding next ID and storing policy.
    options: Policy creation options (title, status, author, etc.).
    sync_registry: Whether to sync the registry after creation.

  Returns:
    PolicyCreationResult with ID, path, and filename.

  Raises:
    PolicyAlreadyExistsError: If policy file already exists at computed path.
  """
  # Generate next ID
  policy_id = generate_next_policy_id(registry)

  # Create filename
  title_slug = create_title_slug(options.title)
  filename = f"{policy_id}-{title_slug}.md"
  policy_path = registry.directory / filename

  # Check if file already exists
  if policy_path.exists():
    msg = f"Policy file already exists: {policy_path}"
    raise PolicyAlreadyExistsError(msg)

  # Build frontmatter
  frontmatter = build_policy_frontmatter(
    policy_id,
    options.title,
    options.status,
    options.author,
    options.author_email,
  )

  # Load template body and render with Jinja2
  template_path = get_templates_dir(registry.root) / "policy-template.md"
  template_body = extract_template_body(template_path)
  template = Template(template_body)
  content = template.render(policy_id=policy_id, title=options.title)

  # Write file
  frontmatter_yaml = yaml.safe_dump(frontmatter, sort_keys=False)
  full_content = f"---\n{frontmatter_yaml}---\n\n{content}"

  policy_path.parent.mkdir(parents=True, exist_ok=True)
  policy_path.write_text(full_content, encoding="utf-8")

  # Sync registry if requested
  if sync_registry:
    registry.sync()

  return PolicyCreationResult(
    policy_id=policy_id,
    path=policy_path,
    filename=filename,
  )


__all__ = [
  "PolicyCreationOptions",
  "PolicyCreationResult",
  "PolicyAlreadyExistsError",
  "generate_next_policy_id",
  "create_title_slug",
  "build_policy_frontmatter",
  "create_policy",
]
