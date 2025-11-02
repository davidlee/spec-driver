# DE-005 Revised Design (2025-11-02)

## Problem with Original Design

Original design (Tasks 1.1-1.6) was overengineered:
- **Task 1.3** (completion module): Tried to programmatically complete specs - brittle, assumes we know better than agents
- **Task 1.1** (`show template`): Unclear value - agents can read template files directly
- Overall: Building complex automation when agents can do the thinking

## Simplified Design

### Core Principle
CLI does minimal mechanical work (replace body with template). Agent does the thinking (fill sections intelligently).

### Revised Tasks

#### Task 1.2: Implement Stub Detection
**Status**: Unchanged from revised approach in `STATUS-BASED-STUB-DETECTION.md`

```python
def is_stub_spec(spec_path: Path) -> bool:
    """Detect if spec is a stub."""
    frontmatter, _ = load_validated_markdown_file(spec_path)

    # Primary: explicit stub status
    if frontmatter.get("status") == "stub":
        return True

    # Fallback: line count for human error tolerance
    total_lines = spec_path.read_text().count('\n') + 1
    return total_lines <= 30
```

**Files**:
- `supekku/scripts/lib/specs/detection.py`
- `supekku/scripts/lib/specs/detection_test.py`

**Tests**:
- `test_is_stub_spec_status_stub()` - status="stub" → True
- `test_is_stub_spec_line_count()` - 28 lines → True
- `test_is_stub_spec_modified()` - 200 lines → False
- `test_is_stub_spec_draft_long()` - status="draft", 100 lines → False

#### Task 1.4: Build CLI Backfill Command (REVISED)
**Purpose**: Replace stub spec body with fresh template (preserving frontmatter)

```python
@app.command("spec")
def backfill_spec(
    spec_id: str,
    force: bool = False,
    root: RootOption = None,
) -> None:
    """Replace stub spec body with template, preserving frontmatter."""
    # 1. Load spec
    registry = SpecRegistry(root or get_repo_root())
    spec = registry.get(spec_id)

    # 2. Check if stub (unless --force)
    if not force and not is_stub_spec(spec.path):
        error(f"{spec_id} has been modified. Use --force to replace anyway.")

    # 3. Load template
    template = load_template("spec.md")

    # 4. Render with frontmatter values
    body = template.render(
        spec_id=spec.frontmatter["id"],
        name=spec.frontmatter["name"],
        kind=spec.frontmatter["kind"],
        # Leave YAML blocks as template boilerplate
        spec_relationships_block="{{spec_relationships_block}}",
        spec_capabilities_block="{{spec_capabilities_block}}",
        spec_verification_block="{{spec_verification_block}}",
    )

    # 5. Write back (preserve frontmatter, replace body)
    write_spec(spec.path, frontmatter=spec.frontmatter, body=body)

    print(f"✓ Backfilled {spec_id}: {spec.path}")
```

**What it does**:
- Checks if spec is stub (or `--force` to override)
- Replaces entire body with template
- Fills in `{spec_id}`, `{name}`, `{kind}` from frontmatter
- Leaves sections as boilerplate for agent to complete
- Preserves all frontmatter unchanged

**What it doesn't do**:
- Doesn't try to intelligently fill sections
- Doesn't analyze contracts
- Doesn't make inferences
- Doesn't ask questions

**Files**:
- `supekku/cli/backfill.py`
- `supekku/cli/backfill_test.py`

**Tests**:
- `test_backfill_spec_stub_success()` - happy path
- `test_backfill_spec_not_stub_no_force()` - requires --force
- `test_backfill_spec_force_override()` - --force works
- `test_backfill_spec_preserves_frontmatter()` - FM unchanged
- `test_backfill_spec_fills_basic_vars()` - spec_id/name/kind filled

#### Task 1.5: Write Agent Command (REVISED)
**Purpose**: Agent workflow orchestrating backfill + intelligent completion

`.claude/commands/supekku.backfill.md`:

```markdown
---
description: Backfill stub specifications with intelligent completion
---

# Backfill Spec Workflow

## Overview
Complete auto-generated stub specs by resetting to template, then intelligently filling sections using contracts and inference.

## Workflow

### 1. Reset spec to template
```bash
uv run spec-driver backfill spec SPEC-123
```
This replaces the body with fresh template (preserving frontmatter).

### 2. Read the spec
Read the backfilled spec to understand structure.

### 3. Gather context
- Read contracts: `specify/{kind}/{spec-id}/contracts/*.md`
- Read related specs if referenced
- Read code if needed

### 4. Complete sections intelligently
Fill in each section using:
- Contract analysis
- Code inference
- Reasonable assumptions
- **Ask user ≤3 clarifying questions** (only when truly needed)

Sections to complete:
- Section 1: Intent & Summary
- Section 3: Requirements (FR/NF)
- Section 4: Architecture & Design
- Section 6: Testing Strategy
- YAML blocks (relationships, capabilities, verification)

### 5. Validate
```bash
uv run spec-driver sync
uv run spec-driver validate
```

### 6. Evidence
Document what was completed and key decisions made.

## Quality Standards
- [ ] All YAML blocks valid
- [ ] Requirements testable and linked
- [ ] Capabilities map to requirements
- [ ] Architecture section has substance
- [ ] Testing strategy concrete
- [ ] Assumptions documented where made

## Notes
- Make reasonable assumptions rather than asking questions
- Mark assumptions clearly in spec (e.g., "Assuming X based on Y")
- Only ask user if decision significantly impacts design
- Prefer inferring from contracts over guessing
```

#### Task 1.6: Integration Testing (SIMPLIFIED)
**Purpose**: End-to-end validation

Tests:
1. CLI: `test_backfill_integration()` - full workflow programmatic
2. Manual: Backfill real stub spec, verify completeness
3. Validation: `just test && just lint && just pylint`

## Task Summary

| Task | What Changed | Status |
|------|--------------|--------|
| 1.1 | Keep for now (may delete later) | ✅ Complete |
| 1.2 | Unchanged (status-based detection) | ⏸️ Todo |
| 1.3 | **DELETED** (completion module removed) | ❌ Removed |
| 1.4 | Simplified: just replace body with template | ⏸️ Todo |
| 1.5 | Revised: agent does intelligent completion | ⏸️ Todo |
| 1.6 | Simplified: basic integration test | ⏸️ Todo |

## Benefits of New Design

1. **Simpler code**: CLI does mechanical work only
2. **More flexible**: Agents can adapt completion strategy
3. **Less brittle**: No assumptions about "correct" spec structure
4. **Faster to implement**: Fewer edge cases to handle
5. **Better separation**: CLI = mechanics, Agent = intelligence

## What Agents Do Better
- Analyzing contracts for meaning
- Inferring requirements from code
- Making design decisions
- Asking clarifying questions
- Adapting to spec variations

## What CLI Does Better
- File I/O operations
- Stub detection (status + line count)
- Template rendering
- Validation that spec exists
- Preventing accidental overwrites
