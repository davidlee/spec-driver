"""Metadata definitions for workflow orchestration schemas.

Defines BlockMetadata for the 5 workflow artifact schemas and 2 bridge
block schemas from DR-102 §3 and §7.  Registration at module level
ensures schemas appear in ``spec-driver list schemas``.

Design authority: DR-102 (DE-102).
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
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
# Helper: common sub-structures
# ---------------------------------------------------------------------------


def _artifact_block(*, required: bool = True) -> FieldMetadata:
  """Common artifact identification block."""
  return FieldMetadata(
    type="object",
    required=required,
    description="Artifact identification",
    properties={
      "id": FieldMetadata(
        type="string",
        required=True,
        description="Entity ID (e.g., DE-090)",
      ),
      "kind": FieldMetadata(
        type="enum",
        required=True,
        enum_values=ARTIFACT_KIND_VALUES,
        description="Artifact kind",
      ),
      "path": FieldMetadata(
        type="string",
        required=False,
        description="Relative path to artifact",
      ),
      "notes_path": FieldMetadata(
        type="string",
        required=False,
        description="Relative path to notes file",
      ),
    },
  )


def _timestamps_block(fields: dict[str, FieldMetadata]) -> FieldMetadata:
  """Timestamps object with caller-specified fields."""
  return FieldMetadata(
    type="object",
    required=True,
    description="Timestamps",
    properties=fields,
  )


def _finding_disposition() -> FieldMetadata:
  """Disposition sub-schema for a review finding (DR-109 §3.4)."""
  return FieldMetadata(
    type="object",
    required=False,
    description="Finding disposition record",
    properties={
      "action": FieldMetadata(
        type="enum",
        required=True,
        enum_values=FINDING_DISPOSITION_ACTION_VALUES,
        description="Disposition action",
      ),
      "authority": FieldMetadata(
        type="enum",
        required=True,
        enum_values=DISPOSITION_AUTHORITY_VALUES,
        description="Who made the disposition decision",
      ),
      "actor_id": FieldMetadata(
        type="string",
        required=False,
        description="Specific identity when needed",
      ),
      "rationale": FieldMetadata(
        type="string",
        required=False,
        description="Required for waive, defer",
      ),
      "backlog_ref": FieldMetadata(
        type="string",
        required=False,
        description="Backlog item ref (e.g. ISSUE-045), when action=defer",
      ),
      "resolved_at": FieldMetadata(
        type="string",
        required=False,
        description="Git sha, when action=fix",
      ),
      "superseded_by": FieldMetadata(
        type="string",
        required=False,
        description="Finding ID, when action=supersede",
      ),
      "timestamp": FieldMetadata(
        type="string",
        required=False,
        description="ISO 8601 timestamp",
      ),
    },
  )


def _finding_item() -> FieldMetadata:
  """Single review finding record (DR-109 §3.4)."""
  return FieldMetadata(
    type="object",
    description="Review finding",
    properties={
      "id": FieldMetadata(
        type="string",
        required=True,
        description="Finding ID (e.g., R3-001), unique across all lists",
      ),
      "title": FieldMetadata(
        type="string",
        required=True,
        description="Short title",
      ),
      "summary": FieldMetadata(
        type="string",
        required=False,
        description=(
          "Finding summary (required for open/superseded, "
          "optional for resolved/waived)"
        ),
      ),
      "status": FieldMetadata(
        type="enum",
        required=True,
        enum_values=FINDING_STATUS_VALUES,
        description="Finding status (derived from disposition)",
      ),
      "disposition": _finding_disposition(),
      "files": FieldMetadata(
        type="array",
        required=False,
        description="Related file paths",
        items=FieldMetadata(type="string", description="File path"),
      ),
      "related_invariants": FieldMetadata(
        type="array",
        required=False,
        description="Related invariant IDs",
        items=FieldMetadata(type="string", description="Invariant ID"),
      ),
      "resolution_summary": FieldMetadata(
        type="string",
        required=False,
        description="How finding was resolved",
      ),
    },
  )


def _findings_list(*, required: bool = False) -> FieldMetadata:
  """List of finding records."""
  return FieldMetadata(
    type="array",
    required=required,
    description="List of review findings",
    items=_finding_item(),
  )


# ---------------------------------------------------------------------------
# 3.1  Workflow State — supekku:workflow.state@v1
# ---------------------------------------------------------------------------

WORKFLOW_STATE_METADATA = BlockMetadata(
  version=STATE_VERSION,
  schema_id=STATE_SCHEMA,
  description="Current orchestration status and pointers for a workflow artifact",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=STATE_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{STATE_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=STATE_VERSION,
      required=True,
      description=f"Schema version (must be {STATE_VERSION})",
    ),
    "artifact": _artifact_block(),
    "plan": FieldMetadata(
      type="object",
      required=False,
      description="Plan reference (absent if no IP exists)",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Plan ID (e.g., IP-090)",
        ),
        "path": FieldMetadata(
          type="string",
          required=False,
          description="Relative path to plan file",
        ),
      },
    ),
    "phase": FieldMetadata(
      type="object",
      required=True,
      description="Current phase",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Phase ID (e.g., IP-090.PHASE-05)",
        ),
        "path": FieldMetadata(
          type="string",
          required=False,
          description="Relative path to phase sheet",
        ),
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=PHASE_STATUS_VALUES,
          description="Phase status",
        ),
      },
    ),
    "workflow": FieldMetadata(
      type="object",
      required=True,
      description="Workflow orchestration state",
      properties={
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=WORKFLOW_STATUS_VALUES,
          description="Current workflow status",
        ),
        "active_role": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ROLE_VALUES,
          description="Currently active role",
        ),
        "next_role": FieldMetadata(
          type="enum",
          required=False,
          enum_values=ROLE_VALUES,
          description="Expected next role",
        ),
        "handoff_boundary": FieldMetadata(
          type="enum",
          required=False,
          enum_values=HANDOFF_BOUNDARY_VALUES,
          description="Default trigger boundary",
        ),
        "claimed_by": FieldMetadata(
          type="string",
          required=False,
          description="Agent/operator identity holding the claim (null when unclaimed)",
        ),
        "previous_state": FieldMetadata(
          type="enum",
          required=False,
          enum_values=WORKFLOW_STATUS_VALUES,
          description="State before blocking (set by block, cleared by unblock)",
        ),
      },
    ),
    "pointers": FieldMetadata(
      type="object",
      required=False,
      description="Paths to related workflow files",
      properties={
        "current_handoff": FieldMetadata(
          type="string",
          required=False,
          description="Path to handoff file",
        ),
        "review_index": FieldMetadata(
          type="string",
          required=False,
          description="Path to review index",
        ),
        "review_findings": FieldMetadata(
          type="string",
          required=False,
          description="Path to review findings",
        ),
        "sessions": FieldMetadata(
          type="string",
          required=False,
          description="Path to sessions file",
        ),
        "review_bootstrap": FieldMetadata(
          type="string",
          required=False,
          description="Path to review bootstrap doc",
        ),
      },
    ),
    "timestamps": _timestamps_block(
      {
        "created": FieldMetadata(
          type="string",
          required=True,
          description="Creation timestamp (ISO 8601)",
        ),
        "updated": FieldMetadata(
          type="string",
          required=True,
          description="Last update timestamp (ISO 8601)",
        ),
      }
    ),
  },
  examples=[
    {
      "schema": STATE_SCHEMA,
      "version": STATE_VERSION,
      "artifact": {
        "id": "DE-090",
        "kind": "delta",
        "path": ".spec-driver/deltas/DE-090-example",
        "notes_path": ".spec-driver/deltas/DE-090-example/notes.md",
      },
      "plan": {
        "id": "IP-090",
        "path": ".spec-driver/deltas/DE-090-example/IP-090.md",
      },
      "phase": {
        "id": "IP-090.PHASE-01",
        "status": "in_progress",
        "path": ".spec-driver/deltas/DE-090-example/phases/phase-01.md",
      },
      "workflow": {
        "status": "implementing",
        "active_role": "implementer",
        "handoff_boundary": "phase",
      },
      "timestamps": {
        "created": "2026-03-20T10:00:00+00:00",
        "updated": "2026-03-20T12:30:00+00:00",
      },
    }
  ],
)


# ---------------------------------------------------------------------------
# 3.2  Handoff — supekku:workflow.handoff@v1
# ---------------------------------------------------------------------------

WORKFLOW_HANDOFF_METADATA = BlockMetadata(
  version=HANDOFF_VERSION,
  schema_id=HANDOFF_SCHEMA,
  description=("Durable phase-boundary transition payload for structured handoffs"),
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=HANDOFF_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{HANDOFF_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=HANDOFF_VERSION,
      required=True,
      description=f"Schema version (must be {HANDOFF_VERSION})",
    ),
    "artifact": FieldMetadata(
      type="object",
      required=True,
      description="Artifact identification",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Entity ID",
        ),
        "kind": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ARTIFACT_KIND_VALUES,
          description="Artifact kind",
        ),
      },
    ),
    "transition": FieldMetadata(
      type="object",
      required=True,
      description="Role transition details",
      properties={
        "from_role": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ROLE_VALUES,
          description="Originating role",
        ),
        "to_role": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ROLE_VALUES,
          description="Target role",
        ),
        "boundary": FieldMetadata(
          type="enum",
          required=False,
          enum_values=HANDOFF_BOUNDARY_VALUES,
          description="Transition boundary type",
        ),
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=HANDOFF_TRANSITION_STATUS_VALUES,
          description="Transition status",
        ),
      },
    ),
    "phase": FieldMetadata(
      type="object",
      required=True,
      description="Phase context for handoff",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Phase ID",
        ),
        "status": FieldMetadata(
          type="enum",
          required=False,
          enum_values=PHASE_STATUS_VALUES,
          description="Phase status at handoff time",
        ),
      },
    ),
    "required_reading": FieldMetadata(
      type="array",
      required=True,
      min_items=1,
      description="Documents the receiving role must read",
      items=FieldMetadata(type="string", description="Document path"),
    ),
    "related_documents": FieldMetadata(
      type="array",
      required=False,
      description="Additional related documents",
      items=FieldMetadata(type="string", description="Document path"),
    ),
    "key_files": FieldMetadata(
      type="array",
      required=False,
      description="Key source files relevant to handoff",
      items=FieldMetadata(type="string", description="File path"),
    ),
    "verification": FieldMetadata(
      type="object",
      required=False,
      description="Verification state at handoff time",
      properties={
        "commands": FieldMetadata(
          type="array",
          required=False,
          description="Verification commands",
          items=FieldMetadata(type="string", description="Command"),
        ),
        "summary": FieldMetadata(
          type="string",
          required=False,
          description="Verification summary",
        ),
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=VERIFICATION_STATUS_VALUES,
          description="Overall verification status",
        ),
      },
    ),
    "git": FieldMetadata(
      type="object",
      required=False,
      description="Git state at handoff time",
      properties={
        "head": FieldMetadata(
          type="string",
          required=True,
          description="HEAD commit (short hash)",
        ),
        "branch": FieldMetadata(
          type="string",
          required=False,
          description="Current branch",
        ),
        "worktree": FieldMetadata(
          type="object",
          required=False,
          description="Worktree state",
          properties={
            "has_uncommitted_changes": FieldMetadata(
              type="bool",
              required=True,
              description="Whether worktree has uncommitted changes",
            ),
            "has_staged_changes": FieldMetadata(
              type="bool",
              required=True,
              description="Whether worktree has staged changes",
            ),
          },
        ),
      },
    ),
    "open_items": FieldMetadata(
      type="array",
      required=False,
      description="Open items (next steps, blockers, questions, risks)",
      items=FieldMetadata(
        type="object",
        description="Open item",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Item ID (unique within handoff)",
          ),
          "kind": FieldMetadata(
            type="enum",
            required=True,
            enum_values=OPEN_ITEM_KIND_VALUES,
            description="Item kind",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            description="Item summary",
          ),
          "blocking": FieldMetadata(
            type="bool",
            required=True,
            description="Whether this item blocks progress",
          ),
        },
      ),
    ),
    "design_tensions": FieldMetadata(
      type="array",
      required=False,
      description="Unresolved design tensions",
      items=FieldMetadata(type="string", description="Tension description"),
    ),
    "unresolved_assumptions": FieldMetadata(
      type="array",
      required=False,
      description="Unresolved assumptions",
      items=FieldMetadata(type="string", description="Assumption"),
    ),
    "decisions_to_preserve": FieldMetadata(
      type="array",
      required=False,
      description="Decisions the next role should preserve",
      items=FieldMetadata(type="string", description="Decision"),
    ),
    "next_activity": FieldMetadata(
      type="object",
      required=True,
      description="What the receiving role should do next",
      properties={
        "kind": FieldMetadata(
          type="enum",
          required=True,
          enum_values=NEXT_ACTIVITY_KIND_VALUES,
          description="Next activity kind",
        ),
        "summary": FieldMetadata(
          type="string",
          required=False,
          description="Activity summary",
        ),
      },
    ),
    "timestamps": _timestamps_block(
      {
        "emitted_at": FieldMetadata(
          type="string",
          required=True,
          description="Handoff emission timestamp (ISO 8601)",
        ),
      }
    ),
  },
  examples=[
    {
      "schema": HANDOFF_SCHEMA,
      "version": HANDOFF_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "transition": {
        "from_role": "implementer",
        "to_role": "reviewer",
        "boundary": "phase",
        "status": "pending",
      },
      "phase": {"id": "IP-090.PHASE-01", "status": "complete"},
      "required_reading": [
        ".spec-driver/deltas/DE-090-example/notes.md",
        ".spec-driver/deltas/DE-090-example/phases/phase-01.md",
      ],
      "key_files": ["supekku/cli/show.py"],
      "verification": {
        "status": "pass",
        "commands": ["uv run python -m pytest"],
        "summary": "All tests pass",
      },
      "git": {
        "head": "abc1234",
        "branch": "main",
        "worktree": {
          "has_uncommitted_changes": False,
          "has_staged_changes": False,
        },
      },
      "open_items": [
        {
          "id": "OI-001",
          "kind": "next_step",
          "summary": "Review phase 01 output",
          "blocking": False,
        },
      ],
      "next_activity": {"kind": "review", "summary": "Review phase 01 changes"},
      "timestamps": {"emitted_at": "2026-03-20T14:00:00+00:00"},
    }
  ],
)


# ---------------------------------------------------------------------------
# 3.3  Review Index — supekku:workflow.review-index@v1
# ---------------------------------------------------------------------------

REVIEW_INDEX_METADATA = BlockMetadata(
  version=REVIEW_INDEX_VERSION,
  schema_id=REVIEW_INDEX_SCHEMA,
  description="Reviewer bootstrap cache for amortizing review setup cost",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=REVIEW_INDEX_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{REVIEW_INDEX_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=REVIEW_INDEX_VERSION,
      required=True,
      description=f"Schema version (must be {REVIEW_INDEX_VERSION})",
    ),
    "artifact": FieldMetadata(
      type="object",
      required=True,
      description="Artifact identification",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Entity ID",
        ),
        "kind": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ARTIFACT_KIND_VALUES,
          description="Artifact kind",
        ),
      },
    ),
    "review": FieldMetadata(
      type="object",
      required=True,
      description="Review session state",
      properties={
        "session_scope": FieldMetadata(
          type="enum",
          required=False,
          enum_values=REVIEW_SESSION_SCOPE_VALUES,
          description="Review session scope",
        ),
        "bootstrap_status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=BOOTSTRAP_STATUS_VALUES,
          description="Bootstrap cache status",
        ),
        "last_bootstrapped_at": FieldMetadata(
          type="string",
          required=True,
          description="Last bootstrap timestamp (ISO 8601)",
        ),
        "judgment_status": FieldMetadata(
          type="enum",
          required=False,
          enum_values=REVIEW_STATUS_VALUES,
          description="Review judgment status (DR-109 §3.3)",
        ),
        "source_handoff": FieldMetadata(
          type="string",
          required=False,
          description="Path to source handoff file",
        ),
      },
    ),
    "domain_map": FieldMetadata(
      type="array",
      required=True,
      min_items=1,
      description="Domain areas the reviewer has learned",
      items=FieldMetadata(
        type="object",
        description="Domain area entry",
        properties={
          "area": FieldMetadata(
            type="string",
            required=True,
            description="Area name (unique within domain_map)",
          ),
          "purpose": FieldMetadata(
            type="string",
            required=True,
            description="Area purpose",
          ),
          "files": FieldMetadata(
            type="array",
            required=True,
            min_items=1,
            description="Files in this area",
            items=FieldMetadata(type="string", description="File path"),
          ),
        },
      ),
    ),
    "invariants": FieldMetadata(
      type="array",
      required=False,
      description="Known invariants to protect during review",
      items=FieldMetadata(
        type="object",
        description="Invariant",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Invariant ID (unique within invariants)",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            description="Invariant summary",
          ),
        },
      ),
    ),
    "risk_areas": FieldMetadata(
      type="array",
      required=False,
      description="Identified risk areas",
      items=FieldMetadata(
        type="object",
        description="Risk area",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Risk area ID (unique within risk_areas)",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            description="Risk description",
          ),
          "files": FieldMetadata(
            type="array",
            required=False,
            description="Related files",
            items=FieldMetadata(type="string", description="File path"),
          ),
        },
      ),
    ),
    "review_focus": FieldMetadata(
      type="array",
      required=False,
      description="Areas to focus review effort",
      items=FieldMetadata(type="string", description="Focus area"),
    ),
    "known_decisions": FieldMetadata(
      type="array",
      required=False,
      description="Decisions the reviewer should be aware of",
      items=FieldMetadata(
        type="object",
        description="Known decision",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Decision ID (unique within known_decisions)",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            description="Decision summary",
          ),
        },
      ),
    ),
    "staleness": FieldMetadata(
      type="object",
      required=True,
      description="Cache staleness tracking",
      properties={
        "cache_key": FieldMetadata(
          type="object",
          required=True,
          description="Cache key for staleness detection",
          properties={
            "phase_id": FieldMetadata(
              type="string",
              required=True,
              description="Phase ID at cache time",
            ),
            "head": FieldMetadata(
              type="string",
              required=True,
              description="Git HEAD at cache time",
            ),
          },
        ),
        "invalidation_triggers": FieldMetadata(
          type="array",
          required=False,
          description="Events that would invalidate the cache",
          items=FieldMetadata(type="string", description="Trigger description"),
        ),
      },
    ),
  },
  examples=[
    {
      "schema": REVIEW_INDEX_SCHEMA,
      "version": REVIEW_INDEX_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "review": {
        "bootstrap_status": "warm",
        "last_bootstrapped_at": "2026-03-20T14:00:00+00:00",
        "judgment_status": "pending",
        "source_handoff": "workflow/handoff.current.yaml",
      },
      "domain_map": [
        {
          "area": "CLI show commands",
          "purpose": "Render artifact details to terminal",
          "files": ["supekku/cli/show.py", "supekku/cli/schema.py"],
        },
      ],
      "invariants": [
        {
          "id": "INV-001",
          "summary": "show schema output must be valid JSON Schema Draft 2020-12",
        },
      ],
      "risk_areas": [
        {
          "id": "RA-001",
          "summary": "Hardcoded metadata lookup may miss new block types",
          "files": ["supekku/cli/schema.py"],
        },
      ],
      "review_focus": ["Schema completeness", "Example validity"],
      "known_decisions": [
        {"id": "DEC-110-001", "summary": "Attach metadata to BlockSchema"},
      ],
      "staleness": {
        "cache_key": {"phase_id": "IP-090.PHASE-01", "head": "abc1234"},
        "invalidation_triggers": ["New phase started", "DR revised"],
      },
    }
  ],
)


# ---------------------------------------------------------------------------
# 3.4  Review Findings — supekku:workflow.review-findings@v2
# ---------------------------------------------------------------------------


def _round_entry() -> FieldMetadata:
  """Single round entry in the accumulative rounds array (DR-109 §3.5)."""
  return FieldMetadata(
    type="object",
    description="Review round entry",
    properties={
      "round": FieldMetadata(
        type="int",
        required=True,
        description="Round number (monotonically increasing)",
      ),
      "status": FieldMetadata(
        type="enum",
        required=True,
        enum_values=REVIEW_STATUS_VALUES,
        description="Round outcome status",
      ),
      "reviewer_role": FieldMetadata(
        type="enum",
        required=False,
        enum_values=ROLE_VALUES,
        description="Role performing the review",
      ),
      "completed_at": FieldMetadata(
        type="string",
        required=False,
        description="Round completion timestamp (ISO 8601)",
      ),
      "summary": FieldMetadata(
        type="string",
        required=False,
        description="Round summary (free-text)",
      ),
      # session: opaque dict, autobahn-owned (DR-109 §3.6).
      # Not validated by schema — passes through unvalidated.
      "blocking": _findings_list(),
      "non_blocking": _findings_list(),
    },
  )


REVIEW_FINDINGS_METADATA = BlockMetadata(
  version=REVIEW_FINDINGS_VERSION,
  schema_id=REVIEW_FINDINGS_SCHEMA,
  description="Accumulative issue ledger across review rounds (v2)",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=REVIEW_FINDINGS_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{REVIEW_FINDINGS_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=REVIEW_FINDINGS_VERSION,
      required=True,
      description=f"Schema version (must be {REVIEW_FINDINGS_VERSION})",
    ),
    "artifact": FieldMetadata(
      type="object",
      required=True,
      description="Artifact identification",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Entity ID",
        ),
        "kind": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ARTIFACT_KIND_VALUES,
          description="Artifact kind",
        ),
      },
    ),
    "review": FieldMetadata(
      type="object",
      required=True,
      description="Review state",
      properties={
        "current_round": FieldMetadata(
          type="int",
          required=True,
          description="Latest round number",
        ),
      },
    ),
    "rounds": FieldMetadata(
      type="array",
      required=True,
      min_items=1,
      description="Accumulative round entries (DR-109 §3.5)",
      items=_round_entry(),
    ),
  },
  examples=[
    {
      "schema": REVIEW_FINDINGS_SCHEMA,
      "version": REVIEW_FINDINGS_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "review": {"current_round": 1},
      "rounds": [
        {
          "round": 1,
          "status": "changes_requested",
          "reviewer_role": "reviewer",
          "completed_at": "2026-03-20T16:00:00+00:00",
          "blocking": [
            {
              "id": "R1-001",
              "title": "Missing error handling in schema lookup",
              "summary": "Fallback path does not log the block type that failed.",
              "status": "open",
              "files": ["supekku/cli/schema.py"],
            },
          ],
          "non_blocking": [
            {
              "id": "R1-002",
              "title": "Typo in description field",
              "summary": "Minor typo.",
              "status": "resolved",
              "disposition": {
                "action": "fix",
                "authority": "author",
                "resolved_at": "def5678",
                "timestamp": "2026-03-20T17:00:00+00:00",
              },
            },
          ],
        },
      ],
    }
  ],
)


# ---------------------------------------------------------------------------
# 3.5  Sessions — supekku:workflow.sessions@v1
# ---------------------------------------------------------------------------

# Session entry is a map of role name → session record, which we model as
# an object with dynamic keys.  FieldMetadata doesn't support dynamic keys
# natively, so we validate the top-level structure and defer per-entry
# validation to command-level code.  The metadata captures the schema/version
# and artifact block; the sessions map is validated as a required object.

_SESSION_ENTRY = FieldMetadata(
  type="object",
  description="Session entry for a role",
  properties={
    "session_name": FieldMetadata(
      type="string",
      required=True,
      description="Session name (string or null)",
    ),
    "sandbox": FieldMetadata(
      type="string",
      required=False,
      description="Sandbox identifier",
    ),
    "status": FieldMetadata(
      type="enum",
      required=True,
      enum_values=SESSION_STATUS_VALUES,
      description="Session status",
    ),
    "last_seen": FieldMetadata(
      type="string",
      required=True,
      description="Last seen timestamp (ISO 8601 or null)",
    ),
  },
)

WORKFLOW_SESSIONS_METADATA = BlockMetadata(
  version=SESSIONS_VERSION,
  schema_id=SESSIONS_SCHEMA,
  description="Runtime mapping of roles to sessions (optional, non-authority)",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=SESSIONS_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{SESSIONS_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=SESSIONS_VERSION,
      required=True,
      description=f"Schema version (must be {SESSIONS_VERSION})",
    ),
    "artifact": FieldMetadata(
      type="object",
      required=True,
      description="Artifact identification",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Entity ID",
        ),
        "kind": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ARTIFACT_KIND_VALUES,
          description="Artifact kind",
        ),
      },
    ),
    # Sessions is a map of role_name → session_entry with dynamic keys.
    # FieldMetadata requires non-empty properties for object type, so we
    # model it as a sentinel object with a single documented example key.
    # Command-level validation handles per-entry checks.
    "sessions": FieldMetadata(
      type="object",
      required=True,
      description=("Map of role name to session entry (at least one entry required)"),
      properties={
        # Sentinel — FieldMetadata requires non-empty properties
        # for object type.  Real entries use dynamic role-name keys;
        # command-level code validates per-entry shape.
        "_entry_shape": _SESSION_ENTRY,
      },
    ),
  },
  examples=[
    {
      "schema": SESSIONS_SCHEMA,
      "version": SESSIONS_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "sessions": {
        "implementer": {
          "session_name": "pi-session-abc",
          "status": "active",
          "last_seen": "2026-03-20T14:30:00+00:00",
        },
        "reviewer": {
          "session_name": None,
          "status": "absent",
          "last_seen": None,
        },
      },
    }
  ],
)


# ---------------------------------------------------------------------------
# 7.1  Notes Bridge — supekku:workflow.notes-bridge@v1
# ---------------------------------------------------------------------------

NOTES_BRIDGE_METADATA = BlockMetadata(
  version=NOTES_BRIDGE_VERSION,
  schema_id=NOTES_BRIDGE_SCHEMA,
  description="Pointer block in notes.md linking to workflow control plane files",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=NOTES_BRIDGE_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{NOTES_BRIDGE_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=NOTES_BRIDGE_VERSION,
      required=True,
      description=f"Schema version (must be {NOTES_BRIDGE_VERSION})",
    ),
    "artifact": FieldMetadata(
      type="string",
      required=True,
      description="Entity ID (e.g., DE-090)",
    ),
    "workflow_state": FieldMetadata(
      type="string",
      required=True,
      description="Relative path to workflow/state.yaml",
    ),
    "current_handoff": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to handoff file",
    ),
    "review_index": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to review index",
    ),
    "review_findings": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to review findings",
    ),
    "review_bootstrap": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to review bootstrap doc",
    ),
  },
  examples=[
    {
      "schema": NOTES_BRIDGE_SCHEMA,
      "version": NOTES_BRIDGE_VERSION,
      "artifact": "DE-090",
      "workflow_state": "workflow/state.yaml",
      "current_handoff": "workflow/handoff.current.yaml",
      "review_index": "workflow/review-index.yaml",
    }
  ],
)


# ---------------------------------------------------------------------------
# 7.2  Phase Bridge — supekku:workflow.phase-bridge@v1
# ---------------------------------------------------------------------------

PHASE_BRIDGE_METADATA = BlockMetadata(
  version=PHASE_BRIDGE_VERSION,
  schema_id=PHASE_BRIDGE_SCHEMA,
  description="Phase-close signal block in phase sheets for handoff emission",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=PHASE_BRIDGE_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{PHASE_BRIDGE_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=PHASE_BRIDGE_VERSION,
      required=True,
      description=f"Schema version (must be {PHASE_BRIDGE_VERSION})",
    ),
    "phase": FieldMetadata(
      type="string",
      required=True,
      description="Phase ID (e.g., IP-090.PHASE-05)",
    ),
    "status": FieldMetadata(
      type="enum",
      required=True,
      enum_values=PHASE_STATUS_VALUES,
      description="Phase status",
    ),
    "handoff_ready": FieldMetadata(
      type="bool",
      required=True,
      description="Whether phase completion should trigger handoff emission",
    ),
    "review_required": FieldMetadata(
      type="bool",
      required=False,
      description="Whether handoff should target reviewer role (defaults to false)",
    ),
    "current_handoff": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to current handoff file",
    ),
  },
  examples=[
    {
      "schema": PHASE_BRIDGE_SCHEMA,
      "version": PHASE_BRIDGE_VERSION,
      "phase": "IP-090.PHASE-01",
      "status": "complete",
      "handoff_ready": True,
      "review_required": False,
    }
  ],
)


# ---------------------------------------------------------------------------
# Schema Registration
# ---------------------------------------------------------------------------

# Placeholder renderers — real renderers will be added in later phases
# when CLI commands need to emit these blocks.


def _placeholder_renderer(**kwargs: object) -> str:  # noqa: ARG001
  """Placeholder renderer for workflow schemas (real renderers in Phase 02+)."""
  return ""


_WORKFLOW_SCHEMAS: list[tuple[str, str, int, str, BlockMetadata]] = [
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
  # Metadata objects
  "NOTES_BRIDGE_METADATA",
  "PHASE_BRIDGE_METADATA",
  "REVIEW_FINDINGS_METADATA",
  "REVIEW_INDEX_METADATA",
  "WORKFLOW_HANDOFF_METADATA",
  "WORKFLOW_SESSIONS_METADATA",
  "WORKFLOW_STATE_METADATA",
]
