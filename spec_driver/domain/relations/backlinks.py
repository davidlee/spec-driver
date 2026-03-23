"""Generic backlink computation for artifact registries.

Extracts the duplicated backlink-building pattern from individual registries
into a reusable helper. Per ADR-002, backlinks are computed at runtime from
forward references, not stored in frontmatter.

Design reference: DE-125, DR-125 §3.3 (registry rule).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, runtime_checkable


@runtime_checkable
class BacklinkTarget(Protocol):  # pylint: disable=too-few-public-methods
  """Record that can receive computed backlinks.

  Single-property Protocol is intentional — see ADR-009.
  """

  backlinks: dict[str, list[str]]


def build_backlinks(
  targets: dict[str, BacklinkTarget],
  sources: Iterable[tuple[str, Iterable[str]]],
  category: str,
  *,
  clear: bool = True,
) -> None:
  """Compute reverse references from sources into targets.

  For each ``(source_id, referenced_target_ids)`` pair in *sources*,
  if a referenced ID exists in *targets*, add *source_id* to that
  target's ``backlinks[category]`` list.

  This replaces the pattern where registries lazy-import sibling
  registries to walk forward references. Instead, the **caller**
  collects source data and passes it in.

  Args:
    targets: Records receiving backlinks, keyed by their ID.
    sources: Iterable of ``(source_id, target_ids)`` pairs. Each pair
        represents one source record and the target IDs it references.
    category: Backlink bucket name (e.g. ``"decisions"``, ``"policies"``).
    clear: If True (default), clear existing backlinks on all targets
        before computing. Set to False when accumulating multiple
        categories in sequence.

  Example::

      # In PolicyRegistry.sync(), instead of lazy-importing DecisionRegistry:
      decision_sources = [
          (dec.id, dec.policies) for dec in decisions.values()
      ]
      build_backlinks(policies, decision_sources, "decisions")
  """
  if clear:
    for target in targets.values():
      target.backlinks = {}

  for source_id, referenced_ids in sources:
    for target_id in referenced_ids:
      if target_id in targets:
        targets[target_id].backlinks.setdefault(category, []).append(source_id)


def build_backlinks_multi(
  targets: dict[str, BacklinkTarget],
  source_groups: Iterable[tuple[Iterable[tuple[str, Iterable[str]]], str]],
) -> None:
  """Compute backlinks from multiple source categories in one pass.

  Clears backlinks once, then accumulates from each source group.

  Args:
    targets: Records receiving backlinks, keyed by their ID.
    source_groups: Iterable of ``(sources, category)`` pairs. Each group
        is processed with ``build_backlinks(..., clear=False)``.

  Example::

      # In StandardsRegistry.sync():
      build_backlinks_multi(standards, [
          ([(d.id, d.standards) for d in decisions.values()], "decisions"),
          ([(p.id, p.standards) for p in policies.values()], "policies"),
      ])
  """
  for target in targets.values():
    target.backlinks = {}

  for sources, category in source_groups:
    build_backlinks(targets, sources, category, clear=False)


__all__ = [
  "BacklinkTarget",
  "build_backlinks",
  "build_backlinks_multi",
]
