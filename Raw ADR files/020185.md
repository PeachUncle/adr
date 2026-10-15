# ADR 002: Code Style Configuration for JavaScript

## Status

Accepted

## Context

Establishing a consistent and well-defined code style is crucial to ensuring maintainability and readability across the team. This is especially important for a reference project, where others will look to us for best practices. There have been various discussions around code style preferences, but in order to move forward efficiently and provide a clear standard, we have decided to adopt a combination of widely accepted tools and defaults.

### Code Style vs. Linting

It's important to clarify the distinction between code style and linting:

- **Code style** deals with how the code is formatted, focusing on whitespace, indentation, line length, and similar aesthetic aspects.
- **Linting** focuses on code correctness, ensuring that the code conforms to coding standards and best practices (e.g., checking for unused variables or enforcing proper variable naming conventions).

For this ADR, we are focusing on code style alone, with a decision on linting to follow separately. This keeps the responsibilities and configuration of each tool clear and specialized.

### Prettier for JavaScript Code Styling

We will use **Prettier**, which is widely accepted as the go-to tool for JavaScript code formatting. Prettier automates code formatting, ensuring that our codebase remains consistent no matter who writes the code or which editor is used. By relying on Prettier's well-thought-out defaults, we reduce the time spent debating style choices and avoid the complexity of highly customized configurations.

### EditorConfig for Extended Configuration

To complement Prettier, we will also use **EditorConfig**. This tool helps extend the formatting rules slightly and communicates to text editors and IDEs how files should be styled. EditorConfig is useful for ensuring consistency when Prettier cannot enforce certain rules, or in non-JavaScript files.

By using these two tools together, we ensure that our codebase remains consistent and accessible across different editors, while keeping configuration lightweight.

## Decision

We will use **Prettier** for JavaScript code styling, adhering to its defaults with the following two exceptions:
1. **Line width**: We will increase the maximum line length from 80 characters to **120 characters**. Modern screens are more than capable of displaying over 80 characters, and forcing the line length to such a small width can lead to cluttered code that is less readable. 120 characters strikes a good balance between readability and making efficient use of screen real estate.

2. **Indentation**: We will use **tabs for indentation** rather than spaces. This is a growing best practice in the context of accessibility, as it allows individuals to set their own preferred indentation size. It also helps make indentation visually distinct from actual spaces, which can improve clarity when working in code that mixes both.

**YAML files are excluded from this rule**, as they do not support tabs and require spaces for indentation.

To enforce these decisions, we will use an `.editorconfig` file in combination with Prettier’s configuration. EditorConfig will hint to editors and IDEs to follow these formatting rules outside of what Prettier covers.

## Consequences

- **Positive**:
	- Adopting Prettier with minimal customizations reduces debates and ensures that we follow industry standards for JavaScript code formatting.
	- The use of tabs for indentation improves accessibility and allows individual developers to customize their coding experience without impacting the rest of the team.
	- Combining Prettier with EditorConfig ensures a consistent code style across different editors and environments, extending style rules to non-JavaScript files where necessary.

- **Negative**:
	- Developers unfamiliar with tab-based indentation may need a brief adjustment period.
	- Prettier's opinionated nature limits flexibility, but this trade-off is mitigated by the consistency and time saved on code reviews and formatting debates.
