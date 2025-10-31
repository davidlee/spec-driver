#!/usr/bin/env python3
"""Validate structured revision change blocks and optionally format them."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

# pylint: disable=wrong-import-position
from supekku.scripts.lib.backlog import find_repo_root  # type: ignore
from supekku.scripts.lib.cli_utils import add_root_argument
from supekku.scripts.lib.revision_blocks import (  # type: ignore
  RevisionBlockValidator,
  RevisionChangeBlock,
  ValidationMessage,
  extract_revision_blocks,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
  """Parse command-line arguments for revision block validation.

  Args:
    argv: Optional list of command-line arguments. Defaults to sys.argv.

  Returns:
    Parsed argument namespace.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "paths",
    nargs="*",
    type=Path,
    help="Revision markdown files to validate",
  )
  parser.add_argument(
    "--all",
    dest="scan_all",
    action="store_true",
    help="Scan change/revisions/**/RE-*.md automatically",
  )
  add_root_argument(parser)
  parser.add_argument(
    "--format",
    dest="format_blocks",
    action="store_true",
    help="Rewrite blocks with canonical YAML formatting when valid",
  )
  parser.add_argument(
    "--strict",
    action="store_true",
    help="Treat missing structured blocks as errors",
  )
  parser.add_argument(
    "--print-schema",
    action="store_true",
    help="Print the revision change JSON schema to stdout and exit",
  )
  return parser.parse_args(argv)


def discover_revision_files(
  root: Path,
  explicit: list[Path],
  scan_all: bool,
) -> list[Path]:
  """Discover revision markdown files to validate.

  Args:
    root: Repository root path.
    explicit: List of explicitly specified file or directory paths.
    scan_all: Whether to scan all revision files automatically.

  Returns:
    Sorted list of revision file paths to validate.
  """
  if explicit:
    resolved = []
    for entry in explicit:
      path = entry if entry.is_absolute() else root / entry
      if path.is_dir():
        resolved.extend(sorted(path.rglob("RE-*.md")))
      else:
        resolved.append(path)
    return sorted(set(resolved))
  if scan_all:
    revision_root = root / "change" / "revisions"
    if not revision_root.is_dir():
      return []
    return sorted(revision_root.rglob("RE-*.md"))
  return []


def format_file(content: str, updates: list[tuple[RevisionChangeBlock, str]]) -> str:
  """Apply formatting updates to file content.

  Args:
    content: Original file content.
    updates: List of (block, replacement) tuples to apply.

  Returns:
    Updated file content with replacements applied.
  """
  updated = content
  for block, replacement in sorted(
    updates,
    key=lambda item: item[0].content_start,
    reverse=True,
  ):
    updated = block.replace_content(updated, replacement)
  return updated


def main(argv: list[str] | None = None) -> int:
  """Validate and optionally format revision block YAML in markdown files.

  Args:
    argv: Optional command-line arguments.

  Returns:
    Exit code: 0 on success, 1 on validation errors.
  """
  args = parse_args(argv)
  if args.print_schema:
    _print_schema()
    return 0

  root = find_repo_root(args.root)
  files = discover_revision_files(root, list(args.paths), args.scan_all)

  if not files:
    return 1

  validator = RevisionBlockValidator()
  exit_code = 0

  for path in files:
    try:
      content = path.read_text(encoding="utf-8")
    except OSError:
      exit_code = 1
      continue

    blocks = extract_revision_blocks(content, source=path)
    if not blocks:
      if args.strict:
        exit_code = 1
      else:
        pass
      continue

    updates: list[tuple[RevisionChangeBlock, str]] = []
    file_has_error = False
    for _index, block in enumerate(blocks):
      try:
        data = block.parse()
      except ValueError:
        exit_code = 1
        file_has_error = True
        continue

      messages = validator.validate(data)
      if messages:
        exit_code = 1
        file_has_error = True
        _emit_messages(path, messages)
        continue

      if args.format_blocks:
        formatted = block.formatted_yaml(data)
        if formatted != block.yaml_content:
          updates.append((block, formatted))

    if args.format_blocks and updates and not file_has_error:
      updated_content = format_file(content, updates)
      if updated_content != content:
        path.write_text(updated_content, encoding="utf-8")
    elif not file_has_error:
      pass

  return exit_code


def _emit_messages(_path: Path, messages: list[ValidationMessage]) -> None:
  for message in messages:
    message.render_path()


def _print_schema() -> None:
  pass


if __name__ == "__main__":
  raise SystemExit(main())
