# ADR-001: Refactor Automation from Custom Factory to Standardized Tooling

**Status:** Accepted **Date:** 2025-10-18

## Context

The project initially used a custom automation framework located in the
`factory/` directory, orchestrated by a `Taskfile.yml` at the root. This system
consisted of numerous shell scripts to handle tasks like building, cleaning,
testing, and committing. While functional, this approach required maintaining a
significant amount of custom, imperative shell script code, creating a higher
barrier to entry for new contributors and increasing the project's maintenance
burden.

## Decision

We will remove the entire `factory/` directory and the root `Taskfile.yml`. The
project's automation and quality control will now rely on a combination of
declarative configuration and industry-standard, standalone tools.

- **Formatting:** Will be handled exclusively by **Prettier**.
- **Linting:** Will be handled by tools like **markdownlint**.
- **Development Workflow:** Will be orchestrated by the **`contextvibes` CLI**
  (as it matures).
- **Environment:** Will continue to be defined declaratively by **Nix**.

## Justification

This decision is driven by our core principle of simplifying the project and
reducing the amount of custom code we need to maintain.

- **Standardization:** Prettier is the industry standard for code formatting.
  Relying on it makes our project more familiar to new contributors.
- **Reduced Complexity:** Eliminating dozens of custom shell scripts
  dramatically reduces the project's complexity and attack surface for bugs.
- **Declarative over Imperative:** Relying on configuration files
  (`.prettierrc.json`, `.dev.nix`) is more robust and easier to understand than
  a collection of interdependent scripts.
- **Focus:** This allows the `contextvibes` CLI to become the single, focused
  entry point for all high-level developer workflows, rather than competing with
  a parallel `go-task` system.

## Consequences

- **Positive:**
  - The project is significantly simpler and easier to maintain.
  - Documentation quality and consistency will be improved through automated
    formatting.
- **Negative:**
  - The root `README.md` and other documentation that referenced the "Factory"
    model must be updated.
  - The `contextvibes` CLI now becomes the critical path for all future workflow
    automation. Its development and functionality are paramount.
