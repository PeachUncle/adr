---
status: accepted
date: 2025-09-09
decision-makers: [product owner, development team]
consulted: []
informed: []
---

# Use Context-Triggered Standards Review for LLM Development

## Context and Problem Statement

Standards maintenance and evolution in LLM-assisted development requires a different approach than traditional team-based periodic reviews. The original decision management system included periodic reviews and proactive alternative proposals that are impractical for single developers working with LLMs. A more contextual, event-driven approach is needed that integrates naturally into the development workflow.

## Decision Drivers

- LLM development often involves individual developers rather than teams
- Periodic scheduled reviews are difficult to maintain in solo development contexts
- Context-triggered reviews integrate naturally into development workflow
- Standards should evolve based on actual usage and exemption patterns
- Review processes should be automated and practical for AI-assisted development

## Considered Options

- Keep periodic review cycles (status quo)
- Use context-triggered reviews based on development events
- Eliminate reviews entirely and rely only on exemption tracking
- Hybrid approach combining periodic and context-triggered reviews

## Decision Outcome

Chosen option: "Use context-triggered reviews based on development events", because it integrates naturally into LLM-assisted development workflows, provides automatic review triggers based on actual usage, and eliminates the coordination overhead of scheduled reviews.

### Consequences

- Good, because reviews happen when they're most relevant (during related work)
- Good, because LLMs can automatically identify review triggers during development
- Good, because standards evolution is driven by actual usage patterns
- Good, because reduces coordination overhead for solo developers
- Bad, because might miss some standards that need review but aren't actively encountered
- Neutral, because requires developers to understand and act on review triggers

### Confirmation

Standards review triggers will be implemented in the decision management process and LLM instructions. Compliance can be verified by checking that standards with multiple exemptions are flagged for review and that dependency updates trigger relevant standards reviews.

## Pros and Cons of the Options

### Keep Periodic Review Cycles

Traditional scheduled review approach from team-based development.

- Good, because ensures all standards get regular attention
- Good, because provides predictable review schedule
- Bad, because requires coordination and scheduling overhead
- Bad, because reviews may happen when standards aren't actively relevant
- Bad, because impractical for solo LLM-assisted development

### Use Context-Triggered Reviews

Event-driven reviews based on development activities.

- Good, because integrates naturally into development workflow
- Good, because reviews happen when standards are most relevant
- Good, because LLMs can automatically identify review opportunities
- Good, because eliminates scheduling coordination overhead
- Bad, because some standards might not get reviewed if not actively used
- Neutral, because requires clear triggers and developer awareness

### Eliminate Reviews Entirely

Rely only on exemption tracking without formal reviews.

- Good, because simplest approach with minimal overhead
- Bad, because standards might become outdated without active review
- Bad, because no mechanism to promote successful proposed standards
- Bad, because might accumulate technical debt from outdated standards

### Hybrid Approach

Combination of periodic and context-triggered reviews.

- Good, because captures benefits of both approaches
- Bad, because adds complexity and coordination overhead
- Bad, because still requires periodic review scheduling
- Neutral, because provides comprehensive coverage but at higher cost

## More Information

This decision supersedes the periodic review requirements in the original decision management specification. The new approach focuses on three main review triggers:

1. **Contextual Reviews**: When creating related decisions, updating dependencies, or encountering conflicts
2. **Usage Assessment**: Promoting standards with positive production usage and flagging unused ones
3. **Exemption-Driven Reviews**: Automatic review when exemption count exceeds threshold (3+)

This approach is specifically designed for LLM-assisted development where individual developers work with AI assistants that can automatically identify and suggest review opportunities during normal development activities.
