# ADR-004: Use Sentry for Error Tracking and Observability

**Date**: 2025-10-21
**Status**: Accepted
**Deciders**: @team

## Context

Educational project teaching production-ready practices needs observability solution to demonstrate:
- Error tracking and monitoring
- Performance monitoring
- User feedback collection
- Breadcrumbs for debugging

Requirements:
- Free tier for educational use
- Easy integration with React
- Real-world production tool
- Good developer experience
- Educational value (students learn industry-standard tool)

## Considered Options

1. **Sentry**
   - Pros: Industry standard, excellent React integration, free tier generous, best-in-class UX
   - Cons: Requires external service (but free tier sufficient)

2. **LogRocket**
   - Pros: Session replay, console logs, network monitoring
   - Cons: Expensive (no good free tier), overkill for educational project

3. **Custom logging (console.log + monitoring)**
   - Pros: No dependencies, simple
   - Cons: Not production-ready, no aggregation, manual collection, teaches bad habits

4. **Datadog**
   - Pros: Enterprise-grade, comprehensive
   - Cons: Expensive, complex setup, overkill for learning

## Decision

Use **Sentry** for error tracking and observability

## Rationale

- **Industry standard**:
  - Used by Airbnb, Microsoft, Dropbox, Discord
  - Students learn tool they'll use in real jobs
  - Best practices baked in

- **Free tier**:
  - 5,000 errors/month (sufficient for course)
  - 10,000 performance units
  - Unlimited projects
  - Session replay included

- **React integration**:
  - Official `@sentry/react` package
  - Error Boundary component
  - React Router integration
  - Performance monitoring for React

- **Features for learning**:
  - Breadcrumbs: Track user actions before error
  - Context: Attach user data, custom tags
  - Source maps: See original TypeScript code
  - Releases: Track deployments
  - User feedback: Dialog for bug reports

- **Developer experience**:
  - 5-minute setup
  - Beautiful dashboard
  - Email notifications
  - Slack integration (optional)
  - Detailed error traces

Educational value demonstration:
```typescript
// Breadcrumbs
Sentry.addBreadcrumb({
  message: 'User added item to cart',
  category: 'cart.action',
  data: { productId, price }
})

// Custom metrics
Sentry.setMeasurement('cart.items', itemCount, 'none')

// Error capture with context
Sentry.captureException(error, {
  tags: { feature: 'checkout' },
  user: { id: userId }
})
```

## Consequences

### Positive
+ Students learn industry-standard observability tool
+ Real error tracking in demo deployments
+ Breadcrumbs teach debugging practices
+ Performance monitoring demonstrates Core Web Vitals
+ User feedback dialog shows production UX patterns
+ Source maps preserve debugging experience
+ Free tier sufficient for entire course
+ Easy setup (< 10 lines of code)

### Negative
- External dependency (requires internet for reporting)
- Requires Sentry account creation
- Free tier has retention limits (30 days)
- Error data sent to external service (privacy consideration for production)

## Implementation Details

**Setup** (`src/infrastructure/sentry.ts`):
```typescript
import * as Sentry from '@sentry/react'

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration()
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
})
```

**Error Boundary**:
```typescript
<Sentry.ErrorBoundary fallback={<ErrorFallback />}>
  <App />
</Sentry.ErrorBoundary>
```

**Custom metrics**:
```typescript
// Track business metrics
Sentry.setTag('cart.items.count', itemCount)
Sentry.setMeasurement('cart.value', subtotal, 'none')
```

**Breadcrumbs**:
```typescript
// Track user journey
Sentry.addBreadcrumb({
  message: 'User added item to cart',
  category: 'cart.action',
  level: 'info',
  data: { productId, name, price }
})
```

## Privacy Considerations

For educational use:
- No real user data collected
- Demo credentials only
- Source maps optional (enabled for learning)
- Can disable in production with env vars

## References

- [Sentry React documentation](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Sentry pricing](https://sentry.io/pricing/) - Free tier details
- [Sentry best practices](https://docs.sentry.io/product/best-practices/)
- Course: Demonstrates breadcrumbs, custom metrics, error capture, user feedback
