---
title: "Using PNPM as Monorepo Orchestrator"
date: 2025-07-19
status: accepted
---

## Context

The project is structured as a monorepo containing multiple JavaScript/TypeScript packages (e.g., frontend, backend services). A tool is needed to manage dependencies, link packages, and run scripts across these packages efficiently.

## Decision

We will use **PNPM** as our monorepo orchestrator. PNPM's workspace feature will be utilized to manage the interdependencies and scripts of the various packages within the monorepo.

## Alternatives Considered

* **Bazel (Build System)**:
  * **Pros**: Language-agnostic, excellent for polyglot monorepos, provides hermetic builds, remote caching, and highly efficient incremental builds. Ideal for very large, complex projects with diverse language stacks.
  * **Cons**: High learning curve and significant setup complexity. It is a build system, not a package manager, so it would still require a separate package manager for JavaScript dependencies.
* **Yarn Workspaces**:
  * **Pros**: Mature, widely adopted, good performance.
  * **Cons**: Can be slower than PNPM for installation due to its flat `node_modules` structure. Less efficient disk space usage compared to PNPM's content-addressable store.
* **NPM Workspaces**:
  * **Pros**: Native to NPM, no additional tool needed.
  * **Cons**: Generally slower and less efficient than both Yarn and PNPM for monorepo management, especially with large numbers of dependencies or packages.
* **Lerna (Monorepo Manager)**:
  * **Pros**: Dedicated monorepo management tool with advanced features like versioning and publishing. Can be used on top of Yarn/NPM/PNPM workspaces.
  * **Cons**: Can add unnecessary complexity if only basic workspace management is needed. Its role has somewhat diminished as package managers have integrated more monorepo features.
* **Nx (Monorepo Toolkit)**:
  * **Pros**: Provides an extensible toolkit with code generation, smart build systems (computation caching, affected commands), and integrated tooling. Strong for web development ecosystems.
  * **Cons**: Can be opinionated and introduce a significant amount of configuration. Primarily focused on web development.

## Consequences

* **Positive**:
  * **Disk Space Efficiency**: PNPM uses a content-addressable store to link dependencies, meaning each version of a dependency is only stored once on disk, saving significant space.
  * **Faster Installations**: Due to its unique linking strategy, PNPM often performs faster installations, especially in monorepos with many shared dependencies.
  * **Strictness**: PNPM creates a non-flat `node_modules` by default, which helps prevent accidental access to undeclared dependencies, leading to more robust and reliable builds.
  * **Simplicity**: PNPM workspaces provide a straightforward way to manage multiple packages without excessive configuration, striking a good balance between features and complexity for our current needs.
* **Negative**:
  * **Learning Curve**: Developers unfamiliar with PNPM might need a short adjustment period.
  * **Tooling Compatibility**: While generally good, some older tools or custom scripts might have assumptions about `node_modules` structure that conflict with PNPM's approach (though this is rare with modern tools).

This decision leverages PNPM's strengths in efficiency and strictness, which are highly beneficial for managing dependencies and development workflows in a JavaScript/TypeScript-centric monorepo setup, without introducing the higher complexity of a full build system like Bazel or a comprehensive toolkit like Nx at this stage.
