"""Migration folder-name parser (F-13: valid Python module name).

Folder shape: ``v<MAJOR>_<MINOR>_<PATCH>_<NNN>_<slug>/`` — valid Python
package identifier (starts with letter; no dots/dashes). Sort key
``(version, ordinal)`` orders the discovery walk.
"""

from __future__ import annotations

from dataclasses import dataclass

from packaging.version import Version

from spec_driver.presentation.cli.constants import MIGRATION_FOLDER_PATTERN


@dataclass(frozen=True)
class ParsedFolder:
  """Parsed migration folder name.

  ``version`` + ``ordinal`` together form the total-order sort key.
  """

  version: Version
  ordinal: int
  slug: str
  name: str


def parse_migration_folder(name: str) -> ParsedFolder | None:
  """Parse a migration folder name; return ``None`` on mismatch.

  Non-matching names (``_protocol``, ``__pycache__``, dotted-version
  shapes, missing prefix) return ``None`` so the orchestrator can
  skip them silently.
  """
  match = MIGRATION_FOLDER_PATTERN.match(name)
  if match is None:
    return None

  parts = match.groupdict()
  version = Version(f"{parts['major']}.{parts['minor']}.{parts['patch']}")
  return ParsedFolder(
    version=version,
    ordinal=int(parts["ordinal"]),
    slug=parts["slug"],
    name=name,
  )
