---
name: implement
description: implement a well-defined task or implementation plan
---
`spec-driver find card $ARGUMENTS`

Read the card, design doc. (if you haven't already)

read any memories which are relevant

If there's an implementation plan, read it and
- if it's already begun, you don't need /preflight

NOTE: the design doc is canon; the plan is guidance. If they conflict meaningfully: /consult

Workflow alignment reminders:
- Default to delta-first execution flow for implementation work.
- Treat revision-first as a concession path, not the default.
- Treat ceremony mode as guidance posture; do not assume runtime enforcement from ceremony alone.
- For delta close-out, follow `uv run spec-driver complete delta` prerequisites (especially coverage readiness).

proceed with implementation.

take /notes after each complete unit of work on the task card

pay attention to doctrine, and to the decisions made in the plan. If you encounter unforeseen obstacles, /consult

if running low on context: stop before you run out of context for /continuation
