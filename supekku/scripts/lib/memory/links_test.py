"""Tests for memory link parsing and resolution."""

from __future__ import annotations

from supekku.scripts.lib.memory.links import (
  LinkGraphNode,
  LinkResolutionResult,
  MissingLink,
  ParsedLink,
  ResolvedLink,
  compute_backlinks,
  expand_link_graph,
  links_to_frontmatter,
  parse_links,
  resolve_all_links,
  resolve_parsed_link,
)

_SRC = "mem.fact.test"


# ── Parser tests ─────────────────────────────────────────────


class TestParseLinks:
  """parse_links extracts [[...]] tokens from body text."""

  def test_empty_body(self) -> None:
    assert parse_links("") == []

  def test_no_links(self) -> None:
    assert parse_links("Just plain text with no links.") == []

  def test_single_link(self) -> None:
    result = parse_links("See [[ADR-001]] for details.")
    assert result == [
      ParsedLink(raw="ADR-001", target="ADR-001", label=None),
    ]

  def test_multiple_links(self) -> None:
    result = parse_links("See [[ADR-001]] and [[SPEC-002]].")
    assert len(result) == 2
    assert result[0].target == "ADR-001"
    assert result[1].target == "SPEC-002"

  def test_link_with_label(self) -> None:
    result = parse_links("See [[ADR-001|Auth Decision]].")
    assert result == [
      ParsedLink(
        raw="ADR-001|Auth Decision",
        target="ADR-001",
        label="Auth Decision",
      ),
    ]

  def test_memory_id_link(self) -> None:
    result = parse_links("Related: [[mem.pattern.cli.skinny]]")
    assert result[0].target == "mem.pattern.cli.skinny"

  def test_memory_shorthand_link(self) -> None:
    result = parse_links("See [[pattern.cli.skinny]]")
    assert result[0].target == "pattern.cli.skinny"

  def test_dedup_by_target(self) -> None:
    result = parse_links("[[ADR-001]] again [[ADR-001]].")
    assert len(result) == 1

  def test_dedup_keeps_first_label(self) -> None:
    result = parse_links("[[ADR-001|First]] and [[ADR-001|Second]].")
    assert len(result) == 1
    assert result[0].label == "First"

  def test_whitespace_stripped_from_target(self) -> None:
    result = parse_links("See [[ ADR-001 ]].")
    assert result[0].target == "ADR-001"

  def test_whitespace_stripped_from_label(self) -> None:
    result = parse_links("See [[ADR-001| Auth Decision ]].")
    assert result[0].label == "Auth Decision"

  # --- Code fence skipping ---

  def test_skips_fenced_code_block(self) -> None:
    body = "Before\n```\n[[ADR-001]]\n```\nAfter [[SPEC-001]]"
    result = parse_links(body)
    assert len(result) == 1
    assert result[0].target == "SPEC-001"

  def test_skips_tilde_fenced_code_block(self) -> None:
    body = "Before\n~~~\n[[ADR-001]]\n~~~\nAfter [[SPEC-001]]"
    result = parse_links(body)
    assert len(result) == 1
    assert result[0].target == "SPEC-001"

  def test_skips_fenced_with_language(self) -> None:
    body = "Before\n```yaml\n[[ADR-001]]\n```\nAfter [[SPEC-001]]"
    result = parse_links(body)
    assert len(result) == 1
    assert result[0].target == "SPEC-001"

  # --- Inline code skipping ---

  def test_skips_inline_code(self) -> None:
    body = "Use `[[ADR-001]]` syntax. See [[SPEC-001]]."
    result = parse_links(body)
    assert len(result) == 1
    assert result[0].target == "SPEC-001"

  def test_skips_double_backtick_inline(self) -> None:
    body = "Use ``[[ADR-001]]`` syntax. See [[SPEC-001]]."
    result = parse_links(body)
    assert len(result) == 1
    assert result[0].target == "SPEC-001"

  # --- Edge cases ---

  def test_empty_brackets_ignored(self) -> None:
    assert parse_links("[[]]") == []

  def test_whitespace_only_brackets_ignored(self) -> None:
    assert parse_links("[[  ]]") == []

  def test_nested_brackets_not_supported(self) -> None:
    """Nested [[ inside ]] captures first close."""
    result = parse_links("[[foo[[bar]]]]")
    assert len(result) == 1

  def test_link_at_start_of_line(self) -> None:
    result = parse_links("[[ADR-001]] starts here")
    assert result[0].target == "ADR-001"

  def test_link_at_end_of_line(self) -> None:
    result = parse_links("ends here [[ADR-001]]")
    assert result[0].target == "ADR-001"

  def test_adjacent_links(self) -> None:
    result = parse_links("[[ADR-001]][[SPEC-002]]")
    assert len(result) == 2

  def test_multiline_body(self) -> None:
    body = "Line 1 [[ADR-001]]\nLine 2 [[SPEC-002]]\nLine 3 [[DE-033]]"
    result = parse_links(body)
    assert len(result) == 3


