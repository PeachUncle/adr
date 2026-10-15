# Purpose of the Init Playbook Prompt and Tool

## Status

Accepted

## Context

The Model Context Protocol (MCP) includes a mechanism for servers to expose prompts as resources. However, there is no inherent mechanism within the protocol to guarantee that a client (such as a Large Language Model) will proactively load and utilize these prompt resources at the beginning of a new task or project interaction. For the MCP Playbook server, it is crucial that the AI is immediately aware of the available tools and the expected documentation practices for a given project.

## Decision

To ensure the AI is consistently informed about the MCP Playbook server's capabilities and documentation guidelines, we have implemented the `init_playbook` tool and a corresponding `initPlaybookPrompt`. Although MCP servers can expose prompts, the `init_playbook` tool serves as an explicit instruction for the AI to receive and process the necessary runtime guidance.

A client-side mechanism will be implemented to automatically call the `init_playbook` tool at the start of a new project interaction. This forces the AI to execute the tool, which in turn provides the `initPlaybookPrompt` containing the current list of tools and documentation instructions.

## Consequences

- **Guaranteed AI Awareness:** By requiring the AI to run the `init_playbook` tool, we ensure that it receives the most up-to-date instructions and a list of available tools at the beginning of each project interaction, regardless of whether it would have otherwise loaded the prompt resource.
- **Implicit Updates:** This mechanism allows us to update the `initPlaybookPrompt` with new tools or revised instructions, and engineers will implicitly receive these updates when the client triggers the `init_playbook` tool in a new project context, without requiring manual intervention or awareness of the prompt resource itself.
- **Consistent Behavior:** Promotes consistent AI behavior across different projects by providing a standardized initial instruction set.
- **Redundancy:** Creates a slight redundancy with the MCP prompt resource mechanism, but this is deemed acceptable to guarantee proactive instruction delivery.
