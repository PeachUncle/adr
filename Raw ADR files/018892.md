# Architectural Decision Record: Integrating Pre-commit Hooks

## Status

Accepted

## Context

Maintaining high code quality and enforcing consistent standards across contributions is essential in a collaborative
development environment. Manually running linting and formatting tools introduces human error and slows down workflows.
Integrating automated pre-commit hooks ensures that code quality checks are consistently applied before changes are
committed to the repository.

## Decision

We will use `pre-commit` to manage and enforce pre-commit hooks for automated linting, formatting, and other checks. The
following hooks will be included:

1. **Ruff**: To enforce linting and formatting standards.
2. **End-of-file Fixer**: To ensure proper file endings.
3. **Trailing Whitespace Fixer**: To remove unnecessary whitespace.
4. **Other Necessary Hooks**: Additional hooks will be added as the project evolves.

## Reasons

1. **Consistency**: Pre-commit hooks enforce code quality standards uniformly across all contributors.
2. **Automation**: Eliminates manual steps for running checks, reducing errors and saving time.
3. **Collaboration**: Ensures that all team members adhere to project standards before merging changes.
4. **Efficiency**: Identifies issues earlier in the development workflow, reducing the cost of fixing them later.
5. **Integration with Git**: Pre-commit hooks are natively supported by Git, making them easy to integrate.

## Consequences

1. Contributors must install `pre-commit` locally and configure their Git environments.
2. Initial setup of pre-commit hooks may require updating existing code to meet enforced standards.
3. Commit processes may take slightly longer as hooks are executed, but the time saved in review and corrections
4. outweighs this cost.

## Implementation

1. Add a `.pre-commit-config.yaml` file to the repository with the following configuration:

   ```yaml
   repos:
     - repo: https://github.com/charliermarsh/ruff-pre-commit
       rev: v0.0.288  # Use the latest version
       hooks:
         - id: ruff
           args: ["--fix"]
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v4.3.0  # Use the latest version
       hooks:
         - id: end-of-file-fixer
         - id: trailing-whitespace
   ```

2. Install `pre-commit` as a development dependency:

   ```bash
   pip install pre-commit
   ```

3. Install the hooks locally:

   ```bash
   pre-commit install
   ```

4. Add `pre-commit` execution to CI workflows to ensure hooks are run for all contributions.

5. Update the developer documentation with installation and usage instructions for pre-commit.

## Alternatives Considered

1. **Manual Checks**: Rejected due to inconsistency and increased risk of human error.
2. **Other Hook Managers**: Alternatives like Husky (for JavaScript) were evaluated but are not natively suited for
3. Python.

## Decision Owner

Tom Willis

## Date

2024-12-10
