# Requirements Additions - 2025-11-04

## Summary

Added 5 new functional requirements to PROD-010 (CLI Agent UX) covering command consistency, discoverable help, and file validation.

## New Requirements

### FR-011: Backlog Command Shortcuts
**Requirement**: CLI MUST provide kind-specific backlog list shortcuts (issues/problems/improvements/risks)

**Rationale**: Consistent with other artifact patterns (specs/deltas/adrs/requirements); reduces cognitive load

**Commands**:
- `list issues`
- `list problems`
- `list improvements`
- `list risks`

All equivalent to `list backlog -k <kind>` but more discoverable and consistent with `create issue|problem|improvement|risk` pattern.

**Verification**: VT-PROD010-BACKLOG-001

---

### FR-012: Built-in Help System
**Requirement**: CLI MUST provide help command showing core concepts, workflows, and conventions from markdown sources

**Rationale**: Agents and users need discoverable help without consulting external docs or web searches

**Commands**:
- `help concepts` - Core spec-driver concepts
- `help workflows` - Standard workflows (authoring, implementation, review)
- `help conventions` - Naming, structure, patterns

**Current Gap**: No built-in help system; users must read GitHub docs or local files manually

**Verification**: VT-PROD010-HELP-001

---

### FR-013: Help Doc Categories
**Requirement**: Help system MUST distinguish between immutable (spec-driver core) and customizable (project-specific) documentation

**Rationale**: Users need to know what they can modify vs what represents framework fundamentals

**Implementation**:
- Immutable docs served from package installation
- Customizable docs served from project directory (e.g., `.spec-driver/docs/`)
- Help command indicates source: `[core]` vs `[project]`

**Example**:
```
$ spec-driver help workflows
=== Workflows [core] ===
Framework-defined workflows...

=== Workflows [project] ===
Custom project workflows...
```

**Verification**: VT-PROD010-HELP-002

---

### FR-014: Install Help Templates
**Requirement**: CLI MUST support installing customizable help docs to project for user modification

**Rationale**: Projects need to document their own workflows and conventions alongside framework docs

**Commands**:
- `help install workflows` - Install workflow template
- `help install conventions` - Install conventions template
- `install help-templates` - Install all help templates

**Implementation**: Copy markdown templates from package to `.spec-driver/docs/` for user editing

**Verification**: VT-PROD010-HELP-003

---

### FR-015: Per-File Validation
**Requirement**: CLI MUST support per-file validation of frontmatter and YAML blocks

**Rationale**: Users need to validate individual files during authoring without running full workspace validation

**Commands**:
- `validate file <path>` - Validate frontmatter schema and all embedded YAML blocks
- `validate file <path> --json` - Machine-readable output
- `validate file <path> --strict` - Enforce stricter rules

**Validation Coverage**:
- Frontmatter schema validation against kind
- All embedded YAML blocks (supekku:* schemas)
- Required field presence
- Type checking
- Enum value validation

**Current Gap**: Only workspace-level validation exists; no targeted file validation for authoring workflow

**Verification**: VT-PROD010-VALIDATE-001

---

## Updated Capability Overview

PROD-010 now provides **7 core capabilities** (was 6):

1. **Consistent JSON Output** (FR-001, FR-002)
2. **Universal Filtering** (FR-003, FR-004, FR-005)
3. **Schema Introspection** (FR-006, FR-007)
4. **Discoverable Help System** (FR-012, FR-013, FR-014, FR-015) ← NEW
5. **Machine-Readable Mode** (FR-008, FR-009, NF-001)
6. **Improved Error Guidance** (FR-010, NF-002)
7. **Command Consistency** (FR-011) ← NEW

## Priority Classification

New requirements added to **Priority 3: Self-Documentation** and **Priority 6: Command Consistency**:

- **Priority 3**: FR-012, FR-013, FR-014, FR-015 (Help and validation)
- **Priority 6**: FR-011 (Backlog shortcuts)

## Implementation Notes

### Help System Design Considerations

1. **Markdown Source Management**:
   - Core docs in package: `supekku/docs/{concepts,workflows,conventions}.md`
   - Project docs in: `.spec-driver/docs/{concepts,workflows,conventions}.md`
   - Load order: project overrides core (or display both)

2. **Template Structure**:
   ```markdown
   # Workflows [Customizable]

   ## Implementation Workflow
   [Your project's implementation process]

   ## Review Workflow
   [Your project's review process]
   ```

3. **Help Command Structure**:
   - `spec-driver help` - Show available topics
   - `spec-driver help <topic>` - Display topic content
   - `spec-driver help install <topic>` - Install template
   - `spec-driver help list` - List all help files (core + project)

### File Validation Design Considerations

1. **Scope**:
   - Single file validation only
   - No cross-file relationship validation (use `validate` for that)
   - Fast feedback for authoring workflow

2. **Error Output**:
   ```
   $ spec-driver validate file specify/tech/SPEC-110/SPEC-110.md

   ✓ Frontmatter: Valid (kind: spec)
   ✓ supekku.spec.relationships@v1 (line 35)
   ✗ supekku.spec.capabilities@v1 (line 88)
     - Missing required field: capabilities[0].requirements
     - Invalid field: capabilities[0].unknown_field

   1 block with errors
   ```

3. **Integration**:
   - Can be called from editor integrations
   - Fast enough for on-save validation
   - JSON output for tool integration

## Testing Requirements

All new requirements have corresponding verification artifacts:

- VT-PROD010-BACKLOG-001: Test backlog shortcuts with filters
- VT-PROD010-HELP-001: Test help command displays markdown
- VT-PROD010-HELP-002: Test help distinguishes core vs project
- VT-PROD010-HELP-003: Test help template installation
- VT-PROD010-VALIDATE-001: Test per-file validation

## Related Work

- UX Research Report: `docs/ux-research-cli-2025-11-03.md` Section 10 (Principle of Least Surprise)
- SPEC-110: supekku/cli Specification (implementation target)
- AGENTS.md: Architectural constraints for CLI implementation

## Next Steps

1. Fix FR-011 requirements regex extraction bug (another agent working on this)
2. Implement backlog shortcuts (FR-011) - straightforward delegation to existing `list backlog -k`
3. Design help system architecture (FR-012, FR-013, FR-014)
4. Implement file validation command (FR-015) - extend existing validation infrastructure
