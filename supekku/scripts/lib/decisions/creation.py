"""Shared logic for creating architecture decision records (ADRs)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from supekku.scripts.lib.decisions.registry import DecisionRegistry

# ADR template content
ADR_TEMPLATE = """# {adr_id}: {title}

## Context

**Brief** description of the problem or situation that requires a decision.

## Decision

The decision that was made and key reasoning.

## Consequences

### Positive
- Benefits of this decision

### Negative
- Trade-offs or downsides

### Neutral
- Other impacts to be aware of

## Verification
- Required test suites, monitoring, or audits ensuring compliance.

## References
- [Design artefact link]
- [External research]
"""


@dataclass
class ADRCreationOptions:
  """Options for creating a new ADR."""

  title: str
  status: str = "draft"
  author: str | None = None
  author_email: str | None = None


@dataclass
class ADRCreationResult:
  """Result of creating a new ADR."""

  adr_id: str
  path: Path
  filename: str


class ADRAlreadyExistsError(Exception):
  """Raised when attempting to create an ADR file that already exists."""


def generate_next_adr_id(registry: DecisionRegistry) -> str:
  """Generate the next available ADR ID.

  Args:
    registry: Decision registry to scan for existing IDs.

  Returns:
    Next available ADR ID (e.g., "ADR-042").
  """
  decisions = registry.collect()
  max_id = 0
  for decision_id in decisions:
    match = re.match(r"ADR-(\d+)", decision_id)
    if match:
      max_id = max(max_id, int(match.group(1)))

  next_id = max_id + 1
  return f"ADR-{next_id:03d}"


def create_title_slug(title: str) -> str:
  """Create URL-friendly slug from title.

  Args:
    title: Human-readable title.

  Returns:
    Lowercase slug with hyphens.
  """
  return re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")


def build_adr_frontmatter(
  adr_id: str,
  title: str,
  status: str,
  author: str | None = None,
  author_email: str | None = None,
) -> dict:
  """Build frontmatter dictionary for ADR.

  Args:
    adr_id: ADR identifier (e.g., "ADR-001").
    title: Human-readable title.
    status: Status value (e.g., "draft", "accepted").
    author: Optional author name.
    author_email: Optional author email.

  Returns:
    Dictionary containing ADR frontmatter.
  """
  today = date.today().isoformat()
  frontmatter = {
    "id": adr_id,
    "title": f"{adr_id}: {title}",
    "status": status,
    "created": today,
    "updated": today,
    "reviewed": today,
  }

  # Add author info if provided
  if author or author_email:
    author_info = {}
    if author:
      author_info["name"] = author
    if author_email:
      author_info["contact"] = f"mailto:{author_email}"
    frontmatter["authors"] = [author_info]

  # Add other empty fields for the new schema
  frontmatter.update(
    {
      "owners": [],
      "supersedes": [],
      "superseded_by": [],
      "policies": [],
      "specs": [],
      "requirements": [],
      "deltas": [],
      "revisions": [],
      "audits": [],
      "related_decisions": [],
      "related_policies": [],
      "tags": [],
      "summary": "",
    },
  )

  return frontmatter


def create_adr(
  registry: DecisionRegistry,
  options: ADRCreationOptions,
  *,
  sync_registry: bool = True,
) -> ADRCreationResult:
  """Create a new ADR with the next available ID.

  Args:
    registry: Decision registry for finding next ID and storing ADR.
    options: ADR creation options (title, status, author, etc.).
    sync_registry: Whether to sync the registry after creation.

  Returns:
    ADRCreationResult with ID, path, and filename.

  Raises:
    ADRAlreadyExistsError: If ADR file already exists at computed path.
  """
  # Generate next ID
  adr_id = generate_next_adr_id(registry)

  # Create filename
  title_slug = create_title_slug(options.title)
  filename = f"{adr_id}-{title_slug}.md"
  adr_path = registry.directory / filename

  # Check if file already exists
  if adr_path.exists():
    msg = f"ADR file already exists: {adr_path}"
    raise ADRAlreadyExistsError(msg)

  # Build frontmatter
  frontmatter = build_adr_frontmatter(
    adr_id,
    options.title,
    options.status,
    options.author,
    options.author_email,
  )

  # Create content
  content = ADR_TEMPLATE.format(adr_id=adr_id, title=options.title)

  # Write file
  frontmatter_yaml = yaml.safe_dump(frontmatter, sort_keys=False)
  full_content = f"---\n{frontmatter_yaml}---\n\n{content}"

  adr_path.parent.mkdir(parents=True, exist_ok=True)
  adr_path.write_text(full_content, encoding="utf-8")

  # Sync registry if requested
  if sync_registry:
    registry.sync()

  return ADRCreationResult(
    adr_id=adr_id,
    path=adr_path,
    filename=filename,
  )
