"""Drift ledger registry — read-only discovery and access.

Discovers drift ledger files in .spec-driver/drift/ and provides
find/iter/collect access. No YAML registry sync (deferred per IMPR-007 D2).

See DEC-065-04.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterator
from pathlib import Path

from supekku.scripts.lib.core.paths import get_drift_dir
from supekku.scripts.lib.core.spec_utils import load_markdown_file

from .models import DriftLedger
from .parser import parse_ledger_body

logger = logging.getLogger(__name__)

# Matches DL-NNN or DL-NNN-slug filenames
_LEDGER_FILE_RE = re.compile(r"^DL-\d+.*\.md$")


class DriftLedgerRegistry:
  """Read-only registry for drift ledger discovery and access.

  Discovers ledger files in .spec-driver/drift/ on first access (lazy).
  """

  def __init__(self, root: Path | None = None) -> None:
    self._root = root
    self._ledgers: dict[str, DriftLedger] | None = None

  def _load(self) -> dict[str, DriftLedger]:
    """Discover and parse all drift ledger files."""
    if self._ledgers is not None:
      return self._ledgers

    drift_dir = get_drift_dir(self._root)
    self._ledgers = {}

    if not drift_dir.is_dir():
      return self._ledgers

    for path in sorted(drift_dir.iterdir()):
      if not path.is_file() or not _LEDGER_FILE_RE.match(path.name):
        continue
      ledger = _load_ledger(path)
      if ledger is not None:
        self._ledgers[ledger.id] = ledger

    return self._ledgers

  def collect(self) -> dict[str, DriftLedger]:
    """Return all discovered drift ledgers, keyed by ID."""
    return dict(self._load())

  def find(self, ledger_id: str) -> DriftLedger | None:
    """Find a single drift ledger by ID."""
    return self._load().get(ledger_id)

  def iter(self, *, status: str | None = None) -> Iterator[DriftLedger]:
    """Iterate over drift ledgers, optionally filtered by status."""
    for ledger in self._load().values():
      if status is None or ledger.status == status:
        yield ledger


def _load_ledger(path: Path) -> DriftLedger | None:
  """Load a single drift ledger from a markdown file."""
  try:
    fm, body = load_markdown_file(path)
  except (OSError, ValueError, KeyError):
    logger.warning("Failed to load drift ledger: %s", path, exc_info=True)
    return None

  ledger_id = fm.get("id", "")
  if not ledger_id:
    logger.warning("Drift ledger missing 'id' in frontmatter: %s", path)
    return None

  freeform_body, entries = parse_ledger_body(body)

  return DriftLedger(
    id=ledger_id,
    name=fm.get("name", ""),
    status=fm.get("status", "open"),
    path=path,
    created=str(fm.get("created", "")),
    updated=str(fm.get("updated", "")),
    delta_ref=fm.get("delta_ref", ""),
    body=freeform_body,
    frontmatter=fm,
    entries=entries,
  )
