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
    REVISION_BLOCK_MARKER,
    RevisionBlockValidator,
    RevisionChangeBlock,
    ValidationMessage,
    extract_revision_blocks,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
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
    root: Path, explicit: list[Path], scan_all: bool
) -> list[Path]:
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
    updated = content
    for block, replacement in sorted(
        updates, key=lambda item: item[0].content_start, reverse=True
    ):
        updated = block.replace_content(updated, replacement)
    return updated


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.print_schema:
        _print_schema()
        return 0

    root = find_repo_root(args.root)
    files = discover_revision_files(root, list(args.paths), args.scan_all)

    if not files:
        print("no revision files matched", file=sys.stderr)
        return 1

    validator = RevisionBlockValidator()
    exit_code = 0

    for path in files:
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"[ERROR] {path}: {exc}")
            exit_code = 1
            continue

        blocks = extract_revision_blocks(content, source=path)
        if not blocks:
            if args.strict:
                print(f"[ERROR] {path}: missing {REVISION_BLOCK_MARKER} block")
                exit_code = 1
            else:
                print(f"[WARN] {path}: no {REVISION_BLOCK_MARKER} block found")
            continue

        updates: list[tuple[RevisionChangeBlock, str]] = []
        file_has_error = False
        for index, block in enumerate(blocks):
            try:
                data = block.parse()
            except ValueError as exc:
                print(f"[ERROR] {path} block#{index + 1}: {exc}")
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
                print(f"[UPDATED] {path}")
        elif not file_has_error:
            print(f"[OK] {path}")

    return exit_code


def _emit_messages(path: Path, messages: list[ValidationMessage]) -> None:
    for message in messages:
        loc = message.render_path()
        print(f"[ERROR] {path}:{loc}: {message.message}")


def _print_schema() -> None:
    from supekku.scripts.lib.revision_blocks import REVISION_BLOCK_JSON_SCHEMA

    import json

    print(json.dumps(REVISION_BLOCK_JSON_SCHEMA, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
