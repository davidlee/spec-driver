"""Public workflow API for programmatic consumers (e.g., autobahn)."""

from supekku.scripts.lib.workflow.state_machine import (
    WorkflowState,
    TransitionCommand,
    TransitionResult,
    apply_transition,
)

from supekku.scripts.lib.workflow.review_state_machine import (
    BootstrapStatus,
    ReviewStatus,
    FindingStatus,
    FindingDispositionAction,
    DispositionAuthority,
    FindingDisposition,
    ReviewFinding,
    apply_review_transition,
    can_approve,
    derive_finding_status,
    derive_bootstrap_status,
)

from supekku.scripts.lib.workflow.review_io import (
    collect_blocking_findings,
)

from supekku.scripts.lib.workflow.state_io import (
    read_state,
)

from supekku.scripts.lib.workflow.staleness import (
    StalenessResult,
    evaluate_staleness,
)

# Exception types that represent the API contract boundaries
from supekku.scripts.lib.workflow.review_state_machine import (
    ReviewTransitionError,
    ReviewApprovalGuardError,
)

from supekku.scripts.lib.workflow.state_machine import (
    TransitionError,
    ClaimError,
)

from supekku.scripts.lib.workflow.review_io import (
    FindingsNotFoundError,
    FindingsValidationError,
    FindingsVersionError,
    ReviewIndexNotFoundError,
    ReviewIndexValidationError,
)

from supekku.scripts.lib.workflow.state_io import (
    StateNotFoundError,
    StateValidationError,
)

# Placeholder: Composed operations (prime_review, complete_review, summarize_review) 
# will be re-exported here once extracted from supekku/cli/workflow.py as part of DE-124.

__all__ = [
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
    "ReviewTransitionError",
    "ReviewApprovalGuardError",
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
