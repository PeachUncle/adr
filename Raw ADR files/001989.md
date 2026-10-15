---
title: "Using Husky for Git Hooks"
date: 2025-07-19
status: accepted
---

## Context

To enforce code quality standards, run linters, formatters, and tests before commits or pushes, a mechanism for Git hooks is required. There are several tools available for managing Git hooks in a JavaScript/TypeScript monorepo environment.

## Decision

We will use **Husky** for managing Git hooks in this project. Husky provides a simple and effective way to configure Git hooks directly within `package.json` or dedicated script files, making it easy to integrate with `pnpm` workspaces and run pre-commit/pre-push scripts.

## Alternatives Considered

* **`pre-commit` (Python-based hook manager)**:
  * **Pros**: Widely used in Python ecosystems, good for managing hooks for various languages.
  * **Cons**: Primarily Python-centric, which might introduce an unnecessary dependency for a JavaScript/TypeScript-heavy monorepo. Integration with `pnpm` workspaces might be less straightforward compared to a JavaScript-native solution.
* **Manual Git Hooks**: Manually configuring scripts in the `.git/hooks` directory.
  * **Pros**: No external dependencies.
  * **Cons**: Difficult to share and maintain across a team, not version-controlled effectively, and not easily integrated into `package.json` scripts.

## Consequences

* **Positive**:
  * **Ease of Setup**: Husky is straightforward to set up and configure, especially within a Node.js/JavaScript project.
  * **Version Control**: Hooks are defined in `package.json` or dedicated files, ensuring they are version-controlled and shared across all developers.
  * **Integration with PNPM**: Works seamlessly with `pnpm` scripts, allowing `pnpm` commands to be executed as part of Git hooks.
  * **Cross-Platform**: Reliable across different operating systems.
* **Negative**:
  * **Node.js Dependency**: Requires Node.js and `pnpm` to be installed for hooks to function, which is already a project dependency.

This decision aligns with the project's primary use of JavaScript/TypeScript and `pnpm` for monorepo management, providing a native and integrated solution for Git hook enforcement.
