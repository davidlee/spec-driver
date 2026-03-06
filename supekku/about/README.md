# About

This directory is no longer the primary handbook for spec-driver.

Per `ADR-005`, the canonical guidance layers are:

- memories for conceptual understanding
- skills for procedural guidance

Use this directory as lightweight routing/reference material only.

## Start Here

- Overview: `uv run spec-driver show memory mem.signpost.spec-driver.overview --raw`
- Core loop: `uv run spec-driver show memory mem.pattern.spec-driver.core-loop --raw`
- Lifecycle: `uv run spec-driver show memory mem.signpost.spec-driver.lifecycle-start --raw`
- File map: `uv run spec-driver show memory mem.signpost.spec-driver.file-map --raw`
- Memory inventory: `uv run spec-driver list memories`

If you are working with an agent, ask it to explain spec-driver by consulting
memories before reading broad prose docs.

## What This Directory Should Contain

- short reference material
- file maps and schema notes
- generated or derived views where useful
- routing to memories, skills, ADRs, and specs

It should not act as a competing handbook for workflow doctrine or day-to-day
procedural guidance.

## Current Reference Files

- `dogma.md`: compact project tenets loaded by boot
- `lifecycle.md`: code-truth lifecycle and coverage reference
- `frontmatter-schema.md`: schema/reference material
- `*.d2` / `*.svg`: supporting diagrams
