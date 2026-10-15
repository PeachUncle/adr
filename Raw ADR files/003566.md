---
status: proposed
date: 2024-12-11
decision-makers: Michael Ogunrinde, James Bateman, Cory-Newman
---

# Technology Stack Selection for AML System

## Context and Problem Statement

The AML system needs a modern, maintainable, and scalable technology stack that can support our web application requirements. We need to choose technologies for frontend development, styling, and database management that work well together and provide a good developer experience while ensuring optimal performance and user experience.

## Decision Drivers

* Must support rapid development and iteration
* Need to ensure good performance and SEO capabilities
* Must be well-documented with strong community support
* Should have a smooth learning curve for the team
* Must support responsive design and modern UI patterns
* Should enable efficient state management
* Must integrate well with our chosen database system
* Should provide good developer tooling and debugging capabilities

## Considered Options

### Frontend Framework

* Next.js + React
* Angular
* Vue.js
* Remix
* Plain React

### Styling Solutions

* TailwindCSS with UI components
* Material UI
* Plain CSS/SCSS
* Styled Components
* CSS Modules

### UI Component Libraries

* Shadcn/UI with TailwindCSS
* Material UI
* Chakra UI
* Ant Design
* Custom components

## Decision Outcome

Chosen stack:

* Next.js with React for frontend framework
* TailwindCSS for styling
* Shadcn/UI and Frostbite for UI components
* MySQL for database (covered in separate ADR)

Because:

1. Next.js provides excellent SEO capabilities and server-side rendering
2. React has a large ecosystem and strong community support
3. TailwindCSS enables rapid development with utility-first approach
4. Shadcn/UI provides high-quality, customizable components
5. The chosen stack has good integration between components
6. Tools are well-documented and actively maintained
7. Stack matches team's technical expertise

### Planned Implementation Approach

1. Frontend Architecture:
   * Next.js pages and routing
   * React components structure
   * State management strategy
   * API integration approach

2. Styling Structure:
   * TailwindCSS configuration
   * Component theming
   * Responsive design approach
   * Custom utility classes

3. Development Environment:
   * Code organisation
   * Build process
   * Development tools
   * Testing framework

### Consequences

* Good, because it provides a modern and maintainable codebase
* Good, because it enables rapid development with pre-built components
* Good, because it ensures good performance through Next.js optimisations
* Bad, because it requires learning TailwindCSS utility classes
* Bad, because it needs careful management of component dependencies

### Confirmation

We will validate this decision through:

1. Prototype development
2. Performance testing
3. Developer feedback
4. Build process evaluation
5. Component library assessment

## Pros and Cons of the Options

### Next.js + React

* Good, because of built-in SSR and routing
* Good, because of large ecosystem and community
* Good, because of excellent documentation
* Good, because of TypeScript support
* Bad, because of potential complexity in configuration
* Bad, because of learning curve for SSR concepts

### TailwindCSS with UI Components

* Good, because of rapid development capabilities
* Good, because of consistent styling approach
* Good, because of built-in responsive design
* Good, because of performance benefits
* Bad, because of initial learning curve
* Bad, because of verbose class names

### Shadcn/UI and Frostbite

* Good, because of high-quality, customizable components
* Good, because of modern design patterns
* Good, because of accessibility support
* Bad, because of potential upgrade challenges
* Bad, because of dependency management complexity

## More Information

Implementation requirements:

1. Development Setup:
   * Project structure guidelines
   * Coding standards
   * Build configuration
   * Testing framework selection

2. Training Requirements:
   * Next.js/React best practices
   * TailwindCSS usage
   * Component library documentation
   * Development workflow

3. Performance Considerations:
   * Bundle size optimisation
   * Image optimisation
   * Code splitting strategy
   * Caching approach

4. Future Planning:
   * Scalability considerations
   * Maintenance strategy
   * Update procedures
   * Documentation requirements
