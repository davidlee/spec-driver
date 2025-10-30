"""Registry for managing and accessing specification files."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from .backlog import find_repo_root
from .spec_models import Spec
from .spec_utils import load_validated_markdown_file


class SpecRegistry:
    """Discovery service for SPEC/PROD artefacts."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = find_repo_root(root)
        self.tech_dir = self.root / "specify" / "tech"
        self.product_dir = self.root / "specify" / "product"
        self._specs: dict[str, Spec] = {}
        self.reload()

    def reload(self) -> None:
        """Reload all specs from the filesystem."""
        self._specs.clear()
        self._load_directory(
            self.tech_dir, expected_prefix="SPEC-", expected_kind="spec",
        )
        self._load_directory(
            self.product_dir, expected_prefix="PROD-", expected_kind="prod",
        )

    def get(self, spec_id: str) -> Spec | None:
        """Get a spec by its ID."""
        return self._specs.get(spec_id)

    def all_specs(self) -> list[Spec]:
        """Return all loaded specs."""
        return list(self._specs.values())

    def find_by_package(self, package: str) -> list[Spec]:
        """Find all specs that reference the given package."""
        return [spec for spec in self._specs.values() if package in spec.packages]

    # ------------------------------------------------------------------
    def _load_directory(
        self, directory: Path, *, expected_prefix: str, expected_kind: str,
    ) -> None:
        if not directory.exists():
            return
        for entry in directory.iterdir():
            if entry.is_dir():
                for candidate in self._iter_prefixed_files(entry, expected_prefix):
                    self._register_spec(candidate, expected_kind)
            elif entry.is_file() and entry.name.startswith(expected_prefix):
                self._register_spec(entry, expected_kind)

    def _iter_prefixed_files(self, directory: Path, prefix: str) -> Iterator[Path]:
        """Iterate over files with the given prefix in a directory."""
        yield from directory.glob(f"{prefix}*.md")

    def _register_spec(self, path: Path, expected_kind: str) -> None:
        frontmatter, body = load_validated_markdown_file(path, kind=expected_kind)
        spec_id = frontmatter.id
        if not spec_id:
            return
        self._specs[spec_id] = Spec(
            id=spec_id,
            path=path,
            frontmatter=frontmatter,
            body=body,
        )


__all__ = ["SpecRegistry"]
