"""Public workflow API for programmatic consumers (e.g., autobahn)."""

from supekku.scripts.lib.workflow.review_io import (
    FindingsNotFoundError,
    FindingsValidationError,
    FindingsVersionError,
    ReviewIndexNotFoundError,
    ReviewIndexValidationError,
)

# Exceptions — existing ones from supekku
from supekku.scripts.lib.workflow.review_state_machine import (
    BootstrapStatus,
    DispositionAuthority,
    FindingDisposition,
    FindingDispositionAction,
    FindingStatus,
    ReviewFinding,
    ReviewStatus,
    ReviewTransitionCommand,
    ReviewTransitionError,
    apply_review_transition,
    can_approve,
    collect_blocking_findings,
    derive_bootstrap_status,
    derive_finding_status,
)
from supekku.scripts.lib.workflow.staleness import (
    StalenessResult,
    evaluate_staleness,
)
from supekku.scripts.lib.workflow.state_io import (
    StateNotFoundError,
    StateValidationError,
    read_state,
)
from supekku.scripts.lib.workflow.state_machine import (
    ClaimError,
    TransitionCommand,
    TransitionError,
    TransitionResult,
    WorkflowState,
    apply_transition,
)

# Composed operations — stubs until DE-124 implementation
# New exceptions created by DE-124 also live in operations.py
from .operations import (
    CompleteResult,
    DeltaNotFoundError,
    DispositionResult,
    DispositionValidationError,
    FindingNotFoundError,
    PrimeAction,
    PrimeResult,
    ReviewApprovalGuardError,
    ReviewSummary,
    TeardownResult,
    complete_review,
    disposition_finding,
    prime_review,
    resolve_delta_dir,
    summarize_review,
    teardown_review,
)

__all__ = [
    # --- Operations ---
    "resolve_delta_dir",
    "prime_review",
    "complete_review",
    "disposition_finding",
    "teardown_review",
    "summarize_review",
    # --- Operation result types ---
    "PrimeAction",
    "PrimeResult",
    "CompleteResult",
    "DispositionResult",
    "TeardownResult",
    "ReviewSummary",
    # --- Workflow state machine ---
    "WorkflowState",
    "TransitionCommand",
    "TransitionResult",
    "apply_transition",

    # --- Review enums ---
    "BootstrapStatus",
    "ReviewStatus",
    "FindingStatus",
    "FindingDispositionAction",
    "DispositionAuthority",
    "ReviewTransitionCommand",

    # --- Review models ---
    "FindingDisposition",
    "ReviewFinding",

    # --- Review state machine functions ---
    "apply_review_transition",
    "can_approve",
    "collect_blocking_findings",
    "derive_finding_status",
    "derive_bootstrap_status",

    # --- State I/O ---
    "read_state",

    # --- Staleness ---
    "StalenessResult",
    "evaluate_staleness",

    # --- Exceptions ---
    "DeltaNotFoundError",
    "ReviewApprovalGuardError",
    "FindingNotFoundError",
    "DispositionValidationError",
    "ReviewTransitionError",
    "TransitionError",
    "ClaimError",
    "StateNotFoundError",
    "StateValidationError",
    "FindingsNotFoundError",
    "FindingsValidationError",
    "FindingsVersionError",
    "ReviewIndexNotFoundError",
    "ReviewIndexValidationError",
]
