# 7. Immutable Ledger as Source of Truth

**Date:** 2024-01-15

## Status

Accepted

## Context

Financial trading platforms require:
- Complete audit trail of all monetary movements
- Regulatory compliance for financial record keeping
- Reconciliation capability between services
- Protection against data tampering

Multiple services handle funds: Funds Service (wallet), Payment Service (deposits), Trade Service (settlements). Without a central authority, reconciling balances becomes error-prone.

## Decision

We implement a dedicated **Ledger Service** as the immutable source of truth for all financial transactions:

### Design Principles

1. **Append-Only**: Entries are never updated or deleted, only appended
2. **Double-Entry**: Every transaction has debit and credit legs (if applicable)
3. **Immutable**: Once written, ledger entries cannot be modified
4. **Authoritative**: The ledger balance is the "true" balance for reconciliation

### Ledger Entry Types
- `DEPOSIT` - Funds added to wallet
- `WITHDRAWAL` - Funds removed from wallet
- `TRADE_BUY` - Funds spent on stock purchase
- `TRADE_SELL` - Funds received from stock sale
- `FEE` - Transaction fees
- `ADJUSTMENT` - Corrections (with audit trail)

### Integration Pattern
1. Other services (Funds, Trade) perform operations
2. They call Ledger Service to record the entry
3. Ledger Service publishes events for consumers
4. Report Service builds projections from ledger events

### API Design
```
POST /api/ledger/entries       # Append new entry (internal)
GET  /api/ledger/user/{userId} # Get user's ledger (read-only)
GET  /api/ledger/balance/{userId} # Get computed balance
```

## Consequences

### Positive
- Complete, tamper-evident audit trail
- Single source of truth for balance reconciliation
- Regulatory compliance (cannot delete records)
- Enables event sourcing patterns for reporting
- Historical balance queries at any point in time

### Negative
- Additional service dependency for financial operations
- Storage grows indefinitely (no deletions)
- Corrections require compensating entries, not updates
- Query performance may degrade without proper indexing

### Mitigations
- Database-level indexing optimized for common queries
- Archival strategy for old entries (future consideration)
- Compensating transaction pattern for corrections
- Read replicas for report queries if needed
