# Notes for DE-026

## Background Research

### Current Implementation
- Location: `supekku/scripts/lib/sync/adapters/zig.py:325-423`
- Methods to remove:
  - `_generate_zig_docs()` - orchestrates doc generation
  - `_parse_zig_file()` - parses individual Zig files for doc comments
  - `_extract_declaration()` - extracts declaration signatures from `pub` lines
- Limitations:
  - Regex-based parsing misses complex patterns
  - No support for comptime, inline fn, advanced doc comments
  - Inconsistent with standard Zig documentation tools

### Reference Implementation
- GoAdapter: `supekku/scripts/lib/sync/adapters/go.py:176-400`
- Pattern:
  - Check tool availability with `which()`
  - Subprocess calls with proper flag handling
  - Support `--check` mode for CI
  - Generate multiple variants (public, internal)
  - Hash-based change detection

### zigmarkdoc Tool
- Location: `~/.local/bin/zigmarkdoc`
- Key flags:
  - `--check`: Exit 1 if output differs (CI mode)
  - `--include-private` / `-p`: Include non-pub declarations
  - `--output` / `-o <PATH>`: Output file path
  - `--no-source`: Omit source code blocks (optional)
- Output: Deterministic Markdown documentation

## Decisions Made
1. **Fallback behavior**: No fallback - raise ZigmarkdocNotAvailableError
   - Error message includes installation instructions: https://github.com/davidlee/zigmarkdoc
   - Rationale: Fail fast, prevent degraded behavior, simpler maintenance
2. **Contract paths**: Yes - update to match GoAdapter pattern
   - Current: `contracts/zig/{slug}-public.md`
   - Target: `contracts/interfaces.md`, `contracts/internals.md`
   - Rationale: Consistency across adapters
3. **CI setup**: N/A - local CI only, no automation needed

## Implementation Tasks (Outline)

### Phase 1: Core Implementation
1. Add `is_zigmarkdoc_available()` function
2. Add `ZigmarkdocNotAvailableError` exception class
3. Refactor `generate()` method:
   - Replace manual parser calls with subprocess to zigmarkdoc
   - Support `--check` flag
   - Generate both public and all variants
4. Update `describe()` to return both variants
5. Remove obsolete methods: `_generate_zig_docs`, `_parse_zig_file`, `_extract_declaration`

### Phase 2: Testing
1. Unit tests for `is_zigmarkdoc_available()`
2. Unit tests for `generate()` with mocked subprocess
3. Integration tests with real Zig source files
4. Update existing tests if any exist

### Phase 3: Contract Regeneration
1. Run `uv run spec-driver sync --language zig` to regenerate all contracts
2. Review generated contracts for quality
3. Commit updated contracts
