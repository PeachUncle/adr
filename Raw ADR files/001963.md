# ADR-000: LangGraph StateGraph for Pipeline Orchestration

## Status

Accepted

## Context

The Gematria system requires a robust workflow orchestration system to manage the complex ETL pipeline of Hebrew noun extraction, validation, enrichment, and database integration. The system needs:

- Conditional branching based on validation results
- Error handling and retry logic
- State persistence for resumability
- Observability and monitoring
- Scalability for batch processing

## Decision

Use LangGraph's StateGraph for workflow orchestration instead of a custom queue-based system.

## Rationale

LangGraph StateGraph provides:

1. **Better Error Handling**: Built-in error states and recovery mechanisms
2. **Conditional Logic**: Native support for branching based on state conditions
3. **State Persistence**: Postgres checkpointer for resumable workflows
4. **Observability**: Built-in monitoring and debugging capabilities
5. **Maintainability**: Declarative workflow definition vs imperative queue management

## Alternatives Considered

### Custom Queue System

- **Pros**: Full control, no external dependencies
- **Cons**: Complex error handling, manual state management, harder to debug
- **Rejected**: Would require reinventing LangGraph's features poorly

### Apache Airflow

- **Pros**: Mature, feature-rich, great for complex workflows
- **Cons**: Heavyweight, overkill for single-machine deployment, complex setup
- **Rejected**: Too much infrastructure for a research/analysis tool

### Prefect

- **Pros**: Modern, Python-native, good for data pipelines
- **Cons**: Additional complexity, learning curve
- **Not Chosen**: LangGraph better fits the AI/agent workflow model

## Consequences

### Positive

- Cleaner, more maintainable code
- Better error handling and debugging
- Built-in resumability
- Future-proof for adding new nodes/edges

### Negative

- Learning curve for LangGraph
- Additional dependency
- Slightly more complex than simple queues

## Implementation Notes

- Use Postgres checkpointer for production resumability
- Implement proper error states in the graph
- Add monitoring/logging for each node transition
- Keep graph definition declarative and well-documented

## Related ADRs

- ADR-001: Database architecture impacts state persistence
- ADR-003: Error handling strategy (future)
