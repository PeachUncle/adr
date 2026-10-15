# ADR-013: MCP + Spatial Intelligence Integration Pattern

## ⚠️ DEPRECATION NOTICE (October 2, 2025)

**This ADR has been superseded by ADR-038 for spatial intelligence patterns.**

### Key Changes:
- ADR-038 documents THREE valid spatial patterns (not one mandatory pattern)
- Pattern choice is now domain-appropriate, not universal
- See ADR-038 for current spatial intelligence policy

### Valid Patterns per ADR-038:
1. **Granular Adapter Pattern** (e.g., Slack)
2. **Embedded Intelligence Pattern** (e.g., Notion)
3. **Delegated MCP Pattern** (e.g., Calendar)

### This ADR Remains Valid For:
- MCP protocol integration principles
- General spatial intelligence concepts
- Historical architectural decisions

### For Current Policy:
**See ADR-038: Spatial Intelligence Integration Patterns (September 30, 2025)**

---mm

**Status:** Accepted
**Date:** August 12, 2025
**Supersedes:** Direct API integration patterns
**Related:** ADR-001 (MCP Integration), ADR-008 (MCP Connection Pooling)

## Context

Archaeological investigation of GitHub integrations reveals pattern fragmentation with 3+ different implementation approaches. Current state includes:

- **Direct API Integration**: `services/integrations/github/github_agent.py` using PyGithub
- **MCP Protocol**: `services/mcp/consumer/github_adapter.py` with protocol abstraction
- **Spatial Intelligence**: `services/integrations/slack/spatial_adapter.py` as gold standard

This fragmentation creates maintenance overhead, inconsistent user experience, and prevents leveraging our 8-dimensional spatial intelligence across all external systems.

**Slack Spatial Intelligence** has proven to be our architectural signature differentiator, providing:
- 8-dimensional cognitive understanding of external system interactions
- Consistent attention management across tools
- Natural language spatial metaphors for complex integrations

## Decision

**ALL external tool integrations MUST use the unified MCP + Spatial Intelligence pattern:**

1. **MCP Protocol Layer**: Standardized communication protocol for all external systems
2. **Spatial Intelligence Layer**: 8-dimensional cognitive understanding and context mapping
3. **No Direct API Integrations**: All external system access routed through MCP+Spatial
4. **Architectural Signature**: Spatial intelligence as core competitive differentiator

## Pattern Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│  External Tool  │    │   MCP Protocol   │    │ Spatial Intelligence│
│                 │◄──►│                  │◄──►│                   │
│ • GitHub        │    │ • Connection     │    │ • 8 Dimensions    │
│ • Notion        │    │   Pooling        │    │ • Context Mapping │
│ • Linear        │    │ • Circuit        │    │ • Attention Model │
│ • Confluence    │    │   Breaker        │    │ • Emotional State │
└─────────────────┘    │ • Fallback       │    │ • Navigation      │
                       │   Strategy       │    │   Intent          │
                       └──────────────────┘    └────────────────────┘
                                │                        │
                                └──────────┬─────────────┘
                                           │
                                  ┌────────▼─────────┐
                                  │  Domain Models   │
                                  │                  │
                                  │ • Pure Business  │
                                  │   Logic          │
                                  │ • No External    │
                                  │   Dependencies   │
                                  │ • Spatial Context│
                                  └──────────────────┘
