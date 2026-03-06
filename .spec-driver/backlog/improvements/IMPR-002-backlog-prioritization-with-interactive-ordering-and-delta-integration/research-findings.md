# IMPR-002 Research Findings

## Current State Analysis

### Backlog Architecture

**Domain Model** (`supekku/scripts/lib/backlog/models.py`):
- `BacklogItem` dataclass with fields: id, kind, status, title, path, frontmatter
- Kind-specific fields: severity (p1/p2/p3), categories, impact, likelihood, created, updated
- No priority or ordering field currently exists

**Registry** (`supekku/scripts/lib/backlog/registry.py`):
- `discover_backlog_items()` - discovers items from filesystem
- Returns items **sorted by ID** (line 320): `return sorted(items, key=lambda x: x.id)`
- No ordering persistence mechanism exists
- No backlog registry YAML file (unlike deltas, decisions, requirements which have `.spec-driver/registry/*.yaml`)

**CLI** (`supekku/cli/list.py`):
- `list_backlog()` command at line 1168-1245
- Supports filters: `--kind`, `--status`, `--filter` (substring), `--regexp`
- Outputs: table (default), json, tsv
- No ordering options currently available

**Formatters** (`supekku/scripts/lib/formatters/backlog_formatters.py`):
- `format_backlog_list_table()` - renders items as rich table
- Displays: ID, Kind, Status, Title, Severity columns
- Severity field already exists and is displayed
- Comment at line 86: "Get severity/priority if available (issues and risks have it)"

### Existing Prioritization Concept

From `supekku/about/backlog.md` (lines 23-24):
> "Prioritisation lives in dedicated Markdown lists (e.g. `backlog/backlog.md`). The list order is canonical; scripts ensure new artefacts get appended, while humans/agents reorder lines to reflect priority."

**Key insight:** There's a documented *intent* for priority lists but it's not currently implemented in the tooling.

### Severity Field

Actual values from backlog items: `p1`, `p2`, `p3` (with p3 being most common in current data)
- Issues have severity field
- Improvements do not have severity field
- Current ordering is purely chronological by ID

## Implementation Areas

### 1. Ordering Storage

**Options:**

A. **Backlog Registry** (recommended, aligns with existing patterns):
   - Create `.spec-driver/registry/backlog.yaml`
   - Store ordering metadata alongside item metadata
   - Parallel to decisions.yaml, requirements.yaml, etc.
   - Structure:
     ```yaml
     items:
       ISSUE-003:
         kind: issue
         status: in-progress
         priority_index: 1
       IMPR-002:
         kind: improvement
         status: idea
         priority_index: 2
     ```

B. **Priority field in frontmatter**:
   - Add `priority: <int>` to each backlog item's frontmatter
   - More distributed, harder to maintain consistency
   - Doesn't align with existing registry pattern

C. **Separate priority list file**:
   - `backlog/priority-order.md` or `.spec-driver/backlog-order.yaml`
   - Just ordered list of IDs
   - Simpler but loses context

**Recommendation:** Option A (Backlog Registry) - consistent with existing architecture patterns

### 2. Ordering Logic

**Default Sort Order (when implemented):**
1. User-specified priority (if exists)
2. Severity (p1 > p2 > p3) for items without user priority
3. ID (chronological fallback)

**Implementation location:**
- New function in `supekku/scripts/lib/backlog/registry.py`
- `def sort_backlog_items(items: list[BacklogItem], *, order_by: str = "priority") -> list[BacklogItem]`
- Read priority data from backlog registry

### 3. Interactive Editor Flow

**New CLI command flag:**
- Add `--prioritize` / `--prioritise` to `list_backlog()` and related commands
- When enabled:
  1. Get filtered items based on other flags
  2. Generate markdown list representation
  3. Launch `$EDITOR` (or fallback: `VISUAL`, then `vi`)
  4. Parse edited list to extract ordering
  5. Merge ordering with existing priority data (preserve unshown items)
  6. Write to backlog registry

**Editor format:**
```markdown
# Backlog Priority Order

Reorder items below by moving lines up/down. Save and exit to apply.

- [ ] ISSUE-003: Create supekku/INIT.md with spec-driver invocation patterns
- [ ] IMPR-002: Backlog prioritization with interactive ordering
- [ ] ISSUE-005: Implement orphan detection protection
```

**Components needed:**
- Editor invocation utility (new in `supekku/scripts/lib/core/`)
- Markdown list parser
- Priority merge algorithm (handles sparse/filtered lists)

### 4. Registry Sync

**New sync operation:**
- Add `sync backlog` command
- Scan `backlog/*/` directories
- Generate/update `.spec-driver/registry/backlog.yaml`
- Similar to existing `sync decisions`, `sync specs` commands

**Location:**
- `supekku/cli/sync.py` - add new command
- `supekku/scripts/lib/backlog/registry.py` - add sync function

### 5. CLI Enhancements

**New flags for `list backlog`:**
- `--prioritize` / `--prioritise` - interactive ordering mode
- `--order-by-id` / `-o` - explicit ID-based ordering (current behavior)

**Default behavior change:**
- When registry exists with priority data: use priority ordering
- When registry doesn't exist: fallback to ID ordering
- User can always override with `--order-by-id`

### 6. Delta Integration

**`create delta --from-backlog ITEM-ID`:**

Location: `supekku/cli/create.py` - enhance existing `create_delta()` command

Template population:
- Read backlog item frontmatter
- Extract title, status, related requirements
- Pre-populate delta template with context
- Link delta back to backlog item via frontmatter relation

## Dependencies & Constraints

