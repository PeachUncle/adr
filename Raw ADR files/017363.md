# ADR-015: Idempotency Keys for Payment Operations

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-005 (Lightning Network)](./ADR-005-lightning-network-payments.md), [ADR-012 (PostgreSQL)](./ADR-012-postgresql-supabase.md)

## Context

Financial operations must be idempotent to prevent duplicate charges:

**Problem Scenarios**:
1. **Network Retry**: User's request times out, browser retries automatically
2. **Impatient User**: User clicks "Pay" button multiple times
3. **Webhook Replay**: Payment processor sends duplicate webhook
4. **Race Conditions**: Concurrent requests for same operation

**Without Idempotency**:
```typescript
// User clicks "Subscribe" twice in quick succession
POST /api/payments/subscribe { userId: '123', amount: 1000 }
POST /api/payments/subscribe { userId: '123', amount: 1000 }

// Result: User charged twice! 💸💸
```

**Impact**: Users charged multiple times, erosion of trust, refund overhead.

## Decision

We will implement **idempotency keys** for all payment and financial operations using Stripe's idempotency pattern.

**How It Works**:
1. Client generates unique idempotency key (UUID)
2. Client includes key in API request header
3. Server stores key + response for 24 hours
4. Duplicate requests with same key return cached response
5. Keys expire after 24 hours (cleanup)

**Implementation**:
```typescript
// Client-side: Generate and send idempotency key
async function createPayment(amount: number): Promise<Invoice> {
  const idempotencyKey = crypto.randomUUID();

  const response = await fetch('/api/payments/invoice', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
    },
    body: JSON.stringify({ amount }),
  });

  return response.json();
}

// Server-side: Idempotency middleware
interface IdempotencyRecord {
  key: string;
  response: any;
  statusCode: number;
  createdAt: Date;
}

class IdempotencyService {
  constructor(
    private db: Database,
    private cache: CacheService
  ) {}

  async checkIdempotency(key: string): Promise<IdempotencyRecord | null> {
    // Check cache first (fast path)
    const cached = await this.cache.get<IdempotencyRecord>(`idempotency:${key}`);
    if (cached) return cached;

    // Check database (persistent storage)
    const record = await this.db.query(
      'SELECT * FROM idempotency_keys WHERE key = $1',
      [key]
    );

    if (record) {
      // Warm cache
      await this.cache.set(`idempotency:${key}`, record, 86400); // 24 hours
      return record;
    }

    return null;
  }

  async storeIdempotency(
    key: string,
    response: any,
    statusCode: number
  ): Promise<void> {
    const record = {
      key,
      response,
      statusCode,
      createdAt: new Date(),
    };

    // Store in database (persistent)
    await this.db.query(
      `INSERT INTO idempotency_keys (key, response, status_code, created_at)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (key) DO NOTHING`,
      [key, JSON.stringify(response), statusCode, record.createdAt]
    );

    // Cache for fast access
    await this.cache.set(`idempotency:${key}`, record, 86400);
  }
}

// Middleware
function idempotencyMiddleware(req: Request, res: Response, next: NextFunction) {
  const idempotencyKey = req.headers['idempotency-key'] as string;

  // Only apply to POST/PUT/PATCH (mutating operations)
  if (!['POST', 'PUT', 'PATCH'].includes(req.method)) {
    return next();
  }

  // Require idempotency key for payment endpoints
  if (req.path.includes('/payments') && !idempotencyKey) {
    return res.status(400).json({
      error: 'Idempotency-Key header required for payment operations',
    });
  }

  if (idempotencyKey) {
    const existing = await idempotencyService.checkIdempotency(idempotencyKey);

    if (existing) {
      // Return cached response
      return res
        .status(existing.statusCode)
        .json(existing.response);
    }

    // Store original res.json to intercept response
    const originalJson = res.json.bind(res);
    res.json = (body: any) => {
      // Save response for future duplicate requests
      idempotencyService.storeIdempotency(
        idempotencyKey,
        body,
        res.statusCode
      );

      return originalJson(body);
    };
  }

  next();
}

// Apply to payment routes
app.use('/api/payments', idempotencyMiddleware);
```

**Database Schema**:
```sql
CREATE TABLE idempotency_keys (
  key TEXT PRIMARY KEY,
  response JSONB NOT NULL,
  status_code INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auto-cleanup after 24 hours
CREATE INDEX idx_idempotency_created_at ON idempotency_keys(created_at);

-- Cleanup job (run hourly)
DELETE FROM idempotency_keys
WHERE created_at < NOW() - INTERVAL '24 hours';
```

## Consequences

### Positive

1. **Prevents Duplicate Payments**: Guaranteed safety
   - User clicks "Pay" 10 times → charged once
   - Network retry → same response
   - Webhook replay → deduplicated

2. **Network Resilience**: Safe to retry failed requests
   - Client can retry on timeout without fear
   - Improves reliability
   - Better user experience

