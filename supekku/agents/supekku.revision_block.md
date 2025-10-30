# Slash Command: Create Supekku Revision Block: $ARGUMENTS

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

If you were not given a filename, requirement code or other information that would allow you to investigate and complete the following task, you should read the following with the expectation you will be given such information shortly in a follow-up. 

## Context

You need to add a `supekku:revision.change@v1` block to a revision document. This block formally tracks changes to specifications and requirements in a structured format.

Refer to `.spec-driver/about/README.md` and `.spec-driver/about/glossary.md` for a general understanding of the framework before proceeding if you are unfamiliar with it.

## Commands to Run


1. `just supekku::print-revision-block-schema` - Get the JSON schema for the YAML revision block format. Read this before writing the revision block.
2. `just supekku::validate-workspace-revision-blocks` - Validate all revision blocks in the workspace. Validation must be successful for the task to be complete.

## Block Format
Refer to the JSON schema as the canonical source for a valid revision block. As a guide (refer to schema) the block must be formatted as:
```yaml supekku:revision.change@v1
schema: supekku.revision.change
version: 1
metadata:
  revision: [REVISION_ID]
  generated_at: [ISO_TIMESTAMP]
  prepared_by: [AUTHOR]
specs:
  - spec_id: [TARGET_SPEC_ID]
    action: [created|updated|retired]
    summary: [DESCRIPTION]
    requirement_flow:
      added: [LIST_OF_NEW_REQUIREMENTS]
      moved_in: [LIST_OF_MOVED_IN_REQUIREMENTS]
      moved_out: [LIST_OF_MOVED_OUT_REQUIREMENTS]
      removed: [LIST_OF_REMOVED_REQUIREMENTS]
    section_changes:
      - section: [SECTION_NAME]
        change: [added|removed|modified|renamed]
        notes: [DESCRIPTION]
requirements:
  - requirement_id: [FULL_REQUIREMENT_ID]
    kind: [functional|non-functional]
    action: [introduce|modify|move|retire]
    summary: [BRIEF_DESCRIPTION]
    destination:
      spec: [TARGET_SPEC_ID]
      requirement_id: [FULL_REQUIREMENT_ID]
    origin:
      - kind: [backlog|spec|requirement|external]
        ref: [SOURCE_REFERENCE]
        notes: [CONTEXT]
    lifecycle:
      introduced_by: [REVISION_ID]
      status: [pending|in-progress|live|retired]
```

Process

1. Analyze the source requirements/improvements/specifications to understand what changes are being made
2. Create the revision block mapping source requirements to target specification requirements
3. Use action types: "introduce" for new requirements, "move" for relocating existing ones, "modify" for changes, "retire" for removals
4. Ensure all requirement IDs follow the pattern: SPEC-[ID].(FR|NFR)-[ID]
5. Add the block to the revision document
6. Run validation to ensure correct format and auto-formatting

Key Points

- The block must be valid YAML with the exact header format shown
- All requirements must have proper traceability from origin to destination
- The validation command will auto-format the YAML if syntax is correct
- Each requirement should map to a specific functional area in the target specification