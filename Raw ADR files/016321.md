# Plausible Analytics Integration for Privacy-First Visitor Insights

- Status: accepted
- Date: 2025-01-22

## Context and Problem Statement

The Securing the Realm website needed basic visitor analytics to understand:
1. Which content resonates with readers
2. Traffic sources and referral patterns
3. Geographic distribution of audience
4. Popular pages and topics
5. Success of content strategy

However, traditional analytics platforms presented significant privacy concerns:
- Tracking cookies violating user privacy
- Personal data collection requiring GDPR consent banners
- Invasive user profiling and cross-site tracking
- Data sold to third parties
- Contribution to surveillance capitalism

We needed analytics that respect user privacy while providing actionable insights, comply with GDPR/CCPA by default, and align with our values of transparency and user respect.

## Decision Drivers

- **Privacy-First**: No cookies, no personal data collection, no cross-site tracking
- **GDPR/CCPA Compliance**: Compliant by default, no consent banners needed
- **Data Transparency**: Users can see what data is collected
- **Performance**: Minimal JavaScript, non-blocking loading
- **Actionable Metrics**: Sufficient insights for content strategy
- **Data Ownership**: Control over analytics data
- **Open Source**: Transparent codebase, auditable
- **Cost**: Reasonable pricing for hosted service
- **Ease of Integration**: Simple script integration with Astro

## Considered Options

### Option 1: Google Analytics 4 (GA4)

- Description: Industry-standard analytics platform from Google
- Pros:
  - Comprehensive feature set
  - Industry standard, familiar to stakeholders
  - Free tier available
  - Extensive integrations
  - Machine learning insights
  - User journey tracking
- Cons:
  - ❌ Privacy nightmare: extensive tracking, cookies, fingerprinting
  - ❌ Requires GDPR consent banners
  - ❌ Personal data collection and profiling
  - ❌ Data shared with Google for advertising
  - ❌ Overkill for simple content site
  - ❌ Large JavaScript bundle (performance impact)
  - ❌ Complex configuration
  - ❌ Violates EU privacy regulations without consent

### Option 2: Matomo (Self-Hosted)

- Description: Open-source, self-hosted analytics platform
- Pros:
  - Full data ownership
  - Privacy-focused options available
  - GDPR compliant
  - Comprehensive features
  - Open source, auditable
  - No data sharing with third parties
- Cons:
  - ❌ Requires self-hosting infrastructure (cost, maintenance)
  - ❌ Database and server management
  - ❌ Security updates and patches required
  - ❌ Complex configuration
  - ❌ Ongoing operational burden
  - ❌ Cookies still used (unless disabled, reducing accuracy)

### Option 3: Fathom Analytics

- Description: Privacy-first, lightweight analytics platform
- Pros:
  - Privacy-focused, no cookies
  - GDPR compliant by default
  - Simple, clean interface
  - Fast, lightweight script
  - Hosted service (no infrastructure)
  - No consent banners needed
- Cons:
  - Higher cost than Plausible ($14-24/mo vs $9-19/mo)
  - Smaller feature set than competitors
  - Less active development community
  - Proprietary (not open source)

### Option 4: Plausible Analytics (Chosen)

- Description: Privacy-first, open-source, lightweight analytics platform
- Pros:
  - ✅ **Privacy-First**: No cookies, no personal data, anonymous by default
  - ✅ **GDPR/CCPA Compliant**: No consent banners needed
  - ✅ **Lightweight**: <1KB script, non-blocking async loading
  - ✅ **Open Source**: Fully auditable, transparent practices
  - ✅ **Simple Metrics**: Page views, referrers, countries, devices
  - ✅ **No Data Sharing**: Data never sold or shared
  - ✅ **Managed Service**: No infrastructure to maintain
  - ✅ **Transparent Pricing**: Clear, fair pricing model
  - ✅ **Performance**: Minimal impact on page load
  - ✅ **Custom Instance**: Can use custom domain to avoid ad blockers
- Cons:
  - Not free (paid managed service)
  - Limited compared to GA4 (but that's a feature, not a bug)
  - No user journey tracking (by design, for privacy)
  - Requires paid plan for custom domains

## Decision Outcome

Chosen option: "Plausible Analytics (Managed Service)"

Justification:

**Privacy Approach:**

Plausible is designed with privacy as the core principle:

1. **No Cookies**: Plausible doesn't use cookies at all
   - No consent banners required
   - No cookie notices needed
   - GDPR/CCPA compliant by default
   - No localStorage or persistent tracking

2. **No Personal Data Collection**:
   - IP addresses are anonymized immediately (cannot be de-anonymized)
   - No unique user IDs or fingerprinting
   - No cross-site or cross-device tracking
   - No behavioral profiling
   - Visitors remain completely anonymous

3. **Minimal Data Collection**:
   - Page URL (what content is viewed)
   - HTTP Referer (where traffic comes from)
   - Browser User-Agent (anonymized device/browser info)
   - Country/region (derived from anonymized IP, not stored)
   - That's it. No other data collected.

4. **Data Ownership**:
   - We own all analytics data
   - Data never sold or shared with third parties
   - No data used for advertising
   - Can export all data anytime
   - Can delete all data anytime

5. **Transparency**:
   - Open source (AGPLv3) - fully auditable
   - Public roadmap and development
   - Transparent privacy policy
   - No hidden tracking or data collection
   - Users can see exactly what's tracked

6. **Compliance**:
   - GDPR compliant by design (no consent needed)
   - CCPA compliant (no personal data sale)
   - PECR compliant (no cookies)
   - Recommended by privacy advocates
   - Used by privacy-conscious organizations

**Technical Excellence:**

- **Performance**: <1KB script vs 45KB+ for Google Analytics
- **Non-Blocking**: Async loading, no impact on page render
- **Reliable**: 99.9% uptime SLA on managed service
- **Simple Integration**: Single script tag in `<head>`
- **Custom Instance**: Using proxy endpoint to maximize data collection
- **Astro Compatible**: Works perfectly with static site generation

**Actionable Insights:**

While simpler than GA4, Plausible provides all metrics we actually need:
- Page views and unique visitors
- Top pages and content performance
- Traffic sources (referrers, social, direct)
- Geographic distribution (country-level only, privacy-preserving)
- Device types (desktop, mobile, tablet)
- Browser and OS information (for compatibility)

We specifically **don't want** (and Plausible doesn't provide):
- Individual user tracking (privacy violation)
- Behavioral profiling (creepy and unnecessary)
- Conversion funnels for e-commerce (not applicable)
- User journey mapping (privacy-invasive)
- Demographics beyond country (not needed, invasive)

