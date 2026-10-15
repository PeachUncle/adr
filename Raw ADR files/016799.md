# ADR-001: GTM-First Analytics Architecture

**Status**: Accepted  
**Date**: 2025-09-03  
**Deciders**: Project team  
**Tags**: analytics, architecture, gtm, ga4

---

## Context

The project needs a flexible, maintainable analytics implementation that allows analysts and tag managers to configure tracking without requiring code changes. Multiple analytics platforms (GA4, Matomo, potentially others) need to be supported.

### Options Considered

1. **Direct GA4 Integration**: Include GA4 snippet directly in HTML
2. **GTM-First Architecture**: All analytics configured through Google Tag Manager
3. **Hybrid Approach**: Direct GA4 + supplemental GTM tags

---

## Decision

We will adopt a **GTM-First architecture** where:
- Google Tag Manager loads early in the page lifecycle
- GA4 is configured entirely within GTM (no direct GA4 snippet)
- GTM always loads, regardless of consent state
- Consent Mode v2 controls tag behavior, not GTM loading
- All ecommerce and custom events pushed to `dataLayer`

---

## Rationale

### Advantages
- **Flexibility**: Analysts can modify tracking without code deploys
- **Centralization**: Single container manages all tags
- **Industry Standard**: Common pattern in enterprise implementations
- **A/B Testing**: Easy to test tracking changes via GTM preview
- **Consent Orchestration**: GTM respects Consent Mode signals automatically
- **Reduced Client Bloat**: One tag container instead of multiple snippets

### Trade-offs
- **Dependency**: Requires GTM account and configuration
- **Learning Curve**: Users must understand GTM concepts
- **Debug Complexity**: Issues require GTM preview + browser devtools

---

## Consequences

### Positive
- Users can customize GA4 configuration without touching code
- Additional platforms (Matomo, ODP) can be added via GTM/MTM
- Tag management becomes a configuration exercise
- Easier to demonstrate tag manager patterns

### Negative
- Setup documentation must cover GTM configuration
- Users without GTM knowledge may struggle initially
- Requires sample GTM container export for quickstart

### Neutral
- GTM always loads (2-3KB overhead), but behavior gated by consent
- Need comprehensive documentation for GTM setup

---

## Implementation Notes

- GTM ID configured via environment variable or `public/config.json`
- App pushes events to `window.dataLayer` with GA4-compatible schemas
- Consent defaults set before GTM loads (Consent Mode v2)
- Optional sGTM support via `transport_url` dataLayer variable
- Debug logging available in development mode

---

## Related

- ADR-004: Google Consent Mode v2 Integration
- `docs/GTM_CONTAINER.md`: GTM configuration guide
- `docs/ANALYTICS.md`: Analytics integration overview
- `docs/gtm/container_shop404.json`: Sample GTM export
