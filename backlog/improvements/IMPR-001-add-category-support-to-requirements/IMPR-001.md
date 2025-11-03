---
id: IMPR-001
name: Add category support to requirements
created: '2025-11-04'
updated: '2025-11-04'
status: idea
kind: improvement
---

# Add category support to requirements

## Problem

Requirements currently lack categorization, making it difficult to filter and organize them by functional area, quality attribute, or concern. This limits the ability to efficiently navigate large requirement sets and understand requirement distribution across categories.

## Proposed Solution

Add category support to requirements with the following capabilities:

### 1. Category Definition Syntax

Requirements can specify categories inline using parenthetical notation:

```markdown
**NF-001**(performance): System shall respond within 100ms
**FR-042**(authentication): User shall provide valid credentials
```

Categories should also be supported in spec frontmatter YAML:

```yaml
requirements:
  - id: NF-001
    category: performance
    description: System shall respond within 100ms
```

### 2. Requirements List Command Enhancements

- Add `--category` filter for case-sensitive substring matching on category names
- Display category as a column in list output
- Support regexp filter (`-r/--regexp`) operating on category field
- Support case-insensitive filter (`-i/--ignore-case`) for category matching

### 3. Data Model Changes

- Add `category` attribute to requirement model
- Parse category from inline `**REQ-ID**(category):` syntax
- Parse category from YAML frontmatter `category:` attribute
- Store category in requirements registry

## Expected Benefits

- **Improved Navigation**: Filter requirements by functional area (auth, storage, reporting)
- **Quality Focus**: Easily view all security, performance, or reliability requirements
- **Spec Organization**: Understand requirement distribution across categories
- **Better Reports**: Generate category-based coverage reports and metrics

## Implementation Scope

### Parser Changes
- Extend requirement inline syntax parser to capture category from parenthetical notation
- Extend YAML frontmatter parser to read `category` attribute
- Update requirement model to include optional `category` field

### CLI Changes
- Add `--category` option to `spec-driver list requirements`
- Add category column to default list output format
- Extend regexp and case-insensitive filters to operate on category field

### Registry Changes
- Include `category` in requirements registry YAML
- Update registry sync to preserve category metadata

### Testing
- Unit tests for category parsing (inline and YAML)
- Integration tests for category filtering
- Test edge cases: missing category, special characters, whitespace

## Examples

### Filtering by category
```bash
# Show all performance requirements
spec-driver list requirements --category performance

# Show all authentication requirements (case-insensitive)
spec-driver list requirements --category auth -i

# Show requirements matching category pattern
spec-driver list requirements --category 'auth|security' -r
```

### List output with categories
```
ID       Category        Status      Description
FR-001   authentication  proposed    User login with credentials
FR-002   authentication  accepted    Password complexity rules
NF-001   performance     accepted    Response time under 100ms
NF-002   reliability     proposed    99.9% uptime SLA
```

## Architectural Decisions

### Hierarchy Support
Categories support user-defined hierarchy delimiters (e.g., `/`, `.`, `::`). No formal hierarchy structure is enforced - users are free to adopt conventions that suit their needs:
- `security/authentication`
- `performance.database`
- `ui::accessibility`

Filtering treats categories as simple strings (substring/regexp matching), allowing flexible querying regardless of delimiter choice.

### Taxonomy Validation
No predefined taxonomy. Categories are freeform text, promoting ease of use and adaptability to different domain models. Teams can establish conventions in their project documentation if desired.

### Categorization Requirement
Categories are **optional**. Uncategorized requirements display an empty category column or a configurable placeholder (e.g., `-` or `uncategorized`).

### Precedence Rules
Following existing requirement merge patterns:

**Body content takes precedence over frontmatter** for descriptive fields (consistent with current `title`, `kind`, `path` behavior).

When a requirement is defined in both locations:
1. **Body syntax** `**FR-001**(auth): description` → category is `auth`
2. **Frontmatter YAML** includes `category: security` → ignored during merge
3. **Result**: category = `auth` (body wins)

This ensures:
- Source of truth is visible in the spec body where requirements are read
- Consistent with existing merge behavior for `title` and `kind`
- Simple mental model: body content is authoritative for requirement definition

**Fallback behavior**: If only frontmatter defines category (no inline category in body), use frontmatter value. This supports legacy specs or alternative authoring styles.

### Implementation Notes
The merge strategy in `RequirementRecord.merge()` already establishes this pattern:
```python
return RequirementRecord(
  # ... existing fields preserved
  title=other.title,           # new record (body) wins
  kind=other.kind or self.kind,  # new record preferred
  path=other.path or self.path,  # new record preferred
)
```

Category should follow the same pattern: `category=other.category or self.category`
