# justfile

From the project root, run
`just --list supekku`

before submitting code for user approval, run
`just supekku::all` 

ensure all tests and lint warnings are green - no exceptions(*).

You cannot suppress lint warnings without user approval.

`just supekku::lint`

The point of linting is to improve the quality of the code.

`uv run pylint supekku/scripts/lib/spec_sync` to run pylint on a particular module only.

NEVER prioritise task completion over technical quality or delivering value to users.

(*) - exception: we are currently working towards "lint zero". for this to be
practical, you must fix all lint warnings in any file you touch, but can leave
untouched files.

# python

we use uv because nixos. `uv run python`

