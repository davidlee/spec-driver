"""Private shared creation engine for governance artifacts (DEC-116-6 / DR §4).

DO NOT import from this module externally. Public API is:
  - supekku.scripts.lib.decisions.creation  → create_adr, ADRCreationOptions, etc.
  - supekku.scripts.lib.policies.creation   → create_policy, PolicyCreationOptions,
    etc.
  - supekku.scripts.lib.standards.creation  → create_standard,
    StandardCreationOptions, etc.

Those modules are thin wrappers around _create_governance_artifact.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Template

from supekku.scripts.lib.core import slugify
from supekku.scripts.lib.core.events import record_artifact
from supekku.scripts.lib.core.ids import next_sequential_id
from supekku.scripts.lib.core.paths import get_templates_dir
from supekku.scripts.lib.core.templates import extract_template_body


@dataclass(frozen=True)
class _GovernanceArtifactSpec:
  """Specification for a governance artifact kind (ADR / Policy / Standard).

  Drives the shared creation engine. ``label`` (not ``prefix``) is used for
  error messages so wording stays unchanged (e.g. 'Policy file already exists').
  """

  prefix: str
  label: str
  template_name: str
  render_var: str
  build_frontmatter: Callable[[str, Any], dict[str, Any]]
  # (artifact_id, options) -> frontmatter dict


class _AlreadyExistsError(Exception):
  """Raised when the target file already exists. Message includes label."""


def _create_governance_artifact(
  spec: _GovernanceArtifactSpec,
  registry: Any,  # FrontmatterFileRegistry subclass — untyped to avoid import cycle
  options: Any,  # *CreationOptions subclass
  *,
  sync_registry: bool = True,
) -> tuple[str, Path]:
  """Create a governance artifact (ADR / Policy / Standard).

  Shared implementation — the 3 public ``create_X`` functions are thin wrappers.

  Args:
    spec: Kind specification (prefix, label, template, frontmatter builder).
    registry: Governance registry instance.
    options: Creation options dataclass (must have ``.title``, ``.status``,
             ``.author``, ``.author_email``).
    sync_registry: Whether to call ``registry.sync()`` after creation.

  Returns:
    Tuple of ``(artifact_id, file_path)``.

  Raises:
    _AlreadyExists: If the computed file path already exists.
  """
  # Generate next ID
  artifact_id = next_sequential_id(registry.collect(), spec.prefix)
  record_artifact(artifact_id)

  # Build filename and path
  title_slug = slugify(options.title)
  filename = f"{artifact_id}-{title_slug}.md"
  file_path = registry.directory / filename

  # Check for existing file
  if file_path.exists():
    msg = f"{spec.label} file already exists: {file_path}"
    raise _AlreadyExistsError(msg)

  # Build frontmatter via per-kind builder
  frontmatter = spec.build_frontmatter(artifact_id, options)

  # Load template body and render with Jinja2
  template_path = get_templates_dir(registry.root) / spec.template_name
  template_body = extract_template_body(template_path)
  template = Template(template_body)
  content = template.render(**{spec.render_var: artifact_id, "title": options.title})

  # Write file
  frontmatter_yaml = yaml.safe_dump(frontmatter, sort_keys=False)
  full_content = f"---\n{frontmatter_yaml}---\n\n{content}"

  file_path.parent.mkdir(parents=True, exist_ok=True)
  file_path.write_text(full_content, encoding="utf-8")

  # Sync registry if requested
  if sync_registry:
    registry.sync()

  return artifact_id, file_path


__all__ = [
  "_GovernanceArtifactSpec",
  "_AlreadyExistsError",
  "_create_governance_artifact",
]
