"""Utilities for creating and managing specification files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from .paths import SPEC_DRIVER_DIR, get_templates_dir
from .spec_utils import dump_markdown_file

if TYPE_CHECKING:
  from collections.abc import MutableMapping


@dataclass(frozen=True)
class CreateSpecOptions:
  """Configuration options for creating specifications."""

  spec_type: str = "tech"
  include_testing: bool = True
  emit_json: bool = False


@dataclass(frozen=True)
class CreateSpecResult:
  """Result information from creating a specification."""

  spec_id: str
  directory: Path
  spec_path: Path
  test_path: Path | None

  def to_json(self) -> str:
    """Serialize result to JSON format.

    Returns:
      JSON string representation of the result.
    """
    payload = {
      "id": self.spec_id,
      "dir": str(self.directory),
      "spec_file": str(self.spec_path),
    }
    if self.test_path is not None:
      payload["test_file"] = str(self.test_path)
    return json.dumps(payload)


class SpecCreationError(RuntimeError):
  """Raised when creation fails due to invalid configuration."""


class TemplateNotFoundError(SpecCreationError):
  """Raised when a specification template cannot be found."""


class RepositoryRootNotFoundError(SpecCreationError):
  """Raised when the repository root cannot be located."""


@dataclass
class SpecTemplateConfig:
  """Configuration for specification template processing."""

  base_dir: Path
  prefix: str
  kind: str
  template_path: Path
  testing_template_path: Path | None = None


def create_spec(spec_name: str, options: CreateSpecOptions) -> CreateSpecResult:
  spec_name = spec_name.strip()
  if not spec_name:
    msg = "spec name must be provided"
    raise SpecCreationError(msg)

  repo_root = find_repository_root(Path.cwd())
  today = date.today().isoformat()

  config = build_template_config(repo_root, options.spec_type)

  config.base_dir.mkdir(parents=True, exist_ok=True)

  next_id = determine_next_identifier(config.base_dir, config.prefix)
  slug = slugify(spec_name) or config.kind
  spec_dir = config.base_dir / next_id
  spec_dir.mkdir(parents=True, exist_ok=True)

  spec_path = spec_dir / f"{next_id}.md"
  spec_body = extract_template_body(config.template_path)
  frontmatter = build_frontmatter(
    spec_id=next_id,
    slug=slug,
    name=spec_name,
    kind=config.kind,
    created=today,
  )
  dump_markdown_file(spec_path, frontmatter, spec_body)

  test_path: Path | None = None
  if (
    options.spec_type == "tech"
    and options.include_testing
    and config.testing_template_path is not None
  ):
    test_body = extract_template_body(config.testing_template_path)
    test_path = spec_dir / f"{next_id}.tests.md"
    test_frontmatter = build_frontmatter(
      spec_id=f"{next_id}.TESTS",
      slug=f"{slug}-tests",
      name=f"{spec_name} Testing Guide",
      kind="guidance",
      created=today,
    )
    dump_markdown_file(test_path, test_frontmatter, test_body)

  slug_dir = config.base_dir / "by-slug"
  slug_dir.mkdir(exist_ok=True)
  slug_target = slug_dir / slug
  if slug_target.exists() or slug_target.is_symlink():
    slug_target.unlink()
  slug_target.symlink_to(Path("..") / spec_dir.name)

  package_dir = config.base_dir / "by-package"
  package_dir.mkdir(exist_ok=True)
  packages = frontmatter.get("packages") or []
  for package in packages:
    package_path = package_dir / Path(package) / "spec"
    package_path.parent.mkdir(parents=True, exist_ok=True)
    if package_path.exists() or package_path.is_symlink():
      package_path.unlink()
    package_path.symlink_to(Path("..") / ".." / spec_dir.name)

  return CreateSpecResult(
    spec_id=next_id,
    directory=spec_dir,
    spec_path=spec_path,
    test_path=test_path,
  )


def find_repository_root(start: Path) -> Path:
  """Find repository root by searching for .git or spec-driver templates.

  Args:
    start: Path to start searching from.

  Returns:
    Repository root path.

  Raises:
    RepositoryRootNotFoundError: If repository root cannot be found.
  """
  for path in [start, *start.parents]:
    # Check for .git or spec-driver templates directory
    if (path / ".git").exists():
      return path
    if (path / SPEC_DRIVER_DIR / "templates").exists():
      return path
  msg = "Could not determine repository root (missing .git or spec-driver templates)"
  raise RepositoryRootNotFoundError(
    msg,
  )


def build_template_config(repo_root: Path, spec_type: str) -> SpecTemplateConfig:
  """Build template configuration for the specified spec type.

  Args:
    repo_root: Repository root path.
    spec_type: Type of spec ("tech" or "product").

  Returns:
    SpecTemplateConfig with paths and settings.

  Raises:
    SpecCreationError: If spec type is not supported.
  """
  spec_type = spec_type.lower()
  templates_dir = get_templates_dir(repo_root)
  if spec_type == "tech":
    return SpecTemplateConfig(
      base_dir=repo_root / "specify" / "tech",
      prefix="SPEC",
      kind="spec",
      template_path=templates_dir / "tech-spec-template.md",
      testing_template_path=templates_dir / "tech-testing-template.md",
    )
  if spec_type == "product":
    return SpecTemplateConfig(
      base_dir=repo_root / "specify" / "product",
      prefix="PROD",
      kind="prod",
      template_path=templates_dir / "product-spec-template.md",
      testing_template_path=None,
    )
  msg = f"Unsupported spec type: {spec_type}"
  raise SpecCreationError(msg)


def determine_next_identifier(base_dir: Path, prefix: str) -> str:
  """Determine next sequential spec identifier.

  Args:
    base_dir: Directory containing existing specs.
    prefix: Identifier prefix (e.g., "SPEC", "PROD").

  Returns:
    Next available identifier (e.g., "SPEC-042").
  """
  highest = 0
  if base_dir.exists():
    for entry in base_dir.iterdir():
      if not entry.is_dir():
        continue
      match = re.search(r"(\d{3,})", entry.name)
      if not match:
        continue
      try:
        highest = max(highest, int(match.group(1)))
      except ValueError:
        continue
  return f"{prefix}-{highest + 1:03d}"


def slugify(name: str) -> str:
  """Convert name to URL-friendly slug.

  Args:
    name: Human-readable name.

  Returns:
    Lowercase slug with hyphens.
  """
  return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def extract_template_body(path: Path) -> str:
  """Extract markdown body from template file.

  Args:
    path: Path to template file.

  Returns:
    Extracted markdown content.

  Raises:
    TemplateNotFoundError: If template file doesn't exist.
  """
  if not path.exists():
    msg = f"Template not found: {path}"
    raise TemplateNotFoundError(msg)
  content = path.read_text(encoding="utf-8")
  match = re.search(r"```markdown\s*(.*?)```", content, re.DOTALL)
  if match:
    body = match.group(1).strip()
    return body + "\n"
  return "# TODO: Fill spec body\n"


def build_frontmatter(
  *,
  spec_id: str,
  slug: str,
  name: str,
  kind: str,
  created: str,
) -> MutableMapping[str, object]:
  """Build YAML frontmatter dictionary for spec file.

  Args:
    spec_id: Unique spec identifier.
    slug: URL-friendly slug.
    name: Human-readable spec name.
    kind: Spec kind/type.
    created: Creation date (ISO format).

  Returns:
    Frontmatter dictionary.
  """
  return {
    "id": spec_id,
    "slug": slug,
    "name": name,
    "created": created,
    "updated": created,
    "status": "draft",
    "kind": kind,
    "aliases": [],
  }


__all__ = [
  "CreateSpecOptions",
  "CreateSpecResult",
  "RepositoryRootNotFoundError",
  "SpecCreationError",
  "TemplateNotFoundError",
  "create_spec",
]
