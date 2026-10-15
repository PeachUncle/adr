# ADR 0010: API Definition Generation and Specification

## Status

Accepted

## Context

To ensure consistency, maintainability, and ease of use for the backend API (initially defined in ADR 0003), we need to establish clear guidelines for how the API definition is created, stored, and specified. Key considerations include the location of the definition file, the method for generating it (manual vs. automated), and the specification format to use. We discussed storing the definition within the source code structure (e.g., `backend/api/`) versus a dedicated documentation folder or the root, using automated tools like `swaggo/swag` versus manual creation, and adopting standard formats like OpenAPI.

## Decision

We have decided on the following approach for managing the backend API definition:

1. **Storage Location:** The generated API definition file (e.g., `openapi.yaml` or `swagger.json`) will be stored in a dedicated directory: `backend/docs/`. This clearly separates generated documentation artifacts from source code.

2. **Generation Method:** We will use the `swaggo/swag` tool (`github.com/swaggo/swag`) to automatically generate the API definition from annotations written directly in the Go source code. This approach keeps the documentation closely tied to the implementation, reducing the risk of drift.

3. **Specification Format:** We will use the OpenAPI Specification (OAS) version 3.x. This is the industry standard, providing wide compatibility with various development and documentation tools.

## Consequences

* **Pros:**
  * Generated definition files are clearly separated in `backend/docs/`.
  * Automation via `swaggo/swag` ensures the API definition stays synchronized with the Go code implementation with minimal manual effort.
  * Adherence to OpenAPI 3.x standard facilitates the use of standard tooling for documentation UI, client generation, testing, etc.
  * `swaggo/swag` is a well-established and widely used tool in the Go ecosystem.

* **Cons:**
  * Developers need to learn the specific annotation syntax required by `swaggo/swag`.
  * The build or development process must incorporate the `swag init` command (or equivalent) to generate/update the definition file.
  * Initial setup and integration of `swaggo/swag` into the project require some effort.

## Implementation Guide

### Prerequisites

Install the `swag` CLI tool:
```bash
go install github.com/swaggo/swag/cmd/swag@latest
```

### Annotation Requirements

All API handler functions must include the following Swagger annotations:

1. **General API Information** (in `main.go`):
```go
// @title OpsCore Backend API
// @version 1.0
// @description This is the API documentation for the OpsCore backend service.
// @host localhost:8080
// @BasePath /api/v1
```

2. **Handler Annotations** (in handler files):
```go
// @Summary Brief description
// @Description Detailed description
// @Tags tag-name
// @Accept json
// @Produce json
// @Param paramName path/query/body type true/false "Description" example:"value"
// @Success 200 {object} schema.ResponseType "Success message"
// @Failure 400 {object} schema.ErrorResponse "Error message"
// @Router /path [method]
```

### Annotation Best Practices

1. **Schema References**: Always use the full package path for schema types:
   - ✅ Correct: `schema.ErrorResponse`
   - ❌ Incorrect: `ErrorResponse` or `handlers.ErrorResponse`

2. **Import Statement**: Ensure proper import of the schema package in handler files:
```go
import (
    "opscore/backend/internal/git_repository/interfaces/api/schema"
)
```

3. **Complete Coverage**: Every public API endpoint must have Swagger annotations to appear in the generated documentation.

### Generation Command

To generate or update the API documentation, run:

```bash
cd /workspaces/backend
swag init -g cmd/server/main.go -o docs --parseDependency --parseInternal --exclude internal/user,internal/execution_record,internal/document
```

**Command Parameters Explanation:**
- `-g cmd/server/main.go`: Specifies the main entry point file containing general API info
- `-o docs`: Output directory for generated files
- `--parseDependency`: Parse external dependencies
- `--parseInternal`: Parse internal packages
- `--exclude`: Exclude modules that are not yet implemented or routed (prevents parsing errors)

### Known Issues and Solutions

#### Issue 1: Unknown Field Errors in Generated Code

**Problem**: After running `swag init`, you may encounter compilation errors:
```
docs/docs.go:524:2: unknown field LeftDelim in struct literal
docs/docs.go:525:2: unknown field RightDelim in struct literal
```

**Solution**: The generated `docs/docs.go` may contain deprecated fields. Manually remove `LeftDelim` and `RightDelim` from the `SwaggerInfo` struct:

```go
// Before (with errors)
var SwaggerInfo = &swag.Spec{
    // ... other fields ...
    LeftDelim:  "{{",
    RightDelim: "}}",
}

// After (fixed)
var SwaggerInfo = &swag.Spec{
    // ... other fields ...
    // Remove LeftDelim and RightDelim
}
```

#### Issue 2: Multiple Schema Packages Conflict

**Problem**: If multiple modules (e.g., `git_repository`, `user`, `execution_record`) have handler files with Swagger annotations but are not yet routed in `main.go`, `swag init` may fail with errors like:
```
cannot find type definition: schema.CreateGroupRequest
```

**Solution**: Use the `--exclude` flag to skip unimplemented modules:
```bash
--exclude internal/user,internal/execution_record,internal/document
```

Only include modules that are actually registered in the router.

#### Issue 3: Schema Type Not Found

**Problem**: Compilation error when schema types cannot be resolved.

**Root Cause**: `swag` cannot find the schema package or type definitions.

**Solution**:
1. Ensure schema types are defined in the correct package
2. Use full package path in annotations (e.g., `schema.ErrorResponse`)
3. Use `--parseDependency` and `--parseInternal` flags

### Accessing Swagger UI

After generation and server startup, access the Swagger UI at:
```
http://localhost:8080/swagger/index.html
```

The endpoint configuration in `main.go`:
```go
r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
```

### Workflow

1. **Add/Modify API Handler**: Write or update handler function with complete Swagger annotations
2. **Generate Documentation**: Run the `swag init` command with appropriate flags
3. **Fix Generated Code**: If necessary, remove deprecated fields from `docs/docs.go`
4. **Verify**: Start the server and check Swagger UI for the new/updated endpoint
5. **Commit**: Include both the handler changes and regenerated `docs/` files in version control

### Notes

- **Regeneration Required**: The `swag init` command must be run every time handler annotations are added or modified
- **Version Control**: All files in `backend/docs/` are generated artifacts but should be committed to the repository for consistency
- **Specification Version**: OpenAPI 3.x remains the intended and accepted specification for the project (see Decision above). However, due to current limitations of `swaggo/swag`, the generated documentation is in Swagger 2.0 format. Migration to OpenAPI 3.x will be prioritized as soon as tool support becomes available or an alternative solution is adopted.
