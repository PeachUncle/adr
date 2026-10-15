# ADR-006: AI Analysis of Encrypted Entries

## Status
Proposed

## Context
With our end-to-end encryption system, users' journal entries are completely private - even we cannot read them. However, this prevents AI-powered features like mood analysis, pattern detection, and personalized insights. We need a way to enable AI analysis while maintaining user privacy and control.

## Decision
We will implement a selective sharing mechanism that allows users to temporarily share specific encrypted entries with an AI analysis service. The AI service will operate as a special "trusted entity" in our encryption system, with its own keypair and strict security controls.

### Key Design Decisions:
1. **Explicit User Control**: Users must explicitly select which entries to analyze
2. **Time-Limited Access**: Shares expire after analysis or a user-defined period
3. **Secure Processing**: AI service runs in a secure enclave with no persistent storage
4. **Insights Only**: Only derived insights are stored, never raw content
5. **Audit Trail**: Every analysis is logged for transparency

## Consequences

### Positive
- Enables powerful AI features while maintaining encryption
- Users retain complete control over their data
- Creates premium monetization opportunity
- Maintains zero-knowledge architecture
- Builds trust through transparency

### Negative
- Adds complexity to the encryption system
- Requires secure enclave infrastructure
- Users must trust the AI service implementation
- Additional user education needed

### Neutral
- Requires careful UI/UX design for consent
- Need robust audit and monitoring systems
- Performance impact needs optimization

## Alternatives Considered

### 1. Client-Side Analysis
Run AI models directly in the browser.
- ✅ Perfect privacy
- ❌ Limited model capabilities
- ❌ High client resource usage
- ❌ Difficult to update models

### 2. Homomorphic Encryption
Process encrypted data without decrypting.
- ✅ Theoretically perfect privacy
- ❌ Extremely slow (1000x+)
- ❌ Limited operations possible
- ❌ Not practical for NLP tasks

### 3. No AI on Encrypted Content
Simply don't offer AI features for encrypted entries.
- ✅ Simplest approach
- ❌ Limits product value
- ❌ Forces privacy vs features choice
- ❌ Competitive disadvantage

### 4. Separate Unencrypted Analysis Copy
Let users maintain an unencrypted copy for analysis.
- ✅ Simple implementation
- ❌ Defeats purpose of encryption
- ❌ Confusing UX
- ❌ Security risk

## Implementation Plan

1. **Week 1-2**: Build secure AI service infrastructure
2. **Week 3**: Implement sharing mechanism
3. **Week 4**: Create analysis engine integration
4. **Week 5**: Design and build UI components
5. **Week 6**: Security audit and testing

## Security Measures

1. **Secure Enclave**: Use hardware-backed secure execution
2. **Attestation**: Verify AI service integrity
3. **Rate Limiting**: Prevent abuse
4. **Audit Logging**: Complete transparency
5. **Memory Wiping**: Secure deletion after processing

## Success Criteria

- 30% of encrypted entry users try AI analysis
- <5s analysis latency
- Zero security incidents
- 4.5+ user satisfaction rating
- 20% premium conversion uplift

## References
- [Client-Side Encryption Specification](../encryption/client-side-encryption.md)
- [AI Analysis Technical Specification](../ai-analysis/technical-specification.md)
- [Goal System Design](../core/goal-system-design-v2.md)

## Decision Date
2025-01-07

## Participants
- Product Manager Agent
- Security Architecture Review
- AI/ML Team Consultation