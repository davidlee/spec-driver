<skills_system priority="1">

## Available Skills

<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Check available skills in <available_skills> below
- Skills are loaded via slash commands or agent tooling
- Each skill contains detailed instructions for completing specific tasks

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>

<available_skills>

<skill>
<name>boot</name>
<description>Mandatory onboarding. Every agent MUST execute this on startup, or as soon as becoming aware of it.</description>
<location>project</location>
</skill>

<skill>
<name>preflight</name>
<description>Before starting something new: understand task, intent, and context</description>
<location>project</location>
</skill>

<skill>
<name>consult</name>
<description>Identify and address obstacles, significant decisions, or emergent complexity. You MUST use this skill if you encounter unanticipated obstacles during implementation.</description>
<location>project</location>
</skill>

<skill>
<name>implement</name>
<description>implement a well-defined task or implementation plan</description>
<location>project</location>
</skill>

<skill>
<name>notes</name>
<description>Whenever you complete a task or phase - record implementation notes.</description>
<location>project</location>
</skill>

<skill>
<name>continuation</name>
<description>Write a prompt to help the next agent continue effectively.</description>
<location>project</location>
</skill>

</available_skills>

</skills_system>
