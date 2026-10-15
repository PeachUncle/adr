# ADR 004: Use Tailwind CSS for styling

- **Date created**: 28/06/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

For styling this application, we need a solution that provides:

- Rapid development and prototyping capabilities
- Consistent design system
- Good performance characteristics
- Maintainable and scalable styling approach

Tailwind CSS offers a utility-first approach that allows for rapid development while maintaining consistency. It provides:

- Comprehensive utility classes for common styling needs
- Built-in design system with consistent spacing, colours, and typography
- Excellent tree-shaking to eliminate unused styles
- Strong integration with modern build tools
- Responsive design utilities
- Customisable design tokens

Alternative approaches considered:

- Styled-components: More overhead and runtime cost
- (S)CSS Modules: More verbose and requires more custom CSS
- Traditional (S)CSS: Harder to maintain consistency and requires more boilerplate

## Discussions

- Alex Foxleigh - Tailwind provides the best balance of development speed, maintainability, and performance for this project.
The utility-first approach works particularly well with component-based architecture. Whilst it is not my personal preference
(I'm a big fan of the SCSS modules approach) for a project like this one, Tailwind makes the most sense.

## Decision

Use Tailwind CSS as the primary styling solution for the project.

## Consequences

**Positive:**

- Rapid development with utility classes
- Consistent design system out of the box
- Excellent performance through automatic purging of unused styles
- Strong responsive design capabilities
- Customisable design tokens for brand consistency
- Large community and ecosystem support

**Negative:**

- Learning curve for developers unfamiliar with utility-first approach
- HTML classes can become verbose for complex styling
- Can actually make large projects less readable and therefore harder to maintain
- Can paradoxically cause higher congnitive complexity on heavily styled elements
- Potential for inconsistent custom styles if not managed properly
- Requires discipline to maintain design system consistency

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge 