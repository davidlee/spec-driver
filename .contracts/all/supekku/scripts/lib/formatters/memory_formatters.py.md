# supekku.scripts.lib.formatters.memory_formatters

Memory display formatters.

Pure formatting functions with no business logic.
Formatters take MemoryRecord objects and return formatted strings for display.

## Functions

- `_calculate_column_widths(terminal_width) -> dict[Tuple[int, int]]`: Calculate column widths for memory table based on terminal width.
- `_format_dates(record) -> list[str]`: Format date fields if present.
- `_format_detail_lines(record) -> list[str]`: Build lines for a memory detail view, omitting empty optional fields.
- `_format_links(links) -> list[str]`: Format links dict as indented sub-lines.
- `_format_priority(priority) -> list[str]`: Format priority dict as indented sub-lines.
- `_format_provenance(provenance) -> list[str]`: Format provenance dict as indented sub-lines.
- `_format_relations(relations) -> list[str]`: Format relations list as indented entries.
- `_format_scope(scope) -> list[str]`: Format scope dict as indented sub-lines.
- `_prepare_memory_row(record) -> list[str]`: Prepare a single row for the memory table.
- `_prepare_memory_tsv_row(record) -> list[str]`: Prepare a single memory record as a plain TSV row (no markup).
- `format_link_graph_json(nodes) -> str`: Format link graph nodes as JSON array.

Args:
  nodes: List of LinkGraphNode objects.

Returns:
  JSON string with list of node dicts.
- `format_link_graph_table(nodes) -> str`: Format link graph nodes as a compact table.

Columns: depth, id, name, type.

Args:
  nodes: List of LinkGraphNode objects (BFS order).

Returns:
  Formatted table string. Empty string if no nodes.
- `format_link_graph_tree(nodes) -> str`: Format link graph nodes as an indented tree.

Each depth level is indented by two spaces. Shows id and name.

Args:
  nodes: List of LinkGraphNode objects (BFS order).

Returns:
  Formatted tree string. Empty string if no nodes.
- `format_memory_details(record) -> str`: Format a memory record as multi-line detail string.

Args:
  record: MemoryRecord to format.

Returns:
  Human-readable detail string.
- `format_memory_list_json(records) -> str`: Format memory records as JSON array.

Args:
  records: List of MemoryRecord objects.

Returns:
  JSON string with structure: {"items": [...]}.
- `format_memory_list_table(records, format_type, truncate) -> str`: Format memory records as table, JSON, or TSV.

Args:
  records: List of MemoryRecord objects.
  format_type: Output format (table|json|tsv).
  truncate: If True, truncate long fields.

Returns:
  Formatted string in requested format.
