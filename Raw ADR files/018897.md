# Migrate from Pip and Related Tools to `uv` for Dependency Management

## Context

Our project currently uses traditional Python tools like `pip`, `requirements.in`, and `requirements-dev.in` for
dependency management. While this setup has served us well, it comes with some limitations:

- Managing development and production dependencies separately can be cumbersome.
- Dependency resolution can be slow and less deterministic.
- Keeping `requirements` files synchronized requires extra tooling (e.g., `pip-tools`).

To streamline the workflow, we propose migrating to `uv`, a modern Python package manager from Astral.

## Decision

We will migrate our project to use `uv` for dependency management and task running.

**Key reasons for adopting `uv`:**

1. **Unified Project Management:**
   - `uv` combines dependency management, task running, and environment configuration within a single tool.
2. **Improved Dependency Resolution:**
   - Faster and more reliable resolution of dependencies.
3. **Simplified Configuration:**
   - All dependencies and tasks are defined in the `pyproject.toml`, reducing the need for multiple files.
4. **Custom Task Management:**
   - `uv` makes it easy to define and run project-specific tasks like tests, linting, and builds.

## Process

1. **Install `uv`**

   ```bash
   pip install uv
   ```

1. **Convert existing requirements files:**
   - Transfer dependencies from `requirements.in` and `requirements-dev.in` to the `pyproject.toml` file.

    ```bash
        uv add -r requirements.in
        uv add --dev requirements-dev.in
    ```

1. **Add dependencies using `uv`:**

   ```bash
   uv add <dependency>
   ```

1. **Define project configuration in `pyproject.toml`:**
   - Add project setting.

   ```toml
   [tool.uv]
   package = true
   ```

## Consequences

### Positive Consequences

- **Simplified dependency management** with fewer files and commands.
- **Improved reproducibility** through deterministic dependency resolution.
- **Custom task automation** directly within the `uv` environment.

### Potential Drawbacks

- **Learning curve:** Team members will need to familiarize themselves with `uv`.
- **Compatibility:** Some legacy tools or workflows may need adjustments.

## Related Decisions

This ADR is related to our ongoing efforts to streamline the development workflow, including:

- Using `nox` for task automation.
- Replacing `Black`, `isort`, and other linters with `Ruff`.

## Status

**Approved.**

The transition to `uv` will be executed immediately after this ADR is documented.

## Next Steps

1. Complete the `pyproject.toml` and `requirements.*` migration process.
1. Update the GitHub Action workflows, as needed.
1. Update the project documentation to reflect `uv` usage.

## Notes

- As part of this transition, the `pyproject.toml` will serve as the single source of truth for dependencies and tasks.
- The `requirements` files will be deprecated and removed after the migration is complete.