### External Dependencies

No new external dependencies required. Use existing:
- `typer` - CLI framework
- `rich` - table formatting
- `yaml` - registry files
- Standard library: `os.environ`, `subprocess`, `tempfile` for editor invocation

### Architectural Constraints

1. **Maintain thin CLI pattern** - delegate logic to domain layer
2. **Pure functions in formatters** - no business logic
3. **Test-first development** - write tests before implementation
4. **No premature abstraction** - specific before generic

### Integration Points

**Files requiring modification:**
- `supekku/scripts/lib/backlog/models.py` - add priority field to BacklogItem
- `supekku/scripts/lib/backlog/registry.py` - add ordering, sync, merge functions
- `supekku/cli/list.py` - add --prioritize, --order-by-id flags
- `supekku/cli/sync.py` - add sync backlog command
- `supekku/cli/create.py` - add --from-backlog flag to create delta

**New files needed:**
- `supekku/scripts/lib/core/editor.py` - editor invocation utility
- `supekku/scripts/lib/backlog/priority.py` - priority management logic
- `.spec-driver/registry/backlog.yaml` - registry file (generated)
- Test files for all new modules

## Merge Algorithm: Head-Tail Partitioning

The core challenge is merging user-provided ordering (from filtered subset) with existing global ordering while preserving positions of filtered-out items.

### Mental Model

Think of the ordered list as partitions of `(shown_item, [unshown_followers])` pairs:

**Example:**
```
Original items: a b c d e f g h i
Filtered view (shows only): B F G

Partitioned structure:
[nil, [a]]      # Prefix: items before first shown item
[B, [c,d,e]]    # B followed by its unshown tail
[F, []]         # F with no followers
[G, [h,i]]      # G followed by its unshown tail
```

When user reorders to `G, B, F`, the **tails move atomically with their heads**:
```
[G, [h,i]]      # G's tail moves with it
[B, [c,d,e]]    # B's tail moves with it
[F, []]         # F's (empty) tail moves with it
```

**Flattened result:** `a g h i b c d e f`

### Key Properties

- **Tails are immutable** - unshown items always stay with their head
- **Reordering is atomic** - move (head, tail) pairs as units
- **Preservation is automatic** - relative order within tails never changes
- **New items append to end** - clear, predictable behavior
- **Storage is flat** - simple priority index array after merge

### Implementation Sketch

```python
def build_partitions(all_items, filtered_items):
  """Partition items into (shown, [unshown_followers]) pairs.

  Returns: [(head, [tail_items]), ...] plus prefix items
  """
  prefix = []
  partitions = []
  current_tail = []
  seen_first_shown = False

  for item in all_items:
    if item in filtered_items:
      seen_first_shown = True
      partitions.append((item, current_tail))
      current_tail = []
    else:
      if not seen_first_shown:
        prefix.append(item)
      else:
        current_tail.append(item)

  # Handle trailing unshown items
  if current_tail:
    partitions.append((None, current_tail))

  return prefix, partitions

def merge_ordering(prefix, partitions, new_filtered_order):
  """Reorder partitions based on new filtered order, then flatten."""
  # Create lookup for partitions by head
  partition_map = {head: (head, tail) for head, tail in partitions if head}

  # Reorder based on new_filtered_order
  result = prefix.copy()

  for head in new_filtered_order:
    if head in partition_map:
      head_item, tail_items = partition_map[head]
      result.append(head_item)
      result.extend(tail_items)

  # Handle any trailing unshown items (partitions with None head)
  for head, tail in partitions:
    if head is None:
      result.extend(tail)

  return result

```

### Complexity Assessment

**Simple:**
- Building partitions: O(n) single pass
- Reordering partitions: O(m) where m = filtered items
- Flattening: O(n)

**Edge cases handled:**
- Empty filter (no shown items): all items stay in original order
- All items filtered: straightforward reorder with no tails
- Items created during edit session: append to end
- Items deleted from filesystem: skip during partition build

### Storage Format

Registry stores **ordered list of IDs**. Position in list = priority.

```yaml
ordering:
  - ISSUE-003
  - IMPR-002
  - ISSUE-005
  - ISSUE-009
```

That's it. No indices, no gaps, no floating point. The list order is canonical.

## Open Questions

1. **Registry schema details:**
   - Should registry track all backlog metadata or just priority?
   - How to handle items deleted from filesystem but still in registry?

2. **Conflict resolution:**
   - What happens if user manually edits two items to same priority_index?
   - How to handle items renamed/deleted during interactive session?

3. **Sync frequency:**
   - Should priority data auto-sync like decisions do?
   - Or require explicit `sync backlog` call?

4. **Requirements in backlog items:**
   - Current frontmatter schema already supports `related_requirements` field
   - Need to verify this is properly parsed and displayed
   - Add validation in sync command

## Next Steps

1. Write detailed implementation plan (create IP document)
2. Create phase sheets for incremental delivery
3. Start with foundational pieces:
   - Backlog registry structure
   - Sync command
   - Registry read/write utilities
4. Then add priority ordering (without interactive editing)
5. Finally add interactive editor flow
6. Conclude with delta integration

## Effort Estimate

**Rough complexity breakdown:**

- Backlog registry + sync: **Medium** (similar to existing registries)
- Priority ordering logic: **Small** (sorting with custom key)
- Interactive editor flow: **Medium** (editor invocation, parsing, merge algorithm)
- CLI integration: **Small** (flags and orchestration)
- Delta integration: **Small** (template population)
- Testing: **Medium** (comprehensive coverage needed)

**Total:** ~5-8 focused work sessions for complete implementation
