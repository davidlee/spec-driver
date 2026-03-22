# supekku.scripts.lib.workflow.review_state_machine

Review lifecycle state machine with explicit transitions and guards.

Implements two sub-lifecycles from DR-109:

- Bootstrap: derived status with validity invariants (§3.2)
- Judgment: command-driven state machine (§3.3)

Plus finding disposition model (§3.4) and approval guard (§3.3).

Design authority: DR-109.

## Constants

- `_BS` - ---------------------------------------------------------------------------
- `_RC`
- `_RS` - ---------------------------------------------------------------------------

## Functions

- `_check_disposition(finding_id, d) -> list[str]`: Validate a single finding's disposition for approval.
- `_derive_from_index(index) -> BootstrapStatus`: Derive status from an existing review-index.

Mirrors the staleness evaluation logic from staleness.py but
returns a BootstrapStatus rather than StalenessResult.

- `_extract_cached_files(index) -> set[str]`: Extract file paths from cached domain_map.
- `apply_review_transition(current, command) -> ReviewStatus`: Apply a judgment transition command.

Returns the new ReviewStatus.

Raises:
ReviewTransitionError: If the transition is invalid. - ---------------------------------------------------------------------------

- `can_approve(blocking_findings) -> tuple[Tuple[bool, list[str]]]`: Check whether approval is permitted.

Evaluates disposition constraints on all blocking findings.
The guard checks disposition, not status — status is derived from
disposition and checking both creates short-circuit bugs.

Returns (allowed, reasons) where reasons lists blocking violations. - ---------------------------------------------------------------------------

- `collect_blocking_findings(rounds) -> list[ReviewFinding]`: Collect all blocking findings from all rounds.

Finding IDs are round-scoped (R{round}-{seq}) and unique across
rounds — no deduplication is needed. Dispositions are applied
in-place within the originating round, so each finding's current
disposition state is always in its originating entry. - ---------------------------------------------------------------------------

- `derive_bootstrap_status(index) -> BootstrapStatus`: Derive current bootstrap status from observable context.

Deterministic — no I/O, no mutation. The only code that writes
bootstrap_status is review prime, which always writes WARM.

When previous_status is provided, raises AssertionError if the
derived transition is illegal (indicates a derivation logic bug). - ---------------------------------------------------------------------------

- `derive_finding_status(disposition) -> FindingStatus`: Derive finding status from disposition action.

Status is a convenience projection — disposition is authoritative.

## Classes

### BootstrapStatus

Bootstrap status values (DR-109 §3.2).

Derived, not command-driven. The stored value is a snapshot —
true status comes from observable context.

_---------------------------------------------------------------------------_

**Inherits from:** StrEnum

### DispositionAuthority

Who made the disposition decision (DR-109 §3.4).

**Inherits from:** StrEnum

### FindingDisposition

Structured disposition record for a review finding.

_---------------------------------------------------------------------------_

**Inherits from:** BaseModel

### FindingDispositionAction

Actions that can be taken on a finding (DR-109 §3.4).

**Inherits from:** StrEnum

### FindingStatus

Finding status — derived from disposition action (DR-109 §3.4).

**Inherits from:** StrEnum

### ReviewFinding

A single review finding with optional disposition.

**Inherits from:** BaseModel

### ReviewStatus

Judgment lifecycle states (DR-109 §3.3).

**Inherits from:** StrEnum

### ReviewTransitionCommand

Judgment transition commands (DR-109 §3.3).

**Inherits from:** StrEnum

### ReviewTransitionError

Raised when a review judgment transition is invalid.

**Inherits from:** Exception

#### Methods

- `__init__(self, current, command, message) -> None`
