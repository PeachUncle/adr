# ADR 0017: Application-Level Data Validation

## Status

Accepted

## Context

The OpsCore application handles various types of data that require validation beyond what database constraints can enforce. While the database schema (ADR 0005) enforces basic constraints like NOT NULL and CHECK constraints, the application layer needs to perform more sophisticated validation to ensure data integrity and security.

Key areas requiring application-level validation include:
1. Variable definitions and values (ADR 0013)
2. Document versions and metadata
3. Execution records and status transitions
4. File paths and security-sensitive inputs

## Decision

The application will enforce the following validation rules at the domain and application layers:

### VariableDefinition Validation

VariableDefinition objects must be validated when parsing from frontmatter or receiving from API requests:

- **name**: Alphanumeric characters and underscores only, maximum 100 characters
  - Pattern: `^[a-zA-Z0-9_]+$`
  - Prevents injection attacks and ensures compatibility with templating
- **label**: Non-empty string, maximum 255 characters
  - Required for UI display
- **description**: Optional string, maximum 1000 characters
- **type**: Must be one of: `"string"`, `"number"`, `"boolean"`, `"date"`
  - Enforces type safety for variable values
- **required**: Must be boolean value
- **defaultValue**: Type must match the `type` field
  - String values for `type: "string"`
  - Numeric values for `type: "number"`
  - Boolean values for `type: "boolean"`
  - ISO 8601 date strings for `type: "date"`

### VariableValue Validation

VariableValue objects must be validated when executing procedures:

- **name**: Must match a variable name defined in the document's VariableDefinition array
  - Prevents undefined variable references
- **value**: Type must match the corresponding VariableDefinition's type
  - String, number, boolean, or date based on definition
- **Required variables**: All variables marked as `required: true` must have values
  - Execution cannot proceed without required values

### DocumentVersion Validation

DocumentVersion data must be validated when creating or updating versions:

- **title**: Non-empty string, maximum 255 characters
  - Required for document identification
- **file_path**: Valid relative path with security checks
  - No directory traversal sequences (`../`, `..\\`)
  - No absolute paths (must be relative to repository root)
  - Maximum 500 characters
- **commit_hash**: Valid Git SHA hash
  - 40 characters (SHA-1) or 64 characters (SHA-256)
  - Hexadecimal characters only: `^[a-f0-9]{40}$` or `^[a-f0-9]{64}$`
- **doc_type**: Must be one of: `"procedure"`, `"knowledge"`
- **tags**: Array of valid tag strings
  - Each tag: maximum 50 characters, alphanumeric and hyphens
  - Pattern per tag: `^[a-zA-Z0-9-]+$`
- **variables**: Must be valid VariableDefinition array (can be null or empty)
  - Each element validated per VariableDefinition rules
- **content**: Non-empty Markdown text
  - Must contain actual content (not just whitespace)

### ExecutionRecord Validation

ExecutionRecord data must be validated during procedure execution:

- **variable_values**: All variable names must exist in the document version's variables
  - Prevents invalid variable references
  - All values must match their definition types
- **status**: Status transitions must follow valid state machine
  - Valid transitions:
    - `in_progress` → `completed`
    - `in_progress` → `failed`
  - Invalid transitions:
    - `completed` → `in_progress` (cannot restart completed execution)
    - `failed` → `in_progress` (cannot restart failed execution)
    - `completed` → `failed` (cannot change outcome)
    - `failed` → `completed` (cannot change outcome)

### General Security Validations

All user inputs must be validated for security:

- **No SQL injection**: All database queries use parameterized statements
- **No path traversal**: File paths validated to prevent directory traversal
- **Input sanitization**: User-provided strings sanitized before storage
- **Length limits**: All strings have reasonable maximum lengths to prevent DoS

## Implementation Approach

### Domain Layer Validation

Value objects and entities in the domain layer enforce validation in their constructors:

```go
// Example: VariableDefinition value object
func NewVariableDefinition(name, label, description, varType string, required bool, defaultValue interface{}) (*VariableDefinition, error) {
    if !isValidVariableName(name) {
        return nil, errors.New("invalid variable name format")
    }
    if label == "" {
        return nil, errors.New("label cannot be empty")
    }
    if !isValidType(varType) {
        return nil, errors.New("invalid variable type")
    }
    // ... more validation
    
    return &VariableDefinition{
        name: name,
        label: label,
        // ...
    }, nil
}
```

### Application Layer Validation

Use cases validate DTOs before passing to domain layer:

```go
// Example: CreateDocumentVersionUseCase
func (uc *CreateDocumentVersionUseCase) Execute(ctx context.Context, input CreateVersionDTO) error {
    // Validate input DTO
    if err := validateDocumentVersionInput(input); err != nil {
        return err
    }
    
    // Create domain object (with additional domain validation)
    version, err := entity.NewDocumentVersion(...)
    if err != nil {
        return err
    }
    
    // Persist
    return uc.repo.Save(ctx, version)
}
```

### API Layer Validation

API schemas use binding tags for basic validation, but delegate complex validation to lower layers:

```go
type CreateVersionRequest struct {
    Title      string   `json:"title" binding:"required,max=255"`
    FilePath   string   `json:"filePath" binding:"required,max=500"`
    CommitHash string   `json:"commitHash" binding:"required,len=40"`
    // ... more fields
}
```

## Consequences

### Pros

- **Data Integrity**: Ensures data quality throughout the system
- **Security**: Prevents injection attacks and path traversal vulnerabilities
- **Early Error Detection**: Catches invalid data before it reaches the database
- **Clear Contracts**: Explicit validation rules document expected data formats
- **Consistency**: Validation rules are documented and enforced uniformly
- **Type Safety**: Strong typing with validation catches errors at compile time

### Cons

- **Implementation Overhead**: Requires writing validation logic in multiple layers
- **Maintenance**: Validation rules must be kept in sync across layers
- **Performance**: Validation adds computational overhead (minimal but measurable)
- **Testing Complexity**: Each validation rule needs test coverage

## Related ADRs

- ADR 0005: Database Schema - Defines database-level constraints that complement application validation
- ADR 0007: Backend Architecture - Defines where validation occurs in the onion architecture
- ADR 0013: Document Variable Definition - Defines the structure of variables that need validation
- ADR 0014: Execution Record and Evidence Management - Defines execution record lifecycle and state machine
- ADR 0015: Backend Custom Error Design - Defines how validation errors are represented and returned

## References

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [PostgreSQL Data Type Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
