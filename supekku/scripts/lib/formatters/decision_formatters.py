"""Decision/ADR display formatters.

Pure formatting functions with no business logic.
Formatters take DecisionRecord objects and return formatted strings for display.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from supekku.models.decision import Decision


def format_decision_details(decision: "Decision") -> str:
  """Format decision details as multi-line string for display.

  Args:
    decision: Decision object to format

  Returns:
    Formatted string with all decision details
  """
  lines = []

  # Basic fields
  lines.append(f"ID: {decision.id}")
  lines.append(f"Title: {decision.title}")
  lines.append(f"Status: {decision.status}")

  # Timestamps
  if decision.created:
    lines.append(f"Created: {decision.created}")
  if decision.decided:
    lines.append(f"Decided: {decision.decided}")
  if decision.updated:
    lines.append(f"Updated: {decision.updated}")
  if decision.reviewed:
    lines.append(f"Reviewed: {decision.reviewed}")

  # People
  if decision.authors:
    lines.append(f"Authors: {', '.join(str(a) for a in decision.authors)}")
  if decision.owners:
    lines.append(f"Owners: {', '.join(str(o) for o in decision.owners)}")

  # Relationships
  if decision.supersedes:
    lines.append(f"Supersedes: {', '.join(decision.supersedes)}")
  if decision.superseded_by:
    lines.append(f"Superseded by: {', '.join(decision.superseded_by)}")

  # References to other artifacts
  if decision.specs:
    lines.append(f"Related specs: {', '.join(decision.specs)}")
  if decision.requirements:
    lines.append(f"Requirements: {', '.join(decision.requirements)}")
  if decision.deltas:
    lines.append(f"Deltas: {', '.join(decision.deltas)}")
  if decision.revisions:
    lines.append(f"Revisions: {', '.join(decision.revisions)}")
  if decision.audits:
    lines.append(f"Audits: {', '.join(decision.audits)}")

  # Related items
  if decision.related_decisions:
    lines.append(f"Related decisions: {', '.join(decision.related_decisions)}")
  if decision.related_policies:
    lines.append(f"Related policies: {', '.join(decision.related_policies)}")

  # Tags
  if decision.tags:
    lines.append(f"Tags: {', '.join(decision.tags)}")

  # Backlinks
  if decision.backlinks:
    lines.append("\nBacklinks:")
    for link_type, refs in decision.backlinks.items():
      lines.append(f"  {link_type}: {', '.join(refs)}")

  return "\n".join(lines)
