# ADR-004: Google Consent Mode v2 Integration

**Status**: Accepted  
**Date**: 2025-09-03  
**Deciders**: Project team  
**Tags**: consent, privacy, gdpr, gtm, analytics

---

## Context

Modern web applications must respect user privacy preferences and comply with regulations like GDPR. The project needs a consent management solution that:
- Gates analytics and marketing tags appropriately
- Integrates with Google Tag Manager
- Demonstrates industry best practices
- Provides clear user controls

Google Consent Mode v2 is the current standard for consent signaling to Google tags.

### Options Considered

1. **No Consent Management**: Let GTM/tags fire unconditionally
2. **Simple Banner**: Show notice, no enforcement
3. **Consent Mode v1**: Original Google consent implementation
4. **Consent Mode v2**: Enhanced consent with additional signals
5. **Third-Party CMP**: OneTrust, Cookiebot, etc.

---

## Decision

We will implement **Google Consent Mode v2** with:
- Consent defaults set to `denied` before any tags load
- Custom consent banner with category controls (necessary, functional, analytics, marketing, experimentation)
- Consent state updates via `gtag('consent', 'update', ...)`
- Category mapping:
  - `analytics_storage` ↔ analytics banner category
  - `ad_storage`, `ad_user_data`, `ad_personalization` ↔ marketing category
- Banner state persisted to `localStorage`
- Matomo consent via `_paq.requireConsent()` + `rememberConsentGiven()`

---

## Rationale

### Why Consent Mode v2?
- **Current Standard**: Required for Google Ads, recommended for GA4
- **Granular Control**: Separate consent types for different purposes
- **GTM Integration**: Native support in GTM
- **Future-Proof**: Google's ongoing consent strategy
- **Behavioral Modeling**: GA4 can model conversions with limited data

### Why Custom Banner?
- **Educational Value**: Shows implementation patterns
- **Customization**: Tailored to demo needs
- **Transparency**: Source code visible for learning
- **Cost**: No third-party CMP fees

### Trade-offs
- **Not Production-Grade**: Real sites should use audited CMPs
- **Maintenance**: Must keep up with consent standard changes
- **Legal Review**: Users must adapt for their jurisdiction

---

## Consequences

### Positive
- Demonstrates proper consent gating patterns
- Shows Consent Mode v2 implementation details
- Users can learn from real working code
- Respects demo user privacy preferences
- Compatible with GTM-first architecture (ADR-001)

### Negative
- Custom banner requires maintenance
- Legal compliance responsibility shifts to users
- Not suitable for production without legal review
- May not cover all regional consent requirements

### Neutral
- Banner UI is basic (can be enhanced)
- Consent state is device-local (no cross-device sync)

---

## Implementation Details

### Consent Defaults (index.html)
```javascript
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('consent', 'default', {
  ad_storage: 'denied',
  ad_user_data: 'denied',
  ad_personalization: 'denied',
  analytics_storage: 'denied',
  wait_for_update: 500
});
```

### Category Mapping
| Banner Category | Consent Mode Types | Purpose |
|----------------|-------------------|---------|
| Necessary | N/A (always true) | Essential site functionality |
| Functional | N/A (custom) | Site personalization, preferences |
| Analytics | `analytics_storage` | Measurement, analytics |
| Marketing | `ad_storage`, `ad_user_data`, `ad_personalization` | Advertising, remarketing |
| Experimentation | N/A (custom) | A/B testing, optimization |

### Matomo Integration
- `_paq.push(['requireConsent'])` queued before MTM loads
- `_paq.push(['rememberConsentGiven'])` when analytics consent granted
- `_paq.push(['forgetConsentGiven'])` when analytics consent revoked
- MTM tags gated by `cookies_statistical` event or `consent.analytics` DLV

---

## Future Considerations

### v2 Enhancements
- **Regional Defaults**: Different defaults for EU vs non-EU
- **Redaction**: PII redaction when consent denied
- **URL Passthrough**: Propagate consent state across domains

### Advanced Features
- **Legitimate Interest**: Separate from consent
- **Vendor Management**: IAB TCF support
- **Consent Receipts**: Audit trail of consent choices
- **Cross-Device Sync**: Requires backend

---

## Compliance Notes

⚠️ **This implementation is for demonstration purposes only.**

- Not audited for GDPR, CCPA, or other regulations
- Users must conduct legal review for their jurisdiction
- Consent wording and categories may need adjustment
- Consider third-party CMP for production sites
- Document legal basis for each data processing activity

---

## Related

- ADR-001: GTM-First Analytics Architecture
- ADR-003: Matomo Tag Manager Only
- `src/components/ConsentBanner.jsx`: Banner implementation
- `docs/ANALYTICS.md`: Consent integration overview
- `docs/MATOMO_ECOMMERCE_MAPPING.md`: Matomo consent events
