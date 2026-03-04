#!/usr/bin/env zsh

DIR=$CLAUDE_PROJECT_DIR;
if [[ -z "$CLAUDE_PROJECT_DIR" ]]; then
  DIR=$PWD;
fi

which fd > /dev/null && fd mem $DIR/memory --changed-within=12h || find $DIR/memory -mtime 1
