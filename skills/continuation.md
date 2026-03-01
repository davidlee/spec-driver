---
name: continuation
description: write a thorough continuation prompt for the next agent
---

first ensure /notes on the task card are up to date.

if there is already a 'New Agent Instructions' section, read and update it.
otherwise, create one, including:
- the task card code
- any required reading (with paths): design doc, plans, etc.
- any key files or memories / recommendations to build necessary context from a cold start
- any relevant doctrines
- any incomplete work or loose ends
- any advice / relevant knowledge for the next task(s)

print the path to the task card.

identify the next logical activity and instruct the agent to:
- if it is to design document:
   - /brainstorming
- if it is to execute an implementation plan:
   - /implement
- otherwise:
   - /preflight

