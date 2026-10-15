# ADR-013: TypeScript Service Layer Standardization

## Status

Accepted

## Context

The frontend codebase has evolved to require a robust, maintainable, and scalable pattern for TypeScript service modules. Previous ADRs and documentation recommended domain-based API modules, centralized API logic, and consistent error handling, but did not formalize a concrete, enforceable standard for service structure, API abstraction, and endpoint configuration.

## Decision

The following architectural standard is adopted for all TypeScript service modules:

### 1. Service Structure

- **Class-based services**: Each domain (e.g., courses, learning tasks) implements a class encapsulating all related async methods.
- **Singleton export**: Each service is exported as a singleton instance.
- **TSDoc/JSDoc**: All public classes and methods must be documented.
- **Separation of concerns**: React hooks and UI logic are extracted from services.

### 2. API Abstraction

- **Generic API Layer**: All HTTP calls are made via a generic, type-safe `apiService` abstraction, wrapping axios and supporting error logging, auth interception, and extensibility.
- **No direct axios calls**: Components and services must not use axios directly.

### 3. Endpoint Configuration

- **Centralized API_CONFIG**: All endpoints are defined in a single configuration object, supporting both static and dynamic (function-based) endpoints.
- **Maintainability**: Changes to endpoint paths or base URLs are made in one place.

### 4. Error Handling

- **Consistent error handling**: All service methods must catch and rethrow errors with domain-relevant messages.
- **Centralized logging**: Errors are logged in the API layer.

### 5. Typing and Documentation

- **Strict typing**: All service methods must use strict TypeScript types for parameters and return values.
- **No `any` types**: Avoid `any` in service interfaces and responses.

### 6. Backward Compatibility

- **Legacy exports**: When refactoring, export legacy function names as references to new methods, with deprecation notices.

## Consequences

- **Supersedes**: This ADR formalizes and supersedes any previous, less-specific guidance on service structure, API config, and HTTP abstraction (see ADR-002, ADR-005).
- **Template**: `learningTaskService.ts` and `courseService.ts` are canonical templates for new services.
- **API_CONFIG**: Is required for all new and refactored services.
- **Migration**: Legacy services must be migrated to this standard as part of ongoing technical debt reduction.

## References

- [TypeScript Services Standardization Initiative](../drafts/typescript_services_standardization.md)
- [Task: TypeScript Services Standardization](../tasks/Task_TYPESCRIPT-SERVICES-STANDARDIZATION-001.md)
- [learningTaskService.ts](../../frontend/src/services/resources/learningTaskService.ts)
- [courseService.ts](../../frontend/src/services/resources/courseService.ts)
- [apiService.ts](../../frontend/src/services/api/apiService.ts)
- [apiConfig.ts](../../frontend/src/services/api/apiConfig.ts)
- ADR-002-TypeScript-Typenstruktur.md
- ADR-005-Frontend_Architecture.MD

## Status

Accepted 2025-04-12

## Superseded/Updated ADRs

- ADR-002-TypeScript-Typenstruktur.md (service/API structure section)
- ADR-005-Frontend_Architecture.MD (API service structure section)
