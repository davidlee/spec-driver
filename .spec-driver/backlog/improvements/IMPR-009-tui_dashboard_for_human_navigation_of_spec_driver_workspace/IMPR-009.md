---
id: IMPR-009
name: TUI dashboard for human navigation of spec-driver workspace
created: '2026-03-06'
updated: '2026-03-06'
status: resolved
kind: improvement
deltas: [DE-052, DE-053, DE-054, DE-061]
related_decisions: [ADR-006]
related_issues: [ISSUE-019]
related_improvements: [IMPR-008]
---

# TUI dashboard for human navigation of spec-driver workspace

## Problem

Spec-driver manages 13+ artifact types with rich lifecycle semantics and
cross-artifact relationships. Navigating this via CLI (`list`, `show`, `find`)
works but is friction-heavy for humans who want to browse, explore
relationships, or monitor agent activity in real time.

[lazyspec](https://github.com/jkaloger/lazyspec) demonstrates that a terminal
dashboard for spec-like artifacts is immediately useful. However, lazyspec is
Rust/ratatui and covers only 4 document types — adapting it would mean bridging
cargo + uv and losing access to spec-driver's registries and formatters.

## Proposal

Build a native Python TUI as part of spec-driver, using
[Textual](https://textual.textualize.io/) as the framework.

Entry point: `spec-driver tui` (or bare `spec-driver` with no subcommand).

Reads `workflow.toml` for directory layout. Reuses existing registries,
formatters, and theme infrastructure.

### MVP features

- **Artifact browser**: type selector, filtered list, markdown preview (3-panel)
- **Type/status filtering**: leverage existing registry filter capabilities
- **Search**: fuzzy/substring across all artifact types
- **Editor integration**: shell out to `$EDITOR` on selected artifact
- **File watching**: live reload via `watchfiles` when artifacts change on disk

### Agent session tracking ("track" mode)

A dedicated panel or view mode that follows spec-driver activity in real time,
aimed at humans watching an agent work.

**Architecture: event log + Unix domain socket hybrid**

| Concern                 | Solution                                           |
| ----------------------- | -------------------------------------------------- |
| Persistent audit trail  | JSONL event log at `.spec-driver/run/events.jsonl` |
| Real-time TUI updates   | Unix domain socket at `.spec-driver/run/tui.sock`  |
| Session attribution     | `SPEC_DRIVER_SESSION` env var set by agent/hook    |
| Follow specific session | TUI filters on session ID                          |
| Follow all activity     | TUI shows unfiltered stream                        |
| No TUI running          | Socket send fails silently; log still written      |

**CLI side (emitter):** Every `spec-driver` CLI invocation appends a structured
JSONL event and fire-and-forgets a UDP datagram to the socket if it exists:

```jsonl
{
  "ts": "...",
  "session": "claude-abc123",
  "cmd": "create delta",
  "artifacts": [
    "DE-049"
  ],
  "status": "ok"
}
```

The socket emit is non-blocking, stdlib-only (`socket.AF_UNIX`,
`socket.SOCK_DGRAM`), and costs nothing when no TUI is listening.

**TUI side (receiver):** Textual's async architecture listens on the socket for
live events. On startup, replays recent history from the event log to catch up.

**Track view:**

```
 Track: session claude-abc123
 14:23:01  create delta DE-049
 14:23:03  draft-design-revision DR-001 (DE-049)
 14:23:12  create phase phase-01 (DE-049)
 14:23:45  complete delta DE-049

 Artifacts touched: DE-049, DR-001, SPEC-012
```

Selecting an event navigates to that artifact in the browser panel.

**Session modes:**

- Follow specific session (by ID or selection)
- Follow all local activity (grouped/colored by session)
- Replay recent events from log on launch

### Stretch features

- Relation graph view (spec-driver has richer link semantics than lazyspec)
- Inline artifact creation (thin form delegating to existing `create` internals)
- Verification/coverage dashboard
- Drift indicators

## Why Textual

- Python-native: no polyglot build friction
- CSS-like styling, reactive widgets, built-in `MarkdownViewer`
- Ships with `DataTable`, `Tree`, `Input`, `TextArea` — maps to the panel layout
- Rich integration already implicit in spec-driver's formatter/theme layer
- Active project with good documentation

## Dependencies

- **ISSUE-019** (registry API drift) should land first. Normalising registries
  on a consistent `find(id)` + `collect()` interface means the TUI consumes a
  clean API rather than building throwaway adapters around current
  inconsistencies. Without it, the TUI needs per-type adapter logic for three
  different lookup patterns plus a function-based BacklogRegistry.
- **IMPR-008** (configurable paths) is not blocking — using `paths.py` getters
  avoids hardcoding. When IMPR-008 makes those getters config-aware, the TUI
  inherits it for free.

## Design constraints

- TUI is a presentation layer only — no business logic
- Reuse registries and formatters; do not duplicate domain logic
- Event emission must be zero-cost when no TUI is running
- `workflow.toml` is the single source of truth for directory layout
- Follow ADR-006 canonical paths (`.spec-driver/` root)

## Exit Criteria

- PROD spec authored covering the TUI as a product surface (user problems,
  outcomes, success metrics)
- DE-052, DE-053, DE-054 completed
- `spec-driver tui` launches and is usable for browsing and tracking

## References

- lazyspec: Rust/ratatui TUI for project documentation (4 doc types, 3-panel
  dashboard, fuzzy search, file watching, editor integration, relation graph)
- ADR-006: consolidate workspace directories under `.spec-driver/`
- IMPR-008: configurable workspace directory layout
