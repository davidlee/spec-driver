# `.spec-driver/`

This directory contains the project-local spec-driver installation and generated
agent guidance.

For explanation of how spec-driver works, prefer the memory layer:

- ask the agent to explain spec-driver by consulting memories
- or run `uv run spec-driver list memories`

For procedural “how do I do this?” guidance, prefer the skills layer:

- skills live under `.agents/skills/`
- boot loads the initial routing guidance, then skills pull in detail on demand

## What Lives Here

- `.spec-driver/AGENTS.md`: project bootstrap for agents
- `.spec-driver/agents/`: generated agent-facing markdown projected from local config
- `.spec-driver/hooks/`: local hook docs; `doctrine.md` is user-owned
- `.spec-driver/registry/`: derived registries
- `.spec-driver/workflow.toml`: workflow configuration
- `.spec-driver/skills.allowlist`: installed skill allowlist

## Start Here

- Overview: `uv run spec-driver show memory mem.signpost.spec-driver.overview --raw`
- Core loop: `uv run spec-driver show memory mem.pattern.spec-driver.core-loop --raw`
- File map: `uv run spec-driver show memory mem.signpost.spec-driver.file-map --raw`
- Lifecycle: `uv run spec-driver show memory mem.signpost.spec-driver.lifecycle-start --raw`
- Project workflow: `uv run spec-driver show memory mem.pattern.project.workflow --raw`

## Installed Skills

Current project skills live under `.agents/skills/`.
Key ones include:

- `boot`
- `preflight`
- `retrieving-memory`
- `doctrine`
- `scope-delta`
- `draft-design-revision`
- `plan-phases`
- `execute-phase`
- `audit-change`
- `close-change`

## Memory Inventory

Use `uv run spec-driver list memories` for the full current list.
Common spec-driver memories include:

- `mem.signpost.spec-driver.overview`
- `mem.pattern.spec-driver.core-loop`
- `mem.signpost.spec-driver.ceremony`
- `mem.concept.spec-driver.posture`
- `mem.concept.spec-driver.truth-model`
- `mem.concept.spec-driver.spec`
- `mem.concept.spec-driver.delta`
- `mem.concept.spec-driver.design-revision`
- `mem.concept.spec-driver.plan`
- `mem.concept.spec-driver.revision`
- `mem.concept.spec-driver.audit`
- `mem.concept.spec-driver.contract`
- `mem.concept.spec-driver.verification`
- `mem.concept.spec-driver.requirement-lifecycle`
- `mem.pattern.spec-driver.delta-completion`

## Rule Of Thumb

- memories explain
- skills instruct
- ADRs/specs govern
- generated docs project local configuration

If two docs explain the same thing differently, treat that as drift and prefer
memories/skills unless an ADR or spec explicitly governs the question.
