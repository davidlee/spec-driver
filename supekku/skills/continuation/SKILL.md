---
name: continuation
description: Write a prompt to help the next agent continue effectively.
---

Ensure /notes on the task card are up to date.

If there is already a 'New Agent Instructions' section, read and update it.
otherwise, create one, including:
- task card code
- required reading
- related documents
- key files
- relevant memories
- relevant doctrines
- any important user instructions or decisions
- any incomplete work or loose ends
- other advice or knowledge applicable to the next task(s)
- file paths for any files / documents referenced.

Then, print the path to the task card.

Identify the next logical activity and print instructions for the next agent.

Usually this means a simple instruction to invoke the appropriate skill:
- write a design document:
   - /brainstorming
- execute an implementation plan:
   - /implement
- otherwise:
   - /preflight
