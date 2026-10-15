# 10. Decision to Use Conventional Commits for Commit Messages

## Status

**Accepted**

## Context

Consistent and descriptive commit messages are critical for understanding the history of a project, collaborating effectively, and automating tasks like changelog generation. The Conventional Commits standard provides a structured format for commit messages, making it easier to:

1. Understand the scope and intent of changes at a glance.
2. Generate changelogs and release notes automatically.
3. Facilitate better code reviews by providing context for changes.
4. Maintain a clean and professional repository history.

## Decision

The project will adopt the **Conventional Commits** specification for commit messages. This decision ensures that commit messages follow a standardized format, enabling clear communication and integration with tools that leverage this structure.

### Conventional Commit Format

Each commit message will include the following elements:

1. **Type** (required): Describes the category of change (e.g., `feat`, `fix`, `docs`, `style`).
2. **Scope** (optional): Provides additional context about the part of the codebase affected.
3. **Subject** (required): A short description of the change.
4. **Body** (optional): A more detailed explanation of the change.
5. **Footer** (optional): Additional information, such as breaking changes or issue references.

Example:

```text
<type>(<scope>): <subject>

<body>

<footer>
```

#### Example Commit Messages

- `feat(customer): add support for customer profiles`
- `fix(api): resolve null pointer exception on POST /customers`
- `docs(readme): update installation instructions`
- `refactor(database): optimize query for fetching customer data`
- `chore: update dependencies`
- `improve(ui): enhance customer search interface usability`

## Consequences

### Benefits

- **Improved Clarity**: Commit messages provide clear context for changes.
- **Automation**: Tools like `commitlint` and `semantic-release` can automate changelog generation and versioning.
- **Standardization**: Ensures all contributors follow the same format, improving consistency.
- **Collaboration**: Makes it easier for reviewers to understand the intent of changes.

### Drawbacks

- **Learning Curve**: New contributors may need to familiarize themselves with the Conventional Commits standard.
- **Enforcement**: Requires additional tooling or processes (e.g., pre-commit hooks or CI checks) to ensure adherence.

## Alternatives Considered

1. **Freeform Commit Messages**:
    - Rejected because they lack structure and consistency, making it harder to understand changes or automate tasks.

2. **Custom Commit Guidelines**:
    - Rejected because Conventional Commits is a widely adopted standard with toolchain support, reducing the need to create and enforce a custom solution.

## Implementation Plan

1. **Documentation**:
    - Add Conventional Commits guidelines to the `CONTRIBUTING.md` file.
    - Provide examples and a quick reference for contributors.

2. **Tooling**:
    - Integrate `commitlint` into the CI pipeline to validate commit messages.
    - Optionally use `husky` to enforce the standard locally with pre-commit hooks.

3. **Onboarding**:
    - Share the Conventional Commits guide with the team and encourage adherence during code reviews.

## Conclusion

Adopting Conventional Commits ensures that commit messages are clear, consistent, and actionable. This practice enhances the project’s maintainability, facilitates automation, and improves collaboration. The benefits of this decision outweigh the minor effort required to implement and enforce the standard.
