"""Legacy re-export shim — see spec_driver.core.spec_utils.

Pure primitives live in spec_driver.core.spec_utils.
Kind-aware dump_markdown_file_create lives in spec_driver.orchestration.templates
(DEC-128-004: kind rendering is an orchestration concern per POL-003).
"""

from spec_driver.core.spec_utils import (  # noqa: F401
  MarkdownLoadError,
  append_unique,
  dump_markdown_file_update,
  ensure_list_entry,
  extract_h1_title,
  load_markdown_file,
  load_validated_markdown_file,
  write_markdown_file,
)
from spec_driver.orchestration.templates import (  # noqa: F401
  dump_markdown_file_create,
)

__all__ = [
  "MarkdownLoadError",
  "append_unique",
  "dump_markdown_file_create",
  "dump_markdown_file_update",
  "ensure_list_entry",
  "extract_h1_title",
  "load_markdown_file",
  "load_validated_markdown_file",
  "write_markdown_file",
]
