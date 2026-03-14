---
id: mem.fact.pi.append-system-md-discovery
name: pi APPEND_SYSTEM.md auto-discovery
kind: memory
status: active
memory_type: fact
created: '2026-03-14'
updated: '2026-03-14'
verified: '2026-03-14'
confidence: high
tags:
- pi
- system-prompt
- context-injection
summary: pi auto-discovers .pi/APPEND_SYSTEM.md and appends it to system prompt
scope:
  paths:
  - .pi/APPEND_SYSTEM.md
  globs:
  - .pi/**
provenance:
  sources:
  - "@mariozechner/pi-coding-agent/dist/core/resource-loader.js (discoverAppendSystemPromptFile)"
  - DE-093
---

# pi APPEND_SYSTEM.md auto-discovery

pi looks for `APPEND_SYSTEM.md` in two locations (first match wins):
1. `.pi/APPEND_SYSTEM.md` — project-local (under `CONFIG_DIR_NAME`, which is `.pi`)
2. `~/.pi/agent/APPEND_SYSTEM.md` — global

Content is appended to the system prompt after the base prompt, tools, skills, and AGENTS.md context.

- Re-read on `/reload` (as part of `resourceLoader.reload()`)
- NOT re-read per turn — system prompt is stable across turns (cache-safe)
- pi also supports `.pi/SYSTEM.md` (replaces the entire system prompt — avoid)
- Undocumented in pi README; found in `resource-loader.js` source

spec-driver uses this for preboot governance context injection ([[DE-093]]).
