# ADR-003: No Analytics or Tracking

## Status

Accepted

## Context

Many web templates include analytics (Google Analytics, Plausible, etc.) or tracking scripts by default. We need to decide whether to include any form of analytics in this template.

Considerations:
- Privacy implications
- User expectations
- Development insights
- Regulatory compliance (GDPR, CCPA)
- Alignment with project values

## Decision

We will include **ZERO analytics, tracking, or telemetry** in this template.

This means:
- No Google Analytics
- No Plausible Analytics
- No Matomo
- No Hotjar or heatmaps
- No error tracking (Sentry, etc.)
- No fingerprinting
- No cookies
- No localStorage tracking
- No third-party scripts

## Consequences

### Positive

- **Maximum Privacy**: Users' behavior is never tracked
- **GDPR/CCPA Compliant**: No personal data collected means no compliance burden
- **Faster Load Times**: No analytics scripts to load
- **Censorship Resistant**: No tracking dependencies that can be blocked or compromised
- **Trust**: Users can verify privacy claims
- **Security**: Fewer third-party dependencies means fewer vulnerabilities
- **Clean Codebase**: No tracking code to maintain

### Negative

- **No Usage Insights**: Developers won't know how their site is used
- **No Error Monitoring**: Client-side errors won't be automatically reported
- **No A/B Testing**: Can't easily test variations
- **Less "Professional"**: Some may expect analytics

### Mitigations

For users who need insights:
- Self-host privacy-friendly analytics (Plausible, Matomo, Umami)
- Use server log analysis (if using traditional hosting)
- Implement optional, opt-in client-side logging
- Use IPFS gateway logs (with user awareness)

**Important**: If users add analytics, they must:
1. Update the privacy policy
2. Ensure GDPR/CCPA compliance
3. Document it in their README
4. Consider using privacy-preserving options

## Code Examples

### What We DON'T Include

```javascript
// ❌ NO Google Analytics
// <!-- Global site tag (gtag.js) -->
// <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>

// ❌ NO Error Tracking
// Sentry.init({ dsn: "..." });

// ❌ NO Fingerprinting
// const fingerprint = await FingerprintJS.load();
```

### What Users Can Add (Optionally)

```javascript
// ✅ Self-hosted, privacy-friendly (user's choice)
// <script defer data-domain="yourdomain.com" src="https://plausible.yourdomain.com/js/script.js"></script>

// With proper disclosure in privacy policy
```

## Verification

Users can verify our no-tracking claim by:

1. **Inspecting the code** (it's open source)
2. **Checking network requests** in browser DevTools
3. **Running privacy audits** (Blacklight, PrivacyScore, etc.)
4. **Reading PRIVACY-AUDIT.md**

## Alternatives Considered

**Privacy-Friendly Analytics (Plausible, Matomo)**
- Even privacy-friendly analytics collect data
- Still requires privacy policy updates
- Self-hosting burden for users
- Not everyone needs/wants analytics
- Decision: Leave this to users to add if needed

**Opt-In Analytics**
- Adds complexity
- Still collects data (even if optional)
- Cookie banners required
- Decision: Doesn't align with "privacy by default" principle

**Aggregated, Anonymous Metrics**
- Still technically tracking
- Can be fingerprinted
- Hard to prove anonymity
- Decision: Violates "zero tracking" principle

## References

- [GDPR Article 25: Data Protection by Design](https://gdpr-info.eu/art-25-gdpr/)
- [Mozilla Privacy Principles](https://www.mozilla.org/privacy/principles/)
- [The Markup: Blacklight](https://themarkup.org/blacklight)

## Notes

This is a core principle of the template. If analytics are needed, they should be:
- Self-hosted
- Clearly documented
- Compliant with regulations
- Properly disclosed to users

Any PR attempting to add tracking will be rejected.

---

**Date**: 2025-11-12
**Deciders**: Template Maintainers
**Reviewed**: N/A
