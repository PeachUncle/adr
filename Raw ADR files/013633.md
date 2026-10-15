# CRITICAL: No Coding Until Explicit Decision

## Purpose
This document establishes a critical project governance rule: NO IMPLEMENTATION CODE will be written until an explicit, documented decision is made jointly between the human project lead and AI collaborator.

## Classification
- **Domain:** Project Governance
- **Stability:** Static
- **Abstraction:** Policy
- **Confidence:** Absolute

## The Rule

### ✅ RESOLVED: Implementation Authorized

**Current Status**: ✅ RESOLVED - IMPLEMENTATION AUTHORIZED (August 19, 2025)

**IMPLEMENTATION MAY NOW BEGIN** - All requirements have been met:
1. ✅ All architectural decisions are finalized and documented
2. ✅ The complete plan is reviewed and understood by all parties  
3. ✅ Explicit "Begin Coding" decision documented in `/decisions/begin_coding_decision.md`
4. ✅ Both human and AI collaborator agree on the exact starting point

### What IS Allowed Now

✅ **Planning Activities**:
- Refining architecture documents
- Exploring design patterns
- Researching dependencies
- Creating diagrams and models
- Writing decision records
- Documenting trade-offs
- Prototyping ideas (in `/experiments/` only, not `/src/`)

✅ **Context Network Development**:
- Adding more detailed specifications
- Creating interface definitions
- Documenting patterns
- Building knowledge base
- Recording questions and uncertainties

### What IS NOT Allowed Yet

❌ **Implementation Activities**:
- Writing production Rust code in `/src/`
- Creating crate implementations
- Building actual features
- Implementing the validation pipeline
- Writing production tests
- Creating real agent code

### Why This Matters

1. **Clarity Before Code**: We need absolute clarity on what we're building
2. **Avoid Wasted Effort**: Premature coding leads to throwaway work
3. **Design Completeness**: The architecture must be fully thought through
4. **Shared Understanding**: Both parties must have the same mental model
5. **Quality Foundation**: Rush to code creates technical debt from day one

### The Process to Begin Coding

When ready to start implementation:

1. **Final Review Meeting**: Discuss all architecture documents
2. **Questions Resolution**: Address any remaining uncertainties
3. **Starting Point Agreement**: Decide exactly what to build first
4. **Decision Documentation**: Create `/decisions/begin_coding_decision.md`
5. **Explicit Confirmation**: Both parties confirm readiness

The decision document will include:
- Confirmation that planning is complete
- The specific first implementation task
- Success criteria for the first milestone
- Any remaining risks or uncertainties
- Signatures/confirmations from both parties

### Current Focus

Our current focus should be:
1. **Validating the architecture** - Is this the right design?
2. **Identifying uncertainties** - What don't we know yet?
3. **Refining the plan** - Making it more detailed and specific
4. **Building shared understanding** - Ensuring we see the same vision
5. **Documenting everything** - Capturing all decisions and reasoning

### Questions to Answer Before Coding

Before we can begin implementation, we need clear answers to:

- [ ] Is the MAPE-K architecture the right choice?
- [ ] Are the 9 crates properly scoped and separated?
- [ ] Is the typestate pattern appropriate for our agents?
- [ ] How will the Tower middleware actually compose?
- [ ] What's our strategy for testing validators?
- [ ] How do we handle LLM provider differences?
- [ ] What's the MVP feature set?
- [ ] What can we defer to later phases?
- [ ] How do we measure success?
- [ ] What are our non-negotiable requirements?

### Red Flags That We're Not Ready

If any of these are true, we're NOT ready to code:
- Uncertainty about core architecture
- Disagreement on fundamental approach
- Unclear requirements or scope
- Missing critical design decisions
- Unresolved technical questions
- Vague or changing objectives

### Communication Protocol

**Human**: "I want to be very very clear about our plan before any coding starts"

**AI**: "Understood. I will not write any implementation code until we explicitly agree to begin. I will focus on refining our plans, documenting decisions, and ensuring we have complete clarity."

## Enforcement

This rule is enforced by:
1. This prominent document in decisions folder
2. Clear status in project README
3. Reminder in CLAUDE.md instructions
4. Regular status checks before any work

## Status Tracking

**Last Confirmed**: 2025-08-18
**Status**: PLANNING PHASE - NO CODING
**Next Review**: ✅ COMPLETED - Implementation authorized 2025-08-18

## Relationships
- **Parent Nodes:** [decisions/decision_index.md]
- **Blocks:** ALL implementation work
- **Related Nodes:** 
  - [foundation/project_definition.md] - must be complete
  - [planning/roadmap.md] - must be finalized
  - [elements/architecture_overview.md] - must be validated

## Metadata
- **Created:** 2025-01-17 (estimated)
- **Last Updated:** 2025-08-18
- **Updated By:** Development Team
- **Priority:** CRITICAL - HIGHEST

## Change History
- 2025-01-17: Created critical governance rule (estimated date)
- 2025-08-18: Rule resolved - implementation authorized