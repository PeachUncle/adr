# ADR-005: Domain Error Handling Strategy

## Context

In a Domain-Driven Design (DDD) architecture, error handling must reflect the semantics of the domain while integrating cleanly with infrastructure concerns like HTTP transport and API documentation. Prior to this ADR, domain errors were inconsistently defined and tightly coupled to runtime behavior, making them harder to test, document, and maintain.

## Decision

We introduce a consistent Domain Error strategy using:

* A shared base class: `BaseDomainError`
* A centralized HTTP status code map: `DomainHttpCode`
* Per-use-case domain-specific error subclasses
* Compatibility with ResultValue, exception filters, and Swagger

### 1. BaseDomainError

Located under `@timeboxing/shared`, this abstract class provides:

* A standard shape for all domain errors
* Static `statusCode` and `swaggerMessage` for consistent integration
* A runtime constructor for dynamic `.message`

```ts
export abstract class BaseDomainError extends Error {
  static statusCode?: number;
  static swaggerMessage: string = 'Default message by BaseDomainError';

  constructor(message: string) {
    super(message);
    this.name = new.target.name;
  }
}
```

### 2. DomainHttpCode

Located under `@timeboxing/shared`, this constant map centralizes all status codes used across domain error classes:

```ts
export const DomainHttpCode = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
} as const;
```

### 3. Domain Error Subclasses

Each domain-specific error extends `BaseDomainError`, providing a static status code and message for Swagger and HTTP handling, while preserving dynamic context at runtime:

```ts
export class InvalidEmailError extends BaseDomainError {
  static override readonly statusCode = DomainHttpCode.UNPROCESSABLE_ENTITY;
  static override readonly swaggerMessage = 'Invalid email format.';

  constructor(email: string) {
    super(`The email "${email}" is invalid.`);
  }
}
```

### 4. Exception Filtering

A global NestJS exception filter handles all `BaseDomainError` subclasses and converts them to structured HTTP responses:

```ts
if (exception instanceof BaseDomainError) {
  const ctor = exception.constructor as typeof BaseDomainError;
  const status = ctor.statusCode ?? 400;

  return response.status(status).json({
    statusCode: status,
    message: exception.message,
    error: exception.name,
  });
}
```

### 5. ResultValue Integration

The `ResultValue<T, E extends Error>` wrapper is used to return domain errors in a functional and testable way. Consumers can unwrap values or throw caught errors based on `isOk` checks.

```ts
if (!result.isOk) throw result.error;
const value = result.unwrap();
```

## Example Usage

```ts
// domain/user/errors/InvalidEmailError.ts
import { BaseDomainError, DomainHttpCode } from '@timeboxing/shared';

export class InvalidEmailError extends BaseDomainError {
  static override readonly statusCode = DomainHttpCode.UNPROCESSABLE_ENTITY;
  static override readonly swaggerMessage = 'Invalid email format';

  constructor(email: string) {
    super(`The email "${email}" is invalid.`);
  }
}
```

## Consequences

* ✅ Consistent and explicit domain errors
* ✅ Fully testable and structured
* ✅ Play well with both ResultValue and throw/catch logic
* ✅ Supports HTTP + Swagger error shapes cleanly
* ❌ Requires maintaining both `swaggerMessage` and `message`
