# SpecDriver - http://github.com/davidlee/spec-driver/

a python spec-driven development framework, based on markdown, YAML, and scripts to manage templating and a shared registry

## Tests

No code without tests. `just test`

## Lint

We have 2 linters. 

`just lint` uses ruff - your code MUST pass with zero warnings.

`just pylint` uses pylint - the --fail-under threshold is a ratchet to guide you towards zero warnings, not a cue to stop improving.

If you need to lint an individual file, use `uv run pylint --indent-string "  " ... `

## Disabling Linters

You CANNOT bypass lint rules without explaining your rationale to the User and receiving written acceptance. Under NO CIRCUMSTANCES are you to modify the pyproject.toml or other settings to relax lint rules.