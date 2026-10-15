# Decision: Pivot to MVP Approach

## Date: 2025-01-27

## Status: Approved

## Context

After completing Phase 1.5 (Assignment Management), we had built 17.25 hours of solid infrastructure:
- Complete CRUD operations for clients, rubrics, sections, enrollments, and assignments
- 300 tests with 80%+ coverage
- Well-architected services with proper isolation and permissions

However, we realized we were about to build detailed session management and evaluation systems without ever validating that our core assumption works: **Can AI-powered virtual clients provide valuable practice conversations for social work students?**

Additionally, we discovered the target scale:
- 10,000-20,000 students per semester
- 10-20 conversations per student
- 30+ messages per conversation
- = 6+ million messages per semester

This scale requirement made it clear that some of our initial assumptions (like storing messages as JSON) wouldn't work.

## Decision

**Pause the traditional phased approach and pivot to a 1-week MVP sprint** to validate the core conversation experience with real users.

### Specific Changes:
1. Skip detailed Phase 1.6 (Session Management) and 1.7 (Evaluation)
2. Build minimal session tracking focused on conversations
3. Integrate Anthropic Claude immediately
4. Create Streamlit prototype for rapid testing
5. Get 5-10 teachers testing within one week
6. Gather feedback before building more infrastructure

## Consequences

### Positive:
- **Faster validation**: Real feedback in 1 week vs 6+ weeks
- **Reduced risk**: Find out if core concept works before major investment
- **Better architecture**: Design with real usage patterns in mind
- **Cost clarity**: Actual API costs vs estimates
- **User-driven**: Features based on needs, not assumptions

### Negative:
- **Some rework**: Session model will likely need updates
- **Technical debt**: MVP code won't be production quality
- **Limited features**: Teachers testing with minimal tools
- **Manual processes**: Feedback collection, monitoring, etc.

### Neutral:
- **Different skillset**: More focus on UX and rapid iteration
- **New tools**: Streamlit instead of React (temporarily)
- **Shifted timeline**: 8 weeks to production vs original 6-7

## Alternatives Considered

1. **Continue with original plan**
   - Pro: Systematic, thorough
   - Con: 6+ weeks before validation
   - Rejected: Too risky without validation

2. **Skip to full UI immediately**
   - Pro: Better user experience
   - Con: Slower to test core concept
   - Rejected: UI can wait, conversation can't

3. **Paper prototype with humans**
   - Pro: No development needed
   - Con: Doesn't validate AI quality
   - Rejected: Need to test actual AI

## Implementation Plan

### Week 1: MVP Sprint
- Day 1-2: Minimal models
- Day 3: Anthropic integration  
- Day 4-5: Streamlit prototype
- Day 6-7: Real user testing

### Week 2-3: Validated Foundation
- Build scalable architecture based on learnings
- Proper message handling for 6M+ messages
- Cost controls and monitoring

### Week 4-8: Production Build
- Complete teacher tools
- Production student interface
- Automated evaluation
- Scale testing

## Success Criteria

The pivot will be considered successful if:
1. We complete 10+ test conversations in week 1
2. API costs are under $0.01 per conversation
3. 80%+ of teachers give positive feedback
4. We have clear requirements for Phase 2
5. No fundamental blockers discovered

## References

- Original roadmap: PROJECT_ROADMAP.md (now updated)
- Scale requirements: 10-20k students × 10-20 conversations
- API pricing: Claude Sonnet at $0.03 per conversation
- Similar successful pivots: Lean Startup methodology

## Decision Makers

- Project Owner: [Name]
- Technical Lead: [Name]
- Date Decided: 2025-01-27

---

*This decision can be revisited after Week 1 based on MVP results.*