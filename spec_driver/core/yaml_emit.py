"""Comment-preserving YAML emitter for spec-driver frontmatter.

`emit_yaml_block(data, comments=None)` is the single emit primitive shared by
the template regenerator (`spec_driver.orchestration.templates`), the create-
and update-path dump helpers (`supekku.scripts.lib.core.spec_utils`), and the
legacy compatibility wrapper `dump_frontmatter_yaml`. Comments are appended as
`# ...` to top-level scalar keys only — container values render normally and
nested structures are emitted by stdlib yaml unchanged. See DR-137 §5.1.

The dumper logic (`_FrontmatterDumper` + representers) was previously inlined
as `CompactDumper` in `supekku.scripts.lib.core.frontmatter_writer` and is
preserved here byte-for-byte so the no-comment emit path is regression-free.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import yaml

_FLOW_LIST_WIDTH_LIMIT = 60

_NEEDS_QUOTING_RE = re.compile(
  r"^$"
  r"|^\d{4}-\d{2}-\d{2}$"
  r"|^(true|false|yes|no|on|off|null|~)$"
  r"|^[0-9]"
  r"|^[@`'\"]"
  r"|[:#,\[\]{}]",
  re.IGNORECASE,
)


class _FrontmatterDumper(yaml.SafeDumper):
  """Compact, prettier-compatible YAML dumper.

  - Short scalar lists render as flow-style `[a, b, c]`.
  - Long lists and lists containing dicts render as block-style.
  - Sequences always indent under their parent key (no indentless).
  - Strings YAML would single-quote are double-quoted (prettier convention).
  """

  def increase_indent(  # noqa: D102
    self,
    flow: bool = False,
    indentless: bool = False,  # noqa: ARG002
  ) -> None:
    return super().increase_indent(flow=flow, indentless=False)


def _represent_str(dumper: _FrontmatterDumper, data: str) -> yaml.Node:
  if _NEEDS_QUOTING_RE.search(data):
    style = "'" if '"' in data else '"'
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)
  return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _represent_list(dumper: _FrontmatterDumper, data: list) -> yaml.Node:
  use_flow = (
    all(isinstance(x, (str, int, float, bool)) for x in data)
    and sum(len(str(x)) for x in data) + 2 * len(data) < _FLOW_LIST_WIDTH_LIMIT
  )
  return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=use_flow)


_FrontmatterDumper.add_representer(str, _represent_str)
_FrontmatterDumper.add_representer(list, _represent_list)


_TOPLEVEL_KEY_RE = re.compile(r"^(?P<key>[A-Za-z_][\w-]*):")


def _append_comments(text: str, comments: Mapping[str, str]) -> str:
  """Append `  # <comment>` to lines whose top-level key matches *comments*.

  Comment injection only fires for **scalar** values — lines where the colon
  is immediately followed by a value on the same line (e.g. `key: value`).
  Container-opening lines (`key:` with no value, or `key: []`) are intentionally
  skipped; nested keys are not addressable from the comment map.
  """
  out_lines = []
  for line in text.splitlines():
    match = _TOPLEVEL_KEY_RE.match(line)
    if match is None:
      out_lines.append(line)
      continue
    key = match.group("key")
    if key not in comments:
      out_lines.append(line)
      continue
    # Only annotate scalar lines: the value must be present after the colon
    # and must not be a container-opener (`[]` is acceptable; bare `:` is not).
    after_colon = line[match.end() :].lstrip()
    if not after_colon:
      out_lines.append(line)
      continue
    if after_colon.startswith(("[", "{")) and not after_colon.startswith(
      ("[]", "{}"),
    ):
      out_lines.append(line)
      continue
    out_lines.append(f"{line}  # {comments[key]}")
  return "\n".join(out_lines)


def emit_yaml_block(
  data: Mapping[str, Any],
  comments: Mapping[str, str] | None = None,
) -> str:
  """Emit YAML for *data* with optional inline `# comment` per top-level key.

  - Returns YAML text with no leading/trailing newline and no `---` markers.
  - Output is deterministic: key insertion order preserved; quoting and list
    style match `_FrontmatterDumper`.
  - When *comments* is provided, top-level scalar keys named in the map
    receive a trailing `  # <comment>`. Container values are skipped per
    DR-137 §5.1.
  """
  text = yaml.dump(
    data,
    Dumper=_FrontmatterDumper,
    sort_keys=False,
    allow_unicode=True,
    width=10000,
  ).strip()
  if comments:
    text = _append_comments(text, comments)
  return text
