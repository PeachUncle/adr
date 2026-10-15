# 2. Structured Logging with Pino

Date: 2025-08-28

## Status

Accepted

## Context

The application needed a robust logging solution that would:

- Support structured logging for better observability
- Provide different configurations for development and production environments
- Automatically redact sensitive information for security
- Integrate well with future observability tools (OpenTelemetry)
- Maintain high performance with minimal overhead
- Support contextual logging for request tracing

## Decision

We chose Pino as our logging library because:

1. **Performance**: Pino is one of the fastest Node.js loggers available
2. **Structured Logging**: Native support for JSON-structured logs
3. **Security**: Built-in redaction capabilities for sensitive data
4. **Flexibility**: Environment-based configuration support
5. **Ecosystem**: Strong ecosystem with tools like pino-pretty for development
6. **Future-proof**: Easy integration path with OpenTelemetry

### Implementation Details

- **Environment-based configuration**:
  - Development: Pretty-printed, colorized output for human readability
  - Production: Structured JSON with correlation ID support
  - Test: Silent by default to avoid cluttering test output

- **Security features**:
  - Automatic redaction of sensitive fields (password, token, api_key, etc.)
  - Support for nested field redaction

- **Developer experience**:
  - Child logger creation for module-specific logging
  - Context preservation through withContext method
  - TypeScript support with custom Logger interface

## Consequences

### Positive

- **Improved Observability**: Structured logs are easier to search and analyze
- **Better Security**: Automatic redaction prevents accidental exposure of sensitive data
- **Performance**: Minimal impact on application performance
- **Developer Experience**: Clear, readable logs in development; structured logs in production
- **Maintainability**: Centralized logger configuration
- **Testability**: 100% test coverage achieved for logger module

### Negative

- **Additional Dependency**: Adds Pino and pino-pretty to the dependency tree
- **Learning Curve**: Developers need to understand structured logging patterns
- **Migration Effort**: Existing console.log statements need to be replaced

### Mitigation

- Comprehensive documentation and examples provided in README.md and CLAUDE.md
- TypeScript types ensure proper usage
- Gradual migration approach supported (console.log still works)

## References

- [Pino Documentation](https://getpino.io/)
- [Issue #66: Structured logging and observability foundation](https://github.com/sapientpants/agentic-node-ts-starter/issues/66)
- [PR #73: feat: add structured logging with Pino](https://github.com/sapientpants/agentic-node-ts-starter/pull/73)
