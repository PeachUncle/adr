# ADR-0003: Forms, Validation, and Multi-Model Design

Date: 2025-10-10
Status: Accepted

## Context

- PRD link: [Part A and Part B Requirements](<#section-or-issue>)
- Problem/forces:
  - Need to implement custom forms with validation to enhance user input handling.
  - Extend the blog application with additional model relationships to support complex data structures.
  - Ensure compliance with WCAG 2.2 for accessibility.

## Options

- **A)** Implement custom forms with validation and extend models with additional relationships.
- **B)** Maintain the current implementation without additional forms or relationships.

## Decision

- We choose **A** because:
  - Custom forms with validation improve data integrity and user experience.
  - Extending models with additional relationships supports more complex business and analytics use cases.
  - Compliance with WCAG 2.2 ensures inclusivity and accessibility.

## Consequences

- **Positive:**
  - Enhanced user experience with better form validation.
  - Improved data modeling to support advanced use cases.
  - Accessibility compliance broadens the user base.
- **Negative/Risks:**
  - Increased development time and complexity.
  - Potential for bugs in new form validation or model relationships.

## Additional Updates

- Introduced a `tags` field in the `BlogPost` model to enable many-to-many relationships.
- Enhanced `BlogPostForm` with validation logic for the `title` field, requiring a minimum length of 5 characters.
- Added a "Create Tags" feature to allow users to dynamically manage tags.
  - Implemented a `TagForm` for tag creation.
  - Added a `TagCreateView` to handle tag creation logic.
  - Updated `urls.py` to include a route for the "Create Tags" page.
  - Created a `tag_form.html` template for the tag creation form.

## Validation

- **Measure/rollback:**
  - Test custom forms for validation errors and edge cases.
  - Verify schema changes with migration scripts and schema diagrams.
  - Conduct accessibility testing to ensure WCAG 2.2 compliance.