# 0005 - Organizational Restructuring by Function

## Status

Accepted

## Context

As the HI/AI Policies framework expanded to cover more domains beyond software development, the flat file structure became difficult to navigate and maintain. With over 40 guardrail documents, it became challenging for users to find relevant guidance for their specific needs.

Additionally, the framework was expanding beyond software development to include marketing, design, HR, and other business functions. The existing structure didn't accommodate this expansion well.

## Decision

We have restructured the repository to organize guardrails by functional domains:

1. **Root Directory** - Contains only general framework documents:
   - AI.md (core compliance requirements)
   - GUARDRAILS.md (general guardrails)
   - PROCESS.md (collaboration process)
   - PURPOSE.md (project purpose)
   - README.md (general information)
   - RFC2119.md (RFC 2119 reference)

2. **Domain-Specific Directories** - Each contains guardrails for a specific function:
   - `development/` - Software development guardrails
   - `marketing/` - Marketing guardrails
   - `design/` - Design guardrails
   - `hr/` - Human resources guardrails
   - `finance/` - Finance guardrails

3. **Per-Domain README.md** - Each directory contains a README explaining its purpose and contents.

This structure allows for better organization, easier navigation, and accommodates future expansion into additional business functions.

## Consequences

### Easier
- Users can easily find guardrails relevant to their specific function
- Better organization makes the framework more approachable
- Easier to maintain and update domain-specific guardrails
- Accommodates expansion into new business functions
- Clear separation between general framework and domain-specific guidance

### More Difficult
- Existing links to specific documents may need updating
- Users need to understand the new directory structure
- Slight overhead in maintaining multiple README files