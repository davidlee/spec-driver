# spec-driver Project Overview

## Purpose
Specification-driven development toolkit with multi-language spec sync and documentation generation. Manages ADRs, specifications, deltas, requirements, and change management.

## Tech Stack
- Python 3.10+ (3.12 target)
- typer (CLI framework)
- jinja2, pyyaml, python-frontmatter
- pytest, ruff, pylint
- uv (package manager)

## Structure
- `supekku/cli/` - CLI commands
- `supekku/scripts/` - scripts and lib
- `specify/` - specifications
- `change/` - deltas, revisions, audits
- `backlog/` - issues, problems, improvements