3. **Consistent Behavior**: Deterministic responses
   - Same key → same response
   - No race conditions
   - Predictable system behavior

4. **API Best Practice**: Follows Stripe/industry standard
   - Familiar pattern for developers
   - Well-documented approach
   - Easy to understand and implement

### Negative

1. **Storage Overhead**: Need to store all keys
   - Mitigation: 24-hour expiration, cleanup jobs
   - Typical: 10,000 payments/day = 10,000 keys (minimal)

2. **Complexity**: Additional logic in request flow
   - Mitigation: Middleware handles it transparently
   - Services don't need to know about it

3. **Key Management**: Clients must generate UUIDs
   - Mitigation: Standard UUID library on all platforms
   - Document in API guide

4. **Cache Invalidation**: Need to handle failures during storage
   - If storing idempotency fails, request fails
   - Mitigation: Wrap in transaction

## Alternatives Considered

### 1. Database Unique Constraints
**Pros**: Simpler, no extra table

**Cons**:
- Only prevents duplicates, doesn't return cached response
- User gets error instead of success
- Can't handle retries gracefully

**Why Rejected**: Doesn't provide retry safety, poor UX.

### 2. Request Deduplication Based on Content
**Pros**: No client-side key generation needed

**Cons**:
- Hash collisions possible
- Can't distinguish legitimate duplicate requests
- Race condition if requests arrive simultaneously

**Why Rejected**: Not safe enough for financial operations.

### 3. Distributed Lock
**Pros**: Prevents concurrent execution

**Cons**:
- Doesn't help with retries hours later
- Requires distributed lock service
- Lock timeout complexity

**Why Rejected**: Complementary but not sufficient alone.

### 4. No Idempotency (Hope for the Best)
**Pros**: Simplest

**Cons**:
- Users get charged multiple times
- Trust issues
- Support burden for refunds

**Why Rejected**: Unacceptable for financial application.

## Implementation Notes

**Idempotency Key Generation**:
```typescript
// Client-side (React)
import { v4 as uuidv4 } from 'uuid';

function useIdempotentMutation<T>(
  mutationFn: (data: any) => Promise<T>
) {
  const [idempotencyKey] = useState(() => uuidv4());

  return async (data: any) => {
    return await mutationFn({
      ...data,
      headers: {
        'Idempotency-Key': idempotencyKey,
      },
    });
  };
}

// Usage
const createPayment = useIdempotentMutation(
  (data) => api.post('/payments/invoice', data)
);
```

**Webhook Idempotency**:
```typescript
// Webhooks use their own ID as idempotency key
app.post('/webhooks/lightning', async (req, res) => {
  const webhookId = req.headers['x-webhook-id'];

  // Check if already processed
  const existing = await idempotencyService.checkIdempotency(webhookId);
  if (existing) {
    return res.status(200).json({ status: 'already_processed' });
  }

  // Process webhook
  await processPaymentWebhook(req.body);

  // Mark as processed
  await idempotencyService.storeIdempotency(webhookId, { status: 'ok' }, 200);

  res.status(200).json({ status: 'ok' });
});
```

**Testing Idempotency**:
```typescript
describe('Payment Idempotency', () => {
  it('should prevent duplicate payment processing', async () => {
    const idempotencyKey = uuidv4();

    // First request
    const response1 = await request(app)
      .post('/api/payments/invoice')
      .set('Idempotency-Key', idempotencyKey)
      .send({ amount: 1000 });

    expect(response1.status).toBe(200);
    const invoice1 = response1.body;

    // Duplicate request (same key)
    const response2 = await request(app)
      .post('/api/payments/invoice')
      .set('Idempotency-Key', idempotencyKey)
      .send({ amount: 1000 });

    expect(response2.status).toBe(200);
    const invoice2 = response2.body;

    // Should return same response
    expect(invoice2.id).toBe(invoice1.id);

    // Should NOT create second payment
    const payments = await db.query('SELECT * FROM payments');
    expect(payments.length).toBe(1);
  });
});
```

## Cleanup Strategy

```typescript
// Hourly cleanup job
cron.schedule('0 * * * *', async () => {
  const deleted = await db.query(
    `DELETE FROM idempotency_keys
     WHERE created_at < NOW() - INTERVAL '24 hours'
     RETURNING key`
  );

  logger.info(`Cleaned up ${deleted.length} expired idempotency keys`);

  // Clear from cache
  for (const record of deleted) {
    await cache.delete(`idempotency:${record.key}`);
  }
});
```

## Related Documentation

- [Stripe Idempotency Guide](https://stripe.com/docs/api/idempotent_requests)
- [Payment API Documentation](/docs/api/payments.md)
- [Financial Operations Security](/docs/security/financial-operations.md)
- [Payment Flow Diagram](/docs/architecture/diagrams/epic-005-payment-flow.mmd)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
