# Notes for DE-060

## Implementation

- Self-contained Python script: no supekku imports, inlines JSONL append + socket send
- Path classification via ordered regex list — more specific patterns (phase, DR, IP) before generic delta
- Session ID from hook JSON `session_id` field (authoritative, no env-var needed)
- Hook registered as async PostToolUse on Read|Edit|Write — zero blocking
- Source file: `supekku/claude.hooks/artifact_event.py`
- Settings source: `supekku/claude.settings.json` → installed to `.claude/settings.json`
- Test import uses `importlib.util.spec_from_file_location` because `claude.hooks` dir name has a dot (not a valid Python package)
- Added `supekku/claude.hooks` to pytest testpaths
- 33 tests, all passing. `just` green (2989 passed).
- VH-060-01: pending manual attestation (hook is now active in this session)

## Claude Code Hook API Notes

- PostToolUse JSON on stdin: `{session_id, tool_name, tool_input: {file_path}, cwd, ...}`
- `async: true` in hook config = fire-and-forget, non-blocking
- `$CLAUDE_PROJECT_DIR` available for path resolution in hook command
