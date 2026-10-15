# ADR-005: Project Documentation

## Status

Accepted

## Context

The project requires well-organized documentation to ensure clarity,
maintainability, and accessibility for current and future contributors. To
achieve this, the documentation must be stored in a centralized location within
the repository and be written in a format that is lightweight, easy to read, and
supports version control.

Several options were considered for organizing and formatting project
documentation:

- Store documentation in a `docs` folder as Markdown (`.md`) files.
- Use external tools or platforms for documentation (e.g., Notion, Confluence).
- Write documentation in plain text or other formats.

## Decision

We decided to store project documentation in a `docs` folder within the
repository, using Markdown files.

## Reasons

1. **Centralized Location**:
   The `docs` folder ensures that all project documentation is stored in one
   place, making it easy to locate and manage.

2. **Markdown Simplicity**:
   Markdown is a lightweight markup language that is easy to write and read,
   even without specialized tools. Its simplicity ensures that documentation can
   be quickly updated.

3. **Version Control Integration**:
   Storing documentation alongside the code in the repository ensures it is
   versioned together with the project. Changes to documentation can be tracked,
   reviewed, and reverted if needed.

4. **Developer Familiarity**:
   Markdown is widely used in the software development community and supported
   by many tools, reducing the learning curve for contributors.

5. **Tool Support**:
   Markdown documents can be rendered and previewed in many modern IDEs, text
   editors, and platforms (e.g., GitHub, GitLab), making them accessible to all
   developers.

6. **Scalability**:
   The `docs` folder can accommodate additional files and sub-folders, allowing
   the documentation structure to grow as the project evolves.

7. **Offline Accessibility**:
   Documentation stored in the repository can be accessed offline, ensuring
   availability without relying on external tools or platforms.

## Consequences

1. Contributors will need to follow the established structure and naming
   conventions within the `docs` folder to maintain organization.

2. Markdown has limited styling and formatting capabilities compared to some
   documentation tools, but this is sufficient for most project needs.

## Alternatives Considered

### External Tools or Platforms:

- **Pros**: Rich formatting options, collaborative features.
- **Cons**: Documentation would be decoupled from the codebase, requiring
  additional tools and accounts to access.

### Plain Text:

- **Pros**: Simplicity, no specific syntax required.
- **Cons**: Lacks the readability and formatting options of Markdown.

### Other Formats (e.g., HTML, PDF):

- **Pros**: More advanced formatting options.
- **Cons**: Requires additional tools for creation and editing, less
  convenient for version control.