**Cost-Benefit:**

The managed service fee (~$9-19/month) is justified by:
- Zero infrastructure maintenance
- GDPR compliance by default (no legal risk)
- Performance benefits (faster site)
- Alignment with our privacy values
- Professional image (respecting user privacy)
- No consent banner development needed

## Consequences

### Positive

- **User Privacy Protected**: No personal data collected, no tracking, no cookies
- **Legal Compliance**: GDPR/CCPA compliant without consent banners
- **Performance**: Minimal JavaScript (<1KB), fast page loads
- **Simple Metrics**: Focus on content performance, not user stalking
- **Data Ownership**: Full control over analytics data
- **Professional Image**: Demonstrates respect for user privacy
- **Open Source**: Auditable, transparent, trustworthy
- **Low Maintenance**: Managed service, no infrastructure
- **Ad Blocker Friendly**: Custom instance helps avoid overzealous blocking

### Negative

- **Ongoing Cost**: ~$9-19/month for managed service
  - Mitigation: Affordable for professional site, worth the privacy benefits
- **Limited Metrics**: No user journey or detailed behavior tracking
  - Mitigation: We don't need invasive tracking for content strategy
- **Custom Instance**: Requires custom domain configuration
  - Mitigation: Already configured with custom endpoint

### Neutral

- Data retention: 24-month rolling window (can be adjusted)
- Metrics are site-level, not user-level (intentional design)
- Cannot track individual user behavior (by design, for privacy)

## Implementation Details

**Script Integration:**
```html
<!-- Privacy-friendly analytics by Plausible -->
<script is:inline async src="https://plausible.io/js/pa-EUZMXoBFB9OR9p1BrnWMh.js"></script>
<script is:inline>
  window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};
  plausible.init()
</script>
```

**Location**: `src/layouts/Base.astro` (global header, all pages)

**Configuration:**
- Custom instance endpoint: `pa-EUZMXoBFB9OR9p1BrnWMh.js`
- Async loading: Non-blocking, no performance impact
- `is:inline` directive: Bypasses Astro bundling, direct inclusion
- No tracking parameters: Default privacy-first behavior

**Data Collected:**
- Page URLs (what content is viewed)
- Referrers (where traffic comes from)
- Country (derived from anonymized IP, not stored)
- Device type (desktop, mobile, tablet - anonymized)
- Browser/OS (for compatibility, anonymized)

**Data NOT Collected:**
- IP addresses (anonymized immediately, never stored)
- Cookies or localStorage (none used)
- Personal information (names, emails, etc.)
- Unique user IDs (no cross-session tracking)
- Precise location (only country-level)
- Behavioral data (no profiling)

**Privacy Policy Update Needed:**
While Plausible requires no consent, transparency dictates we should:
1. Add "Analytics" section to privacy policy
2. Explain what Plausible collects (and doesn't)
3. Link to Plausible's privacy policy
4. Confirm no personal data collection
5. Explain data usage (content strategy only)

## Metrics to Track

**Content Performance:**
- Most viewed blog posts and pages
- Content popularity over time
- New vs returning visitor balance

**Traffic Sources:**
- Direct traffic
- Social media referrals (LinkedIn, Twitter/X, YouTube)
- Search engines
- External referrals

**Audience Insights:**
- Geographic distribution (country-level)
- Device types (mobile vs desktop usage)
- Browser/OS for compatibility planning

**Success Indicators:**
- Traffic growth over time
- Engagement with new content
- Referral success from social media

**NOT Tracking:**
- Individual user behavior (privacy violation)
- Conversion funnels (not applicable)
- User demographics beyond country (not needed)
- Session duration (not reliable without cookies)
- Bounce rate (misleading metric for content sites)

## References

- [Plausible Analytics Documentation](https://plausible.io/docs)
- [Plausible Privacy Policy](https://plausible.io/privacy)
- [Plausible vs Google Analytics](https://plausible.io/vs-google-analytics)
- [GDPR Compliance Guide](https://plausible.io/data-policy)
- [Astro Integration Guide](https://docs.astro.build/en/guides/integrations-guide/)
- [Web Analytics Privacy Best Practices](https://plausible.io/privacy-focused-web-analytics)
