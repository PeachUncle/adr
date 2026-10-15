# ADR-000: Orchestration via LangGraph (StateGraph)

## Status

Accepted

## Context

The project requires a robust pipeline orchestration system that supports resumable batch processing, state management, and error recovery. Initial implementation used simple sequential execution, but this lacked the ability to resume interrupted workflows or manage complex state transitions.

## Decision

Use LangGraph (StateGraph) for pipeline orchestration with the following implementation:

1. **Node-based Architecture**: Each pipeline step becomes a LangGraph node
2. **State Management**: Centralized state dictionary passed between nodes
3. **Checkpointer Support**: Built-in checkpointing for resumable execution
4. **Error Handling**: Structured error recovery and retry mechanisms

## Rationale

LangGraph provides:
- **Resumability**: Workflows can be interrupted and resumed from checkpoints
- **State Consistency**: Centralized state management prevents data loss
- **Observability**: Built-in logging and monitoring capabilities
- **Extensibility**: Easy addition of new nodes and workflow modifications

## Alternatives Considered

1. **Custom Orchestrator**: Building a custom workflow engine
   - Pros: Full control, tailored to our needs
   - Cons: High development cost, maintenance burden, potential bugs

2. **Airflow/Celery**: Existing workflow tools
   - Pros: Proven solutions, rich ecosystems
   - Cons: Heavy dependencies, overkill for our use case, complex setup

3. **Sequential Processing**: Continue with simple linear execution
   - Pros: Simplicity, low overhead
   - Cons: No resumability, poor error recovery, limited scalability

## Consequences

### Implementation Requirements
- Add LangGraph dependency
- Implement Postgres checkpointer (ADR-004)
- Create node functions for each pipeline step
- Add state validation and error handling
- Update monitoring and logging systems

### Positive Outcomes
- Resumable batch processing
- Improved error recovery
- Better observability and debugging
- Scalable architecture for future growth

### Risks
- Learning curve for LangGraph
- Additional complexity in state management
- Potential performance overhead

## Notes

Phase 0 uses minimal Hello runner; checkpointer infrastructure implemented (Postgres placeholder + Memory fallback via CHECKPOINTER env var).

## Status Update (PR-004)

- Implemented full LangGraph-compatible Postgres checkpointer with BaseCheckpointSaver interface.
- JSONB storage for checkpoint data and metadata with checkpoint versioning.
- Transactional upsert semantics with ON CONFLICT handling.
- CHECKPOINTER=postgres now fully functional when GEMATRIA_DSN is set; memory remains default for CI/dev.
