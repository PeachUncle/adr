# ADR-003: Adapter Pattern for Payment Integration (Stripe)

**Status**: Accepted  
**Date**: 2025-10-30  
**Decision Makers**: Development Team  
**Technical Story**: Need to integrate payment processing while maintaining testability and flexibility

---

## Context and Problem Statement

The Talavera Subscriptions system requires payment processing for Pro plan subscriptions. The payment integration must:

- Support subscription creation and billing
- Be easily testable without real payment processing
- Allow future migration to different payment providers
- Isolate payment logic from business logic
- Enable development without API keys or external dependencies

Three integration approaches were considered:
1. **Direct Stripe SDK Integration** (tight coupling)
2. **Adapter Pattern with Mock Implementation** ✅ (chosen)
3. **Payment Microservice** (over-engineering for current scale)

---

## Decision Drivers

1. **Testability**: Run tests without external API calls
2. **Flexibility**: Easy to swap payment providers
3. **Development Experience**: Work without API keys
4. **Maintainability**: Isolate payment logic
5. **Cost**: Avoid sandbox charges during development
6. **Simplicity**: Not over-engineer for current needs
7. **BDD Compliance**: Support Cucumber integration tests

---

## Considered Options

### Option 1: Direct Stripe SDK Integration

**Direct approach**: Use Stripe SDK directly in subscription service.

```typescript
// ❌ Tightly coupled
import Stripe from 'stripe';

export async function createSubscription(userId: number, planId: number) {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  
  const paymentIntent = await stripe.paymentIntents.create({
    amount: 999,
    currency: 'usd',
  });
  
  // Business logic mixed with payment logic
  const subscription = await prisma.subscription.create({...});
  
  return subscription;
}
```

**Pros**:
- ✅ Simple initial implementation
- ✅ Direct access to Stripe features

**Cons**:
- ❌ **Tight Coupling**: Business logic depends on Stripe SDK
- ❌ **Testing Nightmare**: Requires mocking Stripe SDK or real API calls
- ❌ **Dev Keys Required**: Can't run without Stripe API keys
- ❌ **Hard to Switch**: Migrating to another provider touches business logic
- ❌ **BDD Tests Fail**: Cucumber tests fail without Stripe credentials

---

### Option 2: Adapter Pattern with Mock ✅ (Selected)

**Abstraction approach**: Define payment adapter interface, implement mock for development/testing.

```typescript
// ✅ Decoupled
export interface StripeAdapter {
  createSubscription(userId: number, planId: number): Promise<PaymentIntent>;
}

export class MockStripeAdapter implements StripeAdapter {
  async createSubscription(userId: number, planId: number): Promise<PaymentIntent> {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
      id: `pi_mock_${Date.now()}_${userId}_${planId}`,
      status: 'succeeded',
      amount: planId === 2 ? 999 : 0,
      currency: 'usd',
    };
  }
}

export const stripeAdapter: StripeAdapter = new MockStripeAdapter();
```

**Pros**:
- ✅ **Loose Coupling**: Business logic depends on interface, not implementation
- ✅ **Easy Testing**: Mock adapter works without external API
- ✅ **No Keys Required**: Develop without Stripe credentials
- ✅ **Swappable**: Can implement real Stripe, PayPal, etc.
- ✅ **BDD Compatible**: Tests run instantly
- ✅ **Clear Seam**: Payment logic isolated

**Cons**:
- ⚠️ Additional abstraction layer
- ⚠️ Need to maintain mock implementation

---

### Option 3: Payment Microservice

**Separate service approach**: Standalone payment service with its own database.

```typescript
// Over-engineered
POST https://payments-service.internal/subscriptions
{
  "userId": 1,
  "planId": 2,
  "provider": "stripe"
}
```

**Pros**:
- ✅ Complete isolation
- ✅ Independent scaling
- ✅ Polyglot (can use different language)

**Cons**:
- ❌ **Over-Engineering**: Not needed for current scale
- ❌ **Operational Complexity**: More services to deploy/monitor
- ❌ **Distributed Transactions**: Consistency challenges
- ❌ **Network Latency**: Additional HTTP calls
- ❌ **Development Overhead**: Separate repo, CI/CD, etc.

---

## Decision Outcome

**Chosen Option**: **Adapter Pattern with Mock Implementation**

### Rationale

