---
id: mem.pattern.installer.boot-architecture
name: Installer & Agent Boot Architecture
kind: memory
status: active
memory_type: pattern
updated: '2026-03-12'
verified: '2026-03-12'
confidence: high
tags:
- spec-driver
- installer
- skills
- boot
- agent-guidance
summary: >-
  How the installer sets up agent guidance, skills, and boot references.
  Covers file ownership (managed vs authored), the agents/boot.md / AGENTS.md
  reference architecture, and the template-driven rendering pipeline.
priority:
  severity: high
  weight: 9
scope:
  commands:
  - uv run spec-driver install
  paths:
  - supekku/scripts/install.py
  - supekku/scripts/lib/skills/sync.py
  - supekku/scripts/lib/core/config.py
  - supekku/scripts/lib/core/preboot.py
  - supekku/claude.hooks/startup.sh
  - supekku/templates/
provenance:
  sources:
  - kind: code
    ref: supekku/scripts/install.py
  - kind: code
    ref: supekku/scripts/lib/skills/sync.py
  - kind: code
    ref: supekku/scripts/lib/core/config.py
  - kind: code
    ref: supekku/scripts/lib/core/preboot.py
  - kind: delta
    ref: DE-091
---

# Installer & Agent Boot Architecture

## Overview

`initialize_workspace` (install.py) sets up the workspace structure, then
`sync_skills` (sync.py) wires agent-facing references. Both are idempotent.

## File Ownership Model

### Managed (overwritten on install/sync)

| File | Writer | Content |
|---|---|---|
| `.spec-driver/AGENTS.md` | `sync_skills` | `<skills_system>` XML block with allowlisted skill metadata |
| `.spec-driver/agents/*.md` | installer | Jinja2-rendered agent guidance (boot, exec, workflow, glossary, policy) |
| `.agents/spec-driver-boot.md` | `spec-driver admin preboot` | Concatenated boot context (governance files + listings) |
| `.claude/rules/spec-driver-boot.md` | installer (symlink) | Symlink → `../../.agents/spec-driver-boot.md` |

### Authored (created if missing, never overwritten)

| File | Content |
|---|---|
| Root `AGENTS.md` | Project-specific agent instructions; gets `@`-references prepended |
| Root `CLAUDE.md` | Project-specific Claude instructions; gets `@`-reference prepended |

## Reference Architecture

Root **AGENTS.md** receives (prepended, idempotent):
```
@.spec-driver/agents/boot.md ← triggers /boot
@.spec-driver/AGENTS.md      ← skills XML
```

Root **CLAUDE.md** receives (prepended, idempotent):
```
@.spec-driver/agents/boot.md ← triggers /boot (no skills XML)
```

CLAUDE.md does NOT get the AGENTS.md skills reference — Claude reads
AGENTS.md natively for skill discovery.

## Config Gating

`[integration]` section in `.spec-driver/workflow.toml`:

| Key | Default | Effect |
|---|---|---|
| `agents_md` | `true` | Prepend references to root AGENTS.md |
| `claude_md` | `true` | Prepend boot reference to root CLAUDE.md |

## Template Pipeline

Templates live in `supekku/templates/`:
- `agents/*.md` → `.spec-driver/agents/*.md` (rendered with workflow config via Jinja2)
- `hooks/*` → `.spec-driver/hooks/*` (create-if-missing, never overwritten)
- Top-level `*.md` → `.spec-driver/templates/*.md` (artifact templates)

Rendering uses Jinja2 via `render_template()` with `{"config": workflow_config}`
as context. Falls back to static defaults if templates are missing.

## Skills Install

`sync_skills()` (callable standalone or from installer):
1. Reads `.spec-driver/skills.allowlist`
2. Installs skill dirs to targets (`.claude/skills/`, `.agents/skills/`)
3. Writes `.spec-driver/AGENTS.md` (skills XML)
4. Prepends `@`-references to root AGENTS.md and CLAUDE.md per config

## Preboot (DE-091)

`startup.sh` hook calls `spec-driver admin preboot` before every session.
Preboot reads the 7 boot-sequence files + 3 governance listings (TSV) and
writes `.agents/spec-driver-boot.md`. The installer creates a symlink at
`.claude/rules/spec-driver-boot.md` so Claude Code loads it into the
cacheable prefix automatically — zero tool calls.

Source: `supekku/scripts/lib/core/preboot.py`

## Boot Flow

1. `startup.sh` hook runs `spec-driver admin preboot` → generates `.agents/spec-driver-boot.md`
2. Claude Code loads `.claude/rules/spec-driver-boot.md` (symlink) into cacheable prefix
3. Agent reads root CLAUDE.md or AGENTS.md
4. `@.spec-driver/agents/boot.md` expands → `/boot`
5. `/boot` triggers boot skill — lightweight validator (checks preboot file exists, warns if missing, prints sigil)
6. Boot skill enforces `/using-spec-driver` routing
