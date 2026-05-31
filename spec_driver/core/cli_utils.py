"""Common utilities for CLI argument parsing and YAML processing."""

import argparse
from pathlib import Path
from re import Match
from typing import Any

import yaml


def add_root_argument(
  parser: argparse.ArgumentParser,
  help_text: str = "Repository root (auto-detected if omitted)",
) -> None:
  """Add a standard --root argument to an argument parser.

  Args:
      parser: The ArgumentParser to add the argument to
      help_text: Custom help text for the --root argument

  """
  parser.add_argument(
    "--root",
    type=Path,
    default=Path.cwd(),
    help=help_text,
  )


def create_parser_with_root(
  description: str,
  help_text: str = "Repository root (auto-detected if omitted)",
) -> argparse.ArgumentParser:
  """Create an ArgumentParser with standard --root argument.

  Args:
      description: Description for the parser
      help_text: Custom help text for the --root argument

  Returns:
      ArgumentParser with --root argument added

  """
  parser = argparse.ArgumentParser(description=description)
  add_root_argument(parser, help_text)
  return parser


def parse_yaml_block(match: Match[str], block_name: str) -> dict[str, Any]:
  """Parse YAML from a regex match, with consistent error handling.

  Args:
      match: Regex match containing YAML in group 1
      block_name: Name of the block type for error messages

  Returns:
      Parsed YAML data as dictionary

  Raises:
      ValueError: If YAML parsing fails or result is not a dict

  """
  if not match:
    msg = f"No {block_name} block found"
    raise ValueError(msg)

  raw = match.group(1)
  try:
    data = yaml.safe_load(raw) or {}
  except yaml.YAMLError as exc:  # pragma: no cover
    msg = f"invalid {block_name} YAML: {exc}"
    raise ValueError(msg) from exc

  if not isinstance(data, dict):
    msg = f"{block_name} block must parse to mapping"
    raise ValueError(msg)

  return data
