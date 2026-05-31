"""Legacy re-export shim — see spec_driver.core.frontmatter_writer."""

from spec_driver.core.frontmatter_writer import (  # noqa: F401
  CompactDumper,
  FieldUpdateResult,
  ListUpdateResult,
  add_frontmatter_list_items,
  dump_frontmatter_yaml,
  remove_frontmatter_list_items,
  update_frontmatter,
  update_frontmatter_fields,
  update_frontmatter_status,
)

__all__ = [
  "CompactDumper",
  "FieldUpdateResult",
  "ListUpdateResult",
  "add_frontmatter_list_items",
  "dump_frontmatter_yaml",
  "remove_frontmatter_list_items",
  "update_frontmatter",
  "update_frontmatter_fields",
  "update_frontmatter_status",
]
