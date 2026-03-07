"""Type selector widget — flat OptionList, colour-grouped (DEC-053-10)."""

from __future__ import annotations

from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from supekku.scripts.lib.core.artifact_view import ArtifactType
from supekku.scripts.lib.formatters.theme import styled_text


class TypeSelected(Message):
  """Posted when the user selects an artifact type."""

  def __init__(self, artifact_type: ArtifactType) -> None:
    super().__init__()
    self.artifact_type = artifact_type


class TypeSelector(OptionList):
  """Artifact type selector with colour-grouped labels."""

  def __init__(
    self,
    counts: dict[ArtifactType, int] | None = None,
    **kwargs,
  ) -> None:
    super().__init__(**kwargs)
    self._counts = counts or {}

  def on_mount(self) -> None:
    self._rebuild_options()

  def refresh_counts(
    self,
    counts: dict[ArtifactType, int],
  ) -> None:
    """Update type counts and rebuild the option list."""
    self._counts = counts
    self._rebuild_options()

  def _rebuild_options(self) -> None:
    self.clear_options()
    for art_type in ArtifactType:
      count = self._counts.get(art_type, 0)
      group_style = f"artifact.group.{art_type.group.value}"
      label = styled_text(
        f"{art_type.plural} ({count})",
        group_style,
      )
      self.add_option(Option(label, id=art_type.value))

  def on_option_list_option_selected(
    self,
    event: OptionList.OptionSelected,
  ) -> None:
    art_type = ArtifactType(event.option_id)
    self.post_message(TypeSelected(art_type))
