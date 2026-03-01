---
name: implement
description: implement a well-defined task or implementation plan
---
uv run spec-driver find card $ARGUMENTS

read the card, design doc. (if you haven't already)

read any memories which are relevant

If there's a plan, read it and use /superpowers:execute-plan
- if it's already begun, you don't need /preflight

NOTE: the design doc is canon; the plan is guidance. If they conflict meaningfully: /consult

proceed with implementation.

take /notes after each complete unit of work on the task card; verify with just check
before commit, run just pre-commit

pay attention to doctrine, and to the decisions made in the plan. If you encounter unforeseen obstacles, /consult

if running low on context: stop before you run out of context to update the task card and print a continuation prompt.
