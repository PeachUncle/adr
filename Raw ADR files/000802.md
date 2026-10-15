---
docid: ADR-094
title: ADR 050 Typescript Mcp Server
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

---
docid: ADR-050
title: TypeScript MCP Server for AI-Assisted Development
owner: @SARAH
status: Accepted
---

## Context

The project currently has a Roslyn MCP server (RoslynMCP) providing AI-assisted C# code analysis and development tools. The frontend codebase uses TypeScript extensively, but lacks equivalent AI tooling for TypeScript development tasks.

We need a TypeScript MCP server to provide similar capabilities for TypeScript code, enabling:
- Symbol search and analysis
- Type checking and error detection
- Refactoring suggestions
- Code intelligence for AI-assisted development

## Decision

Implement a TypeScript MCP server (TypeScriptMCP) using Node.js and TypeScript language services, following the same architectural pattern as RoslynMCP.

## Rationale

### Benefits
- **Parity with C# tooling**: Provides equivalent AI assistance for TypeScript as exists for C#
- **Improved productivity**: AI can leverage TypeScript language services for better code suggestions
- **Consistency**: Follows established MCP server pattern in the project
- **Frontend support**: Addresses the TypeScript-heavy frontend codebase

### Technical Feasibility
- TypeScript provides rich language services APIs
- MCP protocol supports Node.js implementations
- Can integrate with existing TypeScript compiler and tooling

## Implementation

### Architecture
- **Language**: Node.js/TypeScript
- **APIs**: @typescript/language-services
- **Location**: `tools/TypeScriptMCP/`
- **Configuration**: Add to `.vscode/mcp.json`

### Core Tools
- SearchSymbols: Find TypeScript symbols with patterns
- GetSymbolInfo: Detailed symbol information
- FindUsages: Locate all references
- AnalyzeTypes: Type checking and diagnostics
- RefactorSuggestions: Basic refactoring operations

### Dependencies
- @modelcontextprotocol/sdk
- typescript
- @typescript/language-services

## Consequences

### Positive
- Enhanced AI assistance for TypeScript development
- Consistent tooling across C# and TypeScript codebases
- Leverages existing TypeScript ecosystem

### Negative
- Additional maintenance overhead for another MCP server
- Node.js runtime dependency in tools/

### Risks
- TypeScript language services API changes
- Performance considerations for large codebases

## Alternatives Considered

### 1. Extend RoslynMCP
- Rejected: Roslyn is C#-specific, cannot handle TypeScript

### 2. Use existing TypeScript language server
- Rejected: Not MCP-compatible, would require wrapper

### 3. No TypeScript MCP server
- Rejected: Leaves gap in AI tooling parity

## Status

Proposed - Ready for implementation

## References

- [RoslynMCP README](../tools/RoslynMCP/README.md)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [TypeScript Language Services](https://github.com/microsoft/TypeScript/wiki/Using-the-Language-Service-API)