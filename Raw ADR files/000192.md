# 0006 - Repository Restructuring for Multi-Domain Support

## Status

Accepted

## Context

As the HI/AI Policies framework expanded beyond software development to include marketing, design, HR, and other business functions, the flat repository structure became unwieldy. With over 40 guardrail documents in the root directory, it became difficult for users to find relevant guidance for their specific needs.

The repository needed to be restructured to:
1. Better organize guardrails by functional domains
2. Accommodate expansion into non-technical business functions
3. Improve navigation and discoverability
4. Maintain clear separation between general framework documents and domain-specific guidance

## Decision

We have restructured the repository with the following organization:

1. **Root Directory** - Contains only general framework documents:
   - AI.md (core compliance requirements)
   - GUARDRAILS.md (general guardrails)
   - PROCESS.md (collaboration process)
   - PURPOSE.md (project purpose)
   - README.md (general information)
   - RFC2119.md (RFC 2119 reference)

2. **Domain-Specific Directories** - Each contains guardrails for a specific function:
   - `development/` - Software development guardrails (40+ documents)
   - `marketing/` - Marketing guardrails (3 documents, with more to come)
   - `design/` - Design guardrails (README only, placeholder for future)
   - `hr/` - Human resources guardrails (README only, placeholder for future)
   - `finance/` - Finance guardrails (README only, placeholder for future)

3. **Per-Domain README.md** - Each directory contains a README explaining its purpose and contents.

4. **Moved Existing Documents** - All 40+ development guardrails were moved from the root directory to the `development/` directory.

This structure allows for better organization, easier navigation, and accommodates future expansion into additional business functions.

## Consequences

### Easier
- Users can easily find guardrails relevant to their specific function
- Better organization makes the framework more approachable
- Easier to maintain and update domain-specific guardrails
- Accommodates expansion into new business functions
- Clear separation between general framework and domain-specific guidance
- Improved discoverability of related guardrails

### More Difficult
- Existing links to specific documents may need updating
- Users need to understand the new directory structure
- Slight overhead in maintaining multiple README files
- Need to update documentation references throughout the framework