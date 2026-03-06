"""Agent guidance document rendering from workflow.toml config.

Renders .spec-driver/agents/*.md from Jinja templates, substituting
project-specific config values.  Used by both the installer (initial
generation) and sync (keep agent docs fresh after config changes).
"""

from __future__ import annotations

from pathlib import Path

from .config import load_workflow_config
from .paths import SPEC_DRIVER_DIR
from .templates import render_template

# Package root: supekku/ is three levels up from this file
# (supekku/scripts/lib/core/agent_docs.py)
_PACKAGE_ROOT = Path(__file__).parent.parent.parent.parent


def _discover_agent_templates(package_root: Path) -> list[str]:
  """Discover agent template names from supekku/templates/agents/*.md."""
  agents_tpl_dir = package_root / "templates" / "agents"
  if not agents_tpl_dir.is_dir():
    return []
  return sorted(p.stem for p in agents_tpl_dir.glob("*.md"))


def render_agent_docs(
  target_root: Path,
  package_root: Path | None = None,
  *,
  dry_run: bool = False,
) -> list[str]:
  """Render agent guidance templates into .spec-driver/agents/.

  Loads workflow config, renders each agent template with it, and writes
  the result.

  Args:
    target_root: Repository root path.
    package_root: Spec-driver package root (defaults to installed location).
    dry_run: If True, print actions without writing files.

  Returns:
    List of template names that were rendered.

  Raises:
    TemplateNotFoundError: If agent templates are not available.
  """
  if package_root is None:
    package_root = _PACKAGE_ROOT

  config = load_workflow_config(target_root)
  agents_dir = target_root / SPEC_DRIVER_DIR / "agents"
  agents_dir.mkdir(parents=True, exist_ok=True)

  template_names = _discover_agent_templates(package_root)
  for name in template_names:
    content = render_template(
      f"agents/{name}.md",
      {"config": config},
      repo_root=target_root,
    )
    dest = agents_dir / f"{name}.md"
    if dry_run:
      print(f"  [DRY RUN] ./{SPEC_DRIVER_DIR}/agents/{name}.md")
    else:
      dest.write_text(content, encoding="utf-8")

  return template_names


__all__ = ["render_agent_docs"]
