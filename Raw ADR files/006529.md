# ADR-003: In-Memory Code Validation Strategy

## Status
Accepted

## Context
We need to ensure that generated SDKs are syntactically correct, semantically valid, and production-ready before writing files to disk. This prevents the generation of invalid SDKs that would fail to build or contain security vulnerabilities.

## Decision
We will implement a comprehensive in-memory validation system that validates generated code before file creation using a multi-layer validation pipeline.

## Architecture

### Validation Pipeline

#### Layer 1: OAuth2 Structural Validation
- **Purpose**: Ensure generated code contains all required OAuth2 components
- **Implementation**: Pattern matching against generated code strings
- **Validation Points**:
  - OAuth2Client class/object presence
  - PKCE implementation (code verifier, code challenge generation)
  - Required interfaces/types (AuthConfig, TokenSet, AuthError)
  - Authorization URL building and token exchange methods

#### Layer 2: Language-Specific Syntax Validation
- **TypeScript**:
  - Temporary project structure with proper tsconfig.json
  - TypeScript compiler validation with strict type checking
  - Enhanced compiler options (exactOptionalPropertyTypes, noImplicitReturns, etc.)
- **Python**:
  - Python AST compilation with py_compile
  - Module import validation
  - Optional mypy type checking integration

#### Layer 3: Integration Testing Validation
- **TypeScript**: Full npm install and build cycle
- **Python**: Import validation and basic functionality testing
- **Dependency Resolution**: Verify all dependencies can be resolved and installed

### Implementation Strategy

```ocaml
(* Validation result type *)
type validation_result =
  | Ok of unit
  | Error of string

(* Multi-layer validation pipeline *)
let validate_generated_code language code_string =
  code_string
  |> validate_oauth2_structure
  |> Result.bind (validate_language_syntax language)
  |> Result.bind (validate_integration_readiness language)
```

### Temporary Environment Management
- **Isolated Validation**: Each validation runs in a temporary directory
- **Cleanup**: Automatic cleanup of temporary files and directories
- **Process Isolation**: Use separate processes for compiler/interpreter execution
- **Error Capture**: Comprehensive error message capture and formatting

### Validation Configuration
- **Strict Mode** (default): All validation layers enabled
- **Fast Mode**: Skip integration testing for rapid iteration
- **Offline Mode**: Skip network-dependent validations

## CLI Integration

```bash
# Enable validation (default)
auth-sdk-generator --validate specs/app.auth output/

# Disable validation for fast iteration
auth-sdk-generator --no-validate specs/app.auth output/

# Validation-only mode (no file generation)
auth-sdk-generator --validate-only specs/app.auth
```

## Error Reporting

### Comprehensive Error Messages:
- **Context**: Which validation layer failed
- **Details**: Specific error messages from compilers/interpreters
- **Location**: Line numbers and file references when available
- **Suggestions**: Actionable guidance for fixing issues

### Error Message Format:
```
❌ TypeScript validation failed
   📊 Errors found during strict compilation
     src/index.ts:163:5 - error TS2412: Type 'string | undefined' is not assignable to type 'string'
     src/index.ts:164:5 - error TS2412: Type 'string | undefined' is not assignable to type 'string'
```

## Validation-Driven Development

### Generator Quality Assurance:
1. **Test-Driven Development**: Write validation tests before generator implementation
2. **Continuous Validation**: All changes must pass validation pipeline
3. **Regression Prevention**: Validation catches breaking changes immediately
4. **Quality Gates**: Generated SDKs must pass all validation before release

### Performance Optimization:
- **Caching**: Cache compilation results for repeated validations
- **Parallel Validation**: Run multiple validation layers concurrently when possible
- **Incremental Validation**: Only re-validate changed components

## Security Implications

### Code Injection Prevention:
- **Template Sanitization**: Ensure user input cannot inject code into templates
- **Validation Sandboxing**: Run validation in isolated environments
- **Dependency Validation**: Verify all dependencies come from trusted sources

### Generated Code Security:
- **PKCE Enforcement**: Validate PKCE implementation is correctly generated
- **State Parameter Validation**: Ensure state parameter handling is present
- **Token Storage**: Validate secure token handling patterns

## Consequences

### Positive:
- **Zero Invalid SDKs**: No generated SDK will fail to build or contain syntax errors
- **OAuth2 Compliance**: All generated SDKs follow OAuth2 best practices
- **Developer Confidence**: Generated SDKs are guaranteed to be production-ready
- **Early Error Detection**: Catch generator bugs immediately during development
- **Security Assurance**: Generated code follows security best practices

### Negative:
- **Generation Time**: Validation adds overhead to SDK generation process
- **System Dependencies**: Requires language compilers/interpreters on build system
- **Complexity**: Validation system is complex and requires maintenance
- **Resource Usage**: Temporary files and process spawning use system resources

## Testing Strategy

### Validation Tests:
- **Valid Code Tests**: Ensure valid code passes all validation layers
- **Invalid Code Tests**: Ensure invalid code is properly rejected with clear errors
- **Edge Case Tests**: Test boundary conditions and unusual inputs
- **Performance Tests**: Ensure validation completes within reasonable time limits

### Integration Tests:
- **Generated SDK Tests**: Build and test generated SDKs in real environments
- **Cross-Language Consistency**: Ensure all language generators produce equivalent functionality
- **Error Handling Tests**: Verify error messages are helpful and accurate

## Related ADRs
- ADR-001: OCaml-Based Architecture
- ADR-002: Multi-Language SDK Generation Strategy
- ADR-004: Dynamic Dependency Management