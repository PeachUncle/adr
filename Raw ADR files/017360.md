# ADR-012: PostgreSQL with Supabase

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-004 (Repository Pattern)](./ADR-004-repository-pattern.md), [ADR-013 (Redis)](./ADR-013-redis-caching.md)

## Context

We needed a database solution for Sovren with:
- ACID compliance for payment transactions
- Real-time subscriptions for live updates
- Strong consistency for financial data
- Scalability to millions of users
- Developer-friendly tooling
- Authentication integration

## Decision

We will use **PostgreSQL** as our primary database, hosted on **Supabase**.

**Key Features**:
- **PostgreSQL 15**: Industry-leading relational database
- **Supabase**: Managed PostgreSQL with additional features
  - Real-time subscriptions via websockets
  - Built-in authentication
  - RESTful API auto-generated from schema
  - Row-level security (RLS)
  - Database backups and point-in-time recovery

**Schema Example**:
```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  public_key TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payments table (ACID compliance critical)
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  amount_sats INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'paid', 'expired')),
  payment_hash TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  paid_at TIMESTAMPTZ
);

-- Indexes for performance
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_payment_hash ON payments(payment_hash);
```

## Consequences

### Positive

1. **ACID Compliance**: Critical for payment transactions
   - Prevents double-spending
   - Ensures data consistency
   - Supports complex transactions

2. **Real-time Updates**: Supabase real-time subscriptions
   - Live payment status updates
   - Collaborative features
   - WebSocket-based, efficient

3. **Mature Ecosystem**: PostgreSQL has 30+ years of development
   - Battle-tested reliability
   - Extensive documentation
   - Large community

4. **Advanced Features**:
   - JSON/JSONB support for flexible schemas
   - Full-text search
   - Geospatial queries (PostGIS)
   - Custom functions and triggers

5. **Developer Experience**: Supabase provides excellent DX
   - Database UI for administration
   - Automatic API generation
   - Built-in auth integration
   - Generous free tier

### Negative

1. **Vendor Lock-in**: Some Supabase features proprietary
   - Mitigation: Use standard PostgreSQL features where possible
   - Can migrate to self-hosted PostgreSQL if needed

2. **Cost at Scale**: Supabase pricing increases with usage
   - Free tier: 500MB database, 2GB bandwidth
   - Pro: $25/mo for 8GB database
   - Mitigation: Monitor usage, optimize queries

3. **Complexity**: Relational databases require schema design
   - Need to plan schema carefully
   - Migrations can be complex
   - Mitigation: Use migration tools, careful planning

## Alternatives Considered

### 1. MongoDB (NoSQL)
**Pros**:
- Flexible schema
- Easy to get started
- Good for rapid prototyping

**Cons**:
- No ACID transactions (until v4)
- Eventual consistency risky for payments
- Less suitable for relational data
- Harder to query complex relationships

**Why Rejected**: Payment data requires ACID compliance. User/content relationships naturally relational.

### 2. MySQL
**Pros**:
- Popular and well-known
- Good performance
- Mature ecosystem

**Cons**:
- Fewer advanced features than PostgreSQL
- No JSONB support
- Less extensible

**Why Rejected**: PostgreSQL superior for our use case (JSONB, full-text search, extensibility).

### 3. Self-Hosted PostgreSQL
**Pros**:
- Full control
- No vendor lock-in
- Potentially cheaper at scale

**Cons**:
- Operational burden (backups, scaling, security)
- No real-time subscriptions out of box
- Need to build auth separately
- DevOps expertise required

**Why Rejected**: Supabase provides managed PostgreSQL + additional features with minimal operational overhead. Can migrate later if needed.

### 4. Firebase (Firestore)
**Pros**:
- Real-time by default
- Easy to use
- Good free tier

**Cons**:
- NoSQL (eventual consistency)
- Not suitable for financial data
- Expensive at scale
- Vendor lock-in

**Why Rejected**: Not designed for transactional financial data. ACID compliance critical.

## Implementation Notes

**Connection Pooling**:
```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY,
  {
    db: {
      schema: 'public',
    },
    auth: {
      persistSession: false, // Server-side, no session storage
    },
  }
);
```

**Transactions**:
```typescript
// Use PostgreSQL transactions for payment processing
await supabase.rpc('process_payment', {
  user_id: userId,
  amount: amount,
  payment_hash: hash,
});

// SQL function with transaction
CREATE OR REPLACE FUNCTION process_payment(
  user_id UUID,
  amount INTEGER,
  payment_hash TEXT
) RETURNS VOID AS $$
BEGIN
  -- Insert payment
  INSERT INTO payments (user_id, amount_sats, payment_hash, status)
  VALUES (user_id, amount, payment_hash, 'paid');

  -- Update user balance
  UPDATE users
  SET balance = balance + amount
  WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;
```

**Real-time Subscriptions**:
```typescript
// Subscribe to payment updates
const subscription = supabase
  .channel('payment-updates')
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'payments',
      filter: `user_id=eq.${userId}`,
    },
    (payload) => {
      console.log('Payment updated:', payload.new);
    }
  )
  .subscribe();
```

## Migration Strategy

If we need to migrate from Supabase:
1. Export PostgreSQL database dump
2. Import to self-hosted PostgreSQL
3. Replace Supabase client with `pg` client
4. Implement real-time updates with Socket.io or similar
5. Migrate auth to separate service

**Estimated effort**: 2-3 weeks for full migration.

## Related Documentation

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Database Schema](/docs/architecture/database-schema.md)
- [Migration Guide](/docs/database/migrations.md)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
