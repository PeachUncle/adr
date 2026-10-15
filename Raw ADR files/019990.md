---
status: 'accepted'
date: 2025-09-18
decision-makers: Product Owner, Development Team
consulted: Microsoft Clarity documentation, Analytics platform comparison reviews
informed: Development team, Product stakeholders
---

# Use Microsoft Clarity for Website Analytics and Pageview Tracking

## Context and Problem Statement

The voder.ai website needs analytics tracking to understand visitor behavior, page views, and traffic patterns. The product owner requires visibility into how many people are finding and visiting the AI slop validation site, with daily and weekly reporting capabilities. We need to implement a privacy-compliant analytics solution that provides essential business insights without compromising user experience or site performance.

## Decision Drivers

- REQ-PAGEVIEW-TRACKING: System must track when visitors view pages on the site
- REQ-VISITOR-COUNTING: System must identify and count unique visitors accurately
- REQ-METRICS-ACCESS: Product owner needs access to visitor and page view data
- REQ-TREND-VISIBILITY: Data must show visitor patterns over daily and weekly periods
- REQ-PRIVACY-COMPLIANCE: Analytics implementation must respect visitor privacy and applicable regulations
- Minimal performance impact on site loading speed
- Easy integration with existing Vite/TypeScript build system
- Free tier availability for startup budget constraints
- Real-time or near real-time data availability

## Considered Options

- Microsoft Clarity
- Google Analytics 4 (GA4)
- Plausible Analytics
- Fathom Analytics
- Simple Analytics

## Decision Outcome

Chosen option: "Microsoft Clarity", because it provides comprehensive analytics capabilities including pageview tracking, visitor counting, and heatmaps while being completely free, privacy-focused by design, and offering excellent integration options with minimal performance impact.

### Consequences

- Good, because Microsoft Clarity is completely free with no usage limits
- Good, because it provides privacy-compliant analytics without requiring cookie consent banners
- Good, because it offers comprehensive insights including heatmaps and session recordings
- Good, because it has minimal performance impact (script loads asynchronously)
- Good, because it integrates easily with our TypeScript/Vite build system
- Good, because it provides real-time dashboard access for product owner
- Neutral, because it's Microsoft-owned, which may influence data governance considerations
- Bad, because it has fewer customization options compared to Google Analytics
- Bad, because it's less widely adopted than Google Analytics, potentially limiting integration options

### Confirmation

The implementation can be confirmed by:

- Verifying the Clarity script loads successfully in browser developer tools
- Confirming pageview events are recorded in the Microsoft Clarity dashboard
- Testing visitor counting accuracy through controlled visits
- Validating performance impact through Lighthouse scores before and after implementation
- Confirming privacy compliance through GDPR assessment

## Pros and Cons of the Options

### Microsoft Clarity

Microsoft's free web analytics service focusing on user behavior insights and privacy compliance.

- Good, because completely free with no usage limits or paid tiers
- Good, because privacy-first design doesn't require cookie consent in most jurisdictions
- Good, because provides advanced features like heatmaps and session recordings
- Good, because minimal performance impact with async script loading
- Good, because easy integration via npm package or script tag
- Good, because real-time dashboard with intuitive interface
- Neutral, because Microsoft data governance may have different implications than Google
- Bad, because fewer third-party integrations compared to Google Analytics
- Bad, because smaller community and fewer resources for troubleshooting

### Google Analytics 4 (GA4)

Google's latest analytics platform with comprehensive tracking and reporting capabilities.

- Good, because industry standard with extensive documentation and community support
- Good, because comprehensive feature set with advanced reporting capabilities
- Good, because extensive third-party integrations and tools
- Good, because free tier with generous limits for small to medium sites
- Neutral, because requires cookie consent management for GDPR compliance
- Bad, because more complex implementation requiring consent management
- Bad, because larger performance impact due to tracking script size
- Bad, because Google data governance concerns for privacy-conscious users

### Plausible Analytics

Privacy-focused, lightweight analytics alternative to Google Analytics.

- Good, because privacy-first design with no personal data collection
- Good, because extremely lightweight with minimal performance impact
- Good, because simple, clean dashboard interface
- Good, because GDPR compliant without cookie consent requirements
- Bad, because paid service with monthly subscription costs
- Bad, because fewer features compared to Microsoft Clarity or Google Analytics
- Bad, because no free tier, making it unsuitable for startup budget constraints

### Fathom Analytics

Privacy-focused analytics with emphasis on simplicity and compliance.

- Good, because strong privacy focus with no data sharing
- Good, because lightweight implementation
- Good, because simple setup and clean interface
- Bad, because paid service with monthly subscription costs starting at $14/month
- Bad, because limited feature set compared to free alternatives
- Bad, because no free tier available

### Simple Analytics

Minimalist, privacy-focused analytics platform.

- Good, because privacy-first approach with minimal data collection
- Good, because very lightweight implementation
- Good, because simple setup and clean dashboard
- Bad, because paid service starting at $19/month
- Bad, because very limited feature set
- Bad, because no free tier, making it cost-prohibitive for startups

## More Information

Microsoft Clarity was selected based on its optimal balance of comprehensive features, privacy compliance, zero cost, and minimal performance impact. The implementation uses the npm package `@microsoft/clarity` (version 1.0.0) integrated into the main application entry point with the project ID `t5zu4kays7`. The integration follows privacy-first principles and includes error handling to ensure analytics failures don't impact site functionality.

Alternative options were evaluated but rejected due to cost constraints (Plausible, Fathom, Simple Analytics), complexity overhead (Google Analytics 4), or feature limitations relative to the chosen solution.
