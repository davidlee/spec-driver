"""Metadata definitions for workflow orchestration schemas.

Defines BlockMetadata for the 5 workflow artifact schemas and 2 bridge
block schemas from DR-102 §3 and §7.  Registration at module level
ensures schemas appear in ``spec-driver list schemas``.

Design authority: DR-102 (DE-102).
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import FieldMetadata
from supekku.scripts.lib.blocks.schema_registry import (
  BlockSchema,
  register_block_schema,
)
from supekku.scripts.lib.workflow.review_state_machine import (
  BootstrapStatus,
  DispositionAuthority,
  FindingDispositionAction,
  FindingStatus,
  ReviewStatus,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Workflow artifact schemas (DR-102 §3)
STATE_SCHEMA = "supekku.workflow.state"
STATE_VERSION = 1
STATE_MARKER = "supekku:workflow.state@v1"

HANDOFF_SCHEMA = "supekku.workflow.handoff"
HANDOFF_VERSION = 1
HANDOFF_MARKER = "supekku:workflow.handoff@v1"

REVIEW_INDEX_SCHEMA = "supekku.workflow.review-index"
REVIEW_INDEX_VERSION = 1
REVIEW_INDEX_MARKER = "supekku:workflow.review-index@v1"

REVIEW_FINDINGS_SCHEMA = "supekku.workflow.review-findings"
REVIEW_FINDINGS_VERSION = 2
REVIEW_FINDINGS_MARKER = "supekku:workflow.review-findings@v2"

SESSIONS_SCHEMA = "supekku.workflow.sessions"
SESSIONS_VERSION = 1
SESSIONS_MARKER = "supekku:workflow.sessions@v1"

# Bridge block schemas (DR-102 §7)
NOTES_BRIDGE_SCHEMA = "supekku.workflow.notes-bridge"
NOTES_BRIDGE_VERSION = 1
NOTES_BRIDGE_MARKER = "supekku:workflow.notes-bridge@v1"

PHASE_BRIDGE_SCHEMA = "supekku.workflow.phase-bridge"
PHASE_BRIDGE_VERSION = 1
PHASE_BRIDGE_MARKER = "supekku:workflow.phase-bridge@v1"

# Shared enum values (DR-102 §3/§4)
ARTIFACT_KIND_VALUES = ["delta", "plan", "revision", "audit", "task", "other"]
PHASE_STATUS_VALUES = ["not_started", "in_progress", "blocked", "complete", "skipped"]
ROLE_VALUES = ["architect", "implementer", "reviewer", "operator", "other"]
WORKFLOW_STATUS_VALUES = [
  "planned",
  "implementing",
  "awaiting_handoff",
  "reviewing",
  "changes_requested",
  "approved",
  "blocked",
]
HANDOFF_TRANSITION_STATUS_VALUES = ["pending", "accepted", "superseded"]
VERIFICATION_STATUS_VALUES = ["pass", "fail", "partial", "not_run", "unknown"]
NEXT_ACTIVITY_KIND_VALUES = [
  "implementation",
  "review",
  "architecture",
  "verification",
  "operator_attention",
]
OPEN_ITEM_KIND_VALUES = ["next_step", "blocker", "question", "risk"]
BOOTSTRAP_STATUS_VALUES = [e.value for e in BootstrapStatus]
REVIEW_STATUS_VALUES = [e.value for e in ReviewStatus]
FINDING_STATUS_VALUES = [e.value for e in FindingStatus]
FINDING_DISPOSITION_ACTION_VALUES = [e.value for e in FindingDispositionAction]
DISPOSITION_AUTHORITY_VALUES = [e.value for e in DispositionAuthority]
SESSION_STATUS_VALUES = ["active", "paused", "absent", "dead", "unknown"]
REVIEW_SESSION_SCOPE_VALUES = ["artifact", "phase", "task"]
HANDOFF_BOUNDARY_VALUES = ["phase", "task", "manual"]


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------


def _timestamps_block(fields: dict[str, FieldMetadata]) -> FieldMetadata:
  """Timestamps object with caller-specified fields."""
  return FieldMetadata(
    type="object",
    required=True,
    description="Timestamps",
    properties=fields,
  )


# ---------------------------------------------------------------------------
# Re-exports — schema metadata objects from per-schema files
# ---------------------------------------------------------------------------

from supekku.scripts.lib.blocks.handoff_schema import (  # noqa: E402, F401
  WORKFLOW_HANDOFF_METADATA,
)
from supekku.scripts.lib.blocks.notes_bridge_schema import (  # noqa: E402, F401
  NOTES_BRIDGE_METADATA,
)
from supekku.scripts.lib.blocks.phase_bridge_schema import (  # noqa: E402, F401
  PHASE_BRIDGE_METADATA,
  _placeholder_renderer,
)
from supekku.scripts.lib.blocks.review_findings_schema import (  # noqa: E402, F401
  REVIEW_FINDINGS_METADATA,
)
from supekku.scripts.lib.blocks.review_index_schema import (  # noqa: E402, F401
  REVIEW_INDEX_METADATA,
)
from supekku.scripts.lib.blocks.sessions_schema import (  # noqa: E402, F401
  WORKFLOW_SESSIONS_METADATA,
)
from supekku.scripts.lib.blocks.state_schema import (  # noqa: E402, F401
  WORKFLOW_STATE_METADATA,
)

# ---------------------------------------------------------------------------
# Schema Registration
# ---------------------------------------------------------------------------

_WORKFLOW_SCHEMAS: list[tuple[str, str, int, str, object]] = [
  (
    "workflow.state",
    STATE_MARKER,
    STATE_VERSION,
    "Current orchestration status and pointers",
    WORKFLOW_STATE_METADATA,
  ),
  (
    "workflow.handoff",
    HANDOFF_MARKER,
    HANDOFF_VERSION,
    "Durable phase-boundary transition payload",
    WORKFLOW_HANDOFF_METADATA,
  ),
  (
    "workflow.review-index",
    REVIEW_INDEX_MARKER,
    REVIEW_INDEX_VERSION,
    "Reviewer bootstrap cache",
    REVIEW_INDEX_METADATA,
  ),
  (
    "workflow.review-findings",
    REVIEW_FINDINGS_MARKER,
    REVIEW_FINDINGS_VERSION,
    "Stable issue ledger across review rounds",
    REVIEW_FINDINGS_METADATA,
  ),
  (
    "workflow.sessions",
    SESSIONS_MARKER,
    SESSIONS_VERSION,
    "Runtime session map (optional, non-authority)",
    WORKFLOW_SESSIONS_METADATA,
  ),
  (
    "workflow.notes-bridge",
    NOTES_BRIDGE_MARKER,
    NOTES_BRIDGE_VERSION,
    "Pointer block in notes.md to workflow files",
    NOTES_BRIDGE_METADATA,
  ),
  (
    "workflow.phase-bridge",
    PHASE_BRIDGE_MARKER,
    PHASE_BRIDGE_VERSION,
    "Phase-close signal in phase sheets",
    PHASE_BRIDGE_METADATA,
  ),
]

for _name, _marker, _ver, _desc, _meta in _WORKFLOW_SCHEMAS:
  register_block_schema(
    _name,
    BlockSchema(
      name=_name,
      marker=_marker,
      version=_ver,
      renderer=_placeholder_renderer,
      description=_desc,
      metadata=_meta,
    ),
  )


__all__ = [
  # Constants
  "ARTIFACT_KIND_VALUES",
  "BOOTSTRAP_STATUS_VALUES",
  "DISPOSITION_AUTHORITY_VALUES",
  "FINDING_DISPOSITION_ACTION_VALUES",
  "FINDING_STATUS_VALUES",
  "HANDOFF_BOUNDARY_VALUES",
  "HANDOFF_MARKER",
  "HANDOFF_SCHEMA",
  "HANDOFF_TRANSITION_STATUS_VALUES",
  "HANDOFF_VERSION",
  "NEXT_ACTIVITY_KIND_VALUES",
  "NOTES_BRIDGE_MARKER",
  "NOTES_BRIDGE_SCHEMA",
  "NOTES_BRIDGE_VERSION",
  "OPEN_ITEM_KIND_VALUES",
  "PHASE_BRIDGE_MARKER",
  "PHASE_BRIDGE_SCHEMA",
  "PHASE_BRIDGE_VERSION",
  "PHASE_STATUS_VALUES",
  "REVIEW_FINDINGS_MARKER",
  "REVIEW_FINDINGS_SCHEMA",
  "REVIEW_FINDINGS_VERSION",
  "REVIEW_INDEX_MARKER",
  "REVIEW_INDEX_SCHEMA",
  "REVIEW_INDEX_VERSION",
  "REVIEW_SESSION_SCOPE_VALUES",
  "REVIEW_STATUS_VALUES",
  "ROLE_VALUES",
  "SESSION_STATUS_VALUES",
  "SESSIONS_MARKER",
  "SESSIONS_SCHEMA",
  "SESSIONS_VERSION",
  "STATE_MARKER",
  "STATE_SCHEMA",
  "STATE_VERSION",
  "VERIFICATION_STATUS_VALUES",
  "WORKFLOW_STATUS_VALUES",
  # Metadata objects (re-exported)
  "NOTES_BRIDGE_METADATA",
  "PHASE_BRIDGE_METADATA",
  "REVIEW_FINDINGS_METADATA",
  "REVIEW_INDEX_METADATA",
  "WORKFLOW_HANDOFF_METADATA",
  "WORKFLOW_SESSIONS_METADATA",
  "WORKFLOW_STATE_METADATA",
]
