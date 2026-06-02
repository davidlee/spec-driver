"""Re-export shim — see spec_driver.core.templates."""

from spec_driver.core.templates import (
  TemplateNotFoundError,
  extract_template_body,
  get_package_templates_dir,
  get_template_environment,
  load_template,
  render_template,
)

__all__ = [
  "TemplateNotFoundError",
  "extract_template_body",
  "get_package_templates_dir",
  "get_template_environment",
  "load_template",
  "render_template",
]