1. **Test-Driven Development**: BDD/TDD requires tests to run without external dependencies. The adapter pattern enables:
   - Instant test execution (~1.4s for 12 BDD scenarios)
   - No Stripe sandbox costs
   - Deterministic test results

2. **Development Velocity**: Developers can work without:
   - Stripe API keys
   - Network connectivity
   - Third-party rate limits
   - Sandbox account management

3. **Future-Proof**: When ready for production:
   - Implement `RealStripeAdapter implements StripeAdapter`
   - Swap adapter in dependency injection
   - Business logic unchanged

4. **Clear Boundaries**: Payment concerns are isolated:
   - `services/subscriptionService.ts` → business logic
   - `adapters/stripe.ts` → payment integration
   - Easy to understand, test, and maintain

5. **YAGNI Principle**: Microservice is premature optimization. Adapter pattern provides flexibility without complexity.

### Implementation Design

```
┌─────────────────────────────────────┐
│   SubscriptionService               │
│   (Business Logic)                  │
│                                     │
│   - Validate user subscription      │
│   - Check plan exists               │
│   - Create subscription record      │
│   - Create invoice record           │
└──────────────┬──────────────────────┘
               │ depends on
               │
               ▼
┌─────────────────────────────────────┐
│   StripeAdapter (Interface)         │
│                                     │
│   + createSubscription()            │
│   + cancelSubscription()            │
│   + updateSubscription()            │
└──────────────┬──────────────────────┘
               │ implemented by
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌─────────────┐   ┌─────────────────┐
│ MockAdapter │   │ RealStripeAdapter│
│ (Dev/Test)  │   │ (Production)     │
└─────────────┘   └──────────────────┘
```

### Positive Consequences

- ✅ BDD tests run without external dependencies
- ✅ Fast feedback loop (tests < 2s)
- ✅ No API costs during development
- ✅ Easy onboarding (no Stripe account needed)
- ✅ Flexible for future payment providers
- ✅ Clear separation of concerns

### Negative Consequences

- ⚠️ Mock must stay in sync with real Stripe API
- ⚠️ Need integration tests with real Stripe in staging
- ⚠️ Extra file/interface to maintain

### Mitigation Strategies

1. **Mock Accuracy**:
   - Document mock behavior in code comments
   - Reference Stripe API docs in mock implementation
   - Add integration tests for staging environment

2. **Production Readiness**:
   - Create `RealStripeAdapter` when approaching launch
   - Use environment variable to toggle adapters
   - Add staging tests with Stripe sandbox

3. **Team Understanding**:
   - Document adapter pattern in ADR (this document)
   - Add comments explaining why adapter exists
   - Include in onboarding documentation

---

## Implementation Evidence

### Adapter Interface

```typescript
// backend/src/adapters/stripe.ts
export interface PaymentIntent {
  id: string;
  status: 'succeeded' | 'pending' | 'failed';
  amount: number;
  currency: string;
}

export interface StripeAdapter {
  createSubscription(userId: number, planId: number): Promise<PaymentIntent>;
}
```

### Mock Implementation

```typescript
// backend/src/adapters/stripe.ts
export class MockStripeAdapter implements StripeAdapter {
  async createSubscription(userId: number, planId: number): Promise<PaymentIntent> {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Generate fake payment intent ID (similar to Stripe format)
    const paymentIntentId = `pi_mock_${Date.now()}_${userId}_${planId}`;

    // Mock successful payment
    return {
      id: paymentIntentId,
      status: 'succeeded',
      amount: planId === 2 ? 999 : 0, // Pro plan costs $9.99, Free is $0
      currency: 'usd',
    };
  }
}

// Export singleton instance
export const stripeAdapter: StripeAdapter = new MockStripeAdapter();
```

### Usage in Service Layer

```typescript
// backend/src/services/subscriptionService.ts
import { stripeAdapter } from '../adapters/stripe';
import prisma from '../prisma/client';

export async function createSubscription(userId: number, planId: number) {
  // Business logic: validate user, check existing subscription
  const existingSubscription = await prisma.subscription.findFirst({
    where: { userId, status: 'active' },
  });
  
  if (existingSubscription) {
    throw new SubscriptionAlreadyActiveError('User already has an active subscription');
  }

  // Business logic: validate plan
  const plan = await prisma.plan.findUnique({ where: { id: planId } });
  if (!plan) {
    throw new InvalidPlanError('Invalid plan selected');
  }

  // Payment integration: delegate to adapter
  const paymentIntent = await stripeAdapter.createSubscription(userId, planId);

  // Business logic: create records in transaction
  const result = await prisma.$transaction(async (tx) => {
    const subscription = await tx.subscription.create({
      data: { userId, planId, status: 'active' },
      include: { plan: true },
    });

    await tx.invoice.create({
      data: {
        subscriptionId: subscription.id,
        amount: plan.priceMonthly,
        currency: 'usd',
        status: 'paid',
        paymentIntentId: paymentIntent.id, // Link to payment
      },
    });

    return subscription;
  });

  return result;
}
```

