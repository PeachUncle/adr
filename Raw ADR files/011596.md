---
adr_id: ADR001
title: "Adopt mcp-go Library for MCP Protocol Implementation"
status: "accepted"
date: 2025-07-20
authors: ["Development Team"]
---

# ADR001: Adopt mcp-go Library for MCP Protocol Implementation

## Status

accepted - 2025-07-20

## Context

During the implementation of T02_S01 (MCP Protocol Types & Structures), we initially planned to create a custom implementation of the Model Context Protocol (MCP) building on our JSON-RPC foundation. However, we discovered the existence of a mature, well-maintained Go library for MCP: github.com/mark3labs/mcp-go.

The custom implementation approach would require:
- Implementing all MCP message types from scratch
- Ensuring compliance with the MCP specification
- Maintaining the implementation as the specification evolves
- Handling edge cases and protocol nuances
- Extensive testing for protocol compliance

## Decision

We have decided to adopt the github.com/mark3labs/mcp-go library (v0.34.0) as the foundation for our MCP protocol implementation instead of creating a custom implementation.

We will create a wrapper package in `internal/protocol/mcp/` that:
- Provides type aliases for convenient access to mcp-go types
- Offers helper functions for common operations
- Maintains compatibility with our existing JSON-RPC router
- Adds project-specific functionality as needed

## Consequences

### Positive

- **Reduced Development Time**: Eliminates need to implement MCP protocol from scratch
- **Specification Compliance**: Leverages battle-tested, specification-compliant implementation
- **Maintenance Burden**: Reduces long-term maintenance of protocol implementation
- **Quality Assurance**: Benefits from community testing and bug fixes
- **Future-Proofing**: Automatic compatibility with protocol updates
- **Focus on Business Logic**: Allows team to focus on core orchestration features
- **Faster Time to Market**: Accelerates development of MVP features

### Negative

- **External Dependency**: Introduces dependency on third-party library
- **Learning Curve**: Team needs to understand mcp-go API and patterns
- **Customization Limitations**: May be constrained by library's design decisions
- **Version Management**: Need to manage library updates and potential breaking changes

## Alternatives Considered

### Custom MCP Implementation

**Description**: Implement MCP protocol types and handlers from scratch building on our JSON-RPC foundation.

**Reasoning for rejection**: 
- High development effort with limited business value
- Risk of specification non-compliance
- Ongoing maintenance burden
- Slower time to market for core features

### Fork mcp-go Library

**Description**: Fork the mcp-go library and customize it for our specific needs.

**Reasoning for rejection**:
- Creates maintenance burden similar to custom implementation
- Loses benefit of community updates and bug fixes
- Unnecessary complexity for current requirements

### Hybrid Approach

**Description**: Use mcp-go for core protocol handling but implement custom extensions.

**Reasoning for rejection**:
- Our wrapper approach achieves the same benefits with less complexity
- Can still add custom functionality through helper functions and extensions

## Implementation Notes

### Integration Approach
1. Added mcp-go dependency to go.mod
2. Created wrapper package in `internal/protocol/mcp/types.go`
3. Provided type aliases for convenient access: `Tool = mcp.Tool`, etc.
4. Implemented helper functions for common operations
5. Created example server demonstrating integration
6. Updated tests to work with mcp-go types

### Migration Steps Completed
- ✅ Refactored T02_S01 to use mcp-go library
- ✅ Created wrapper package with type aliases
- ✅ Fixed TextResourceContents type alias issue
- ✅ Updated all tests to pass with new implementation
- ✅ Created example server using mcp-go patterns
- ✅ Verified compatibility with existing JSON-RPC router

### Future Considerations
- Monitor mcp-go library updates for new features and breaking changes
- Evaluate need for additional wrapper functions as requirements evolve
- Consider contributing improvements back to mcp-go community

## Related

- Task T02_S01: MCP Protocol Types & Structures
- Task T05_S01: Initialize/Initialized Handshake (should leverage mcp-go capabilities)
- Task T07_S01: MCP Error Extensions (should extend mcp-go error handling)
- Sprint S01 Documentation: Updated to reflect mcp-go integration
- Project Manifest: Updated technical stack to include mcp-go library
