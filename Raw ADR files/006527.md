# ADR-001: OCaml-Based Architecture for SDK Generation

## Status
Accepted

## Context
We need to build a reliable, type-safe authentication SDK generator that can produce SDKs for multiple programming languages. The generator must be maintainable, extensible, and capable of producing production-ready code.

## Decision
We will use OCaml as the primary language for the SDK generator implementation.

## Rationale

### Advantages of OCaml:
1. **Strong Type System**: OCaml's type system prevents many runtime errors and provides excellent compile-time guarantees
2. **Pattern Matching**: Excellent for AST manipulation and code generation workflows
3. **Functional Programming**: Pure functions make code generation predictable and testable
4. **Performance**: Compiled OCaml provides excellent performance for build-time tooling
5. **Dune Build System**: Modern, reliable build system with good dependency management
6. **ppx_deriving**: Automatic code generation for common patterns (show, equality, etc.)

### Architecture Benefits:
- **AST-Driven Design**: OCaml's algebraic data types perfectly model authentication protocol specifications
- **Code Generation**: Pattern matching makes template generation clean and maintainable
- **Error Handling**: Result types provide explicit error handling without exceptions
- **Modularity**: OCaml's module system enables clean separation of concerns

## Implementation Strategy

### Core Components:
1. **AST Layer** (`lib/ast/`): Define authentication protocol data structures
2. **Parser Layer** (`lib/parsers/`): Parse specification files into AST
3. **Generator Layer** (`lib/generators/`): Generate language-specific SDKs from AST
4. **Validation Layer** (`lib/validators/`): Validate generated code before output
5. **Utils Layer** (`lib/utils/`): Shared utilities (version fetching, etc.)

### Build System:
- **Dune**: Modern OCaml build system with workspace support
- **Libraries**: Core, Unix, Str, Yojson for essential functionality
- **Testing**: Integrate with CI for automated validation

## Consequences

### Positive:
- Type-safe code generation reduces bugs in generated SDKs
- Pattern matching makes adding new language targets straightforward
- Functional approach makes testing and reasoning easier
- Compiled binary provides fast generation performance

### Negative:
- OCaml has a smaller ecosystem than mainstream languages
- Learning curve for contributors unfamiliar with functional programming
- Fewer developers with OCaml experience for maintenance

## Alternatives Considered

1. **TypeScript/Node.js**: More accessible but lacks strong typing for AST manipulation
2. **Rust**: Strong typing but steeper learning curve and more verbose syntax
3. **Go**: Simple but lacks pattern matching and algebraic data types
4. **Python**: Easy to write but runtime errors and slower performance

## Related ADRs
- ADR-002: Multi-Language SDK Generation Strategy
- ADR-003: In-Memory Validation Architecture