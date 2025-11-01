"""DEPRECATED: Block handlers moved to supekku.scripts.lib.blocks

This stub exists for backward compatibility during migration.

YAML code block parsing is INFRASTRUCTURE (data format extraction),
not domain logic. All block handlers now live in:
  supekku/scripts/lib/blocks/

Domain logic that USES blocks stays in changes/:
  - artifacts.py: ChangeArtifact models
  - registry.py: Change registries and business rules
  - lifecycle.py: Status management

New imports:
  from supekku.scripts.lib.blocks.revision import ...
  from supekku.scripts.lib.blocks.delta import ...
  from supekku.scripts.lib.blocks.plan import ...
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.delta import (
  RELATIONSHIPS_MARKER as DELTA_RELATIONSHIPS_MARKER,
)
from supekku.scripts.lib.blocks.delta import (
  DeltaRelationshipsBlock,
  extract_delta_relationships,
  load_delta_relationships,
)
from supekku.scripts.lib.blocks.plan import (
  PHASE_MARKER as PHASE_OVERVIEW_MARKER,
)
from supekku.scripts.lib.blocks.plan import (
  PLAN_MARKER as PLAN_OVERVIEW_MARKER,
)
from supekku.scripts.lib.blocks.plan import (
  PhaseOverviewBlock,
  PlanOverviewBlock,
  extract_phase_overview,
  extract_plan_overview,
  load_phase_overview,
  load_plan_overview,
)

# Compatibility re-exports
from supekku.scripts.lib.blocks.revision import (
  REVISION_BLOCK_MARKER,
  RevisionBlockValidator,
  RevisionChangeBlock,
  extract_revision_blocks,
  load_revision_blocks,
)

__all__ = [
  "REVISION_BLOCK_MARKER",
  "RevisionChangeBlock",
  "RevisionBlockValidator",
  "extract_revision_blocks",
  "load_revision_blocks",
  "DELTA_RELATIONSHIPS_MARKER",
  "DeltaRelationshipsBlock",
  "extract_delta_relationships",
  "load_delta_relationships",
  "PLAN_OVERVIEW_MARKER",
  "PHASE_OVERVIEW_MARKER",
  "PlanOverviewBlock",
  "PhaseOverviewBlock",
  "extract_plan_overview",
  "extract_phase_overview",
  "load_plan_overview",
  "load_phase_overview",
]
