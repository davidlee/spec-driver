"""Core foundation utilities for spec-driver.

This package contains foundational utilities depended upon by all other domains:
- paths: Directory and path configuration
- spec_utils: Markdown file I/O
- frontmatter_schema: YAML frontmatter validation
- cli_utils: CLI helper functions
- filters: Filter parsing utilities
- repo: Repository root discovery
- go_utils: Go toolchain utilities
"""

from __future__ import annotations

from .filters import parse_multi_value_filter

__all__: list[str] = [
  "parse_multi_value_filter",
]
