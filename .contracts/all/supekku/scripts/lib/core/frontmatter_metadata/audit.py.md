# supekku.scripts.lib.core.frontmatter_metadata.audit

Audit frontmatter metadata for kind: audit artifacts.

This module defines the metadata schema for audit frontmatter,
extending the base metadata with audit-specific fields including
the per-finding disposition contract (DEC-079-001).

## Constants

- `AUDIT_FRONTMATTER_METADATA` - -- Audit frontmatter schema --
- `AUDIT_MODE_CONFORMANCE` - -- Audit mode constants --
- `AUDIT_MODE_DISCOVERY`
- `DISPOSITION_KIND_ALIGNED`
- `DISPOSITION_KIND_FOLLOW_UP_BACKLOG`
- `DISPOSITION_KIND_FOLLOW_UP_DELTA`
- `DISPOSITION_KIND_REVISION`
- `DISPOSITION_KIND_SPEC_PATCH`
- `DISPOSITION_KIND_TOLERATED_DRIFT`
- `DISPOSITION_STATUS_ACCEPTED`
- `DISPOSITION_STATUS_PENDING`
- `DISPOSITION_STATUS_RECONCILED` - -- Disposition constants (DEC-079-001, DEC-079-007) --
- `FINDING_OUTCOME_ALIGNED` - -- Finding outcome constants --
- `FINDING_OUTCOME_DRIFT`
- `FINDING_OUTCOME_RISK`
- `_DISPOSITION_SCHEMA` - -- Disposition sub-schema (DEC-079-001) --
- `_REF_ITEM_SCHEMA` - -- Structured ref sub-schema (shared by refs and drift_refs) --
- `__all__`
