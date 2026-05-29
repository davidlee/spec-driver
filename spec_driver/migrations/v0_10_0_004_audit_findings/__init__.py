"""Migration step v0_10_0_004_audit_findings — DR-141 §6 placement for audit kind.

Forward-only sweep that:
- Emits supekku:audit.findings@v1 block from FM findings array.
- Cuts FM findings key after block insertion.
- Writes drift entry for invalid outcome values (e.g. 'pass').

Per DEC-138-12 this package may not import from supekku.* or non-migrations spec_driver.
"""

from .migration import AuditFindingsStep

step = AuditFindingsStep()

__all__ = ["AuditFindingsStep", "step"]
