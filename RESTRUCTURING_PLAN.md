# SpecDriver Lib Restructuring Plan

## Overview

Reorganize `supekku/scripts/lib/` from 70 flat modules into domain-based packages.

**Principles**:
- Minimal code refactoring (move files, update imports only)
- Preserve git history with `git mv`
- Test after each domain migration
- Maintain backward compatibility via `__init__.py` re-exports during transition

## Target Structure

```
supekku/scripts/lib/
├── core/                    # Foundation (NEW)
│   ├── __init__.py
│   ├── paths.py             # MOVED from lib/
│   ├── spec_utils.py        # MOVED from lib/
│   ├── frontmatter_schema.py # MOVED from lib/
│   ├── cli_utils.py         # MOVED from lib/
│   └── repo.py              # EXTRACTED from backlog.py::find_repo_root()
│
├── specs/                   # Specifications domain (NEW)
│   ├── __init__.py
│   ├── registry.py          # RENAMED from spec_registry.py
│   ├── models.py            # RENAMED from spec_models.py
│   ├── index.py             # RENAMED from spec_index.py
│   ├── creation.py          # RENAMED from create_spec.py
│   ├── blocks.py            # RENAMED from spec_blocks.py
│   └── *_test.py
│
├── decisions/               # ADR domain (NEW)
│   ├── __init__.py
│   ├── registry.py          # RENAMED from decision_registry.py
│   ├── creation.py          # RENAMED from decision_creation.py
│   └── *_test.py
│
├── changes/                 # Change artifacts domain (NEW)
│   ├── __init__.py
│   ├── registry.py          # RENAMED from change_registry.py
│   ├── artifacts.py         # RENAMED from change_artifacts.py
│   ├── creation.py          # RENAMED from create_change.py
│   ├── lifecycle.py         # RENAMED from change_lifecycle.py
│   ├── completion.py        # RENAMED from completion_revision.py
│   ├── discovery.py         # RENAMED from revision_discovery.py
│   ├── updater.py           # RENAMED from revision_updater.py
│   ├── blocks/              # (NEW)
│   │   ├── __init__.py
│   │   ├── delta.py         # RENAMED from delta_blocks.py
│   │   ├── revision.py      # RENAMED from revision_blocks.py
│   │   └── plan.py          # RENAMED from plan_blocks.py
│   └── *_test.py
│
├── requirements/            # Requirements domain (NEW)
│   ├── __init__.py
│   ├── registry.py          # SPLIT from requirements.py
│   ├── models.py            # SPLIT from requirements.py
│   ├── lifecycle.py         # SPLIT from requirements.py (+ from lifecycle.py)
│   ├── parser.py            # SPLIT from requirements.py
│   ├── sync.py              # SPLIT from requirements.py
│   └── *_test.py
│
├── backlog/                 # Backlog domain (NEW)
│   ├── __init__.py
│   ├── registry.py          # RENAMED from backlog.py (minus find_repo_root)
│   └── *_test.py
│
├── sync/                    # Spec sync domain (RENAMED)
│   ├── __init__.py
│   ├── engine.py            # MOVED from spec_sync/engine.py
│   ├── models.py            # MOVED from spec_sync/models.py
│   ├── adapters/            # MOVED from spec_sync/adapters/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── go.py
│   │   ├── python.py
│   │   └── typescript.py
│   └── *_test.py
│
├── docs/                    # Doc generation (KEEP AS-IS)
│   └── python/
│       └── (... existing modules ...)
│
├── deletion/                # Deletion domain (NEW)
│   ├── __init__.py
│   ├── planner.py           # SPLIT from deletion.py
│   ├── scanner.py           # SPLIT from deletion.py
│   ├── executor.py          # SPLIT from deletion.py
│   └── *_test.py
│
├── relations/               # Relations domain (NEW)
│   ├── __init__.py
│   ├── models.py            # SPLIT from relations.py
│   └── manager.py           # SPLIT from relations.py
│
├── validation/              # Validation domain (NEW)
│   ├── __init__.py
│   └── validator.py         # MOVED from lib/validator.py
│
└── formatters/              # Display formatting (KEEP AS-IS)
    ├── __init__.py
    ├── spec_formatters.py
    ├── change_formatters.py
    └── decision_formatters.py
```

