# ADR 004: Selection of Poetry for dependency and environment management

**Date:** 2025-01-20

## Context

During the development of the project, a need arose for a tool to manage Python dependencies and virtual environments. The previous approach, based on using `requirements.txt` and `venv`, was functional but lacked several key features:

- Support for precise version management (e.g., version locking).
- Automatic handling of transitive dependencies.
- Built-in support for publishing Python packages.
- A cleaner format for managing dependencies and project metadata.

After evaluating available tools such as pip, pipenv, and Poetry, the decision was made to adopt Poetry as the project's standard tool.

## Decision

Poetry was chosen as the tool for managing dependencies and virtual environments in the project.

## Justification

### Advantages of Poetry:

1. **Dependency Management:**
   - Combines dependency and virtual environment management in one tool.
   - Automatically generates a `poetry.lock` file to ensure precise version locking for all dependencies, including transitive ones.

2. **Readable Format:**
   - Replaces the `requirements.txt` file with `pyproject.toml`, which consolidates dependency declarations and project metadata in a clean TOML format.

3. **Automatic Version Management:**
   - Supports specifying version ranges (e.g., `^1.2.3`) and adheres to Semantic Versioning (SemVer).

4. **Built-in Publishing:**
   - Simplifies publishing Python packages to PyPI, making it ideal for reusable components.

5. **Virtual Environment Management:**
   - Automatically creates and manages virtual environments, reducing manual effort.

### Comparison with Alternatives:

- **pip:** Lacks transitive dependency version locking and automatic environment management.
- **pipenv:** Slower than Poetry and offers less robust package publishing capabilities.
- **conda:** More feature-rich but exceeds the project's requirements, as it supports non-Python dependencies.

## Consequences

1. **Positive:**
   - Simplifies dependency and environment management.
   - Ensures consistent and reproducible development environments.
   - Facilitates dependency updates with locked versions for stability.

2. **Negative:**
   - Requires team members to learn how to use Poetry.
   - Initial setup may require extra effort to migrate existing configurations.

## Actions

1. Install Poetry on all development machines and integrate it into the CI/CD pipeline.

2. Migrate existing dependencies from `requirements.txt` to `pyproject.toml` using:

   ```bash
   poetry init
   poetry add <dependencies>
   ```

3. Update project documentation with a guide on using Poetry, including key commands such as:
   - Installing dependencies: `poetry install`
   - Adding a dependency: `poetry add <package>`
   - Running the project: `poetry run python <script>`

4. Verify the CI/CD pipeline functionality after implementing the changes.

## Status

Decision implemented.