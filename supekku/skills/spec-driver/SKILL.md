---
name: spec-driver
description: Use this skill any time work involves creating, listing, finding, showing, editing, completing, syncing, or otherwise interacting with spec-driver entities via the CLI. Trigger it whenever a user asks to create or inspect ADRs, specs, deltas, revisions, audits, memories, policies, standards, backlog items, or related workflow artefacts, especially if there is any temptation to guess IDs, paths, or command shapes.
---

# Spec Driver

Use `spec-driver ...`.

## Defaults

- Never guess the next entity ID. Use `create` and let spec-driver allocate it.
- Prefer direct CLI inspection over browsing generated files when the user asks what exists or what command to run.
- Keep usage compact; reach for `--help` only when the needed subcommand shape is still unclear.
- When the task is about how spec-driver should be used, not just which command
  to type, prefer the relevant memory over ad hoc explanation.

## Memory routing

- Start with `spec-driver show memory mem.signpost.spec-driver.overview --raw`
  for the compact orientation.
- Use `spec-driver show memory mem.pattern.spec-driver.core-loop --raw`
  when the question is about workflow order, canonical path, or what comes next.
- Use the matching concept memory for task-focused guidance:
  `mem.concept.spec-driver.delta`, `mem.concept.spec-driver.spec`,
  `mem.concept.spec-driver.revision`, `mem.concept.spec-driver.audit`,
  `mem.concept.spec-driver.plan`, `mem.concept.spec-driver.backlog`.
- Use `spec-driver show memory mem.pattern.spec-driver.delta-completion --raw`
  before `complete delta`.
- If the right memory is unclear, search first:
  `spec-driver list memories -c "<task or command terms>"`

## Common commands

- Create a new entity: `spec-driver create <kind> "<title>"`
- List entities: `spec-driver list <kind>`
- Find by pattern: `spec-driver find <kind> <pattern>`
- Show one entity: `spec-driver show <kind> <id>`
- View raw/source-oriented output: `spec-driver view <kind> <id>`
- Edit/open via spec-driver: `spec-driver edit <kind> <id>`
- Complete a lifecycle action: `spec-driver complete <kind> <id>`

Common `kind` values include:
- `adr`
- `spec`
- `delta`
- `revision`
- `audit`
- `memory`
- `policy`
- `standard`

## Command discovery

- Top-level commands: `spec-driver --help`
- Subcommands for a group: `spec-driver <group> --help`
- Creation variants: `spec-driver create --help`

When the user asks what is available, prefer showing the relevant group help or
listing the relevant entities instead of dumping every help screen.
