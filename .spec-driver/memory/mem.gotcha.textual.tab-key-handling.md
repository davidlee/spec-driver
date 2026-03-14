---
id: mem.gotcha.textual.tab-key-handling
name: "Textual Tab key: use Binding, not key_tab"
kind: memory
status: active
memory_type: gotcha
created: "2026-03-08"
updated: "2026-03-08"
tags:
  - textual
  - tui
  - keybindings
  - focus
summary:
  Textual app-level focus chain consumes Tab before widget key_tab handlers
  fire. Use Binding('tab', 'action_name') on the widget instead.
---

# Textual Tab key: use Binding, not key_tab

## Problem

Textual's `key_tab` method on a widget (e.g. `Tree.key_tab`) does **not**
intercept the Tab key. The app-level focus chain processes Tab before it reaches
widget key handlers, so the default focus cycling takes over.

## Fix

Use a `Binding` on the widget class instead — bindings take priority over the
app focus chain:

```python
class BundleTree(Tree[Path]):
    BINDINGS = [
        Binding("tab", "focus_artifact_table", show=False),
    ]

    def action_focus_artifact_table(self) -> None:
        self.screen.query_one("#artifact-table").focus()
```

## Discovered

DE-061 Phase 2, task 2.5 (focus management). Confirmed by pilot test failure
where `key_tab` was silently ignored and focus went to the next widget in the
default Tab cycle instead of the explicit target.
