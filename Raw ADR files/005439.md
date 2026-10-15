# ADR-007: Core Encryption Service

## Status
Proposed

## Context

Currently, encryption is being implemented separately in different modules:
- Journal entries have their own encryption implementation
- AI analysis sharing reuses some journal encryption
- Future modules (health, finance, goals) will need encryption

This leads to:
- Code duplication across modules
- Inconsistent security practices
- Difficult maintenance and updates
- Higher risk of security vulnerabilities
- Slower feature development

## Decision

We will create a platform-level Core Encryption Service that provides uniform cryptographic operations across all AI Lifestyle App modules. This service will:

1. **Provide a single, consistent API** for all encryption needs
2. **Support multiple encryption contexts** (one per module)
3. **Enable secure sharing** between users and services
4. **Implement performance optimizations** (caching, workers, batching)
5. **Support advanced features** (searchable encryption, key rotation)

### Key Design Principles:
- **Zero-Knowledge**: Service never sees unencrypted content
- **Module Isolation**: Each module gets its own encryption context
- **Developer Friendly**: Simple API with full TypeScript support
- **Future-Proof**: Supports algorithm upgrades and new features
- **Performance First**: Async operations, caching, and batch processing

## Consequences

### Positive
- **Consistency**: All modules use the same security standards
- **Reusability**: 90% less encryption code per module
- **Maintainability**: Security updates in one place
- **Faster Development**: New features get encryption easily
- **Better Security**: Centralized security auditing
- **Advanced Features**: Enables cross-module sharing
- **Compliance**: Easier to meet HIPAA, GDPR requirements

### Negative
- **Initial Investment**: 2-3 weeks to build core service
- **Migration Effort**: Existing journal encryption needs migration
- **Complexity**: More abstraction layers
- **Testing**: Need comprehensive test suite
- **Documentation**: Requires thorough developer docs

### Neutral
- Changes module architecture patterns
- Requires team training on new API
- Affects bundle size (mitigated by code splitting)

## Alternatives Considered

### 1. Module-Specific Encryption
Each module implements its own encryption.
- ✅ Complete module independence
- ❌ Code duplication
- ❌ Inconsistent security
- ❌ Harder to maintain

### 2. Third-Party Encryption Library
Use an existing encryption framework.
- ✅ Faster initial implementation
- ❌ May not fit our specific needs
- ❌ Vendor lock-in
- ❌ Less control over features

### 3. Server-Side Encryption
Encrypt data on the backend only.
- ✅ Simpler client implementation
- ❌ Not zero-knowledge
- ❌ Server can read data
- ❌ Against our privacy principles

### 4. Hybrid Approach
Core service for new modules, keep journal as-is.
- ✅ Less migration work
- ❌ Inconsistency long-term
- ❌ Two systems to maintain
- ❌ Confusing for developers

## Implementation Plan

### Phase 1: Core Service (Weeks 1-2)
- Build encryption service interface
- Implement key management
- Create provider abstraction
- Add TypeScript definitions

### Phase 2: Migration Tools (Week 3)
- Build migration utilities
- Create compatibility layer
- Test with journal data
- Document migration process

### Phase 3: Journal Migration (Week 4)
- Migrate journal to core service
- Maintain backward compatibility
- Update AI analysis integration
- Comprehensive testing

### Phase 4: New Modules (Weeks 5-6)
- Implement health encryption
- Add financial encryption
- Create goal encryption
- Performance optimization

## Technical Details

### Service Interface
```typescript
interface IEncryptionService {
  initialize(config: ModuleConfig): Promise<void>;
  encrypt<T>(data: T, options?: EncryptOptions): Promise<EncryptedData<T>>;
  decrypt<T>(encrypted: EncryptedData<T>): Promise<T>;
  share(dataId: string, recipientId: string, permissions: SharePermissions): Promise<ShareToken>;
  revoke(shareToken: ShareToken): Promise<void>;
}
```

### Module Integration
```typescript
// Before: Module-specific encryption
class JournalEncryption {
  // 500+ lines of encryption code
}

// After: Using core service
class JournalModule {
  constructor(private encryption: IEncryptionService) {
    encryption.initialize({ moduleId: 'journal' });
  }
  
  async saveEntry(entry: JournalEntry) {
    const encrypted = await this.encryption.encrypt(entry);
    await this.storage.save(encrypted);
  }
}
```

## Success Criteria

- All modules using core service within 3 months
- 90% reduction in module-specific crypto code
- Zero security vulnerabilities in audit
- <50ms encryption overhead
- Positive developer feedback

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Migration breaks existing data | High | Compatibility layer, extensive testing |
| Performance regression | Medium | Benchmarking, optimization, caching |
| Complex API | Medium | Good docs, examples, training |
| Security vulnerability | High | Security audit, penetration testing |

## References
- [Core Encryption Service Specification](../core/encryption-service.md)
- [Client-Side Encryption Design](../encryption/client-side-encryption.md)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)

## Decision Date
2025-01-07

## Participants
- Product Manager Agent
- Backend Architecture Team
- Frontend Architecture Team
- Security Team Consultation

## Review Date
3 months after implementation (reassess based on actual usage)