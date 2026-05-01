---
id: ISSUE-054
name: list deltas dumps Rich traceback when a phase file has invalid YAML frontmatter
created: "2026-05-01"
updated: "2026-05-01"
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# list deltas dumps Rich traceback when a phase file has invalid YAML frontmatter

## Symptom

`spec-driver list deltas` (and likely siblings) crashes with a full Rich
traceback when any phase file under a delta has a YAML parse error in its
frontmatter. The user-facing output is a stack trace ending in
`yaml.scanner.ScannerError: mapping values are not allowed in this context`
with no indication of which file or line is at fault.

## Root cause

`load_change_artifact` (`supekku/scripts/lib/changes/artifacts.py:180`) wraps
the per-phase-file `load_markdown_file` call in
`except (ValueError, OSError)`. PyYAML raises `yaml.YAMLError` (e.g.
`ScannerError`), which is not a subclass of either, so the parse error
escapes the per-file guard.

The surrounding `ChangeRegistry.collect()` catch
(`supekku/scripts/lib/changes/registry.py:84-87`) is also `except ValueError`,
so the YAML error propagates all the way out to the CLI handler and is
rendered as a traceback rather than a friendly message.

The same pattern likely affects sibling loaders (specs, decisions,
backlog) wherever `load_markdown_file` is called inside `except ValueError`.

## Expected

- A clear, actionable message identifying the offending file and ideally the
  line/column of the YAML error (consistent with PROD-010.FR-010).
- The command should skip the bad file and continue listing the rest, or fail
  fast with a clear error — but never dump a Python traceback.

## Repro

1. Edit any `.spec-driver/deltas/DE-XXX/phases/phase-0N.md` so its frontmatter
   contains a YAML parse error (e.g. an unquoted colon inside a value).
2. Run `spec-driver list deltas`.
3. Observe Rich traceback instead of a friendly diagnostic.
