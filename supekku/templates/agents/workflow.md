# Workflow

Ceremony mode: **{{ config.ceremony }}**

## Workflow Stance

- Canonical default narrative is delta-first:
  `delta -> DR -> IP -> phase sheet(s) -> implement -> audit -> revision -> patch specs -> close`
- Revision-first is a concession path (typically town-planner governance), not the default entry path.
- Ceremony mode sets guidance posture, not runtime command enforcement.
- Current runtime enforcement comes from explicit command gates (for example coverage checks in `complete delta`) and command flags.

{% if config.cards.enabled -%}
## Cards

Cards root: `{{ config.cards.root }}`
Lanes: {{ config.cards.lanes | join(', ') }}
ID prefix: `{{ config.cards.id_prefix }}`
{% endif -%}

## Documentation

Artefacts: `{{ config.docs.artefacts_root }}`
Plans: `{{ config.docs.plans_root }}`
