"""Data models for specifications and related entities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .frontmatter_schema import FrontmatterValidationResult


@dataclass(frozen=True)
class Spec:
    """In-memory representation of a specification artefact."""

    id: str
    path: Path
    frontmatter: FrontmatterValidationResult
    body: str

    @property
    def packages(self) -> list[str]:
        packages = self.frontmatter.data.get("packages", [])
        if isinstance(packages, Iterable) and not isinstance(packages, (str, bytes)):
            return [str(item) for item in packages]
        return []

    @property
    def slug(self) -> str:
        return str(self.frontmatter.data.get("slug", ""))

    @property
    def name(self) -> str:
        return str(self.frontmatter.data.get("name", self.id))

    @property
    def kind(self) -> str:
        return str(self.frontmatter.data.get("kind", ""))


__all__ = ["Spec"]
