# ADR-006: CMO Supervisory Agent Architecture

**Status:** Accepted
**Date:** 2025-11-03
**Decision Makers:** Architecture Team
**Related ADRs:** ADR-001 (Multi-agent Architecture)

## Context

The AI Marketing Director system currently has a 3-tier hierarchy:
- **Tier 1 (Specialists):** LinkedIn, Twitter, Bluesky managers
- **Tier 2 (Management):** Social Media Manager, Campaign Manager
- **Tier 3 (Executive):** [Missing supervisory layer]

Without an executive supervisory agent, the system lacks:
1. Strategic oversight across all marketing activities
2. Cross-campaign coordination and prioritization
3. Performance monitoring and resource allocation
4. High-level decision making and approval workflows
5. Unified interface for external systems/users

## Decision

We will implement a **Chief Marketing Officer (CMO) Agent** as the top-level executive supervisory agent that:

1. **Supervises all management-layer agents** (Campaign Manager, Social Media Manager, Content Manager, etc.)
2. **Provides strategic direction** and coordinates cross-functional marketing initiatives
3. **Monitors overall marketing performance** and makes resource allocation decisions
4. **Handles approval workflows** for high-priority or high-budget campaigns
5. **Serves as the primary interface** for external requests and reporting

### Architecture Design

```
┌─────────────────────────────────────────────────┐
│         CMO Agent (Executive Layer)             │
│  - Strategic oversight                          │
│  - Cross-campaign coordination                  │
│  - Resource allocation                          │
│  - Performance monitoring                       │
│  - Approval workflows                           │
└─────────────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│Campaign  │   │Social    │   │Content   │
│Manager   │   │Media Mgr │   │Manager   │
└──────────┘   └──────────┘   └──────────┘
```

### Supported Task Types

1. **create_marketing_strategy**: Define overall marketing objectives and strategy
2. **approve_campaign**: Review and approve/reject campaign proposals
3. **allocate_budget**: Allocate marketing budget across campaigns
4. **monitor_performance**: Get consolidated performance metrics across all channels
5. **coordinate_initiative**: Coordinate multi-campaign marketing initiatives
6. **generate_executive_report**: Generate executive-level marketing reports
7. **set_priorities**: Set priorities across campaigns and channels

### Key Characteristics

- **Registry of Management Agents:** Maintains references to all management-layer agents
- **Strategic State Management:** Tracks marketing strategies, budgets, priorities
- **Approval Workflows:** Can approve/reject campaigns based on strategic alignment
- **Performance Aggregation:** Collects and analyzes data from all management agents
- **Strategy Pattern:** Uses dictionary dispatch for task routing (zero if/elif chains)
- **Graceful Delegation:** Continues operating even if individual managers fail

## Consequences

### Positive

1. **Complete 4-tier hierarchy:** Executive → Management → Specialists → External APIs
2. **Strategic oversight:** High-level control over all marketing activities
3. **Unified interface:** Single point of entry for external requests
4. **Better coordination:** Cross-campaign and cross-channel synchronization
5. **Resource optimization:** Intelligent budget and priority allocation
6. **Compliance with standards:** Follows all coding directives (Strategy Pattern, guard clauses, full type hints, WHY/HOW documentation)

### Negative

1. **Additional complexity:** One more layer in the agent hierarchy
2. **Latency:** Requests through CMO add one delegation hop
3. **Single point of failure:** If CMO fails, entire system coordination suffers (mitigated by graceful degradation)

### Mitigation Strategies

1. **Graceful degradation:** Management agents can operate independently if CMO unavailable
2. **Caching:** Cache strategic decisions to reduce latency
3. **Health monitoring:** Monitor CMO health and auto-recovery mechanisms
4. **Direct access option:** Allow direct management agent access for urgent operations

## Implementation Notes

### Task Delegation Pattern

```python
# CMO delegates to management agents using Strategy Pattern
async def _approve_campaign(self, task: Task) -> dict[str, Any]:
    campaign_id = task.parameters["campaign_id"]

    # Get campaign details from Campaign Manager
    campaign_manager = self._managers[AgentRole.CAMPAIGN_MANAGER]
    status_task = self._create_manager_task(...)
    campaign_data = await campaign_manager.execute(status_task)

    # Evaluate against strategic criteria
    approval = self._evaluate_campaign(campaign_data)

    # Update campaign status
    if approval["approved"]:
        # Delegate launch back to Campaign Manager
        ...
```

### Graceful Degradation

- If CMO unavailable, management agents continue with pre-approved strategies
- Campaigns can be launched directly through Campaign Manager if CMO approval not required
- Performance monitoring continues at management layer even if CMO offline

### Testing Strategy

1. **Unit tests:** 10+ tests covering all task types with mocked managers
2. **Integration tests:** Full 4-tier hierarchy tests (CMO → Campaign → Social Media → Specialists)
3. **Failure scenarios:** Test graceful degradation when managers fail
4. **Performance tests:** Ensure delegation latency acceptable

## Alternatives Considered

### Alternative 1: Peer Management Agents
Have management agents coordinate as peers without executive oversight.

**Rejected because:**
- No strategic oversight or unified decision making
- Difficult to implement cross-campaign coordination
- No clear authority for resource allocation

### Alternative 2: External Orchestration Layer
Implement orchestration logic outside the agent system.

**Rejected because:**
- Breaks the multi-agent architecture pattern
- Loses benefits of agent-based reasoning and decision making
- Creates architectural inconsistency

### Alternative 3: VP Marketing as Intermediate Layer
Add VP Marketing between CMO and managers.

**Deferred because:**
- Can be added later if needed for larger organizations
- CMO can delegate to VP Marketing agents in future
- Current system doesn't require this complexity yet

## References

- ADR-001: Multi-agent Department Architecture
- ADR-002: TDD Methodology
- ADR-005: Exception Wrapping Standard
- MULTIAGENT_ARCHITECTURE.md: System architecture document
- DEVELOPMENT_STANDARDS.md: Coding standards

## Notes

This ADR establishes the CMO as the primary supervisory agent. Future ADRs may introduce additional executive agents (VP Marketing, Director of Communications) as the system scales.
