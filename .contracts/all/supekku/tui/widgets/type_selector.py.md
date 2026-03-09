# supekku.tui.widgets.type_selector

Type selector widget — flat OptionList, colour-grouped (DEC-053-10).

## Classes

### TypeSelected

Posted when the user selects an artifact type.

**Inherits from:** Message

#### Methods

- `__init__(self, artifact_type) -> None`

### TypeSelector

Artifact type selector with colour-grouped labels.

**Inherits from:** OptionList

#### Methods

- `on_mount(self) -> None`
- `on_option_list_option_selected(self, event) -> None`
- `refresh_counts(self, counts) -> None`: Update type counts and rebuild the option list.
- `__init__(self, counts) -> None`
- `_rebuild_options(self) -> None`
