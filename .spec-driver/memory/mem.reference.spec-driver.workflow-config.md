---
id: mem.reference.spec-driver.workflow-config
name: workflow.toml Configuration Reference
kind: memory
status: active
memory_type: reference
updated: '2026-03-08'
verified: '2026-03-08'
confidence: high
tags:
- spec-driver
- configuration
- workflow
summary: Complete reference for all workflow.toml configuration options, their
  defaults, and where they are used.
priority:
  severity: high
  weight: 9
provenance:
  sources:
  - kind: code
    ref: supekku/scripts/lib/core/config.py
---

# workflow.toml Configuration Reference

## Overview

`workflow.toml` lives at `.spec-driver/workflow.toml` and controls spec-driver
behaviour for the project. It is created on `spec-driver init`.

**Loading behaviour**: user values deep-merge (one level) with built-in
defaults. Missing sections and keys always fall back to defaults, so the file
only needs to contain overrides. Extra user keys (e.g.
`spec_driver_installed_version`) are preserved.

**Comment convention**: the default template uses `##` for prose and `#` for
commented-out config lines. Uncomment a `#` line to activate it.

## Top-level Scalars

| Key | Default | Description |
|-----|---------|-------------|
| `ceremony` | `"pioneer"` | Governance posture: `"pioneer"` (lightweight), `"settler"` (moderate), `"town_planner"` (full). Controls which primitives agents activate. |
| `strict_mode` | `false` | When true, `complete delta` enforces all coverage gates. When false, `--force` can bypass. |

## Sections

### [tool]

| Key | Default | Used by |
|-----|---------|---------|
| `exec` | `"uv run spec-driver"` | Agent templates — how to invoke spec-driver |

Detected automatically at install time based on project dependencies and
environment.

### [verification]

| Key | Default | Used by |
|-----|---------|---------|
| `command` | `"just check"` | Agent `exec.md` template — verification command |

### [cards]

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | `true` | Toggle kanban card support |
| `root` | `"kanban"` | Directory for card files |
| `lanes` | `["backlog", "next", "doing", "finishing", "done"]` | Lane names |
| `id_prefix` | `"T"` | Prefix for card IDs (e.g. T001) |

### [docs]

| Key | Default | Description |
|-----|---------|-------------|
| `artefacts_root` | `"docs/artefacts"` | Design document directory |
| `plans_root` | `"docs/plans"` | Implementation plan directory |

### [policy]

| Key | Default | Description |
|-----|---------|-------------|
| `adrs` | `true` | Enable Architecture Decision Records |
| `policies` | `false` | Enable project policies |
| `standards` | `false` | Enable technical standards |

### [events]

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | `true` | Toggle event logging for spec-driver operations |

### [sync]

| Key | Default | Description |
|-----|---------|-------------|
| `spec_autocreate` | `false` | Automatically create unit specs during sync |

### [contracts]

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | `true` | Enable generated contracts corpus |
| `root` | `".contracts"` | Directory under repo root (derived, regenerable) |

### [bootstrap]

| Key | Default | Description |
|-----|---------|-------------|
| `doctrine_path` | `".spec-driver/doctrine.md"` | Project doctrine file loaded at agent boot |

### [skills]

| Key | Default | Description |
|-----|---------|-------------|
| `targets` | `["claude", "codex"]` | Agent config directories for skill sync |

### [integration]

| Key | Default | Description |
|-----|---------|-------------|
| `agents_md` | `true` | Inject @-reference into root AGENTS.md |
| `claude_md` | `true` | Inject @-reference into root CLAUDE.md |

### [dirs]

Directory name overrides for `.spec-driver/` subdirectories:

| Key | Default | Key | Default |
|-----|---------|-----|---------|
| `backlog` | `"backlog"` | `memory` | `"memory"` |
| `tech_specs` | `"tech"` | `product_specs` | `"product"` |
| `decisions` | `"decisions"` | `policies` | `"policies"` |
| `standards` | `"standards"` | `deltas` | `"deltas"` |
| `revisions` | `"revisions"` | `audits` | `"audits"` |
| `issues` | `"issues"` | `problems` | `"problems"` |
| `improvements` | `"improvements"` | `risks` | `"risks"` |

## Key Code References

- **Config definition + loading**: `supekku/scripts/lib/core/config.py`
- **Template generation**: `generate_default_workflow_toml()` in same file
- **Path initialisation from [dirs]**: `supekku/scripts/lib/core/paths.py`
- **Agent template rendering**: `supekku/scripts/lib/core/agent_docs.py`
- **Skills install ([skills], [integration])**: `supekku/scripts/lib/skills/sync.py`
- **Sync preferences ([sync])**: `supekku/scripts/lib/core/sync_preferences.py`
- **Event gating ([events])**: `supekku/cli/main.py`
- **Strict mode**: `supekku/scripts/complete_delta.py`
