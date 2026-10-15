# ADR-001: Use TypeScript for MCP Development

## Status
Accepted

## Context

We need to choose a programming language for developing MCP servers in this workspace. The key considerations are:

- **Type Safety**: MCP involves complex data structures and protocols that benefit from compile-time type checking
- **Developer Experience**: Need good tooling, IDE support, and debugging capabilities
- **MCP SDK Support**: The official MCP SDK has first-class TypeScript support
- **Team Expertise**: Most team members are familiar with TypeScript
- **Ecosystem**: Need access to npm packages for various integrations

JavaScript is the alternative, but it lacks type safety which is crucial for protocol implementations.

## Decision

We will use TypeScript as the primary language for all MCP server development in this workspace.

Specific choices:
- TypeScript 5.0+ for latest features
- Strict mode enabled (`strict: true`)
- ES2022 target for modern JavaScript features
- Module resolution set to Node16/NodeNext
- Source maps enabled for debugging

## Consequences

### Positive
- **Type Safety**: Catch errors at compile time rather than runtime
- **Better IDE Support**: IntelliSense, refactoring, and navigation
- **Self-Documenting**: Types serve as inline documentation
- **MCP SDK Integration**: Seamless integration with TypeScript SDK
- **Refactoring Confidence**: Type system helps with safe refactoring

### Negative
- **Build Step Required**: Need to compile TypeScript to JavaScript
- **Learning Curve**: Developers need to understand TypeScript concepts
- **Configuration Complexity**: More configuration files (tsconfig.json)
- **Slightly Slower Development**: Type annotations take time to write

### Neutral
- **Ecosystem Compatibility**: Can still use JavaScript libraries
- **Gradual Adoption**: Can mix JavaScript and TypeScript if needed
- **Tool Requirements**: Need TypeScript-aware tools and linters

## Implementation

1. Base TypeScript configuration in `tsconfig.base.json`
2. Per-project configurations extending the base
3. Nx handles the build pipeline
4. ESLint configured for TypeScript

## References
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)
- Related ADR: [002-nx-monorepo.md](./002-nx-monorepo.md) 