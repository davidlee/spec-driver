"""Multi-language specification synchronization engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .adapters import (
  GoAdapter,
  LanguageAdapter,
  PythonAdapter,
  TypeScriptAdapter,
  ZigAdapter,
)
from .models import SourceUnit, SyncOutcome

if TYPE_CHECKING:
  from collections.abc import Mapping, Sequence
  from pathlib import Path


class SpecSyncEngine:
  """Engine for synchronizing technical specifications across multiple languages.

  Orchestrates language adapters to discover source units, generate documentation,
  and maintain registry mappings for Go, Python, and other supported languages.
  """

  def __init__(
    self,
    repo_root: Path,
    tech_dir: Path,
    adapters: Mapping[str, LanguageAdapter] | None = None,
  ) -> None:
    """Initialize the multi-language spec sync engine.

    Args:
        repo_root: Root directory of the repository
        tech_dir: Directory containing technical specifications
        adapters: Optional mapping of language -> adapter. If not provided,
                 default adapters for Go and Python will be used.

    """
    self.repo_root = repo_root
    self.tech_dir = tech_dir

    # Set up default adapters if none provided
    if adapters is None:
      adapters = {
        "go": GoAdapter(repo_root),
        "python": PythonAdapter(repo_root),
        "typescript": TypeScriptAdapter(repo_root),
        "zig": ZigAdapter(repo_root),
      }

    self.adapters = adapters

  def synchronize(
    self,
    *,
    languages: Sequence[str] | None = None,
    targets: Sequence[str] | None = None,
    check: bool = False,
  ) -> SyncOutcome:
    """Synchronize specifications across multiple languages.

    Args:
        languages: Optional list of languages to process. If None,
            processes all.
        targets: Optional list of specific targets to process
            (format: "lang:identifier")
        check: If True, only check if docs would change (don't write
            files)

    Returns:
        SyncOutcome with results of the synchronization operation

    """
    active_languages = self._determine_active_languages(languages)
    language_targets = self._parse_targets(targets, active_languages)

    outcome = SyncOutcome(
      processed_units=[],
      created_specs={},
      skipped_units=[],
      warnings=[],
      errors=[],
    )

    # Only process languages that have targets or if no specific targets
    # were requested
    languages_to_process = (
      active_languages if not targets else list(language_targets.keys())
    )

    for language in languages_to_process:
      self._process_language(
        language,
        language_targets.get(language),
        check,
        outcome,
      )

    return outcome

  def _determine_active_languages(
    self,
    languages: Sequence[str] | None,
  ) -> list[str]:
    """Determine which languages to process."""
    if languages is None:
      return list(self.adapters.keys())
    return [lang for lang in languages if lang in self.adapters]

  def _parse_targets(
    self,
    targets: Sequence[str] | None,
    active_languages: list[str],
  ) -> dict[str, list[str]]:
    """Parse targets into language-specific lists."""
    language_targets: dict[str, list[str]] = {}

    if not targets:
      return language_targets

    for target in targets:
      self._add_target_to_language_map(target, active_languages, language_targets)

    return language_targets

  def _add_target_to_language_map(
    self,
    target: str,
    active_languages: list[str],
    language_targets: dict[str, list[str]],
  ) -> None:
    """Add a target to the appropriate language in the target map."""
    if ":" in target:
      self._add_explicit_target(target, active_languages, language_targets)
    else:
      self._add_auto_detected_target(target, active_languages, language_targets)

  def _add_explicit_target(
    self,
    target: str,
    active_languages: list[str],
    language_targets: dict[str, list[str]],
  ) -> None:
    """Add target with explicit language prefix."""
    lang, identifier = target.split(":", 1)
    if lang in active_languages:
      if lang not in language_targets:
        language_targets[lang] = []
      language_targets[lang].append(identifier)

  def _add_auto_detected_target(
    self,
    target: str,
    active_languages: list[str],
    language_targets: dict[str, list[str]],
  ) -> None:
    """Add target by auto-detecting language from identifier patterns."""
    for lang in active_languages:
      adapter = self.adapters[lang]
      if adapter.supports_identifier(target):
        if lang not in language_targets:
          language_targets[lang] = []
        language_targets[lang].append(target)
        break

  def _process_language(
    self,
    language: str,
    lang_targets: list[str] | None,
    check: bool,
    outcome: SyncOutcome,
  ) -> None:
    """Process all source units for a single language."""
    adapter = self.adapters[language]

    try:
      source_units = adapter.discover_targets(
        self.repo_root,
        requested=lang_targets,
      )

      if not source_units:
        outcome.warnings.append(
          f"No source units found for language: {language}",
        )
        return

      for unit in source_units:
        self._process_source_unit(unit, adapter, check, outcome)

    except Exception as e:
      outcome.errors.append(f"Error processing language {language}: {e!s}")

  def _process_source_unit(
    self,
    unit: SourceUnit,
    adapter: LanguageAdapter,
    check: bool,
    outcome: SyncOutcome,
  ) -> None:
    """Process a single source unit."""
    try:
      # Get unit description for spec creation
      adapter.describe(unit)

      # Generate documentation variants
      adapter.generate(unit, check=check)

      # Track successful processing
      outcome.processed_units.append(unit)

      if not check:
        # Simulate spec creation
        unit_key = f"{unit.language}:{unit.identifier}"
        spec_id = f"SPEC-{len(outcome.created_specs) + 900:03d}"
        outcome.created_specs[unit_key] = spec_id

    except Exception as e:
      outcome.errors.append(f"Error processing {unit.identifier}: {e!s}")
      outcome.skipped_units.append(f"{unit.identifier} (error)")

  def get_supported_languages(self) -> list[str]:
    """Get list of supported languages.

    Returns:
        List of language identifiers

    """
    return list(self.adapters.keys())

  def get_adapter(self, language: str) -> LanguageAdapter | None:
    """Get adapter for a specific language.

    Args:
        language: Language identifier

    Returns:
        Language adapter or None if not supported

    """
    return self.adapters.get(language)

  def add_adapter(self, language: str, adapter: LanguageAdapter) -> None:
    """Add or replace adapter for a language.

    Args:
        language: Language identifier
        adapter: Language adapter to add

    """
    self.adapters[language] = adapter

  def supports_identifier(self, identifier: str) -> str | None:
    """Determine which language (if any) supports the given identifier.

    Args:
        identifier: Source identifier to check

    Returns:
        Language name if supported, None otherwise

    """
    for language, adapter in self.adapters.items():
      if adapter.supports_identifier(identifier):
        return language
    return None