# ── Resolver tests ───────────────────────────────────────────


def _artifact_index() -> dict[str, tuple[str, str]]:
  """Shared test artifact index."""
  return {
    "ADR-001": ("specify/decisions/ADR-001-auth.md", "adr"),
    "SPEC-001": ("specify/tech/SPEC-001/SPEC-001.md", "spec"),
    "DE-033": ("change/deltas/DE-033/DE-033.md", "delta"),
    "mem.pattern.cli.skinny": (
      "memory/mem.pattern.cli.skinny.md",
      "memory",
    ),
    "mem.fact.auth": ("memory/mem.fact.auth.md", "memory"),
  }


def _resolve(link: ParsedLink) -> ResolvedLink | MissingLink | None:
  """Shorthand for resolve_parsed_link with test defaults."""
  return resolve_parsed_link(
    link,
    known_artifacts=_artifact_index(),
    source_id=_SRC,
  )


class TestResolveParsedLink:
  """resolve_parsed_link resolves against known artifact index."""

  def test_resolve_adr(self) -> None:
    link = ParsedLink(raw="ADR-001", target="ADR-001", label=None)
    result = _resolve(link)
    assert isinstance(result, ResolvedLink)
    assert result.id == "ADR-001"
    assert result.kind == "adr"
    assert result.path == "specify/decisions/ADR-001-auth.md"

  def test_resolve_spec(self) -> None:
    link = ParsedLink(raw="SPEC-001", target="SPEC-001", label=None)
    result = _resolve(link)
    assert isinstance(result, ResolvedLink)
    assert result.id == "SPEC-001"

  def test_resolve_delta(self) -> None:
    link = ParsedLink(raw="DE-033", target="DE-033", label=None)
    result = _resolve(link)
    assert isinstance(result, ResolvedLink)
    assert result.kind == "delta"

  def test_resolve_memory_canonical(self) -> None:
    link = ParsedLink(
      raw="mem.pattern.cli.skinny",
      target="mem.pattern.cli.skinny",
      label=None,
    )
    result = _resolve(link)
    assert isinstance(result, ResolvedLink)
    assert result.id == "mem.pattern.cli.skinny"
    assert result.kind == "memory"

  def test_resolve_memory_shorthand(self) -> None:
    """Shorthand without mem. prefix resolves via normalization."""
    link = ParsedLink(
      raw="fact.auth",
      target="fact.auth",
      label=None,
    )
    result = _resolve(link)
    assert isinstance(result, ResolvedLink)
    assert result.id == "mem.fact.auth"
    assert result.kind == "memory"

  def test_resolve_with_label(self) -> None:
    link = ParsedLink(
      raw="ADR-001|Auth",
      target="ADR-001",
      label="Auth",
    )
    result = _resolve(link)
    assert isinstance(result, ResolvedLink)
    assert result.label == "Auth"

  def test_self_link_returns_none(self) -> None:
    link = ParsedLink(
      raw="mem.fact.test",
      target="mem.fact.test",
      label=None,
    )
    assert _resolve(link) is None

  def test_self_link_shorthand_returns_none(self) -> None:
    """Shorthand that normalizes to source_id is a self-link."""
    link = ParsedLink(
      raw="fact.test",
      target="fact.test",
      label=None,
    )
    assert _resolve(link) is None

  def test_missing_target(self) -> None:
    link = ParsedLink(raw="ADR-999", target="ADR-999", label=None)
    result = _resolve(link)
    assert isinstance(result, MissingLink)
    assert result.raw == "ADR-999"

  def test_unrecognized_target(self) -> None:
    """Not a known artifact ID and not memory-like."""
    link = ParsedLink(
      raw="something-else",
      target="something-else",
      label=None,
    )
    result = _resolve(link)
    assert isinstance(result, MissingLink)

  # ── mem: URI scheme ──

  def test_mem_scheme_resolves(self) -> None:
    """mem: URI scheme stripped and resolved as mem. prefix."""
    link = ParsedLink(
      raw="mem:fact.auth",
      target="mem:fact.auth",
      label=None,
    )
    result = _resolve(link)
    assert isinstance(result, ResolvedLink)
    assert result.id == "mem.fact.auth"
    assert result.kind == "memory"

  def test_mem_scheme_with_label(self) -> None:
    link = ParsedLink(
      raw="mem:fact.auth|Auth Info",
      target="mem:fact.auth",
      label="Auth Info",
    )
    result = _resolve(link)
    assert isinstance(result, ResolvedLink)
    assert result.label == "Auth Info"

  def test_mem_scheme_self_link(self) -> None:
    """mem: scheme that resolves to source_id is a self-link."""
    link = ParsedLink(
      raw="mem:fact.test",
      target="mem:fact.test",
      label=None,
    )
    assert _resolve(link) is None

  def test_mem_scheme_missing(self) -> None:
    """mem: scheme with unknown target produces MissingLink."""
    link = ParsedLink(
      raw="mem:fact.nonexistent",
      target="mem:fact.nonexistent",
      label=None,
    )
    result = _resolve(link)
    assert isinstance(result, MissingLink)


