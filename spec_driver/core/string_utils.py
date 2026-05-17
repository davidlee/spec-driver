"""String utilities for spec-driver.

Pure functions, no I/O. Hosts reusable shape helpers (did-you-mean,
case folding, ...) consumed by validation and CLI surfaces.
"""

from __future__ import annotations

from collections.abc import Iterable
from difflib import get_close_matches

CLOSEST_MATCH_CUTOFF: float = 0.6


def closest_match(value: str, candidates: Iterable[str]) -> str | None:
  """Return the closest match to *value* from *candidates*, or None.

  Wraps `difflib.get_close_matches(n=1, cutoff=CLOSEST_MATCH_CUTOFF)`.
  Empty and single-character inputs short-circuit to None so trivial
  inputs do not surface spurious matches (e.g. `'a'` against `'audit'`).

  Used by `MetadataValidator` for enum did-you-mean diagnostics. The
  cutoff catches typos (`'in_progres' -> 'in-progress'`) but does not
  bridge semantic alternatives (`'live' -> 'in-progress'`); those belong
  in `FieldMetadata.aliases`. See DEC-137-20 for the spike evidence.
  """
  if len(value) < 2:
    return None
  matches = get_close_matches(value, list(candidates), n=1, cutoff=CLOSEST_MATCH_CUTOFF)
  return matches[0] if matches else None
