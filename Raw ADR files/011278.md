# Argument Validation and Repository Structure

## Status

Accepted

## Context

As the MCP Playbook server grows and includes more tools with various arguments, a consistent and robust method for validating incoming tool arguments is necessary to ensure data integrity and prevent errors. Additionally, a clear and organized repository structure is needed to manage the growing codebase effectively and make it easy for developers to understand where different parts of the server's logic reside.

## Decision

We will use the Zod library for defining and validating the schemas of tool arguments. Zod provides a concise and type-safe way to define expected data structures and automatically generate JSON schemas for the MCP tool definitions. This ensures that incoming arguments conform to the expected types and formats.

The repository will follow a structured organization with dedicated directories for different components:

- `src/tools/`: Contains the definitions of the MCP tools, including their names, descriptions, and input schemas defined using Zod.
- `src/handlers/`: Contains the implementation logic for each tool. Each tool has a corresponding handler function that receives and processes the validated arguments.
- `src/utils/`: Contains shared utility functions, such as those for interacting with the GitHub API (`githubApi.ts`) and general validation utilities (`validationUtils.ts`).
- `src/prompts/`: Contains prompt templates or initial instructions used by the AI when interacting with the server.
- `src/types.ts`: Contains shared TypeScript type definitions.
- `src/index.ts`: The main entry point of the server, responsible for setting up the MCP server instance and routing incoming tool calls to the appropriate handlers.

## Consequences

- **Improved Data Integrity:** Using Zod for validation reduces the likelihood of errors caused by incorrect or unexpected tool arguments.
- **Enhanced Developer Experience:** The clear repository structure makes it easier for developers to navigate the codebase, find relevant files, and understand the separation of concerns.
- **Maintainability:** A consistent validation approach and organized structure contribute to the long-term maintainability of the server.
- **Dependency:** Introduces Zod as a project dependency.