# ── resolve_all_links tests ──────────────────────────────────


def _resolve_body(body: str) -> LinkResolutionResult:
  """Shorthand for resolve_all_links with smaller index."""
  index = {
    "ADR-001": ("specify/decisions/ADR-001.md", "adr"),
    "mem.fact.auth": ("memory/mem.fact.auth.md", "memory"),
  }
  return resolve_all_links(
    body,
    known_artifacts=index,
    source_id=_SRC,
  )


class TestResolveAllLinks:
  """resolve_all_links processes full body text."""

  def test_empty_body(self) -> None:
    result = _resolve_body("")
    assert result.out == []
    assert result.missing == []
    assert result.warnings == []

  def test_mixed_resolved_and_missing(self) -> None:
    result = _resolve_body("See [[ADR-001]] and [[NOPE-999]].")
    assert len(result.out) == 1
    assert result.out[0].id == "ADR-001"
    assert len(result.missing) == 1
    assert result.missing[0].raw == "NOPE-999"

  def test_self_link_produces_warning(self) -> None:
    result = _resolve_body("Self-ref: [[mem.fact.test]].")
    assert result.out == []
    assert result.missing == []
    assert len(result.warnings) == 1
    assert "self" in result.warnings[0].lower()

  def test_dedup_in_resolution(self) -> None:
    result = _resolve_body("[[ADR-001]] and again [[ADR-001]].")
    assert len(result.out) == 1


# ── links_to_frontmatter tests ──────────────────────────────


class TestLinksToFrontmatter:
  """links_to_frontmatter serializes LinkResolutionResult."""

  def test_empty_result(self) -> None:
    result = LinkResolutionResult(
      out=[],
      missing=[],
      warnings=[],
    )
    assert links_to_frontmatter(result) == {}

  def test_resolved_only(self) -> None:
    result = LinkResolutionResult(
      out=[
        ResolvedLink(
          id="ADR-001",
          path="decisions/ADR-001.md",
          label=None,
          kind="adr",
        ),
      ],
      missing=[],
      warnings=[],
    )
    fm = links_to_frontmatter(result, mode="full")
    assert "out" in fm
    assert len(fm["out"]) == 1
    assert fm["out"][0]["id"] == "ADR-001"
    assert fm["out"][0]["kind"] == "adr"
    assert "label" not in fm["out"][0]
    assert "missing" not in fm

  def test_resolved_with_label(self) -> None:
    result = LinkResolutionResult(
      out=[
        ResolvedLink(
          id="ADR-001",
          path="p.md",
          label="Auth",
          kind="adr",
        ),
      ],
      missing=[],
      warnings=[],
    )
    fm = links_to_frontmatter(result, mode="full")
    assert fm["out"][0]["label"] == "Auth"

  def test_missing_only(self) -> None:
    result = LinkResolutionResult(
      out=[],
      missing=[MissingLink(raw="ADR-999")],
      warnings=[],
    )
    fm = links_to_frontmatter(result)
    assert "out" not in fm
    assert "missing" in fm
    assert fm["missing"][0]["raw"] == "ADR-999"

  def test_mixed(self) -> None:
    result = LinkResolutionResult(
      out=[
        ResolvedLink(
          id="SPEC-001",
          path="s.md",
          label=None,
          kind="spec",
        ),
        ResolvedLink(
          id="ADR-001",
          path="a.md",
          label=None,
          kind="adr",
        ),
      ],
      missing=[MissingLink(raw="NOPE-999")],
      warnings=[],
    )
    fm = links_to_frontmatter(result, mode="full")
    # Sorted by id
    assert fm["out"][0]["id"] == "ADR-001"
    assert fm["out"][1]["id"] == "SPEC-001"
    assert len(fm["missing"]) == 1

  def test_sorted_output(self) -> None:
    """out entries sorted by id for deterministic YAML."""
    result = LinkResolutionResult(
      out=[
        ResolvedLink(
          id="SPEC-002",
          path="s2.md",
          label=None,
          kind="spec",
        ),
        ResolvedLink(
          id="ADR-001",
          path="a.md",
          label=None,
          kind="adr",
        ),
        ResolvedLink(
          id="SPEC-001",
          path="s1.md",
          label=None,
          kind="spec",
        ),
      ],
      missing=[],
      warnings=[],
    )
    fm = links_to_frontmatter(result, mode="full")
    ids = [entry["id"] for entry in fm["out"]]
    assert ids == ["ADR-001", "SPEC-001", "SPEC-002"]


# ── Link mode tests ─────────────────────────────────────────


def _mixed_result() -> LinkResolutionResult:
  """Helper: result with both resolved and missing links."""
  return LinkResolutionResult(
    out=[
      ResolvedLink(
        id="ADR-001",
        path="a.md",
        label=None,
        kind="adr",
      ),
    ],
    missing=[MissingLink(raw="NOPE-999")],
    warnings=[],
  )


