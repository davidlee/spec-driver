"""Changes domain - managing change artifacts (deltas, revisions, audits).

This package handles all change artifact functionality:
- registry: ChangeRegistry for managing deltas/revisions/audits
- artifacts: ChangeArtifact model and loading
- creation: Creating new change artifacts
- lifecycle: Status constants and transitions
- completion: Completing/finalizing revisions
- discovery: Discovering revision relationships
- updater: Updating revision metadata
- blocks/: Parsing change-specific markdown blocks
"""

from __future__ import annotations

__all__: list[str] = []
