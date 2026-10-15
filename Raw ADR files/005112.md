# 11. Runtime Validation with Zod

Date: 2025-08-30

## Status

Accepted

## Context

While TypeScript provides excellent compile-time type safety, JavaScript applications need runtime validation for data from external sources:

- User input from forms and APIs
- Data from external APIs and services
- Configuration files and environment variables
- Database query results
- File system data
- WebSocket messages and real-time data

Key requirements:

- TypeScript-first design with automatic type inference
- Comprehensive validation capabilities (strings, numbers, objects, arrays)
- Clear, actionable error messages
- Minimal runtime overhead
- Composable schemas for complex data structures
- Integration with existing TypeScript types

Options considered:

- **Joi**: Mature but not TypeScript-first, requires separate type definitions
- **Yup**: Good TypeScript support but less powerful than alternatives
- **io-ts**: Functional approach, steep learning curve
- **Zod**: TypeScript-first, excellent DX, automatic type inference
- **AJV**: JSON Schema based, fast but verbose

## Decision

We chose **Zod** as our runtime validation library because:

1. **TypeScript-First**: Designed specifically for TypeScript projects
2. **Type Inference**: Automatically infers TypeScript types from schemas
3. **Developer Experience**: Intuitive API with excellent error messages
4. **Comprehensive**: Supports complex validation scenarios
5. **Performance**: Efficient with minimal overhead
6. **Ecosystem**: Growing adoption and community support

### Implementation Details

- **Schema Definition Pattern**:

  ```typescript
  import { z } from 'zod';

  // Define schema
  export const CreateUser = z.object({
    id: z
      .string()
      .regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i),
    email: z.string().regex(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/),
    age: z.number().int().min(13),
  });

  // Infer TypeScript type
  export type CreateUser = z.infer<typeof CreateUser>;
  ```

- **Validation at System Boundaries**:
  - API request/response validation
  - Form input validation
  - Configuration file parsing
  - Database query result validation
  - Environment variable validation

- **Error Handling**:
  - Structured error objects with field-level details
  - Custom error messages for better UX
  - Integration with logging for debugging

- **Patterns and Best Practices**:
  - Colocate schemas with their usage
  - Use schema composition for complex types
  - Validate early at system boundaries
  - Transform and sanitize data during validation
  - Use branded types for domain primitives

## Consequences

### Positive

- **Type Safety**: Runtime validation matches compile-time types exactly
- **Single Source of Truth**: Schema defines both runtime and compile-time types
- **Developer Experience**: Intuitive API reduces learning curve
- **Error Quality**: Detailed, actionable error messages
- **Maintainability**: Changes to validation automatically update types
- **Security**: Prevents invalid data from entering the system
- **Documentation**: Schemas serve as documentation for data structures
- **Composability**: Complex schemas built from simple primitives

### Negative

- **Bundle Size**: Adds ~12KB (gzipped) to bundle
- **Learning Curve**: Developers need to learn Zod patterns
- **Performance**: Runtime validation has computational cost
- **Duplication**: Some validation logic may duplicate database constraints
- **Migration Effort**: Existing validation code needs conversion

### Mitigation

- **Tree Shaking**: Only used validators included in bundle
- **Documentation**: Clear examples and patterns in codebase
- **Performance**: Validate only at boundaries, not internally
- **Caching**: Cache validated configuration and schemas
- **Gradual Migration**: Adopt incrementally for new features
- **Training**: Team education on effective schema design

## References

- [Zod Documentation](https://zod.dev/)
- [TypeScript Type Inference](https://www.typescriptlang.org/docs/handbook/type-inference.html)
- [Parse, Don't Validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
- [Domain Modeling with TypeScript](https://www.domainlanguage.com/ddd/)