class TestLinksToFrontmatterModes:
  """links_to_frontmatter mode parameter controls output shape."""

  def test_default_mode_is_missing(self) -> None:
    """Default mode omits out, keeps missing."""
    result = _mixed_result()
    fm = links_to_frontmatter(result)
    assert "out" not in fm
    assert "missing" in fm
    assert fm["missing"][0]["raw"] == "NOPE-999"

  def test_mode_full_includes_both(self) -> None:
    """Full mode includes out and missing."""
    result = _mixed_result()
    fm = links_to_frontmatter(result, mode="full")
    assert "out" in fm
    assert "missing" in fm

  def test_mode_missing_omits_out(self) -> None:
    """Missing mode omits out, keeps missing."""
    result = _mixed_result()
    fm = links_to_frontmatter(result, mode="missing")
    assert "out" not in fm
    assert "missing" in fm

  def test_mode_none_returns_empty(self) -> None:
    """None mode returns empty dict regardless of content."""
    result = _mixed_result()
    fm = links_to_frontmatter(result, mode="none")
    assert fm == {}

  def test_mode_compact_includes_ids_only(self) -> None:
    """Compact mode includes out with id-only entries."""
    result = _mixed_result()
    fm = links_to_frontmatter(result, mode="compact")
    assert "out" in fm
    assert fm["out"][0] == {"id": "ADR-001"}
    assert "missing" in fm

  def test_mode_missing_empty_missing_returns_empty(self) -> None:
    """Missing mode with no missing links returns empty dict."""
    result = LinkResolutionResult(
      out=[
        ResolvedLink(
          id="ADR-001",
          path="a.md",
          label=None,
          kind="adr",
        ),
      ],
      missing=[],
      warnings=[],
    )
    fm = links_to_frontmatter(result, mode="missing")
    assert fm == {}

  def test_mode_full_empty_result(self) -> None:
    """Full mode with empty result returns empty dict."""
    result = LinkResolutionResult()
    fm = links_to_frontmatter(result, mode="full")
    assert fm == {}

  def test_mode_full_preserves_sort_order(self) -> None:
    """Full mode sorts out entries by id."""
    result = LinkResolutionResult(
      out=[
        ResolvedLink(
          id="SPEC-002",
          path="s.md",
          label=None,
          kind="spec",
        ),
        ResolvedLink(
          id="ADR-001",
          path="a.md",
          label=None,
          kind="adr",
        ),
      ],
      missing=[],
      warnings=[],
    )
    fm = links_to_frontmatter(result, mode="full")
    ids = [e["id"] for e in fm["out"]]
    assert ids == ["ADR-001", "SPEC-002"]

  def test_invalid_mode_raises(self) -> None:
    """Invalid mode raises ValueError."""
    result = _mixed_result()
    try:
      links_to_frontmatter(result, mode="bogus")
      raise AssertionError("Expected ValueError")  # noqa: TRY301
    except ValueError as exc:
      assert "Invalid link mode" in str(exc)


# ── compute_backlinks tests ──────────────────────────────────


class TestComputeBacklinks:
  """compute_backlinks builds reverse edges from forward links."""

  def test_empty_corpus(self) -> None:
    assert compute_backlinks({}) == {}

  def test_single_link(self) -> None:
    bodies = {
      "mem.a": "See [[mem.b]] for details.",
      "mem.b": "No links here.",
    }
    bl = compute_backlinks(bodies)
    assert bl["mem.b"] == ["mem.a"]

  def test_self_link_excluded(self) -> None:
    bodies = {"mem.a": "Self ref [[mem.a]] ignored."}
    bl = compute_backlinks(bodies)
    assert "mem.a" not in bl

  def test_hub_node_multiple_backlinks(self) -> None:
    bodies = {
      "mem.a": "Links to [[mem.hub]].",
      "mem.b": "Also links to [[mem.hub]].",
      "mem.c": "And [[mem.hub]] too.",
      "mem.hub": "The hub.",
    }
    bl = compute_backlinks(bodies)
    assert bl["mem.hub"] == ["mem.a", "mem.b", "mem.c"]

  def test_missing_target_still_tracked(self) -> None:
    """Backlinks include targets not in the corpus."""
    bodies = {"mem.a": "Links to [[PROB-002]]."}
    bl = compute_backlinks(bodies)
    assert bl["PROB-002"] == ["mem.a"]

  def test_mem_uri_scheme_normalized(self) -> None:
    bodies = {"mem.a": "See [[mem:b]] for details.", "mem.b": ""}
    bl = compute_backlinks(bodies)
    assert bl["mem.b"] == ["mem.a"]

  def test_deduplicates_per_source(self) -> None:
    """Same target linked twice from same source appears once."""
    bodies = {"mem.a": "[[mem.b]] and again [[mem.b]]."}
    bl = compute_backlinks(bodies)
    assert bl["mem.b"] == ["mem.a"]

  def test_multiple_targets_from_one_source(self) -> None:
    bodies = {"mem.a": "[[mem.b]] and [[mem.c]]."}
    bl = compute_backlinks(bodies)
    assert bl["mem.b"] == ["mem.a"]
    assert bl["mem.c"] == ["mem.a"]

  def test_results_sorted(self) -> None:
    bodies = {
      "mem.z": "[[mem.target]]",
      "mem.a": "[[mem.target]]",
      "mem.m": "[[mem.target]]",
    }
    bl = compute_backlinks(bodies)
    assert bl["mem.target"] == ["mem.a", "mem.m", "mem.z"]


# ── expand_link_graph tests ──────────────────────────────────