### Test Mocking

```typescript
// backend/src/services/subscriptionService.test.ts
import { vi } from 'vitest';
import { stripeAdapter } from '../adapters/stripe';

// Mock the adapter
vi.mock('../adapters/stripe', () => ({
  stripeAdapter: {
    createSubscription: vi.fn(),
  },
}));

describe('createSubscription', () => {
  it('should create subscription and invoice successfully', async () => {
    // Mock payment success
    vi.mocked(stripeAdapter.createSubscription).mockResolvedValue({
      id: 'pi_test_123',
      status: 'succeeded',
      amount: 999,
      currency: 'usd',
    });

    const subscription = await createSubscription(1, 2);

    expect(subscription).toBeDefined();
    expect(stripeAdapter.createSubscription).toHaveBeenCalledWith(1, 2);
  });
});
```

### BDD Integration

```gherkin
# backend/tests/features/subscriptions.feature
Scenario: Subscribe to Pro plan
  Given a registered user "pro@example.com" with password "password123"
  When the user logs in with "pro@example.com" and "password123"
  And the user subscribes to the "Pro" plan
  Then the response status is 201
  And an invoice is recorded with the plan price
  And the user's project quota should be 10
```

**BDD Step Definition**:
```typescript
// No real Stripe call! Adapter mock handles it.
When('the user subscribes to the {string} plan', async function (planName: string) {
  const plan = await prisma.plan.findUnique({ where: { name: planName } });
  
  this.response = await request(app)
    .post('/api/subscriptions')
    .set('Authorization', `Bearer ${this.token}`)
    .send({ planId: plan!.id });
  
  // Mock adapter returns instantly, test completes in ~100ms
});
```

---

## Future: Real Stripe Implementation

When ready for production:

```typescript
// backend/src/adapters/stripe.ts
import Stripe from 'stripe';

export class RealStripeAdapter implements StripeAdapter {
  private stripe: Stripe;

  constructor() {
    this.stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
      apiVersion: '2023-10-16',
    });
  }

  async createSubscription(userId: number, planId: number): Promise<PaymentIntent> {
    const amount = planId === 2 ? 999 : 0;
    
    const paymentIntent = await this.stripe.paymentIntents.create({
      amount,
      currency: 'usd',
      metadata: { userId, planId },
    });

    return {
      id: paymentIntent.id,
      status: paymentIntent.status as 'succeeded' | 'pending' | 'failed',
      amount: paymentIntent.amount,
      currency: paymentIntent.currency,
    };
  }
}

// Toggle via environment variable
export const stripeAdapter: StripeAdapter = 
  process.env.NODE_ENV === 'production'
    ? new RealStripeAdapter()
    : new MockStripeAdapter();
```

---

## Compliance and Results

### Test Performance
- ✅ BDD tests: 12 scenarios in ~1.4s
- ✅ Unit tests: 13 subscription tests in <50ms
- ✅ No external API calls during testing
- ✅ Zero flaky tests

### Development Experience
- ✅ No Stripe account needed
- ✅ Instant onboarding
- ✅ No API cost during dev
- ✅ Offline development possible

### Code Quality
- ✅ Clear separation of concerns
- ✅ Easily testable
- ✅ SOLID principles (Dependency Inversion)
- ✅ Future-proof architecture

---

## References

- [Adapter Pattern - Gang of Four](https://refactoring.guru/design-patterns/adapter)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Test-Driven Development with Mocks](https://martinfowler.com/articles/mocksArentStubs.html)

---

## Related ADRs

- [ADR-001: ORM Choice (Prisma)](001-orm-choice.md)
- [ADR-002: Auth Token Storage](002-auth-token-storage.md)

---

**Last Updated**: 2025-10-30  
**Supersedes**: None  
**Superseded By**: None  
**Review Date**: When implementing real Stripe integration
