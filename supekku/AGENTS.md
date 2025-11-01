# Invoking

`uv run spec-driver`

before submitting code for user approval, run
`just` 

ensure all tests and lint warnings are green - no exceptions(*).
You cannot suppress lint warnings without user approval.
The point of linting is to improve the quality of the code.

for quicker checks while you work
`just quickcheck`

`uv run pylint supekku/scripts/lib` to run pylint on a particular module only.

NEVER prioritise task completion over technical quality or delivering value to users.

(*) - exception: we are currently working towards "lint zero". for this to be
practical, you must fix all lint warnings in any file you touch, but can leave
untouched files.

# python

we use uv because nixos. `uv run python`
