# Workflow

Ceremony mode: **{{ config.ceremony }}**

## Workflow Stance

- Canonical default narrative is delta-first:
  `delta -> DR -> IP -> phase sheet(s) -> implement -> audit -> revision -> patch specs -> close`
- Revision-first is a concession path (typically town-planner governance), not the default entry path.
- Ceremony mode sets guidance posture, not runtime command enforcement.
- Current runtime enforcement comes from explicit command gates (for example coverage checks in `complete delta`) and command flags.

{% if config.kanban.enabled -%}

## Kanban

Cards root: `{{ config.kanban.root }}`
Lanes: {{ config.kanban.lanes | join(', ') }}
ID prefix: `{{ config.kanban.id_prefix }}`
{% endif -%}

## Documentation

Artefacts: `{{ config.kanban.artefacts_root }}`
Plans: `{{ config.kanban.plans_root }}`
