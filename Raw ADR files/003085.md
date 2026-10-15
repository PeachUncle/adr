# ADR-001: Use .NET 9.0 for MCP Server Implementation

**Status**: Accepted

**Date**: 2025-10-29

## Context

We need to choose a technology stack for implementing an MCP (Model Context Protocol) server. The server needs to:

- Implement the MCP specification for tool discovery and execution
- Provide cross-platform compatibility (Windows, macOS, Linux)
- Offer good performance for JSON-RPC communication over stdio
- Support easy distribution and deployment
- Integrate well with existing Microsoft toolchain and IDEs

## Decision

We will use .NET 9.0 with the official Microsoft ModelContextProtocol SDK for implementing the MCP server.

### Options Considered

1. **.NET 9.0 with Microsoft MCP SDK** ✅
   - Pros: Official Microsoft support, excellent tooling, cross-platform, strong type system, good performance
   - Cons: Newer framework (potential stability concerns), requires .NET knowledge

2. **Node.js with TypeScript**
   - Pros: Large ecosystem, JSON-native, widely adopted for MCP servers
   - Cons: Runtime dependency, less type safety than .NET, performance considerations

3. **Python with official MCP SDK**
   - Pros: Simple syntax, official MCP support, rapid development
   - Cons: Runtime dependency, performance limitations, distribution complexity

4. **Go**
   - Pros: Excellent performance, single binary distribution, no runtime deps
   - Cons: No official MCP SDK, would need custom implementation

## Decision Rationale

- **Official Support**: Microsoft provides the ModelContextProtocol NuGet package with first-class support
- **Performance**: .NET 9.0 offers excellent performance for JSON processing and reflection-based tool discovery
- **Type Safety**: Strong typing helps catch errors at compile time and provides better IDE support
- **Distribution**: Self-contained single-file executables eliminate runtime dependencies
- **Ecosystem**: Rich .NET ecosystem with extensive libraries and tooling
- **IDE Integration**: Native support in Visual Studio and VS Code with excellent debugging experience

## Consequences

### Positive
- Strong type safety reduces runtime errors
- Excellent development experience with Visual Studio/VS Code
- Self-contained distribution simplifies deployment
- Good performance characteristics for MCP workloads
- Official Microsoft support ensures long-term viability
- Cross-platform compatibility out of the box

### Negative
- Learning curve for developers not familiar with .NET
- Larger executable size compared to interpreted languages
- Newer .NET version may have less community content/examples
- Build process requires .NET SDK (though runtime is self-contained)

### Neutral
- Need to follow .NET conventions and patterns
- Dependency on Microsoft's MCP SDK evolution
- Regular updates needed to stay current with .NET releases

## Implementation Notes

- Target .NET 9.0 specifically for latest features and performance improvements
- Use Microsoft.Extensions.Hosting for application lifecycle management
- Leverage dependency injection for tool registration and service management
- Configure multi-platform builds for broad compatibility
- Package as NuGet tool for easy distribution

## Related ADRs

- [ADR-002: Choose stdio Transport for MCP Communication](002-stdio-transport.md)
- [ADR-003: Use Attribute-Based Tool Discovery](003-attribute-based-tools.md)