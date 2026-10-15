# ADR-006: Anti-Corruption Layer Pattern for External API Integration

## Status
Accepted

## Context
ValidaHub integrates with multiple external marketplace APIs (MELI, Amazon, etc.), each with:
- Different data formats and validation rules
- Unique error codes and response structures
- Varying rate limits and retry policies
- Frequent API changes without versioning
- Complex object structures with nested dependencies

The system needs to maintain stability while adapting to external API changes and supporting multiple marketplaces with a unified internal model.

## Decision
We will implement an Anti-Corruption Layer (ACL) pattern to isolate our domain from external marketplace APIs, building on the principles established in ADR-005 (Hexagonal Architecture).

### Architecture Components

```
┌─────────────────────────────────────────────────────────┐
│                     Domain Layer                         │
│                  (Canonical Models)                      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│              Anti-Corruption Layer (ACL)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │               Error Translators                   │   │
│  ├──────────────────────────────────────────────────┤   │
│  │                    Mappers                        │   │
│  │   MELI → Canonical    Amazon → Canonical         │   │
│  ├──────────────────────────────────────────────────┤   │
│  │                    Clients                        │   │
│  │     Retry Logic    Rate Limiting    Caching      │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                 External APIs                            │
│     MELI API        Amazon API       Others...           │
└──────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Canonical Model (CRM - Canonical Rule Model)**
   - Single source of truth for validation rules
   - Platform-agnostic representation
   - Stable internal API

2. **Bidirectional Mapping**
   - External → Canonical: Import and normalize rules
   - Canonical → External: Export for API calls (future)

3. **Error Translation**
   - Map external error codes to internal error types
   - Consistent error handling across marketplaces
   - Retryable vs non-retryable classification

4. **Resilience Patterns**
   - Circuit breaker for repeated failures
   - Exponential backoff with jitter
   - Rate limit handling with Retry-After support
   - Graceful degradation for partial failures

### Implementation Structure

```
apps/api/src/adapters/acl_meli/
├── clients/           # API client with retry logic
├── mappers/          # MELI ↔ Canonical transformation
├── models/           # MELI-specific and Canonical models
├── errors/           # Error translation
├── importers/        # Orchestration layer
└── tests/
    ├── fixtures/     # Real API response samples
    ├── test_contract_mapping.py    # Contract tests
    ├── test_resilience.py          # Failure handling
    └── test_property_based.py      # Property-based tests
```

## Consequences

### Positive
- **Isolation**: Domain logic is protected from external API changes
- **Testability**: Easy to test with mocked external responses
- **Flexibility**: Can adapt to API changes without affecting core logic
- **Consistency**: Unified error handling and retry strategies
- **Maintainability**: Clear separation of concerns
- **Resilience**: Built-in fault tolerance and graceful degradation

### Negative
- **Complexity**: Additional layer of abstraction
- **Maintenance**: Mappers need updates when APIs change
- **Performance**: Extra transformation overhead (mitigated by caching)
- **Duplication**: Some data structure duplication between models

### Mitigation Strategies

1. **Contract Tests**: Detect API changes early
   ```python
   def test_meli_to_canonical_contract():
       # Test with real API response fixtures
       assert mapped_rule.field_name == expected_field
   ```

2. **Fallback Mechanisms**: 
   ```python
   if api_version_changed:
       use_cached_rules()
       notify_admin()
   ```

3. **Monitoring**: Track mapping failures and API changes
   ```python
   @monitor_mapping_health
   def map_to_canonical(external_data):
       # Log unmapped fields for investigation
   ```

## References
- ADR-005: Hexagonal Architecture for ValidaHub
- Martin Fowler: [Anti-Corruption Layer](https://martinfowler.com/bliki/AnticorruptionLayer.html)
- Eric Evans: Domain-Driven Design (Context Mapping)
- [Building Microservices](https://www.oreilly.com/library/view/building-microservices/9781491950340/) - Chapter 4: Integration

## Notes
- Consider implementing a "learning mode" where the ACL can adapt to minor API changes
- Future enhancement: Auto-generate mappers from OpenAPI/Swagger specs when available
- Consider versioning canonical models for breaking changes