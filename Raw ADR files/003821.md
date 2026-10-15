# ADR 001: LangChain Agent Orchestration Evaluation

## Status
Proposed (Phase 1L evaluation pending)

## Context
The shopping agent system requires sophisticated orchestration of multi-step workflows: search → extract → normalize → rank → checkout. Currently planned as a custom FastAPI service with tool planning and action ledger.

LangChain/LangGraph offers:
- Battle-tested agent orchestration patterns
- Built-in state management and streaming
- Human-in-the-loop capabilities
- LangSmith observability for AI-specific metrics
- Extensive tool ecosystem

## Decision
Evaluate LangChain adoption through a controlled Phase 1 proof-of-concept to compare against custom implementation.

## Evaluation Criteria (Phase 1L)

### Performance Requirements
- **Latency**: Must meet p95 Prompt→first offers ≤ 4s target
- **Resource Usage**: Memory/CPU overhead acceptable in production environment
- **Scalability**: Comparable horizontal scaling characteristics

### Functionality Assessment
- **Tool Integration**: Ability to integrate with existing discovery/normalize/offer services
- **State Management**: Action ledger replay capabilities equivalent to custom solution
- **Error Handling**: Graceful failure modes and retry logic
- **Observability**: LangSmith tracing value vs existing OTEL implementation

### Development Experience
- **Integration Complexity**: Effort required to integrate with existing microservices architecture
- **Debugging**: Improvement in agent decision path visibility and debugging
- **Maintainability**: Long-term code maintainability and team productivity

## Implementation Plan
1. **PoC Development**: Implement core search→rank workflow using LangGraph within existing agent service boundary
2. **Performance Benchmark**: Side-by-side comparison in staging environment
3. **Observability Integration**: Add LangSmith alongside existing OTEL tracing
4. **Decision Point**: Document recommendation for Phase 2 adoption based on measurable benefits

## Consequences

### If Adopted
- **Pros**: Leverage proven agent patterns, enhanced AI observability, reduced custom orchestration code
- **Cons**: Additional dependency, potential performance overhead, learning curve for team

### If Rejected
- **Pros**: Full control over orchestration logic, optimized for specific use case, no external dependency
- **Cons**: More custom code to maintain, less standardized observability for AI components

## Notes
- Evaluation scoped to agent orchestration only - not replacing broader microservices architecture
- Decision reversible after Phase 1 if performance/complexity concerns arise
- Consider hybrid approach: LangGraph for complex reasoning, custom code for performance-critical paths