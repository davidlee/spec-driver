"""Registry migration from v1 (flat) to v2 (language-aware) format."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RegistryV2:
  """v2 registry model - language-aware structure.

  Format: {
      "version": 2,
      "languages": {
          "go": {"package/path": "SPEC-XXX"},
          "python": {"module.py": "SPEC-YYY"}
      },
      "metadata": {"created": "2025-01-15", ...}
  }
  """

  version: int
  languages: dict[str, dict[str, str]]
  metadata: dict[str, Any] = field(default_factory=dict)

  @classmethod
  def create_empty(cls) -> RegistryV2:
    """Create empty v2 registry with metadata."""
    return cls(
      version=2,
      languages={},
      metadata={
        "created": datetime.now().isoformat(),
      },
    )

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> RegistryV2:
    """Create v2 registry from dictionary."""
    return cls(
      version=data.get("version", 2),
      languages=data.get("languages", {}),
      metadata=data.get("metadata", {}),
    )

  @classmethod
  def from_file(cls, path: Path) -> RegistryV2:
    """Load v2 registry from JSON file."""
    if not path.exists():
      return cls.create_empty()

    data = json.loads(path.read_text())
    return cls.from_dict(data)

  def save_to_file(self, path: Path) -> None:
    """Save v2 registry to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    # Sort languages and their contents for deterministic output
    sorted_languages = {}
    for language in sorted(self.languages.keys()):
      sorted_languages[language] = dict(sorted(self.languages[language].items()))

    data = {
      "version": self.version,
      "languages": sorted_languages,
      "metadata": self.metadata,
    }

    serialized = json.dumps(data, indent=2) + "\n"
    path.write_text(serialized)

  def add_source_unit(self, language: str, identifier: str, spec_id: str) -> None:
    """Add a source unit mapping to the registry."""
    if language not in self.languages:
      self.languages[language] = {}
    self.languages[language][identifier] = spec_id

  def remove_source_unit(self, language: str, identifier: str) -> bool:
    """Remove a source unit mapping from the registry.

    Args:
        language: Language of the source unit
        identifier: Source identifier

    Returns:
        True if the entry was removed, False if it didn't exist

    """
    if language not in self.languages:
      return False

    if identifier not in self.languages[language]:
      return False

    del self.languages[language][identifier]

    # Clean up empty language dict
    if not self.languages[language]:
      del self.languages[language]

    return True

  def remove_spec(self, spec_id: str) -> int:
    """Remove all source units that map to a specific spec ID.

    Args:
        spec_id: Spec ID to remove (e.g., "SPEC-001")

    Returns:
        Number of source units removed

    """
    removed_count = 0

    for language in list(self.languages.keys()):
      identifiers_to_remove = [
        identifier
        for identifier, sid in self.languages[language].items()
        if sid == spec_id
      ]

      for identifier in identifiers_to_remove:
        if self.remove_source_unit(language, identifier):
          removed_count += 1

    return removed_count

  def get_spec_id(self, language: str, identifier: str) -> str | None:
    """Get spec ID for a specific language and identifier."""
    return self.languages.get(language, {}).get(identifier)

  def get_spec_id_compat(self, identifier: str) -> str | None:
    """Get spec ID with backwards compatibility.

    Searches all languages, with Go as default/fallback for ambiguous cases.
    """
    # First try Go (most common/default)
    go_result = self.get_spec_id("go", identifier)
    if go_result:
      return go_result

    # Then try other languages
    for language, mappings in self.languages.items():
      if language != "go" and identifier in mappings:
        return mappings[identifier]

    return None

  def get_all_source_units(self) -> dict[tuple[str, str], str]:
    """Get all source units as (language, identifier) -> spec_id mapping."""
    result = {}
    for language, mappings in self.languages.items():
      for identifier, spec_id in mappings.items():
        result[(language, identifier)] = spec_id
    return result

  def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for serialization."""
    return {
      "version": self.version,
      "languages": self.languages,
      "metadata": self.metadata,
    }


class LanguageDetector:
  """Detects language from source identifiers using SpecSyncEngine adapters."""

  def __init__(self) -> None:
    """Initialize with language adapters for detection."""
    try:
      # Try relative import first (when used as module)
      # pylint: disable=import-outside-toplevel
      from .spec_sync.adapters import (  # noqa: PLC0415
        GoAdapter,
        PythonAdapter,
      )
    except ImportError:
      # Fall back to absolute import (when used as script)
      # pylint: disable=import-outside-toplevel
      from spec_sync.adapters import GoAdapter, PythonAdapter  # noqa: PLC0415

    # Create adapters for detection (repo_root not needed for detection)
    temp_root = Path("/tmp")
    self.go_adapter = GoAdapter(temp_root)
    self.python_adapter = PythonAdapter(temp_root)

  def detect_language(self, identifier: str) -> str:
    """Detect language from identifier using adapter support checks.

    Uses refined logic for disambiguation when multiple adapters match.

    Args:
        identifier: Source identifier (package path, file path, etc.)

    Returns:
        Language name ("go", "python", etc.)

    """
    # Clear Python indicators (file extensions)
    if identifier.endswith(".py"):
      return "python"

    # Go package patterns (contains slashes, internal/ prefix, etc.)
    if "/" in identifier or identifier.startswith(("cmd", "tools", "internal")):
      return "go"

    # Check specific adapter support as fallback
    python_supports = self.python_adapter.supports_identifier(identifier)
    go_supports = self.go_adapter.supports_identifier(identifier)

    # If only one supports it, use that
    if python_supports and not go_supports:
      return "python"
    if go_supports and not python_supports:
      return "go"

    # Default to Go for backwards compatibility (most existing entries are Go)
    return "go"


__all__ = [
  "LanguageDetector",
  "RegistryV2",
]
