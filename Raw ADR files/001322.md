# ADR-028: Application Delivery Strategy

## Status

Accepted

## Context

The project aims to deliver a highly accessible, performant, and resilient web
application that meets modern user expectations across devices and platforms. To
support this, a decision was required regarding the application's
**delivery strategy** — that is, how the application would be distributed,
cached, and accessed by users beyond traditional web delivery.

The chosen delivery approach needed to support offline usage, installability,
fast repeat visits, and integration with native-like device capabilities without
requiring platform-specific app stores.

## Decision

We selected the **Progressive Web App (PWA)** model as the project's
**Application Delivery Strategy**. This decision enables the application to
function like a native app while remaining web-based and fully installable, with
offline capabilities and consistent performance across sessions.

## Reasons

1. **Installable Experience**:
   - Users can add the app to their home screen or desktop, improving
     accessibility and engagement without going through an app store.

2. **Offline Availability**:
   - With service workers, core assets are cached and available offline,
     improving reliability in poor or no network conditions.

3. **Performance Optimization**:
   - Cached responses reduce latency and enable faster load times for returning
     users.

4. **Consistent Cross-Platform UX**:
   - Delivers a native-like experience on web, desktop, and mobile platforms
     with a single codebase.

5. **Secure and Progressive by Design**:
   - PWAs require HTTPS and embrace progressive enhancement principles, ensuring
     a secure baseline experience with optional advanced features.

6. **Simplified Deployment Lifecycle**:
   - No app store approval process is required. Updates are controlled through
     the web deployment pipeline.

## Consequences

1. **Service Worker Management**:
   - Requires handling cache invalidation, update detection, and offline
     fallbacks to prevent stale content issues.

2. **Testing and Maintenance Overhead**:
   - Additional testing is required for offline scenarios and install flows
     across different browsers and devices.

3. **User Expectations**:
   - Users may expect native-like performance and behavior (e.g., background
     sync, push notifications), which must be carefully managed.

## Alternatives Considered

### Traditional Web App:

- **Pros**: Simpler deployment, no offline or install complexity.
- **Cons**: No offline support, no installability, perceived as less
  "native" or performant.

### Native Mobile App:

- **Pros**: Full access to device APIs and OS features.
- **Cons**: Requires separate codebase, app store submission, and higher
  development and maintenance cost.

### Hybrid Webview App:

- **Pros**: Single codebase, packaged as native.
- **Cons**: Adds runtime overhead, lacks the native performance of PWAs or
  real apps.
