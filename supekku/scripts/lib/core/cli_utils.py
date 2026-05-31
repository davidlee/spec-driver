"""Legacy re-export shim — see spec_driver.core.cli_utils."""

from spec_driver.core.cli_utils import (
  add_root_argument,
  create_parser_with_root,
  parse_yaml_block,
)

__all__ = ["add_root_argument", "create_parser_with_root", "parse_yaml_block"]
