"""Migration step v0_10_0_005_revision_metadata — DE-142 P04, revision kind.

Forward-only sweep that:
- Cuts universal + hand-rolled FM keys (lifecycle, aliases, auditers, source,
  source_specs, destination_specs, requirements).
- Synthesises a supekku:revision.change@v1 block for FM-only records, with
  action: modify and no move/lifecycle/origin (DEC-142-09); specs[] from
  destination_specs only (DEC-142-12).
- Existing block wins (no re-synthesis); never emits drift (DEC-142-10).

Per DEC-138-12 this package may not import from supekku.* or non-migrations spec_driver.
"""

from .migration import RevisionMetadataStep

step = RevisionMetadataStep()

__all__ = ["RevisionMetadataStep", "step"]
