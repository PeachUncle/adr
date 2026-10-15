# ADR-002: Multi-Language SDK Generation Strategy

## Status
Accepted

## Context
We need to generate OAuth 2.0 authentication SDKs for multiple programming languages. Each language has different conventions, dependency management systems, and best practices that must be respected.

## Decision
We will implement a multi-language SDK generation system with language-specific generators that share a common AST and validation framework.

## Architecture

### Shared Components:
1. **Common AST**: Single source of truth for authentication specifications
2. **DSL Parser**: Unified parser for `.auth` specification files
3. **Validation Framework**: Language-agnostic OAuth2 compliance validation
4. **CLI Interface**: Multi-language target selection with consistent UX

### Language-Specific Generators:

#### TypeScript Generator (`lib/generators/typescript/`)
- **Target Audience**: Web applications, Node.js services
- **Key Features**:
  - Strict TypeScript with enhanced type checking
  - Modern OAuth2 client with PKCE support
  - Complete project structure (package.json, tsconfig.json, README.md)
  - Dynamic npm dependency version fetching with fallback strategies
  - Integration with popular TypeScript ecosystem tools

#### Python Generator (`lib/generators/python/`)
- **Target Audience**: Python applications, data science, automation
- **Key Features**:
  - Modern async/await OAuth2 client implementation
  - Dataclasses and comprehensive type hints (Python 3.8+)
  - Complete project structure (setup.py, requirements.txt, configuration files)
  - Integration with Python tooling (mypy, pytest, black)
  - Requests library for HTTP client functionality

## Implementation Strategy

### Generator Interface:
Each language generator implements:
```ocaml
val generate_sdk : auth_spec -> string -> unit
val validate_generated_client : auth_spec -> provider -> unit
```

### Code Generation Approach:
1. **Template-Based**: Use OCaml string interpolation for code templates
2. **AST-Driven**: Generate code structure based on parsed authentication specification
3. **Language-Specific**: Respect each language's idioms and conventions
4. **Complete Projects**: Generate full project structures, not just source files

### Validation Strategy:
1. **Pre-Generation Validation**: Validate AST and configuration before code generation
2. **Structural Validation**: Ensure generated code contains required OAuth2 components
3. **Language-Specific Validation**: Compile/syntax check generated code
4. **Integration Testing**: Verify generated SDKs build and import successfully

## Language Selection Criteria

Languages are prioritized based on:
1. **Community Demand**: Popular languages for authentication integration
2. **Ecosystem Maturity**: Strong OAuth2/HTTP client library ecosystems
3. **Maintainability**: Languages we can effectively support long-term
4. **Use Case Coverage**: Different deployment scenarios (web, mobile, server, etc.)

## CLI Design

```bash
# Language selection
auth-sdk-generator --lang typescript specs/app.auth output/
auth-sdk-generator --lang python specs/app.auth output/

# Validation control
auth-sdk-generator --no-validate specs/app.auth output/
auth-sdk-generator --validate specs/app.auth output/
```

## Consequences

### Positive:
- Unified OAuth2 implementation across multiple languages
- Consistent API surface and behavior across generated SDKs
- Shared validation ensures OAuth2 compliance
- Language-specific best practices are respected
- Easy to add new language targets

### Negative:
- Increased maintenance burden for multiple generators
- Language-specific expertise required for each generator
- Testing complexity scales with number of supported languages
- CLI complexity increases with options and languages

## Future Language Targets

Planned future language support:
1. **Java**: Enterprise applications, Android development
2. **Go**: Cloud services, microservices
3. **Rust**: System programming, performance-critical applications
4. **Swift**: iOS development, server-side Swift
5. **C#/.NET**: Windows applications, enterprise development

## Related ADRs
- ADR-001: OCaml-Based Architecture
- ADR-003: In-Memory Validation Architecture
- ADR-004: Dynamic Dependency Management