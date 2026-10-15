# ADR 004: Transaction Description Storage# ADR 004: Transaction Description Storage



## Status## Status

AcceptedAccepted



## Date## Date

2025-11-162025-11-16



## Context## Context

Transaction descriptions exist in TransactionType table. Decide whether to duplicate in Transaction table or use joins.Transaction descriptions exist in TransactionType table. Decide whether to duplicate in Transaction table or use joins.



## Decision## Decision

Store description only in TransactionType table. Access via joins to maintain normalization.Store description only in TransactionType table. Access via joins to maintain normalization.



## Consequences## Consequences

- **Pros**: Data consistency, no duplication, single source of truth- **Pros**: Data consistency, no duplication, single source of truth

- **Cons**: Requires JOIN operations, slightly more complex queries- **Cons**: Requires JOIN operations, slightly more complex queries

- **Risks**: Performance degradation with high query volume- **Risks**: Performance degradation with high query volume



## Alternatives Considered## Alternatives Considered

- **Denormalized storage**: Faster queries but data duplication and inconsistency risks- **Denormalized storage**: Faster queries but data duplication and inconsistency risks

- **Cache layer**: Fast access but added complexity- **Cache layer**: Fast access but added complexity



## Implementation## Implementation

- Removed description field from Transaction model- Removed description field from Transaction model

- Updated API queries to include TransactionType relation- Updated API queries to include TransactionType relation

- Tests verify description access via joins- Tests verify description access via joins



## Future Considerations## Future Considerations

Monitor performance; consider denormalization if JOINs become bottleneck.Monitor performance; consider denormalization if JOINs become bottleneck.



## Related## Related

- ADR 003: Database Choice- ADR 003: Database Choice</content>
<parameter name="filePath">c:\projects\literate-sniffle\docs\adr\005-transaction-description-storage.md