---
id: IMPR-004
name: Use zigmarkdoc for Zig documentation generation
created: '2026-02-06'
updated: '2026-02-06'
status: idea
kind: improvement
---

# Use zigmarkdoc for Zig documentation generation

## Summary

Replace the basic doc comment parsing in ZigAdapter with zigmarkdoc for proper Zig documentation generation, matching how GoAdapter uses gomarkdoc.

## Current State

The ZigAdapter currently uses a simple regex-based parser to extract `///` and `//!` doc comments from Zig source files. This approach:
- Misses complex documentation patterns
- Doesn't handle comptime, inline fn, or other Zig-specific constructs well
- Produces inconsistent output compared to standard Zig docs

## Proposed Solution

Use zigmarkdoc (`~/dev/lang/zig/zigmarkdoc`) for documentation generation:

1. Check for `zigmarkdoc` availability (similar to `gomarkdoc` check)
2. Call zigmarkdoc with appropriate flags for markdown output
3. Support `--check` mode for verification without modification
4. Generate contracts in `contracts/zig/` directory

## Implementation Notes

- Location: `~/dev/lang/zig/zigmarkdoc`
- Pattern: Follow GoAdapter's gomarkdoc integration
- Fallback: Keep basic parser as fallback when zigmarkdoc unavailable

## Acceptance Criteria

- [ ] ZigAdapter uses zigmarkdoc when available
- [ ] `sync --language zig --check` verifies docs are up-to-date
- [ ] Generated docs match zigmarkdoc output format
- [ ] Graceful fallback when zigmarkdoc not installed
