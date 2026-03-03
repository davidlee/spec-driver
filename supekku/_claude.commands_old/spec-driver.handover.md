---
description: prepare for handoff to the next agent
---

Let's stop here to prepare a thorough handover for the next agent. 

Consider that they will know nothing of your work besides what is in the
project onboarding, and be given the ID of this delta. 

Assume they will begin orienting themselves by calling 
`uv spec-driver show delta $DELTA-ID --json` and reading the files listed.

Your priorities are to:
1. accurately record progress and status
   - all progress and changes are accurately tracked in the Phase Sheet's
     metadata
   - all known relationships to other entities / artefacts are accurately
     reflected in the Delta & IP's metadata
   - anything relevant, surprising, confusing, unknown, noteworthy, or
     concerning you've discovered is recorded for future agents
   - in particular: any weaknesses, shortcomings, potentially skipped,
     outstanding or deferred work is accounted for
   - any valuable future improvements suggested by your experience are noted /
     recommended
   - the notes and metadata (including links to related entities, files
     changed, commits, etc) are correct and up to date
   - notes capture the essential part of all user input (discussions,
     decisions, questions, etc) so that there is no risk of them having to
     repeat it 
   - the DR clearly reflects the design as it is currently understood
   - any other files in the delta bundle relevant to your work so far are
     correct and current 
      - or, it is prominently noted otherwise in the main delta file
   - changes are staged or committed according to the project's governance
   - the above files have a strong signal to noise ratio. 
     - If you, or a previous agent, padded them with extraneous content to
       celebrate how well you ticked off a box, remove it now.
2. provide any additional context which would be useful to the next agent is
bootstrapped effectively
   - ideally there is none, because the previous step captured it all
   - however, it may be useful to: 
     - highlight key elements of particular documents, or provide a recommended
       reading order
     - provide additional knowledge about the project, tool use, successful
       strategies, etc which you learned and which are neither covered by the
       onboarding material, nor an appropriate part of the delta artefacts
       proper
     - describe work you would otherwise continue with after completing this
       delta, which is out of scope 
   - in such cases, create a concise document HANDOVER-PHASE-{XX}.md to supply
     the next agent
3. provide the use with: 
   1. a very concise summary, and 
   2. a very short message they can pass on to the next agent to kick off their
      side of the handover.

Example handover message:
  ```markdown
  I've prepared for handover, and the docs are in good shape for the 
  next agent. Here's a message you can use to get them started:

  ---
  You're picking up DE-XXX; the work so far is accurately recorded.
  Inspect it with: 

  > spec-driver show delta DE-XXX --json

  Read the docs in the delta bundle, and raise any important questions you have.

  When ready, create a sheet for phase 3 with:

  > uv spec-driver create phase --plan IP-XXX --json

  Then ask the user if you should begin task breakdown & flesh out the 
  phase sheet, performing any targeted research required as you go. 
  ```


