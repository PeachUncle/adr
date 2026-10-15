# ADR-0006: Migrate from Centralized to Distributed Session Context Management

## Status
**Proposed**

## Context

The current AgenticOps Value Train™ implementation uses a centralized session context approach with a single `ACTIVE_SESSION.md` file in `/docs/session-context/`. This approach has several limitations that prevent effective Auto-Pilot operation and scalable multi-agent workflows:

### Current Challenges
- **Merge Conflicts**: Multiple agents updating the same file creates frequent conflicts
- **Concurrency Limitations**: Cannot handle multiple parallel phases or tickets
- **Cross-Branch Contamination**: Session state from one branch affects others
- **Context Pollution**: Unrelated work items share the same context space
- **Scalability Barriers**: Single file doesn't scale to multiple concurrent projects

### Auto-Pilot Requirements
The Auto-Pilot system (ADR-0002) requires isolated workspaces for each ticket to operate safely:
- Each issue needs its own branch and folder structure
- Session context must be isolated to prevent conflicts
- Multiple agents must work in parallel without interference
- Context must survive branch merges and phase transitions

## Decision

We will migrate from centralized session context management to a distributed, ticket-based approach:

### New Architecture
1. **Ticket-Based Isolation**: Each GitHub issue gets its own workspace folder
2. **Distributed Context**: Session state stored per-ticket, not globally
3. **Structured Folder Layout**: Consistent organization within each ticket workspace
4. **Context Aggregation**: Tooling to aggregate ticket contexts for global queries
5. **Migration-Safe**: Gradual transition with backward compatibility

### Folder Structure
```
tickets/
  <phase>_<issue_id>/
    ACTIVE_SESSION.md    # Ticket-specific session state
    checklist.md         # Mode checklist for this ticket  
    ticket.yml          # Metadata and relationships
    artifacts/          # Ticket-specific outputs
```

### Implementation Approach
- **Phase 1**: Extend existing scripts to support ticket contexts
- **Phase 2**: Create migration tooling in `migrate_session.py`
- **Phase 3**: Implement Auto-Pilot with ticket-based isolation
- **Phase 4**: Deprecate centralized context (maintain for compatibility)

## Consequences

### Positive
- **Conflict-Free Operation**: No shared files between concurrent tickets
- **True Parallelism**: Multiple agents can work simultaneously without interference
- **Cross-Branch Safety**: Session context isolated to specific branches
- **Scalable Architecture**: Supports unlimited concurrent tickets
- **Clean Handoffs**: Context clearly scoped to specific work items
- **Audit Trail**: Complete history of each ticket's evolution

### Negative
- **Complexity Increase**: More complex than single-file approach
- **Context Fragmentation**: Global state requires aggregation across tickets
- **Migration Effort**: Significant work to update all existing tooling
- **Storage Overhead**: More files and folders to manage
- **Learning Curve**: Team must understand new context model

### Neutral
- **Tool Dependencies**: Requires tooling for context aggregation and migration
- **Backward Compatibility**: Must maintain dual support during transition

## Rationale

Distributed session context is necessary because:

1. **Auto-Pilot Requirement**: Autonomous operation requires conflict-free workspaces
2. **Scalability**: Single file doesn't scale to multiple concurrent workflows
3. **Isolation**: Better encapsulation of work contexts prevents interference
4. **Industry Pattern**: Follows established patterns for distributed version control workflows
5. **Future-Proofing**: Enables advanced features like multi-project support

### Alternatives Considered
- **Branch-Specific Central Context**: Still has conflicts within branches
- **Database Storage**: Adds external dependencies and complexity
- **File Locking**: Reduces concurrency and creates bottlenecks
- **Timestamp-Based Merging**: Error-prone and loses context

### Migration Strategy
1. **Dual Support Period**: Support both centralized and distributed contexts
2. **Gradual Migration**: Migrate ticket-by-ticket as Auto-Pilot processes them
3. **Validation**: Extensive testing to ensure no context loss
4. **Rollback Capability**: Ability to revert if critical issues arise

## Related Decisions
- Enables ADR-0002 (Auto-Pilot) by providing required workspace isolation
- Builds on ADR-0004 (Session-Based Context) by evolving the storage model
- Supports ADR-0001 (Value Train) scalability requirements
- Integrates with ticket folder structure from Value Train specification

## References
- [Value Train Specification](../../agenticops-value-train.md) - Ticket folder structure
- [ADR-0002: Auto-Pilot Implementation](adr-0002-implement-autonomous-agent-orchestration.md)
- [ADR-0004: Session Context Management](adr-0004-adopt-session-based-context-management.md)
- [Current migrate_session.py](../../../scripts/migrate_session.py)