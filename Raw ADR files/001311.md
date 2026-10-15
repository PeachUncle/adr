# ADR-009: EditorConfig

## Status

Accepted

## Context

The project involves multiple files where consistent coding styles (e.g.,
indentation, line endings, and character encoding) are essential to maintain
readability and reduce formatting-related issues. These formatting
inconsistencies can occur due to different developer environments, editor
settings, or platform-specific defaults.

An EditorConfig file is a configuration file that standardizes coding styles
across various editors and IDEs that support the EditorConfig standard.

## Decision

We decided to use an EditorConfig file for managing code formatting standards in
the project.

## Reasons

1. **Consistency Across Environments**:
   An EditorConfig file ensures that all developers (current and future) use
   consistent coding styles regardless of their editor or IDE settings.

2. **Ease of Integration**:
   EditorConfig is natively supported by many popular editors (e.g., VS Code,
   JetBrains IDEs, Sublime Text), or can be enabled with plugins.

3. **Version Control**:
   Including an `.editorconfig` file in the project repository ensures that
   formatting rules are versioned and accessible to all collaborators.

4. **Prevention of Formatting Issues**:
   By enforcing uniform styles, EditorConfig reduces the chances of merge
   conflicts and other issues caused by inconsistent formatting.

5. **Lightweight and Simple**:
   The `.editorconfig` file is straightforward to set up and requires minimal
   effort to maintain.

6. **Support for Multi-language Projects**:
   EditorConfig allows defining rules for specific file types, making it
   versatile for projects with multiple programming languages or file formats.

## Consequences

1. Developers will need to enable EditorConfig support in their editors if it is
   not enabled by default.

2. The project may require occasional updates to the `.editorconfig` file if new
   formatting rules are introduced or the project evolves.

## Alternatives Considered

### Manual Enforcing of Formatting Standards:

- **Pros**: No additional configuration file required.
- **Cons**: Relies on developers to manually adhere to standards, leading to
  inconsistencies.

### Relying on Editor/IDE-specific Settings:

- **Pros**: May leverage existing preferences in developers' environments.
- **Cons**: Difficult to ensure uniformity across different tools and
  environments.
