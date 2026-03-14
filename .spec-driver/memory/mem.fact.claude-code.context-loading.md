---
id: mem.fact.claude-code.context-loading
name: Claude Code Context Loading & Token Caching
kind: memory
status: active
memory_type: fact
created: "2026-03-12"
updated: "2026-03-12"
verified: "2026-03-12"
confidence: high
tags:
  - claude-code
  - token-caching
  - agent-guidance
summary: How Claude Code loads instructions into context and which sources are cache-friendly
---

# Claude Code Context Loading & Token Caching

## How Claude Code loads instructions into context

| Source                                      | When loaded                  | Cache-friendly?                        |
| ------------------------------------------- | ---------------------------- | -------------------------------------- |
| CLAUDE.md (all levels)                      | Session start, automatically | Yes — stable prefix                    |
| `.claude/rules/` (no `paths` frontmatter)   | Session start, automatically | Yes — stable prefix                    |
| `.claude/rules/` (with `paths` frontmatter) | On file access matching glob | No — injected dynamically after prefix |

- CLAUDE.md files are read from disk and injected as conversation-level context before the first turn. They appear under a `# claudeMd` heading. No tool call required.
- Unconditional rules behave identically — loaded at launch, same priority as CLAUDE.md.
- Path-specific rules trigger when Claude reads files matching the glob pattern. They are injected after the stable prefix, breaking the cache boundary.
- Claude Code uses Anthropic prompt caching automatically. Stable prefix content (CLAUDE.md + unconditional rules) is cached across turns within a session.

## `@` reference inlining

- `@` references in CLAUDE.md and AGENTS.md are inlined into the system prompt at session start — fully cacheable, no tool calls.
- `@` references inside skill files are **not** inlined — they appear as literal text in conversation turns, requiring Read tool calls to resolve.
- Implication: anything reachable via `@` from CLAUDE.md/AGENTS.md is in the cacheable prefix for free. The boot tax is specifically for skill-level file reads that happen in conversation turns.
