"""Standard management for spec-driver.

This package provides:
- StandardRecord: Data model for standard metadata
- StandardRegistry: YAML-backed registry for standards
- Standard creation utilities
"""

from supekku.scripts.lib.standards.registry import StandardRecord, StandardRegistry

__all__ = [
  "StandardRecord",
  "StandardRegistry",
]
