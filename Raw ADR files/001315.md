# ADR-012: Programming Language

## Status

Accepted

## Context

The project will be developed using a programming language that supports modern
tooling, and enhanced readability. Additionally, it will utilize modern
ECMAScript Modules (ESM) to align with current JavaScript standards for modular
code structure. This combination aims to ensure a robust, scalable, and
maintainable codebase.

## Decision

We decided to use TypeScript along with ESM Modules for the project.

## Reasons

1. **Type Safety and Improved Developer Experience**:
   TypeScript’s static typing catches errors at compile time, reduces runtime
   bugs, and provides excellent IDE support with features like autocompletion
   and refactoring tools.

2. **Modern Module Standards**:
   ESM is the standard for JavaScript modules, offering better compatibility
   with modern tools and browsers while supporting tree-shaking for optimized
   builds.

3. **Enhanced Code Maintainability**:
   TypeScript’s type annotations and interfaces make the codebase easier to
   understand and maintain, especially as the project grows in complexity.

4. **Rich Ecosystem and Community Support**:
   TypeScript has a vast ecosystem with well-maintained libraries and tools,
   along with comprehensive community resources for troubleshooting and
   learning.

5. **Compatibility with Modern Tooling**:
   ESM Modules integrate seamlessly with modern build tools (e.g., Vite, Rollup,
   Webpack) and runtime environments, ensuring a smooth development workflow.

6. **Scalability**:
   TypeScript’s robust type system ensures that the codebase scales efficiently
   as the project grows or new contributors join.

## Consequences

1. The use of TypeScript requires a compilation step, adding a slight overhead
   to the development and build process.

2. Adopting ESM Modules means that older tooling or runtime environments that do
   not fully support ESM may require polyfills or additional configuration.

3. Developers unfamiliar with TypeScript or ESM may face a learning curve but
   will benefit from the improved tooling and practices in the long term.

## Alternatives Considered

### Plain JavaScript with ESM Modules:

- **Pros**: Simplifies the setup by avoiding the TypeScript compilation step.
- **Cons**: Lacks static typing and the benefits of TypeScript’s tooling,
  making the codebase less robust and harder to maintain.

### TypeScript with CommonJS Modules:

- **Pros**: Broad compatibility with older tools and runtime environments.
- **Cons**: CommonJS is becoming less relevant as the ecosystem shifts toward
  ESM.
