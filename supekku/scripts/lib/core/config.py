"""Re-export shim — see spec_driver.core.config."""
from spec_driver.core.config import (
  DEFAULT_CONFIG,
  detect_exec_command,
  generate_default_workflow_toml,
  get_strict_map,
  is_strict_mode,
  load_workflow_config,
)

__all__ = [
  "DEFAULT_CONFIG",
  "detect_exec_command",
  "generate_default_workflow_toml",
  "get_strict_map",
  "is_strict_mode",
  "load_workflow_config",
]
