# 1. Enhance OpenAlex MCP Implementation with Additional Entities and Features

Date: 2025-10-15

## Status

Accepted

## Context

The current OpenAlex Explorer MCP Server implementation only exposes 4 MCP tools covering 3 of OpenAlex's 8 main entity types (Works, Authors, Concepts). Analysis of the OpenAlex API documentation revealed significant enhancement opportunities that would provide more comprehensive research capabilities to AI agents.

Key gaps identified:
- Missing 5 of 8 main entity types (Topics, Institutions, Sources, Publishers, Funders)
- Lack of advanced filtering capabilities
- No grouping/statistical analysis features
- Limited complex search functionality
- No bulk data operations

## Decision

We will enhance the OpenAlex MCP implementation through a phased approach:

### Phase 1: High-Priority Entity Implementation
Implement the most critical missing entities:
- Topics API (replacement for deprecated Concepts)
- Institutions API (universities and research organizations)
- Sources API (journals, conferences, repositories)

### Phase 2: Advanced Features
Implement analytical capabilities:
- Advanced filtering with inequality, negation, and combination operators
- Grouping and aggregation functionality for statistical analysis
- Complex search queries with boolean operators

### Phase 3: Additional Entities and Bulk Operations
Complete the implementation:
- Publishers API
- Funders API
- Bulk data operations with pagination support

## Consequences

### Positive
- Significantly expanded research capabilities for AI agents
- Comprehensive coverage of OpenAlex API entities
- Advanced analytical tools for research trend identification
- Enhanced value proposition for users
- Better alignment with OpenAlex's current feature set

### Negative
- Increased complexity of the codebase
- Additional maintenance overhead
- Potential performance considerations with more API calls
- Need for comprehensive testing of new features

### Neutral
- Backward compatibility will be maintained
- Existing tools will continue to function unchanged
- Phased implementation allows for iterative development

## Alternatives Considered

1. **Maintain current implementation**: Keep only the existing 4 tools
   - Pro: Minimal maintenance, simpler codebase
   - Con: Limited functionality, missed opportunities

2. **Implement all enhancements at once**: Full enhancement without phases
   - Pro: Complete functionality delivered simultaneously
   - Con: Higher risk, longer time to value, more complex testing

3. **Focus on only one or two enhancements**: Limited scope improvement
   - Pro: Lower risk, faster implementation
   - Con: Still leaves significant gaps in functionality

## Related ADRs

- N/A

## Notes

This decision was made after comprehensive analysis of the OpenAlex API capabilities and comparison with the current MCP implementation. The phased approach balances the need for enhanced functionality with manageable implementation complexity.