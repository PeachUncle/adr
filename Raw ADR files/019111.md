# ADR 006: Use Zod for runtime schema validation

- **Date created**: 28/06/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

For this medal counter application, we implemented comprehensive runtime schema validation using Zod, despite the dataset
being small and well-structured. This decision was made specifically to demonstrate enterprise-scale development patterns, as requested.

**Current Application Context:**

- Small, static dataset (13 countries) with known structure
- Simple JSON file as data source
- No user input or data mutations
- Predictable data shape that matches our TypeScript interfaces

**Scale Demonstration Requirements:**

- Build the application "as if it were a product designed to scale"
- Demonstrate patterns appropriate for larger, more complex systems
- Show how to handle data validation in production environments
- Establish patterns that support future architectural evolution

**Benefits of Zod Implementation:**

**Immediate Value:**

- Runtime type safety that catches issues TypeScript cannot detect at compile-time
- Detailed, field-specific error messages for debugging
- Type inference that keeps TypeScript definitions in sync with validation rules
- Consistent validation patterns across the application

**Future Scale Benefits:**

- **Database Migration Support**: Schemas provide validation layer when migrating from JSON to PostgreSQL/other databases
- **API Documentation**: Schemas can auto-generate OpenAPI specifications
- **Client-Side Validation**: Same schemas can validate user input on frontend forms
- **Integration Testing**: Schemas validate API responses in automated test suites
- **Environment Configuration**: Can validate environment variables and application config
- **Data Import/Export**: Robust validation for importing external datasets

## Discussions

- Alex Foxleigh - While Zod validation is definitely over-engineering for our current small, static dataset, it demonstrates
important patterns for building scalable systems. The schemas establish a foundation that will be invaluable when we migrate
to a real database or add user-generated content. It's the kind of "invest early for future benefits" decision that separates
prototypes from production systems.

## Decision

Implement Zod schema validation throughout the medal data processing pipeline, including:

- Runtime validation of medal data loaded from JSON files
- API parameter validation with detailed error messages  
- Reusable schemas that can be extended for future data sources
- Type-safe validation patterns that scale with application complexity

## Consequences

**Positive:**

- **Future-proofed architecture**: Easy migration path to database-backed data sources
- **Production-ready error handling**: Detailed validation errors aid debugging and monitoring
- **Type safety assurance**: Runtime validation catches issues that static typing cannot
- **Scalable validation patterns**: Consistent approach that works for simple and complex data
- **Developer experience**: Automatic type inference and comprehensive error reporting
- **Testing benefits**: Schemas provide reliable fixtures for integration tests
- **Documentation value**: Schemas serve as living documentation of data contracts

**Negative:**

- **Over-engineering**: Unnecessary complexity for the current small, static dataset
- **Performance overhead**: Runtime validation adds processing time (minimal but measurable)
- **Learning curve**: Additional complexity for developers unfamiliar with Zod
- **Maintenance overhead**: Schemas must be kept in sync with evolving requirements
- **Bundle size**: Additional dependency increases application bundle size

**Justification:**

This decision prioritises **architectural demonstration** and **future scalability** over immediate simplicity. While the
current application doesn't require this level of validation, the patterns established here showcase how to build systems
that can evolve from simple prototypes to complex, database-backed applications without breaking existing interfaces.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge 