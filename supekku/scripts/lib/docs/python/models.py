"""Data models for Python documentation generation API."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum


class VariantType(Enum):
    """Documentation variant types."""

    PUBLIC = "public"
    ALL = "all"
    TESTS = "tests"


@dataclass
class VariantSpec:
    """Specification for a documentation variant."""

    variant_type: VariantType
    include_private: bool = False
    include_tests: bool = False

    @classmethod
    def public(cls) -> "VariantSpec":
        """Create PUBLIC variant spec."""
        return cls(VariantType.PUBLIC, include_private=False, include_tests=False)

    @classmethod
    def all_symbols(cls) -> "VariantSpec":
        """Create ALL variant spec."""
        return cls(VariantType.ALL, include_private=True, include_tests=False)

    @classmethod
    def tests(cls) -> "VariantSpec":
        """Create TESTS variant spec."""
        return cls(VariantType.TESTS, include_private=True, include_tests=True)


@dataclass
class DocResult:
    """Result of documentation generation for a single file/variant combination."""

    variant: str
    path: Path
    hash: str
    status: str  # "created", "changed", "unchanged", "error"
    module_identifier: str  # normalized module path (e.g. "src.module")
    error_message: Optional[str] = None

    @property
    def success(self) -> bool:
        """Whether generation was successful."""
        return self.status != "error"
