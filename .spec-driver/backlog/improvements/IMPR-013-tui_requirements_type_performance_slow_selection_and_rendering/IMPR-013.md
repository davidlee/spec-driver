---
id: IMPR-013
name: "TUI requirements type performance \u2014 slow selection and rendering"
created: "2026-03-10"
updated: "2026-03-10"
status: idea
kind: improvement
---

# TUI requirements type performance — slow selection and rendering

## Problem

When selecting requirements (e.g. PROD-001.FR-001) in the TUI browser, the app
becomes unresponsive for several seconds.

## Initial profiling

- `ArtifactSnapshot` init: ~400ms (all types)
- `RequirementsRegistry` init: ~104ms, 248 records
- DataTable rendering of 248 rows may compound the delay
- Needs further profiling to isolate the dominant bottleneck (registry init,
  table rebuild, preview load, or combination)

## Observed during

DE-087 Phase 03 VA-087-001 walkthrough.
