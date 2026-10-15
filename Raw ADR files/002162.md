# ADR 003: Error Handling Strategy

## Status

Accepted

## Context

The Documentation System needs a consistent approach to error handling across all components. The Level 3 Audit identified several issues with the current approach:

1. Inconsistent error handling across different parts of the system
2. Poor error propagation between layers
3. Lack of structured error information for client consumers
4. Missing contextual information in error logs
5. No clear distinction between different error types (validation, business, technical)

We need an error handling strategy that:
- Provides consistent error handling across all components
- Preserves error context across layer boundaries
- Presents useful information to API consumers
- Supports detailed logging and monitoring
- Distinguishes between different error types

## Decision

We will implement a comprehensive error handling strategy with the following components:

### 1. Domain-Specific Exceptions

Create a hierarchy of domain-specific exceptions that represent business rule violations and domain constraints:

```
BaseException
├── DomainException
│   ├── DocumentException
│   │   ├── DocumentNotFoundException
│   │   ├── DocumentAlreadyExistsException
│   │   ├── DocumentLockedException
│   │   └── ...
│   ├── WorkflowException
│   │   ├── WorkflowNotFoundException
│   │   ├── WorkflowStepInvalidException
│   │   └── ...
│   └── ...
├── ApplicationException
│   ├── ValidationException
│   ├── AuthorizationException
│   ├── AuthenticationException
│   └── ...
└── InfrastructureException
    ├── DatabaseException
    ├── ExternalServiceException
    ├── ConfigurationException
    └── ...
```

### 2. Error Codes and Categorization

Assign unique error codes to exceptions with standardized prefixes:
- `DOM-`: Domain exceptions
- `APP-`: Application exceptions
- `INF-`: Infrastructure exceptions
- `SEC-`: Security exceptions
- `VAL-`: Validation exceptions

### 3. Rich Error Context

Ensure exceptions carry contextual information:
- Error code
- Error message (user-friendly)
- Technical details (for logging)
- Timestamp
- Correlation ID
- Affected resource(s)
- Suggested actions (where applicable)

### 4. Layer-Specific Error Handling

**Domain Layer**:
- Throw domain-specific exceptions for business rule violations
- Keep exceptions focused on domain concepts
- Don't include technical details or infrastructure concerns

**Application Layer**:
- Catch and translate domain exceptions if needed
- Add application context to exceptions
- Throw application-specific exceptions for use case failures

**Infrastructure Layer**:
- Catch technical exceptions and translate to domain/application exceptions
- Log detailed technical information
- Preserve original exception as inner exception

**Interfaces Layer**:
- Catch all exceptions and map to appropriate HTTP status codes
- Format error responses according to API standards
- Log error occurrences with correlation IDs

### 5. Standardized Error Response Format

API error responses will follow a consistent format:

```json
{
  "error": {
    "code": "DOM-1001",
    "message": "Document not found",
    "details": "The requested document with ID '12345' could not be found",
    "timestamp": "2025-04-16T12:34:56.789Z",
    "correlationId": "abc-123-def-456",
    "path": "/api/documents/12345",
    "validationErrors": [
      {
        "field": "title",
        "message": "Title is required"
      }
    ]
  }
}
```

### 6. Global Error Handling

Implement global error handlers at application boundaries that:
- Catch unhandled exceptions
- Transform exceptions to appropriate responses
- Log all errors with contextual information
- Track error metrics for monitoring

### 7. Error Logging Strategy

Log errors with structured information:
- Log in JSON format for machine parsing
- Include correlation ID for request tracing
- Include contextual information (user, resource, action)
- Log stack traces only for unexpected exceptions
- Use appropriate log levels:
  - ERROR: Unexpected system errors
  - WARN: Expected failures (e.g., validation errors)
  - INFO: Normal operations

## Consequences

### Positive

1. **Consistency**: Unified approach to error handling across all components
2. **Traceability**: Error context preserved across layer boundaries
3. **Improved UX**: Clients receive meaningful error information
4. **Better Troubleshooting**: Detailed logs with contextual information
5. **Error Classification**: Clear distinction between different error types

### Negative

1. **Implementation Overhead**: Requires creating and maintaining exception hierarchy
2. **Potential Over-Engineering**: May be excessive for simple use cases
3. **Learning Curve**: Developers need to understand exception hierarchy and when to use each type

## Implementation Details

### Example Domain Exception

```javascript
class DocumentNotFoundException extends DomainException {
  constructor(documentId) {
    super(
      'DOM-1001',                           // Error code
      'Document not found',                 // User-friendly message
      `Document with ID ${documentId} not found` // Technical details
    );
    this.documentId = documentId;
  }
}
```

### Example Application Layer Error Handling

```javascript
class GetDocumentHandler {
  constructor(documentRepository) {
    this.documentRepository = documentRepository;
  }
  
  async handle(query) {
    try {
      const document = await this.documentRepository.getById(query.documentId);
      
      if (!document) {
        throw new DocumentNotFoundException(query.documentId);
      }
      
      return this.mapToDocumentDto(document);
    } catch (error) {
      if (error instanceof DomainException) {
        // Rethrow domain exceptions directly
        throw error;
      }
      
      // Log and translate infrastructure exceptions
      this.logger.error('Error retrieving document', {
        documentId: query.documentId,
        error: error.message,
        stack: error.stack
      });
      
      throw new ApplicationException(
        'APP-2001',
        'Failed to retrieve document',
        `Error retrieving document with ID ${query.documentId}`,
        error
      );
    }
  }
  
  mapToDocumentDto(document) {
    // Map domain object to DTO
  }
}
```

### Example API Controller Error Handling

```javascript
// Global error middleware
function errorMiddleware(err, req, res, next) {
  const correlationId = req.headers['x-correlation-id'] || uuidv4();
  
  // Log the error
  logger.error(`Error processing request: ${err.message}`, {
    correlationId,
    path: req.path,
    method: req.method,
    errorCode: err.code,
    errorMessage: err.message,
    stack: err.stack
  });
  
  // Build standard error response
  const errorResponse = {
    error: {
      code: err.code || 'SYS-0001',
      message: err.userMessage || 'An unexpected error occurred',
      details: err.technicalDetails || err.message,
      timestamp: new Date().toISOString(),
      correlationId,
      path: req.path
    }
  };
  
  // Add validation errors if present
  if (err.validationErrors) {
    errorResponse.error.validationErrors = err.validationErrors;
  }
  
  // Map exception types to HTTP status codes
  let statusCode = 500;
  
  if (err instanceof ValidationException) statusCode = 400;
  else if (err instanceof AuthenticationException) statusCode = 401;
  else if (err instanceof AuthorizationException) statusCode = 403;
  else if (err instanceof DocumentNotFoundException) statusCode = 404;
  // Additional mappings...
  
  res.status(statusCode).json(errorResponse);
}
```

## Compliance

This error handling strategy directly addresses the Level 3 Audit findings by:
1. Providing consistent error handling across all components
2. Establishing clear error propagation between layers
3. Defining structured error information for client consumers
4. Including contextual information in error logs
5. Creating distinct error types for different scenarios (validation, business, technical)

## References

1. "Enterprise Integration Patterns" by Gregor Hohpe and Bobby Woolf
2. "Implementing Domain-Driven Design" by Vaughn Vernon
3. [RFC 7807 - Problem Details for HTTP APIs](https://tools.ietf.org/html/rfc7807)
4. [Microsoft REST API Guidelines](https://github.com/Microsoft/api-guidelines/blob/master/Guidelines.md#7102-error-condition-responses)