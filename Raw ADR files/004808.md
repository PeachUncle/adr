# ADR-001: No External LLM API by Default

## Status

**Accepted** (2026-01-03)

## Context

Users of Acode expect their source code to remain private by default. Many enterprise users cannot use tools that transmit code externally due to:

1. **Security Policies**: Corporate security policies prohibit sending source code to third-party services
2. **Compliance Requirements**: GDPR, SOC2, HIPAA, and other compliance frameworks restrict data transmission
3. **Intellectual Property Protection**: Source code contains trade secrets and proprietary algorithms
4. **Trust**: Users need confidence that their data stays local unless explicitly permitted
5. **Competitive Advantage**: Privacy-first approach differentiates Acode from cloud-only alternatives

The coding assistant market is dominated by cloud-first tools (GitHub Copilot, Cursor, etc.) that transmit code to external LLM APIs by default. This creates a gap for privacy-conscious users and enterprises.

## Decision

**Acode will operate in LocalOnly mode by default**, which prohibits all external LLM API calls. External LLM APIs (OpenAI, Anthropic, Google AI, etc.) are only accessible in Burst mode with explicit user consent.

### Key Principles

1. **Privacy by Default**: No data leaves the user's machine unless explicitly enabled
2. **Opt-In, Not Opt-Out**: External APIs require active user consent, not passive acceptance
3. **Local Models First**: Prioritize local model providers (Ollama, vLLM) for default workflows
4. **Transparent Operation**: Users can verify no external calls through logs and network monitoring

### Implementation

- **Hard Constraint HC-01**: No external LLM API in LocalOnly mode
- **Mode Matrix**: LocalOnly mode denies all external LLM capabilities
- **Denylist**: Comprehensive list of LLM API endpoints blocked by default
- **Default Mode**: Operating mode enum default value is LocalOnly (0)

### Operational Modes

- **LocalOnly** (default): No external LLM APIs allowed
- **Burst**: External LLM APIs allowed with per-session consent (HC-03)
- **Airgapped**: No network access whatsoever (HC-02)

## Consequences

### Positive

1. **User Trust Established**
   - Users can confidently use Acode with proprietary code
   - No surprise data transmission
   - Clear privacy guarantees

2. **Enterprise Adoption Enabled**
   - Meets corporate security requirements
   - Satisfies compliance auditors
   - Deployable in secure environments

3. **Compliance Simplified**
   - GDPR Article 32 (security measures)
   - SOC2 CC6.1 (logical access)
   - ISO 27001 A.13.1.1 (network controls)
   - NIST SP 800-53 SC-7 (boundary protection)

4. **Competitive Differentiation**
   - Unique positioning in market
   - Privacy-first value proposition
   - Alternative to cloud-dependent tools

5. **Regulatory Future-Proofing**
   - Anticipates potential AI data regulations
   - Aligned with emerging privacy standards
   - Reduces legal risk

### Negative

1. **Limited Capability by Default**
   - Local models less powerful than GPT-4, Claude Opus
   - Some tasks require larger context windows
   - May frustrate users wanting "best" AI

2. **Requires Local Infrastructure**
   - Users must install Ollama or vLLM
   - Requires GPU for acceptable performance
   - Higher barrier to entry

3. **User Confusion Possible**
   - Some users expect cloud AI by default
   - May not understand mode differences
   - Requires clear onboarding

4. **Reduced Telemetry**
   - Cannot track usage via API calls
   - Harder to measure model quality
   - Limited improvement feedback loop

5. **Maintenance Overhead**
   - Must maintain LLM API denylist
   - Must detect new LLM providers
   - Security reviews for bypass attempts

## Alternatives Considered

### 1. Cloud-First with Opt-Out

**Description**: Default to external LLM APIs with option to disable

**Rejected Because**:
- Violates privacy-first principle
- Users might not notice data transmission
- Opt-out is weaker than opt-in legally
- Breaks trust if code transmitted unexpectedly

### 2. Hybrid Default (Best Available Model)

**Description**: Use cloud API if available, fall back to local

**Rejected Because**:
- Ambiguous privacy posture
- Hard to reason about data location
- Compliance auditors would reject
- Violates principle of least surprise

### 3. Per-Action Consent

**Description**: Prompt for consent on every LLM API call

**Rejected Because**:
- Too disruptive to workflow
- User fatigue leads to blind acceptance
- Session-scoped consent (Burst mode) is sufficient
- Increases UI complexity

### 4. No Burst Mode (LocalOnly Only)

**Description**: Never allow external LLM APIs

**Rejected Because**:
- Too restrictive for users willing to share
- Eliminates legitimate use cases
- Doesn't serve users who consent
- Reduces utility unnecessarily

## Related Constraints

- **HC-01**: No external LLM API in LocalOnly mode
- **HC-03**: Consent required for Burst mode
- **HC-07**: Fail-safe to LocalOnly on error

## Related ADRs

- [ADR-002: Three Operating Modes](adr-002-three-operating-modes.md)
- [ADR-004: Burst Mode Consent](adr-004-burst-mode-consent.md)

## Implementation Notes

See:
- Task 001.a: Mode Matrix implementation
- Task 001.b: Validation rules and denylist
- CONSTRAINTS.md: HC-01 details

## Review History

- **2026-01-03**: Proposed by Architecture Team
- **2026-01-03**: Accepted by Security, Product, Engineering

## Notes

This ADR represents a foundational architectural decision that influences all subsequent design choices. Changing this decision would require a new ADR and extensive impact analysis.
