---
title: "ADR-0003: Anonymous User Browser Fingerprinting"
description: "Architectural decision for implementing browser fingerprinting to enable anonymous usage limits"
type: "adr"
canonical_url: "/decisions/adr-0003-anonymous-user-browser-fingerprinting"
status: "accepted"
decision_date: "2024-08-20"
review_date: "2025-02-20"
version: "1.0"
last_updated: "2025-01-09"
authors: ["Security Lead"]
reviewers: ["Privacy Officer", "Tech Lead"]
stakeholders: ["Frontend Team", "Backend Team", "Legal Team", "Product Team"]
supersedes: []
related_adrs: ["ADR-0001"]
tags: ["security", "privacy", "anonymity", "browser-fingerprinting", "usage-limits", "conversion"]
impact: "high"
---

# ADR-0003: Anonymous User Browser Fingerprinting

## Status

Accepted

## Context

To reduce friction and increase conversion, we want to offer a "try before you buy" experience
where users can create one free summary without registration. However, we need to prevent abuse while
maintaining anonymity and avoiding persistent tracking across sessions.

## Decision

Implement browser fingerprinting combined with IP address tracking to enable anonymous usage limits
without requiring authentication or persistent cookies.

### Implementation Strategy

- Generate client-side browser fingerprint from: User Agent + Screen Resolution + Timezone + Language
- Combine with server-side IP address for enhanced uniqueness
- Store usage events against anonymous fingerprint + IP combination
- Enforce 1 lifetime summary limit per unique fingerprint+IP pair

### Database Design

```sql
UsageEvent {
  userId: "ANONYMOUS_USER" (special account)
  browserFingerprint: String
  ipAddress: String (hashed for privacy)
  eventType: SUMMARY_CREATED
  metadata: Json
}
```

## Consequences

### Positive Consequences

- **Frictionless Trial**: Users can immediately experience product value
- **Conversion Optimization**: Reduces barriers to first-time usage
- **Abuse Prevention**: Limits anonymous usage without complex tracking
- **Privacy Friendly**: No persistent cookies or cross-site tracking
- **Simple Implementation**: Client-side fingerprinting + server-side validation

### Negative Consequences

- **Bypass Potential**: Sophisticated users can circumvent limits (VPN, browser changes)
- **False Positives**: Legitimate users on shared networks may be blocked
- **Privacy Concerns**: Browser fingerprinting raises privacy questions
- **Maintenance Overhead**: Fingerprinting logic may need updates for new browsers

### Risks

- **Regulatory Compliance**: May face scrutiny under privacy regulations (GDPR, CCPA)
- **Detection Avoidance**: Privacy-focused users may use fingerprinting protection
- **Shared Device Issues**: Multiple family members/coworkers may conflict
- **Network Changes**: Dynamic IPs could allow limit circumvention

## Alternatives Considered

- **No Limits**: Rejected due to potential for service abuse and lack of conversion incentive
- **Persistent Cookies**: Rejected due to cookie consent requirements and easy circumvention
- **IP-only Limits**: Rejected due to shared network issues (offices, public WiFi)
- **Device Storage**: Rejected due to privacy concerns and easy circumvention
- **Email-based Trial**: Rejected due to friction and fake email abuse potential

## Implementation Notes

### Client-Side Fingerprinting

```typescript
const generateFingerprint = () => {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  ctx.textBaseline = 'top'
  ctx.font = '14px Arial'
  ctx.fillText('Browser fingerprint', 2, 2)
  
  return btoa([
    navigator.userAgent,
    screen.width + 'x' + screen.height,
    new Date().getTimezoneOffset(),
    navigator.language,
    canvas.toDataURL()
  ].join('|')).slice(0, 16)
}
```

### Server-Side Validation

```typescript
const checkAnonymousLimit = async (fingerprint: string, ip: string) => {
  const hashedIP = await hash(ip + SALT)
  const existingUsage = await db.usageEvent.findFirst({
    where: {
      userId: 'ANONYMOUS_USER',
      browserFingerprint: fingerprint,
      ipAddressHash: hashedIP,
      eventType: 'SUMMARY_CREATED'
    }
  })
  return !existingUsage
}
```

### Privacy Measures

- Hash IP addresses before storage
- No cross-session data retention beyond usage counting
- Clear documentation of fingerprinting usage
- Easy upgrade path to remove limitations

### User Experience Flow

1. User visits homepage
2. Fingerprint generated client-side
3. User submits YouTube URL
4. Server validates fingerprint+IP hasn't been used
5. If valid: process summary, record usage
6. If exceeded: show conversion modal with signup options

## References

- [Browser Fingerprinting Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Pixel_manipulation_with_canvas)
- [GDPR Compliance for Fingerprinting](https://gdpr.eu/cookies/)
- [Anonymous User Implementation](../src/server/api/routers/summary.ts)

---

*Decision Date: 2024-08-20*
*Review Date: 2025-02-20*
