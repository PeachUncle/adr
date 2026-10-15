---
title: 'ADR 002–TypeScript Monorepo Toolchain (Bun Runtime)'
date: 2025-10-07
status: Accepted
deciders: [Platform/DevEx]
tags: [typescript, monorepo, bun, nx, pnpm, devex]
---

## Decision summary

Use Node.js as the runtime, pnpm for dependency management, and Nx as the
orchestrator. This combination delivers ecosystem maturity, scalability, and
strong developer experience while maintaining compatibility with existing
TypeScript and CI/CD workflows.

---

## Context

This project is a monorepo to improve dependency management, code sharing, and
developer experience.  
The primary runtime environment uses **Node.js**, the most widely supported
JavaScript runtime for both development and production environments.

Because Node.js provides broad ecosystem compatibility, the chosen build system
must consider developer experience, scalability, and maintainability for
TypeScript. As well, the chosen tool requires compatibility with standard
Node-based tooling and CI/CD platforms.

This ADR evaluates available monorepo tools (Nx, Turborepo, Moonrepo, Rush,
Bazel) under Node.js and selects one unified solution.

---

## Decision

Adopt the following stack:

- **Package manager**: `pnpm`
- **Runtime**: `Node.js`
- **Monorepo orchestrator**: `Nx`
- **Versioning**: `Changesets`

This combination—**Node.js + pnpm + Nx**—provides a strong balance between
ecosystem maturity, TypeScript tooling, CI/CD integration, and long-term
maintainability.

---

## Rationale

### Why Nx

- Provides **project graph**, **affected builds**, and **computation caching**
  that drastically reduce CI times.
- Enforces **module boundaries** and **TypeScript project references**,
  improving maintainability and clarity of dependencies.
- Works natively with **Node.js** and major package managers like pnpm and npm.
- Integrates with **Changesets**, CI tools (GitHub Actions, Azure DevOps, GitLab
  CI), and container-based deployments.

### Why pnpm

- Fast, disk-efficient, and deterministic installations.
- Strict `node_modules` linking model prevents hidden dependency leaks.
- Deep integration with Nx, allowing workspace discovery and dependency graph
  generation.

### Why not Yarn or npm

- **Yarn (Berry)** introduces extra configuration complexity (Plug’n’Play) with
  minimal benefits for this project.
- **npm workspaces** adequate but slower and less strict than pnpm for large
  TypeScript repos.

### Why not Turborepo or Moonrepo

- **Turborepo** provides efficient task caching but lacks Nx’s
  project-graph-based boundary enforcement and generator ecosystem.
- **Moonrepo** performant but has a smaller ecosystem and fewer
  TypeScript-specific integrations.

---

## Consequences

### Benefits

- Proven ecosystem and broad developer familiarity with Node.js.
- Strong TypeScript and CI/CD support through Nx’s computation caching and
  project graph.
- Predictable dependency management with pnpm.
- Seamless onboarding for developers using standard Node.js workflows.

### Drawbacks

- Slightly slower cold-start installs compared to Bun.
- Larger Node.js runtime footprint compared to minimal runtimes.
- Requires developers to understand Nx concepts (graph, affected targets,
  caching).

---

## Implementation plan

1. **Initialize Workspace**

   ```bash
   pnpm dlx create-nx-workspace@latest
   ```

1. Enable PNPM workspaces

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

1. Configure Nx

- Define project tags, affected settings, and caching in nx.json.
- Enforce module boundaries and TypeScript project references.
- Enable computation caching and optional remote caching in CI.

Example configuration snippet:

```json
// nx.json
{
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx/tasks-runners/default",
      "options": {
        "cacheableOperations": ["build", "test", "lint", "typecheck"]
      }
    }
  }
}
```

1. Integrate with Node.js Runtime

- Use Node.js v24+ for ES module support and stable performance.
- Add standard Node scripts for development, build, and testing.

```json
// package.json
{
  "scripts": {
    "dev": "nx serve web",
    "test": "nx test",
    "build": "nx build web"
  }
}
```

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: 24
    cache: pnpm
- name: Install dependencies
  run: pnpm install
- name: Build
  run: pnpm nx build web
```

1. Set up Versioning

- Integrate Changesets into CI for automated version bumps and changelog
  generation.

- Configure a release workflow that runs after merges to main.

Example GitHub Actions release job:

```yaml
- name: Version & Publish
  run: |
    pnpm changeset version
    pnpm changeset publish
```

---

## Alternatives considered

| Tool                 | Pros                                 | Cons                                        |
| -------------------- | ------------------------------------ | ------------------------------------------- |
| **npm workspaces**   | Standard, built-in                   | Slower, less strict dependency model        |
| **Yarn workspaces**  | Plug’n’Play option, good performance | Complex configuration, less adoption        |
| **Turborepo**        | Great caching, Vercel integration    | Fewer guardrails than Nx                    |
| **Moonrepo**         | Rust performance, good caching       | Smaller ecosystem                           |
| **Rush (+Heft)**     | Enterprise-grade release governance  | Higher setup complexity                     |
| **Bazel (rules_ts)** | Hermetic, scalable builds            | High complexity, overkill for most JS repos |

---

## References

- [Nx Documentation](https://nx.dev)
- [pnpm Documentation](https://pnpm.io/)
- [Node.js Documentation](https://nodejs.org/)
- [Changesets Documentation](https://github.com/changesets/changesets)
