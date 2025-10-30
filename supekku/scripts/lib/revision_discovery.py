"""Utilities for discovering requirement sources in revision files."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from .revision_blocks import load_revision_blocks
from .spec_utils import load_markdown_file


@dataclass(frozen=True)
class RequirementSource:
    """Location of a requirement in a revision file."""

    requirement_id: str
    revision_id: str
    revision_file: Path
    block_index: int
    requirement_index: int


def _iter_revision_files(revision_dirs: Iterable[Path]) -> Iterator[Path]:
    """Iterate over all revision markdown files in given directories."""
    for directory in revision_dirs:
        if not directory.exists():
            continue
        for bundle in directory.iterdir():
            if not bundle.is_dir():
                continue
            for file in bundle.glob("*.md"):
                if file.name.startswith("RE-"):
                    yield file


def find_requirement_sources(
    requirement_ids: list[str],
    revision_dirs: Iterable[Path],
) -> dict[str, RequirementSource]:
    """Find source locations for requirements in revision files.

    Scans all revision files in the given directories and locates
    requirements in their YAML blocks.

    Args:
        requirement_ids: List of requirement IDs to search for
        revision_dirs: Directories containing revision bundles

    Returns:
        Mapping of requirement_id -> RequirementSource for found requirements.
        Only includes requirements found in revision blocks.

    """
    requirement_set = set(requirement_ids)
    sources: dict[str, RequirementSource] = {}

    for revision_file in _iter_revision_files(revision_dirs):
        # Get revision ID from frontmatter
        frontmatter, _ = load_markdown_file(revision_file)
        revision_id = str(frontmatter.get("id", "")).strip() or revision_file.stem

        # Load and scan revision blocks
        try:
            blocks = load_revision_blocks(revision_file)
        except (OSError, ValueError):
            # Skip files we can't read or parse
            continue

        for block_index, block in enumerate(blocks):
            try:
                data = block.parse()
            except ValueError:
                # Skip malformed blocks
                continue

            requirements = data.get("requirements", [])
            if not isinstance(requirements, list):
                continue

            for req_index, requirement in enumerate(requirements):
                if not isinstance(requirement, dict):
                    continue

                req_id = str(requirement.get("requirement_id", "")).strip()
                if not req_id or req_id not in requirement_set:
                    continue

                # Found a match - record it
                # If duplicate, later occurrence wins (shouldn't happen normally)
                sources[req_id] = RequirementSource(
                    requirement_id=req_id,
                    revision_id=revision_id,
                    revision_file=revision_file,
                    block_index=block_index,
                    requirement_index=req_index,
                )

    return sources


__all__ = ["RequirementSource", "find_requirement_sources"]
