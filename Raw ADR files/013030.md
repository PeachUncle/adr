# 2. MCP Server Architecture Approach

Date: 2025-10-15

## Status

Accepted

## Context

The OpenAlex Explorer project currently implements MCP functionality using Gradio's built-in MCP server capabilities with Server-Sent Events (SSE) transport. This approach provides a quick implementation but may have limitations in terms of performance, scalability, and maintainability as the system grows more complex with additional tools and entities.

Key considerations:
- Current implementation uses Gradio's integrated MCP server in both [app.py](file:///Users/max/Documents/code/openalex-mcp-tool/app.py) and [mcp_server.py](file:///Users/max/Documents/code/openalex-mcp-tool/mcp_server.py)
- Future enhancements will significantly increase the number of MCP tools from 4 to 12
- More complex tools may require better performance characteristics
- Maintainability becomes more important as the codebase grows

## Decision

We will maintain the current Gradio-based MCP server architecture for the immediate term while implementing the planned enhancements, but we acknowledge that a transition to a more specialized MCP framework may be beneficial in the future.

### Current Approach (Accepted for now)
- Continue using Gradio's built-in MCP server with SSE transport
- Maintain dual implementation in [app.py](file:///Users/max/Documents/code/openalex-mcp-tool/app.py) and [mcp_server.py](file:///Users/max/Documents/code/openalex-mcp-tool/mcp_server.py)
- Leverage existing infrastructure and familiarity

### Future Consideration
- Evaluate specialized MCP frameworks like FastMCP for potential transition
- Consider decoupling business logic from transport layers
- Assess performance requirements as tool count increases

## Consequences

### Positive
- Leverages existing investment in Gradio-based implementation
- Maintains consistency with current codebase
- Reduces immediate development complexity
- Allows focus on feature implementation rather than architectural changes

### Negative
- May face scalability challenges with 12+ MCP tools
- Gradio's MCP implementation may have performance limitations
- Tight coupling between business logic and transport layer
- Potential maintenance challenges as system complexity grows

### Neutral
- Provides time to evaluate performance with enhanced toolset
- Allows for iterative improvement rather than big-bang rewrite
- Keeps options open for future architectural evolution

## Alternatives Considered

1. **Immediate transition to FastMCP or similar framework**
   - Pro: Better performance, scalability, and maintainability from the start
   - Con: Significant upfront development effort, risk of delays in feature delivery

2. **Complete decoupling of business logic from transport layer**
   - Pro: Maximum flexibility for future changes
   - Con: Over-engineering for current needs, increased complexity

3. **Microservices architecture with separate MCP service**
   - Pro: Best scalability and independent deployment
   - Con: Excessive complexity for current project scope

## Related ADRs

- [1. Enhance OpenAlex MCP Implementation](file:///Users/max/Documents/code/openalex-mcp-tool/docs/adr/001-enhance-openalex-mcp-implementation.md)

## Notes

This decision acknowledges the lesson learned from historical tasks about transitioning from integrated frameworks to specialized solutions, but prioritizes delivering enhanced functionality to users over architectural perfection. The decision can be revisited after implementing Phase 1 enhancements when we have better data on performance requirements.