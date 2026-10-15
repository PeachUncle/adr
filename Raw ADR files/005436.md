# ADR-005: Client-Side Encryption for Sensitive Content

**Status**: Proposed  
**Date**: 2025-01-07  
**Decision Makers**: Product Manager, Security Team, Development Team

## Context

Users have expressed desire to store highly sensitive content (journal entries, health data, personal goals) with guarantee that even the service provider cannot access it. This is particularly important for:

- Mental health journaling
- Medical information
- Personal struggles and secrets
- Financial goals and data
- Any content users deem ultra-private

Current state: All data is encrypted at rest and in transit, but we have the technical ability to decrypt and read user content if required (e.g., legal requests, debugging).

## Decision

Implement optional client-side end-to-end encryption where:
1. Encryption/decryption happens entirely in the user's browser
2. We never have access to encryption keys
3. Users can selectively share encrypted content with specific friends
4. Multiple recovery options balance security with usability

## Rationale

### 1. Privacy as a Differentiator
- Growing privacy consciousness among users
- Regulatory trends favor zero-knowledge architectures
- Competitive advantage in wellness/health space
- Trust building with privacy-conscious users

### 2. Selective Application
- Not all content needs E2E encryption
- Users choose per-entry (journals) or per-type (health data)
- Maintains functionality for non-encrypted content
- Allows gradual adoption

### 3. Technical Feasibility
- Modern browsers support Web Crypto API
- Proven patterns from Signal, WhatsApp
- Performance impact minimal with proper implementation
- Can be added without major architecture changes

### 4. Business Model
- Premium feature justification
- Higher value for privacy-conscious segments
- Reduced liability for sensitive data
- Compliance with strict privacy regulations

## Technical Approach

### Encryption Scheme
- **Master Key**: PBKDF2 from user password (100k iterations)
- **Personal Keys**: RSA-4096 for key exchange
- **Content Keys**: AES-256-GCM per item
- **Sharing**: Re-encrypt content key with recipient's public key

### Key Management
- Master key never leaves device
- Personal keys stored encrypted on server
- Public keys in directory for sharing
- Content keys encrypted with user's public key

### Recovery Options
1. **24-word mnemonic** (BIP39 standard)
2. **Social recovery** (M of N friends)
3. **No recovery** (maximum security option)

## Consequences

### Positive
- **True privacy**: Zero-knowledge architecture
- **User trust**: Strong privacy guarantee
- **Compliance**: GDPR, HIPAA ready
- **Premium feature**: Monetization opportunity
- **Selective sharing**: Maintains social features
- **Legal protection**: Cannot provide what we don't have

### Negative
- **Complexity**: More complex implementation
- **Support burden**: Cannot help with forgotten passwords
- **Search limitations**: No server-side search of encrypted content
- **AI limitations**: Cannot analyze encrypted content without permission
- **Performance**: Slight overhead for encryption/decryption
- **Development time**: 4-6 weeks for full implementation

### Neutral
- Changes user experience with new concepts
- Requires user education about trade-offs
- Creates two classes of content (encrypted/not)
- May limit some future features

## Implementation Phases

### Phase 1: Core Encryption (2 weeks)
- Basic encryption/decryption
- Key generation and management
- Password-based recovery

### Phase 2: Sharing System (1 week)
- Public key directory
- Secure sharing flow
- Permission management

### Phase 3: Advanced Recovery (1 week)
- Mnemonic phrase generation
- Social recovery setup
- Recovery flows

### Phase 4: UI/UX Polish (1 week)
- Encryption indicators
- Performance optimization
- User education

### Phase 5: Migration & Launch (1 week)
- Existing content encryption option
- Feature flags and rollout
- Documentation and support

## Alternatives Considered

### Option 1: Server-Side Encryption Only
- **Pros**: Simpler, we can help with recovery
- **Cons**: Not true privacy, trust required

### Option 2: Hardware Key Support
- **Pros**: Strongest security
- **Cons**: Poor UX, limited adoption

### Option 3: Proxy Re-Encryption
- **Pros**: Advanced sharing capabilities
- **Cons**: Very complex, newer technology

### Option 4: Homomorphic Encryption
- **Pros**: Allows server processing of encrypted data
- **Cons**: Not practical for our use cases yet

## Success Metrics

### Adoption
- 10% of active users enable encryption within 6 months
- 30% of journal entries encrypted by power users

### Performance
- Encryption adds <100ms to save time
- Decryption adds <50ms to load time
- No impact on unencrypted content

### Business
- 25% higher conversion to premium for encryption users
- 15% reduction in churn for encryption users
- Positive PR and security positioning

## Risks and Mitigations

### Risk: User Lock-out
- **Mitigation**: Multiple recovery options, clear warnings

### Risk: Performance Issues
- **Mitigation**: Web Workers, caching, lazy decryption

### Risk: Complexity Overwhelm
- **Mitigation**: Progressive disclosure, smart defaults

### Risk: Support Burden
- **Mitigation**: Comprehensive docs, community support

## Security Considerations

### Threat Model
- Protects against: Server compromise, legal requests, insider threats
- Does not protect against: Compromised user device, weak passwords

### Audit Requirements
- External security audit before launch
- Penetration testing of key exchange
- Cryptographic implementation review

## References
- [Signal Protocol Documentation](https://signal.org/docs/)
- [Web Crypto API Specification](https://www.w3.org/TR/WebCryptoAPI/)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- Industry Examples: ProtonMail, Standard Notes, Obsidian Sync

## Decision

We will implement client-side encryption as an optional premium feature, starting with journal entries and expanding to other sensitive content types based on user feedback.

**Approved by**: [Pending]  
**Date**: [Pending]