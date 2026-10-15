# ADR 0000: ADR Writing Guidelines and Markdown Standards

## Status

Accepted

## Context

Architectural Decision Records (ADRs) are crucial for documenting significant decisions in this project. To ensure consistency, readability, and prevent recurring formatting issues (like Markdown errors, e.g., MD030 related to list marker spacing), we need to establish clear guidelines for writing ADRs and the Markdown style used within them. Previous ADRs have occasionally contained minor Markdown formatting errors, necessitating manual correction. Establishing clear standards and potentially automated checks will improve quality and efficiency.

## Decision

We will adopt the following guidelines for creating and formatting ADRs:

1. **Standard Structure:** All ADRs must follow the structure defined by Michael Nygard's template, including sections for:

    * Title (as H1 `#`)
    * Status (e.g., Proposed, Accepted, Deprecated, Superseded)
    * Context (background, problem, forces)
    * Decision (the chosen option and justification)
    * Consequences (positive and negative outcomes, tradeoffs)

2. **File Naming:** ADR files will be named using the format `NNNN-kebab-case-title.md`, where `NNNN` is a sequential number (starting from 0000).

3. **Markdown Formatting:**

    * We will adhere to GitHub Flavored Markdown (GFM).

    * Specific attention should be paid to common linting rules to avoid errors. Key rules include (but are not limited to):

        * **MD007 (ul-indent):** List indentation depends on the context:
            * Top-level lists: 0 spaces indentation.
            * Nested list under a symbol list (`*`, `-`): Indent 2 spaces relative to the parent marker.
            * Nested list under a number list (`1.`): Indent 4 spaces relative to the parent marker (aligns with text after `1.`).
          Example:

          ```markdown
          1. Number list item
              * Nested symbol list (4 spaces)
          * Symbol list item
            * Nested symbol list (2 spaces)
              1. Nested number list (2 spaces)
          ```

        * **MD030 (list-marker-space):** Exactly **one** space is required after list markers (`*`, `-`, `+`, or numbered list markers like `1.`). Example: `* List item` (Correct), `*   List item` (Incorrect). **This rule must be strictly followed, especially when generating ADRs using AI assistants.**
        * **MD031 (blanks-around-fences):** Fenced code blocks (```) should be surrounded by blank lines (unless at the start/end of the document).
        * **MD032 (blanks-around-lists):** Lists should be surrounded by blank lines (unless at the start/end of the document or directly inside another list item).
        * Consistent heading levels (`#`, `##`, etc.).
        * Proper code block formatting (using backticks ```).
        * Consistent use of unordered list markers (e.g., prefer `-` or `*`).

    * Developers are encouraged to use Markdown preview features and linters (like `markdownlint` extensions) in their editors to catch issues before committing.

4. **Automation (Future Consideration):** We may implement automated Markdown linting (e.g., using `markdownlint-cli` with a pre-commit hook) in the future to enforce these standards automatically.

## Consequences

* **Pros:**

  * Improved consistency and readability across all ADRs.
  * Reduced likelihood of Markdown formatting errors, particularly those generated automatically.
  * Clearer documentation of architectural decisions.
  * Easier onboarding for new team members reading past decisions.
  * Foundation for potential automated linting.

* **Cons:**

  * Requires developers (and AI assistants) to be mindful of the specified format and Markdown rules.
  * Initial effort to ensure existing ADRs (if any were non-compliant) conform.
