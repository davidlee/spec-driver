---
id: ISSUE-012
name: Capture coverage artefacts separately from verified_by
created: '2025-11-03'
updated: '2025-11-03'
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# Capture coverage artefacts separately from verified_by

## Problem
- Coverage sync currently pushes VT/VA/VH artefact IDs into `RequirementRecord.verified_by`.
- `WorkspaceValidator` expects `verified_by` to contain audit IDs only, so validation now emits hard errors for every coverage entry.
- Provenance is unclear because we cannot distinguish “verified (audit)” from “verified (delta plan VT-902)”.

## Proposal
- Introduce a dedicated `coverage_evidence` field (or similar) on requirement records to hold VT/VA/VH artefacts with source/timestamp metadata.
- Keep `verified_by` reserved for actual audit IDs so existing validator expectations remain correct.
- Update registry sync, lifecycle projections, and reporting/CLI output to surface both audit verification and coverage evidence separately.
- Add validation warnings if coverage evidence exists without baseline status or if no audit exists after a configured grace period (see PROD-009).

## Notes
- Raised while implementing PROD-008/PROD-009 lifecycle semantics.
- Implementation likely happens in the follow-up delta derived from DE-007.
- Coordinate with validation tooling to ensure new field appears in JSON/CLI outputs.
