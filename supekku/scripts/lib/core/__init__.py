"""Core foundation utilities for spec-driver.

This package contains foundational utilities depended upon by all other domains:
- paths: Directory and path configuration
- spec_utils: Markdown file I/O
- frontmatter_schema: YAML frontmatter validation
- cli_utils: CLI helper functions
- filters: Filter parsing utilities
- repo: Repository root discovery
- go_utils: Go toolchain utilities
- npm_utils: npm package manager utilities
- editor: Editor invocation utilities
"""

from __future__ import annotations

from .editor import (
  EditorError,
  EditorInvocationError,
  EditorNotFoundError,
  find_editor,
  invoke_editor,
)
from .filters import parse_multi_value_filter
from .npm_utils import (
  PackageManager,
  PackageManagerInfo,
  detect_package_manager,
  get_install_instructions,
  get_package_manager_info,
  is_bun_available,
  is_npm_available,
  is_npm_package_available,
  is_pnpm_available,
)

__all__: list[str] = [
  "EditorError",
  "EditorInvocationError",
  "EditorNotFoundError",
  "PackageManager",
  "PackageManagerInfo",
  "detect_package_manager",
  "find_editor",
  "get_install_instructions",
  "get_package_manager_info",
  "invoke_editor",
  "is_bun_available",
  "is_npm_available",
  "is_npm_package_available",
  "is_pnpm_available",
  "parse_multi_value_filter",
]
