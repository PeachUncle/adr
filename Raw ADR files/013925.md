# ADR-0005: Code Formatting and Style Guide

- **Status:** Proposed
- **Date:** 2025-12-08
- **Feature:** 1-robotics-book-spec
- **Context:** The book will contain numerous code examples in different languages (Python, JavaScript, URDF). Maintaining a consistent and readable style across all these examples is crucial for educational clarity and professional presentation.

## Decision

The project will adopt and enforce a standardized code formatting and style guide. The following tools will be used:

- **Prettier:** For automated code formatting of JavaScript, TypeScript, and Markdown/MDX files.
- **ESLint:** For enforcing code style and quality rules in JavaScript/TypeScript.
- **Python Formatting (e.g., Black):** To be used for all Python code examples.

These tools will be integrated into the CI pipeline to ensure all contributions adhere to the defined style.

## Consequences

### Positive

- **Consistency:** All code examples will have a uniform look and feel, reducing cognitive load for the reader.
- **Readability:** A consistent style improves the readability and maintainability of the code examples.
- **Automation:** Automates the formatting process, freeing up authors to focus on content and correctness rather than style.

### Negative

- **Initial Setup:** Requires time to configure the necessary tools (Prettier, ESLint, Black) and integrate them into the CI pipeline.
- **Opinionated Rules:** Automated formatters have opinionated rules that may not align with every author's personal preference, but consistency is the primary goal.

## Alternatives Considered

### Manual Formatting

- **Description:** Rely on authors to manually format their code according to a written style guide.
- **Reason for Rejection:** Manual formatting is highly error-prone, time-consuming, and inevitably leads to inconsistencies. The benefits of automated, enforceable standards are essential for a project of this nature.

## References

- **Implementation Plan:** D:\Quarter 4\ai-book\humanoid-robotic-book\specs\1-robotics-book-spec\plan.md
- **Related ADRs:** None