```

## Spatial Dimensions by Tool Category

### Issue Tracking Tools (GitHub, Linear, Jira)
```python
SpatialContext(
    territory_id="github",
    room_id="piper-morgan-product",           # Repository
    path_id="issues/156",                     # Issue number
    attention_level="high",                   # Priority/urgency mapping
    emotional_valence="negative",             # Bug vs feature
    navigation_intent="respond",              # Action required
    external_system="github",
    external_id="156",
    external_context={
        "assignee": "john_doe",
        "milestone": "v1.2",
        "labels": ["bug", "high-priority"]
    }
)
```

### Documentation Tools (Notion, Confluence)
```python
SpatialContext(
    territory_id="notion",
    room_id="product-requirements",           # Database/space
    path_id="pages/PM-workflow-spec",         # Page path
    attention_level="medium",                 # Review priority
    emotional_valence="neutral",              # Informational content
    navigation_intent="investigate",          # Research mode
    external_system="notion",
    external_id="page-uuid-123",
    external_context={
        "last_edited": "2025-08-12T10:00:00Z",
        "author": "pm_team",
        "tags": ["workflow", "specification"]
    }
)
```

### Communication Tools (Slack, Teams)
```python
SpatialContext(
    territory_id="slack",
    room_id="dev-team",                       # Channel
    path_id="threads/1691856123.456789",     # Thread ID
    attention_level="urgent",                 # @mention, DM, etc.
    emotional_valence="positive",             # Sentiment analysis
    navigation_intent="respond",              # Immediate action
    external_system="slack",
    external_id="1691856123.456789",
    external_context={
        "channel": "#dev-team",
        "thread": true,
        "mentions": ["@piper"]
    }
)
```

### Project Management Tools (Asana, Monday, ClickUp)
```python
SpatialContext(
    territory_id="asana",
    room_id="product-roadmap",                # Project
    path_id="tasks/1234567890",               # Task ID
    attention_level="high",                   # Due date proximity
    emotional_valence="neutral",              # Task nature
    navigation_intent="monitor",              # Status tracking
    external_system="asana",
    external_id="1234567890",
    external_context={
        "due_date": "2025-08-15",
        "assignee": "product_team",
        "progress": 0.75
    }
)
```

## Implementation Requirements

### Mandatory Components

1. **MCP Consumer Core**
   - Connection pooling and circuit breaker
   - Protocol abstraction and error handling
   - Fallback strategy implementation

2. **Spatial Adapter**
   - Inherit from `BaseSpatialAdapter`
   - Implement bidirectional ID mapping
   - Provide 8-dimensional context enrichment

3. **Integration Tests**
   - MCP protocol validation
   - Spatial mapping accuracy
   - Fallback behavior verification

### Migration Path

1. **Phase 1: Deprecation Warning** - Add warnings to direct API usage
2. **Phase 2: Dual Implementation** - Support both patterns during transition
3. **Phase 3: Migration Cutover** - Replace direct API with MCP+Spatial
4. **Phase 4: Legacy Cleanup** - Remove deprecated implementations

## Consequences

### Positive

- **Consistent User Experience**: All external tools behave predictably
- **Architectural Signature**: 8-dimensional spatial intelligence differentiator
- **Maintenance Efficiency**: Single integration pattern to maintain
- **Performance Optimization**: Connection pooling and circuit breakers universal
- **Cognitive Load Reduction**: Developers learn one pattern, apply everywhere

### Negative

- **Migration Overhead**: Existing GitHub integration requires significant refactoring
- **Complexity Introduction**: Simple API calls become multi-layer abstractions
- **Performance Impact**: Additional abstraction layers may introduce latency
- **Learning Curve**: Teams must understand spatial intelligence concepts

### Mitigation Strategies

- **Feature Flags**: Enable gradual rollout and rollback capability
- **Documentation**: Comprehensive spatial dimension guides and examples
- **Performance Monitoring**: Track latency impact and optimize bottlenecks
- **Training**: Team education on spatial intelligence benefits and usage

## Compliance

### Mandatory for New Integrations
- All new external system integrations MUST use MCP+Spatial pattern
- No exceptions for "simple" or "temporary" integrations
- Code reviews MUST verify spatial intelligence implementation

### Legacy Integration Timeline
- **90 days**: All existing direct API integrations migrated or deprecated
- **180 days**: Complete removal of direct API integration code
- **Ongoing**: Regular audits to prevent pattern drift

## Success Metrics

### Technical Metrics
- **Integration Pattern Consistency**: 100% of external integrations use MCP+Spatial
- **Performance Impact**: <50ms additional latency per integration call
- **Error Resilience**: 99.9% uptime with circuit breaker protection

### Business Metrics
- **Developer Productivity**: Reduced onboarding time for new integrations
- **User Experience**: Consistent behavior across all external tools
- **Competitive Advantage**: Spatial intelligence as unique differentiator

## References

- **Slack Spatial Implementation**: `services/integrations/slack/spatial_adapter.py`
- **MCP Consumer Core**: `services/mcp/consumer/consumer_core.py`
- **Spatial Base Classes**: `services/integrations/spatial_adapter.py`
- **GitHub Migration Plan**: `docs/development/deprecation-plan.md`

---

*This ADR establishes MCP+Spatial as the mandatory integration pattern, ensuring architectural consistency and leveraging our 8-dimensional spatial intelligence as a competitive differentiator.*
