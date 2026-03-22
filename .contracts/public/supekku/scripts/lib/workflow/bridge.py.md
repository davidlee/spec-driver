# supekku.scripts.lib.workflow.bridge

Bridge block extraction and rendering for workflow orchestration.

Handles notes-bridge (§7.1) and phase-bridge (§7.2) fenced YAML blocks
in markdown files.

Design authority: DR-102 §7.

## Functions

- `extract_notes_bridge(text) -> <BinOp>`: Extract notes-bridge block from notes.md.

Returns parsed dict or None if no block found.
- `extract_phase_bridge(text) -> <BinOp>`: Extract phase-bridge block from phase sheet markdown.

Returns parsed dict or None if no block found.
- `render_notes_bridge() -> str`: Render a notes-bridge fenced YAML block.

Returns the full fenced block string ready for insertion into notes.md.
- `render_phase_bridge() -> str`: Render a phase-bridge fenced YAML block.

Returns the full fenced block string ready for insertion into phase sheets.