def _graph_bodies() -> dict[str, str]:
  return {
    "mem.root": "Links to [[mem.a]] and [[mem.b]].",
    "mem.a": "Links to [[mem.c]].",
    "mem.b": "Links to [[mem.a]] and [[mem.c]].",
    "mem.c": "Leaf node.",
  }


def _graph_names() -> dict[str, str]:
  return {
    "mem.root": "Root",
    "mem.a": "Node A",
    "mem.b": "Node B",
    "mem.c": "Node C",
  }


def _graph_types() -> dict[str, str]:
  return {
    "mem.root": "signpost",
    "mem.a": "concept",
    "mem.b": "concept",
    "mem.c": "fact",
  }


class TestExpandLinkGraph:
  """expand_link_graph does BFS expansion from a root node."""

  def test_depth_zero_returns_root_only(self) -> None:
    nodes = expand_link_graph(
      "mem.root",
      _graph_bodies(),
      _graph_names(),
      _graph_types(),
      max_depth=0,
    )
    assert len(nodes) == 1
    assert nodes[0] == LinkGraphNode("mem.root", "Root", 0, "signpost")

  def test_depth_one(self) -> None:
    nodes = expand_link_graph(
      "mem.root",
      _graph_bodies(),
      _graph_names(),
      _graph_types(),
      max_depth=1,
    )
    ids = [n.id for n in nodes]
    assert ids[0] == "mem.root"
    assert set(ids[1:]) == {"mem.a", "mem.b"}
    assert all(n.depth == 1 for n in nodes[1:])

  def test_depth_two(self) -> None:
    nodes = expand_link_graph(
      "mem.root",
      _graph_bodies(),
      _graph_names(),
      _graph_types(),
      max_depth=2,
    )
    ids = [n.id for n in nodes]
    assert set(ids) == {"mem.root", "mem.a", "mem.b", "mem.c"}
    # mem.c should be at depth 2
    c_node = next(n for n in nodes if n.id == "mem.c")
    assert c_node.depth == 2

  def test_cycle_protection(self) -> None:
    bodies = {
      "mem.a": "[[mem.b]]",
      "mem.b": "[[mem.a]]",
    }
    names = {"mem.a": "A", "mem.b": "B"}
    nodes = expand_link_graph("mem.a", bodies, names, {}, max_depth=5)
    ids = [n.id for n in nodes]
    assert ids == ["mem.a", "mem.b"]

  def test_missing_target_included_but_not_expanded(self) -> None:
    bodies = {"mem.a": "[[mem.unknown]]"}
    names = {"mem.a": "A"}
    nodes = expand_link_graph("mem.a", bodies, names, {}, max_depth=2)
    ids = [n.id for n in nodes]
    assert "mem.unknown" in ids
    # Only 2 nodes — unknown is not expanded
    assert len(nodes) == 2

  def test_preserves_name_and_type(self) -> None:
    nodes = expand_link_graph(
      "mem.root",
      _graph_bodies(),
      _graph_names(),
      _graph_types(),
      max_depth=1,
    )
    a_node = next(n for n in nodes if n.id == "mem.a")
    assert a_node.name == "Node A"
    assert a_node.memory_type == "concept"

  def test_unknown_node_uses_id_as_name(self) -> None:
    bodies = {"mem.a": "[[mem.unknown]]"}
    nodes = expand_link_graph("mem.a", bodies, {}, {}, max_depth=1)
    unknown = next(n for n in nodes if n.id == "mem.unknown")
    assert unknown.name == "mem.unknown"

  def test_max_depth_capped(self) -> None:
    """Depths above 5 are capped to 5."""
    nodes = expand_link_graph(
      "mem.root",
      _graph_bodies(),
      _graph_names(),
      _graph_types(),
      max_depth=100,
    )
    assert all(n.depth <= 5 for n in nodes)

  def test_root_not_in_bodies(self) -> None:
    """Root ID with no body returns just root node."""
    nodes = expand_link_graph(
      "mem.missing",
      {},
      {"mem.missing": "Gone"},
      {},
      max_depth=2,
    )
    assert len(nodes) == 1
    assert nodes[0].id == "mem.missing"
