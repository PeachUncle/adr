# 1. ADRs implementation

## Status

Accepted

Date: 2025-06-17

## Context

As our project grows in complexity, we need a systematic way to document and track important architectural decisions.
Without documenting these decisions, including their context, future decisions will be harder to take and the risk 
of errors in our decisions increases.

## Decision

We will implement Architecture Decision Records (ADRs) using the following approach:

- Use a standardized template for all ADRs
- Store ADRs in version control alongside the code
- Organize ADRs in directories based on their domain/context
- Use adr-tools for managing ADRs
- Review and approve ADRs through pull requests

### What is considered an Architectural Decision?

An architectural decision is a decision that:

- Has significant impact on the system's structure, behavior, or qualities
- Affects multiple components or stakeholders
- Is difficult or costly to change once implemented
- Influences future technical decisions
- Requires careful consideration of tradeoffs and alternatives
- Impacts non-functional requirements (performance, scalability, security, etc.)
- Changes fundamental technical approaches or patterns
- Introduces or removes major dependencies

## Consequences

### Positive

- Clear documentation of architectural decisions and their rationale
- Better onboarding for new team members
- Historical context preservation
- Improved decision-making process through structured documentation
- Easier architectural reviews and audits

### Negative

- Additional overhead in documentation maintenance
- Time investment required for writing and reviewing ADRs
- Potential for outdated ADRs if not properly maintained

### Neutral

- Need for team training on ADR creation and maintenance
- Regular reviews required to ensure ADR relevance
- May need periodic template adjustments based on team feedback

## Implementation Notes

- Use Markdown format for all ADRs
- Follow the established template structure
- Store ADRs in domain-specific directories
- Use adr-tools for file creation and management
- Number ADRs sequentially within their domains
- Include Makefile for standardized ADR creation

## Related Documents

- [ADR template](./../templates/template.md)
- [ADR creation guide](./../README.md)
- [Makefile for ADR management](./../Makefile)

## Contributors

- Àlex Grau Roca
