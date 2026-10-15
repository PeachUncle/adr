# ADR-058: GPT System Prompt Requirements as Operational Governance

## Status

Accepted

## Related ADRs

ADR-017 (Agent Documentation Presence), ADR-051 (Cursor Insight & Handoff)

## Related Rules

050 (OPS Contract), 051 (Cursor Insight & Handoff), 059 (Context Persistence)

## Context

The project uses GPT agents for complex development tasks, with system prompts defining operational behavior, environment initialization, and quality standards. However, these critical requirements exist only in prompts and are not documented in the SSOT governance framework (rules, agents, ADRs). This creates a gap where AI operational contracts are not versioned, reviewed, or enforced through the governance system.

## Decision

Establish GPT system prompt requirements as part of the operational governance framework, documented in ADRs and enforced through rule validation.

## Rationale

- **Operational Consistency**: Ensures all GPT agents operate with consistent, documented standards
- **Governance Coverage**: Brings AI behavior under the same scrutiny as human development processes
- **Change Tracking**: Enables proper versioning and review of AI operational requirements
- **Quality Assurance**: Allows validation that prompts match implemented capabilities
- **Knowledge Preservation**: Prevents loss of operational knowledge when prompts are updated

## Alternatives Considered

1. **Informal Documentation**: Keep requirements in prompts only
   - Pros: Flexible, easy to update
   - Cons: No governance, no version control, no review process

2. **Configuration Files**: Move requirements to YAML/JSON configs
   - Pros: Structured, versionable
   - Cons: Less expressive than natural language, harder to understand

3. **Code Comments**: Document requirements in agent code
   - Pros: Close to implementation
   - Cons: Not comprehensive, scattered across codebase

## Consequences

### Implementation Requirements
- Create ADR documenting GPT system prompt standards and requirements
- Add validation in rule guards to ensure prompt accuracy
- Include prompt updates in PR review checklists
- Establish process for prompt requirement changes

### Positive Outcomes
- Consistent AI behavior across all development sessions
- Proper governance coverage for AI-assisted development
- Versioned operational requirements with change tracking
- Clear validation that prompts match system capabilities

### Risks and Mitigations
- **Overhead**: Additional documentation requirements (mitigated by template reuse)
- **Maintenance Drift**: Prompts and docs diverge (mitigated by validation checks)
- **Complexity**: More governance for AI operations (mitigated by clear value demonstration)

## Implementation Requirements

1. **ADR Creation**: Document GPT system prompt requirements in ADR format
2. **Rule Integration**: Add prompt validation to rule guard checks
3. **PR Process**: Include prompt accuracy review in PR checklists
4. **Change Process**: Establish approval process for prompt requirement changes

## Notes

This ADR establishes the foundation for governed AI-assisted development, ensuring that GPT agents operate within the same structured framework as human developers.
