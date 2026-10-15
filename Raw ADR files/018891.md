# Architectural Decision Record: Integrating Ruff for Code Quality

## Status

Accepted

## Context

Maintaining a clean, consistent, and high-quality codebase is essential for long-term project maintainability and
collaboration. Previously, multiple tools such as Black, isort, and Flake8 were used for formatting, linting, and
enforcing code standards. Managing and configuring these tools independently increased complexity and introduced
redundancy.

## Decision

We will adopt Ruff as the primary tool for linting, formatting, and enforcing code quality. Ruff replaces Black, isort,
and Flake8 while offering better performance and a unified configuration. Ruff will be integrated into the project
through the following mechanisms:

1. **Centralized Configuration**: Ruff will be configured in `pyproject.toml` to consolidate project settings.
2. **Pre-commit Integration**: Ruff will be included in pre-commit hooks to ensure code quality before commits.
3. **Nox Session**: A dedicated Nox session (`lint`) will be added to automate Ruff checks and enforcement during the
development workflow.

## Reasons

1. **Performance**: Ruff is significantly faster than traditional Python linting tools.
2. **Consolidation**: Replacing multiple tools with Ruff simplifies the development environment.
3. **Ease of Use**: Ruff supports autofix functionality, reducing manual effort for code corrections.
4. **Unified Configuration**: Using `pyproject.toml` eliminates the need for multiple configuration files, reducing
complexity.
5. **Compliance with Project Standards**: Ruff aligns with the project’s need for aggressive code quality enforcement.

## Consequences

1. Developers must install Ruff locally and configure their editors for real-time feedback.
2. Existing configurations for Black, isort, and Flake8 will be deprecated and removed.
3. Codebases must be reformatted to align with Ruff’s rules during the transition.

## Implementation

1. Add the following configuration to `pyproject.toml`:

   ```toml
   [tool.ruff]
   target-version = "py310"
   fix = true
   exclude = [
       ".nox/",
       ".git/",
       "__pycache__/",
       "docs/",
       "venv/",
   ]
   select = ["ALL"]
   line-length = 88
   ignore = ["E501", "W503"]
   ```

2. Add Ruff to pre-commit hooks in `.pre-commit-config.yaml`:

   ```yaml
   repos:
     - repo: https://github.com/charliermarsh/ruff-pre-commit
       rev: v0.0.288  # Use the latest version
       hooks:
         - id: ruff
           args: ["--fix"]
   ```

3. Update `noxfile.py` to include a `lint` session:

   ```python
   @nox.session
   def lint(session):
       session.install("ruff")
       session.run("ruff", ".")
   ```

4. Remove redundant configurations and tools (e.g., Black, isort, Flake8).

## Alternatives Considered

1. **Continue Using Multiple Tools**: This was rejected due to increased complexity and slower performance.
2. **Adopt Other Unified Tools**: Alternatives such as pylama or pyflakes were evaluated but found less performant or
lacking in features compared to Ruff.

## Decision Owner

Tom Willis

## Date

2024-12-10
