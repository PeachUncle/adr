# ADR-0008: Sentry + PostHog Observability Stack

## Status
Accepted

## Date
2024-12-30

## Context

Production applications require observability for:

1. **Error Tracking**: Catch and diagnose runtime errors
2. **Performance Monitoring**: Track Core Web Vitals and page load times
3. **User Analytics**: Understand user behavior and feature usage
4. **Session Replay**: Debug issues by watching user sessions

Options evaluated:
- **Sentry**: Industry-leading error tracking and performance
- **PostHog**: Open-source product analytics with feature flags
- **Mixpanel**: User analytics (expensive at scale)
- **LogRocket**: Session replay (expensive)
- **Datadog**: Full observability (enterprise pricing)

## Decision

Use Sentry for error tracking + performance, PostHog for analytics + session replay.

### Sentry Configuration

`sentry.client.config.ts`:

```typescript
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENV,

  // Performance
  tracesSampleRate: 0.1, // 10% of transactions
  profilesSampleRate: 0.1,

  // Session Replay (disabled, using PostHog)
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 0,

  // Filtering
  beforeSend(event) {
    // Filter out known non-issues
    if (event.exception?.values?.[0]?.type === 'ChunkLoadError') {
      return null // Common with code splitting
    }
    return event
  }
})
```

### PostHog Configuration

`src/lib/analytics/posthog.ts`:

```typescript
import posthog from 'posthog-js'

export function initPostHog() {
  if (typeof window !== 'undefined') {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
      capture_pageview: true,
      capture_pageleave: true,

      // Session Recording
      session_recording: {
        maskAllInputs: true,
        maskTextContent: true
      },

      // Performance
      autocapture: true,
      persistence: 'localStorage'
    })
  }
}
```

### Event Tracking

Centralized analytics in `src/lib/analytics/index.ts`:

```typescript
export const ANALYTICS_EVENTS = {
  // Authentication
  LOGIN_SUCCESS: 'login_success',
  LOGIN_FAILURE: 'login_failure',
  LOGOUT: 'logout',

  // CPR Workflow
  CPR_ANALYSIS_START: 'cpr_analysis_start',
  CPR_ANALYSIS_COMPLETE: 'cpr_analysis_complete',
  CPR_CREATE_START: 'cpr_create_start',
  CPR_CREATE_COMPLETE: 'cpr_create_complete',

  // Document
  DOCUMENT_UPLOAD: 'document_upload',
  DOCUMENT_DOWNLOAD: 'document_download',

  // Export
  EXPORT_PDF_START: 'export_pdf_start',
  EXPORT_PDF_SUCCESS: 'export_pdf_success',
  EXPORT_PDF_ERROR: 'export_pdf_error'
}

export function track(event: string, properties?: Record<string, unknown>) {
  posthog.capture(event, properties)
}

export function identify(userId: string, traits?: Record<string, unknown>) {
  posthog.identify(userId, traits)
}
```

### Web Vitals

Core Web Vitals reported to both services:

```typescript
// src/app/layout.tsx
import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Send to PostHog
    posthog.capture('web_vitals', {
      metric_name: metric.name,
      metric_value: metric.value,
      metric_rating: metric.rating
    })

    // Send to Sentry (if performance monitoring enabled)
    // Automatically captured via Sentry integration
  })
}
```

## Consequences

### Positive

1. **Separation of Concerns**: Sentry for errors, PostHog for analytics
2. **Cost Effective**: PostHog open-source, Sentry free tier sufficient
3. **Full Picture**: Errors linked to user sessions
4. **Privacy Options**: Both support data masking
5. **Self-Hostable**: PostHog can be self-hosted if needed
6. **Feature Flags**: PostHog includes feature flags (future use)

### Negative

1. **Two Dashboards**: Need to check both for full picture
2. **SDK Size**: Both libraries add to bundle (~30KB combined)
3. **Rate Limits**: Free tiers have event limits
4. **Data Sync**: No automatic linking between services

### Sampling Strategy

| Metric | Sample Rate | Rationale |
|--------|-------------|-----------|
| Sentry Errors | 100% | All errors captured |
| Sentry Traces | 10% | Performance monitoring |
| PostHog Events | 100% | All analytics events |
| Session Replay | 10% | Storage costs |

### Key Dashboards

**Sentry:**
- Error frequency and trends
- Performance (LCP, FID, CLS)
- Release health

**PostHog:**
- User funnels (signup → CPR complete)
- Feature usage heatmaps
- Session recordings for debugging
- Retention analysis

## References

- [Sentry Next.js SDK](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [PostHog JavaScript SDK](https://posthog.com/docs/libraries/js)
- [Web Vitals](https://web.dev/vitals/)
- `sentry.client.config.ts` - Sentry configuration
- `src/lib/analytics/` - Analytics implementation
