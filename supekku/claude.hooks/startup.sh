#!/bin/sh
# Read the full hook input from stdin (Claude Code passes JSON).
# stdin must be consumed once — boot prompt JSON is written to stdout.
INPUT=$(cat)

# Extract session_id using Python (always available in spec-driver projects)
SESSION_ID=$(echo "$INPUT" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null)

# Persist session ID for all subsequent Bash tool invocations
if [ -n "$CLAUDE_ENV_FILE" ] && [ -n "$SESSION_ID" ]; then
  echo "export SPEC_DRIVER_SESSION=$SESSION_ID" >>"$CLAUDE_ENV_FILE"
fi

# Generate static boot context for cache-optimised agent sessions.
# Errors swallowed — boot skill warns if file is missing.
uv run spec-driver admin preboot "$PWD" >/dev/null 2>&1

# Output the boot prompt (existing behavior)
echo '{"systemMessage":"Welcome to spec-driver","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"you MUST use the /boot skill IMMEDIATELY after receiving the next prompt."}}'
