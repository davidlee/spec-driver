# SpecDriver Architecture Guide

@supekku/INIT.md

Quick reference for agents maintaining architectural integrity.

**Project**: Python spec-driven development framework
**Docs**: http://github.com/davidlee/spec-driver/

## Core Principles

### 1. Separation of Concerns (SRP)

Each module has ONE responsibility:

- **Domain packages** (`decisions/`, `changes/`, `specs/`) - business logic, data models
- **Formatters** (`formatters/`) - pure display functions, no business logic
- **CLI/Scripts** - thin orchestration: args → registry → filter → format → output
- **Core utilities** (`core/`) - shared infrastructure

**Wrong**: Mixing formatting logic in CLI commands
**Right**: CLI calls `format_spec_list_item(spec, options)`

### 2. Avoid Premature Abstraction

Start specific, generalize only when patterns proven across 3+ cases.

- **First formatter**: Extract duplicate code into artifact-specific function
- **Second formatter**: Follow same pattern
- **Third formatter**: NOW consider shared utilities if patterns clear

**Wrong**: Building generic `BaseFormatter` with config before understanding needs
**Right**: `decision_formatters.py`, `change_formatters.py`, `spec_formatters.py` - extract shared utils only when duplication hurts

### 3. Skinny CLI Pattern

CLI/script files orchestrate, never implement:

```python
# GOOD: Thin orchestration
def list_specs(filters):
  registry = SpecRegistry(root)          # Load
  specs = [s for s in registry.all_specs() if matches(s, filters)]  # Filter
  for spec in specs:
    output = format_spec_list_item(spec, options)  # Format
    print(output)                         # Output

# BAD: Business logic in CLI
def list_specs(filters):
  # 50 lines of filtering logic
  # 30 lines of formatting logic
  # Mixing concerns
```

### 4. Pure Functions Over Stateful Objects

Prefer `(input) -> output` over stateful transformations:

```python
# GOOD: Pure formatter
def format_phase_summary(phase: dict, max_len: int = 60) -> str:
  """Pure function: same input → same output, no side effects."""
  return f"{phase['id']}: {truncate(phase['objective'], max_len)}"

# BAD: Stateful formatter
class PhaseFormatter:
  def __init__(self):
    self.max_len = 60
  def format(self, phase):
    self.last_phase = phase  # Side effect
    return ...
```

## Package Structure

```
supekku/scripts/lib/
├── decisions/         # ADR domain: models, registry, creation
├── changes/           # Change artifacts: deltas, revisions, audits
│   ├── blocks/        # Parsers for frontmatter blocks
│   ├── artifacts.py   # ChangeArtifact model
│   ├── registry.py    # ChangeRegistry
│   └── lifecycle.py   # Status management
├── specs/             # Specifications: models, registry, index
├── requirements/      # Requirements domain
├── formatters/        # Display formatting (NO business logic)
│   ├── decision_formatters.py
│   ├── change_formatters.py
│   └── spec_formatters.py
├── core/              # Shared utilities: paths, repo, CLI utils
├── sync/              # Code synchronization adapters
└── validation/        # Schema validation

CLI dependency direction: CLI → Formatters → Domain → Core
```

**Finding the right package**:
- Business logic about decisions? → `decisions/`
- Display formatting? → `formatters/`
- Working with requirements? → `requirements/`
- Shared utility? → `core/`

## Common Patterns

### Adding a Formatter

1. **Create `formatters/{artifact}_formatters.py`**:
   ```python
   """Pure formatting functions with no business logic."""

   def format_{artifact}_list_item(artifact: Artifact) -> str:
     """Format artifact as: id, status, name."""
     return f"{artifact.id}\t{artifact.status}\t{artifact.name}"
   ```

2. **Export in `formatters/__init__.py`**:
   ```python
   from .{artifact}_formatters import format_{artifact}_list_item

   __all__ = [..., "format_{artifact}_list_item"]
   ```

3. **Write comprehensive tests** (`formatters/{artifact}_formatters_test.py`)

4. **Update CLI/scripts** to use formatter instead of inline formatting

### Creating Domain Logic

1. **Choose the right package** based on responsibility
2. **Create models** (`models.py` or `registry.py`)
3. **Implement business logic** (pure functions preferred)
4. **Write tests FIRST** (TDD)
5. **Keep formatters separate** - no display logic in domain

### CLI Commands

Keep CLI files under 150 lines by delegating:

```python
# CLI command structure
@app.command("list")
def list_items(filters):
  # 1. Load from registry
  registry = ItemRegistry(root)

  # 2. Apply filters (or delegate to registry)
  items = [i for i in registry.all() if matches(i, filters)]

  # 3. Format (delegate to formatters)
  for item in items:
    output = format_item(item, options)

  # 4. Output
    print(output)
```

## Consistency & Reuse

Always seek to promote reuse and improvement. Never implement functionality which could exist without first checking if it does.

Pay attention to naming and locating code to promote discovery and improve cohesion.

This is *MUCH MORE IMPORTANT* than quickly finishing your assigned task.

## Quality Standards

### Tests

No code without tests. `just test`

- Write tests BEFORE marking work complete
- Formatters need comprehensive edge case testing
- Aim for clear, maintainable test names

### Lint

We have 2 linters:

- `just lint` (ruff) - MUST pass with zero warnings
- `just pylint` - threshold is a ratchet, not a stopping point

If you need to lint an individual file:
```bash
uv run pylint --indent-string "  " path/to/file.py
```

### Disabling Linters

You CANNOT bypass lint rules without:
1. Explaining rationale to the user
2. Receiving written acceptance

Under NO CIRCUMSTANCES modify `pyproject.toml` to relax lint rules.

## When Breaking Rules

Sometimes you need to deviate. When you do:

1. **Explain why** the established pattern doesn't fit
2. **Propose alternative** with clear benefits
3. **Get approval** before implementing
4. **Document** the exception if accepted

**Valid reasons**:
- Performance bottleneck requires stateful optimization
- Third-party library forces different pattern
- Domain complexity genuinely needs abstraction

**Invalid reasons**:
- "It's easier this way"
- "I'm short on time"
- "I haven't evaluated better ideas"

## Quick Checks

Before beginning implementation:

- [ ] No code without an approved written plan
- [ ] You will write your plan to a file before executing it
- [ ] Research as necessary to ensure it is informed by existing code

When coding:

- [ ] lint and test as you go
- [ ] CLI files thin (<150 lines), delegate to domain
- [ ] Pure functions used where possible
- [ ] No premature abstraction - specific before generic
- [ ] Look for opportunities to consolidate and simplify

Before submitting work:

- [ ] Tests written and passing (`just test`)
- [ ] Both linters passing (`just lint` + `just pylint`)
- [ ] All of the above (fail-fast): `just` 
- [ ] Display logic in `formatters/`, not in domain packages
