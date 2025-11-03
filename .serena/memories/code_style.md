# Code Style & Conventions

## Style
- 2 space indentation
- Google docstring convention
- Type hints required
- Line length: 88
- Python 3.12+ target

## Patterns
- Separation of concerns (SRP)
- Pure functions over stateful objects
- Skinny CLI pattern (orchestration only)
- Domain packages for business logic
- Formatters package for display only

## Quality
- TDD/BDD - tests first
- Both linters must pass (ruff + pylint)
- Pylint fail-under: 0.73 (ratchet - minimum!)
- Pylint target: 10/10 (new), 0.95 (revisited code)
