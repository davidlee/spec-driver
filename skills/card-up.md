---
name: card-up
description: record newly identified task(s) with context
---
`uv run spec-driver create card` $ARGUMENT

append `--lane doing` if it's for immediate action

read and fill out the newly created template.

ask the user if they want to move it to kanban/doing/
