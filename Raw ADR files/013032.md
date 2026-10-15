# ADR 005: Repository Migration to GitHub and FastMCP Architecture Transition

## Status
Accepted

## Context
The OpenAlex Explorer MCP Server has successfully completed Phase 1 enhancements and is entering Phase 2 development. At this stage, we need to make strategic decisions about our development approach and repository management to support future growth and architectural evolution.

## Decision
We will implement two key changes to our development approach:

### 1. Repository Migration to GitHub
- Transition active development from Hugging Face to GitHub
- Maintain the Hugging Face Space for demo purposes only
- Use GitHub for all future development, collaboration, and issue tracking

### 2. FastMCP Architecture Transition
- Plan to migrate from the current Gradio-based MCP implementation to a specialized FastMCP approach
- Begin architectural refactoring in Phase 2 development
- Maintain API compatibility during the transition

## Rationale

### Repository Migration to GitHub
1. **Better Collaboration Tools**: GitHub provides superior tools for team collaboration, code review, and project management
2. **Enhanced CI/CD Capabilities**: GitHub Actions offer more robust continuous integration and deployment options
3. **Improved Issue Tracking**: Better organization and tracking of development tasks, bugs, and feature requests
4. **Industry Standard**: GitHub is the de facto standard for open-source development, making it easier for contributors to participate

### FastMCP Architecture Transition
1. **Performance Optimization**: FastMCP is specifically designed for high-performance MCP operations
2. **Decoupled Architecture**: Separation of business logic from transport layers improves maintainability
3. **Standard Compliance**: Better adherence to MCP specification standards
4. **Scalability**: Improved handling of concurrent connections and requests
5. **Future-Proofing**: Aligns with the evolving MCP ecosystem and best practices

## Implementation Plan

### Phase 1: Repository Migration (Immediate)
1. Update documentation to reflect GitHub as the primary development repository
2. Configure GitHub repository with proper branching strategy and protection rules
3. Set up CI/CD pipelines for automated testing
4. Migrate existing issues and project boards to GitHub

### Phase 2: FastMCP Transition (During Phase 2 Development)
1. Create a new FastMCP-based server implementation
2. Maintain backward compatibility with existing Gradio-based API
3. Gradually migrate tools and functionality to the new architecture
4. Update documentation and examples for the new implementation
5. Perform performance benchmarking and optimization

## Consequences

### Positive
- Improved development workflow and collaboration
- Better performance and scalability for MCP operations
- Enhanced maintainability through architectural decoupling
- Alignment with industry standards and best practices
- Preparation for future enhancements and scaling

### Negative
- Initial overhead in setting up new repository and CI/CD pipelines
- Learning curve for team members unfamiliar with GitHub workflows
- Potential temporary duplication of effort during architecture transition
- Need to maintain two implementations during transition period

### Neutral
- Hugging Face Space will continue to operate for demo purposes
- No breaking changes to existing API contracts
- Existing functionality remains available during transition

## Related ADRs
- [ADR 001: Enhance OpenAlex MCP Implementation](001-enhance-openalex-mcp-implementation.md)
- [ADR 002: MCP Server Architecture](002-mcp-server-architecture.md)
- [ADR 003: Retriever Module Implementation](003-retriever-module-implementation.md)
- [ADR 004: Phase 1 Implementation](004-phase-1-implementation.md)

## Tags
`#repository` `#github` `#fastmcp` `#architecture` `#migration`