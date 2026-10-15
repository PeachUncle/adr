# ADR-026: Spellchecking

## Status

Accepted

## Context

The project includes a significant amount of source code, documentation, and
configuration files where consistent and correct spelling improves clarity,
professionalism, and developer communication. Typos in variable names, comments,
documentation, or configuration files can lead to confusion, reduce
maintainability, and degrade the quality of the user and contributor experience.

Manual proofreading is insufficient and prone to oversight. Therefore, an
automated spellchecking solution is needed that works well with code, supports
developer tooling, and integrates easily into the project's workflow and CI
pipeline.

## Decision

We decided to use **cspell** as the spellchecking tool for the project.

## Reasons

1. **Designed for Codebases**:
   - cspell is built to work with programming languages, recognizing camelCase,
     snake_case, and other naming conventions.

2. **Flexible Configuration**:
   - Supports project-specific word lists, file patterns, and custom
     dictionaries, making it easy to tune for our domain-specific vocabulary.

3. **CI and Editor Integration**:
   - Can be integrated into CI workflows and supported by popular editors like
     VS Code for real-time feedback.

4. **Language and File Support**:
   - Supports a wide range of file types including `.ts`, `.tsx`, `.js`,
     `.json`, `.md`, and configuration files.

5. **Developer Productivity**:
   - Reduces time spent fixing typos during code reviews and helps standardize
     naming and terminology across the project.

6. **Active Maintenance and Community**:
   - cspell is actively maintained with strong documentation and a growing
     plugin ecosystem.

## Consequences

1. **Initial Dictionary Tuning Required**:
   - Project-specific terms, acronyms, and names will need to be added to a
     custom dictionary to avoid false positives.

2. **False Positives in Code Symbols**:
   - While cspell is optimized for code, some unusual variable names or
     abbreviations may be flagged unnecessarily.

3. **Developer Onboarding**:
   - Team members need to understand how to use and update the custom word list,
     especially when CI checks fail due to spelling.

## Alternatives Considered

### Vale:

- **Pros**: Excellent for markdown and prose with grammar/style linting.
- **Cons**: Not optimized for code syntax or identifiers.

### typos:

- **Pros**: Fast, minimal configuration.
- **Cons**: Lighter feature set; fewer integrations.

### codespell:

- **Pros**: Fixes common typos automatically.
- **Cons**: Less flexible, not ideal for TypeScript-heavy projects.

### No Spellchecking:

- **Pros**: No setup or maintenance overhead.
- **Cons**: Inconsistent quality, undetected typos in docs, comments, and
  code.