## Migration Phases

### Phase 0: Preparation
- [x] Create this migration plan
- [ ] Ensure all tests pass before starting
- [ ] Create git branch for restructuring

### Phase 1: Core Foundation
1. Create `core/` package
2. Move: paths.py, spec_utils.py, frontmatter_schema.py, cli_utils.py
3. Extract `find_repo_root()` from backlog.py → core/repo.py
4. Update imports in lib/ modules
5. Run tests

### Phase 2: Specs Domain
1. Create `specs/` package
2. Move & rename: spec_registry.py, spec_models.py, spec_index.py, create_spec.py, spec_blocks.py
3. Update imports
4. Run tests

### Phase 3: Decisions Domain
1. Create `decisions/` package
2. Move & rename: decision_registry.py, decision_creation.py
3. Update imports
4. Run tests

### Phase 4: Changes Domain
1. Create `changes/` package and `changes/blocks/` subpackage
2. Move & rename: change_registry.py, change_artifacts.py, create_change.py, change_lifecycle.py
3. Move & rename blocks: delta_blocks.py, revision_blocks.py, plan_blocks.py
4. Move: completion_revision.py, revision_discovery.py, revision_updater.py
5. Update imports
6. Run tests

### Phase 5: Requirements Domain (COMPLEX)
1. Create `requirements/` package
2. Split requirements.py into 5 modules:
   - models.py (RequirementRecord dataclass)
   - lifecycle.py (status constants)
   - parser.py (extract_requirements_from_spec)
   - registry.py (RequirementsRegistry)
   - sync.py (sync_with_changes)
3. Update imports
4. Run tests

### Phase 6: Remaining Domains
1. Create packages: backlog/, deletion/, relations/, validation/
2. Move/split modules
3. Update imports
4. Run tests

### Phase 7: Sync Domain Consolidation
1. Rename spec_sync/ → sync/
2. Delete old sync_engine.py (verify unused first)
3. Update imports
4. Run tests

### Phase 8: CLI & Scripts Layer
1. Update all imports in supekku/cli/*.py
2. Update all imports in supekku/scripts/*.py
3. Run tests

### Phase 9: Backward Compatibility (OPTIONAL)
1. Add re-exports in lib/__init__.py for critical imports
2. Document deprecation warnings
3. Run tests

### Phase 10: Cleanup
1. Run linter on all changed files
2. Update documentation
3. Update kanban card
4. Create PR

## Import Update Pattern

For each moved module, update imports following this pattern:

**Before**:
```python
from .spec_utils import load_markdown_file
from .paths import get_templates_dir
from .frontmatter_schema import validate_frontmatter
```

**After**:
```python
from .core.spec_utils import load_markdown_file
from .core.paths import get_templates_dir
from .core.frontmatter_schema import validate_frontmatter
```

## Testing Strategy

After each phase:
```bash
just test         # Run all tests
just lint         # Check linting
just pylint       # Check pylint
```

## Rollback Strategy

If tests fail:
1. Identify breaking change
2. Fix imports or revert phase with `git reset --hard`
3. Re-run tests
4. Continue from stable state

## Risk Mitigation

- **High risk modules** (depended by 5+ modules):
  - spec_utils.py → core/spec_utils.py (15+ dependents)
  - paths.py → core/paths.py (8+ dependents)
  - frontmatter_schema.py → core/frontmatter_schema.py (6+ dependents)

- **Mitigation**: Update these first, test thoroughly before proceeding

## Success Criteria

- [ ] All tests pass
- [ ] All lint checks pass
- [ ] No circular imports
- [ ] CLI commands still work
- [ ] Git history preserved for all moved files
- [ ] Code organization clearer (domain-based packages)
