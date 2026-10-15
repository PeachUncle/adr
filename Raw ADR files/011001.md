# ADR-007: Content Manager Agent Architecture

**Status:** Accepted
**Date:** 2025-11-03
**Decision Makers:** Architecture Team
**Related ADRs:** ADR-001 (Multi-agent Architecture), ADR-006 (CMO Supervisory Agent)

## Context

The AI Marketing Director system currently has:
- **Executive Layer:** CMO Agent (strategic oversight)
- **Management Layer:** Campaign Manager, Social Media Manager
- **Specialist Layer:** LinkedIn, Twitter, Bluesky managers

The management layer lacks a **Content Manager** to coordinate content creation, manage the editorial calendar, ensure quality, and coordinate with specialists (Copywriter, SEO Specialist, Designer).

Without a Content Manager:
1. No central content strategy or editorial calendar
2. No coordination between content creation specialists
3. No quality control or brand consistency enforcement
4. No unified content performance tracking
5. Disconnected content efforts across campaigns

## Decision

We will implement a **Content Manager Agent** as a management-layer agent that:

1. **Manages content strategy and editorial calendar**
2. **Coordinates content creation specialists** (Copywriter, SEO Specialist, Designer)
3. **Ensures content quality and brand consistency**
4. **Tracks content performance** across all channels
5. **Integrates with Campaign Manager and Social Media Manager**

### Architecture Design

```
┌─────────────────────────────────────────────────┐
│         Content Manager (Management Layer)      │
│  - Content strategy & editorial calendar        │
│  - Content creation coordination                │
│  - Quality assurance                            │
│  - Performance tracking                         │
└─────────────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│Copywriter│   │   SEO    │   │ Designer │
│          │   │Specialist│   │          │
└──────────┘   └──────────┘   └──────────┘
```

### Supported Task Types

1. **create_content**: Create content with coordination of specialists
2. **review_content**: Review and approve/reject content for quality
3. **schedule_content**: Add content to editorial calendar
4. **generate_content_ideas**: Generate content ideas aligned with strategy
5. **optimize_content**: Optimize existing content for SEO/engagement
6. **get_content_performance**: Track content metrics and ROI
7. **manage_content_calendar**: Manage editorial calendar and deadlines
8. **brief_specialists**: Create content briefs for specialist agents

### Key Characteristics

- **Registry of Specialist Agents:** Maintains references to Copywriter, SEO, Designer
- **Editorial Calendar State:** Tracks scheduled content, deadlines, status
- **Content Library:** Manages created, published, and archived content
- **Quality Standards:** Enforces brand voice, tone, and quality criteria
- **Strategy Pattern:** Uses dictionary dispatch for task routing (zero if/elif chains)
- **Graceful Delegation:** Continues operating even if specialists fail

## Consequences

### Positive

1. **Centralized content strategy:** Unified editorial direction and planning
2. **Quality consistency:** All content reviewed against brand standards
3. **Efficient coordination:** Specialists work together on content projects
4. **Performance tracking:** Unified view of content effectiveness
5. **Campaign integration:** Seamlessly integrates with Campaign and Social Media Managers
6. **Standards compliance:** Follows all coding directives (Strategy Pattern, guard clauses, full type hints, WHY/HOW documentation)

### Negative

1. **Content bottleneck risk:** All content flows through Content Manager
2. **Specialist dependency:** Requires Copywriter, SEO, Designer to be available
3. **Approval delays:** Review process adds latency to content publishing

### Mitigation Strategies

1. **Parallel content creation:** Multiple specialists can work simultaneously
2. **Graceful degradation:** Content Manager continues if some specialists unavailable
3. **Expedited approval:** Priority flag for time-sensitive content
4. **Direct specialist access:** Campaign Manager can directly request content for urgent needs

## Implementation Notes

### Task Delegation Pattern

```python
# Content Manager delegates to specialist agents using Strategy Pattern
async def _create_content(self, task: Task) -> dict[str, Any]:
    content_type = task.parameters["content_type"]
    topic = task.parameters["topic"]

    # Delegate to Copywriter for draft
    copywriter = self._specialists[AgentRole.COPYWRITER]
    draft_task = self._create_specialist_task(...)
    draft = await copywriter.execute(draft_task)

    # Delegate to SEO Specialist for optimization
    seo = self._specialists[AgentRole.SEO_SPECIALIST]
    seo_task = self._create_specialist_task(...)
    optimized = await seo.execute(seo_task)

    # Delegate to Designer for visuals (if needed)
    if content_type in ["blog_post", "social_media"]:
        designer = self._specialists[AgentRole.DESIGNER]
        design_task = self._create_specialist_task(...)
        visuals = await designer.execute(design_task)

    return {"content_id": ..., "status": "ready_for_review"}
```

### Content Workflow States

```python
# Content lifecycle managed by Content Manager
CONTENT_STATES = {
    "draft": "Initial draft created",
    "review": "Under review by Content Manager",
    "revision": "Needs revision by specialists",
    "approved": "Approved for publishing",
    "scheduled": "Scheduled for publication",
    "published": "Published to channels",
    "archived": "Archived content"
}
```

### Integration with Other Managers

```python
# Content Manager works with other management agents
# 1. Campaign Manager requests campaign content
campaign_manager -> content_manager.create_content(campaign_id="campaign_001")

# 2. Content Manager delivers to Social Media Manager
content_manager -> social_media_manager.schedule_post(content_id="content_001")

# 3. CMO reviews content strategy
cmo -> content_manager.get_content_performance(period="Q1")
```

### Graceful Degradation

- If Copywriter unavailable, use templates or previous content
- If SEO Specialist unavailable, publish without optimization
- If Designer unavailable, use text-only content
- Partial failures logged but don't block content pipeline

### Testing Strategy

1. **Unit tests:** 12+ tests covering all task types with mocked specialists
2. **Integration tests:** Full coordination tests with real specialist agents
3. **Content workflow tests:** Test complete lifecycle from draft to published
4. **Failure scenarios:** Test graceful degradation when specialists fail
5. **Calendar tests:** Test scheduling, conflicts, deadline management

## Alternatives Considered

### Alternative 1: Specialists Work Directly with Campaign Manager
Campaign Manager directly coordinates Copywriter, SEO, Designer.

**Rejected because:**
- No unified content strategy or editorial calendar
- Duplicated coordination logic across campaigns
- No central quality control
- Difficult to track content performance holistically

### Alternative 2: Content Manager as Specialist (Not Management)
Make Content Manager a specialist agent alongside others.

**Rejected because:**
- Content coordination is a management function, not specialist execution
- Violates 3-tier hierarchy (Executive → Management → Specialist)
- Would require Campaign Manager to coordinate both content and specialists

### Alternative 3: Split into Content Strategy + Content Production
Separate strategic planning from production coordination.

**Deferred because:**
- Added complexity without clear benefit at current scale
- Can be split later if content volume increases significantly
- Current design supports both functions effectively

## References

- ADR-001: Multi-agent Department Architecture
- ADR-002: TDD Methodology
- ADR-005: Exception Wrapping Standard
- ADR-006: CMO Supervisory Agent
- MULTIAGENT_ARCHITECTURE.md: System architecture document
- DEVELOPMENT_STANDARDS.md: Coding standards

## Notes

This ADR establishes Content Manager as a key management-layer agent. Future enhancements may include:
- AI-powered content idea generation
- Automated A/B testing for content variations
- Content personalization for different audience segments
- Integration with content management systems (CMS)
