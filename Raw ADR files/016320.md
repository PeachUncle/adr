# Giscus Comments Integration for Blog Posts

- Status: accepted
- Date: 2025-11-22

## Context and Problem Statement

The Securing the Realm blog needed a community engagement mechanism to allow readers to discuss technical content, ask questions, and provide feedback. As a technical education platform focused on Azure, cybersecurity, and tabletop gaming, fostering discussion enhances learning and builds community.

Traditional comment systems presented challenges:
1. Privacy concerns with third-party trackers and advertising
2. Moderation complexity and spam management
3. Infrastructure costs for self-hosted solutions
4. Poor integration with our GitHub-centric workflow
5. Requiring users to create yet another account

We needed a solution that respects user privacy, leverages existing authentication, requires minimal infrastructure, and aligns with our open-source, developer-focused audience.

## Decision Drivers

- **Authentication**: Leverage existing identity providers, no separate account system
- **Privacy**: No tracking cookies, minimal data collection, user consent required
- **Security**: Robust authentication, spam prevention, moderation tools
- **Cost**: Minimal or zero infrastructure costs
- **Developer Audience**: GitHub-native workflow appeals to our technical readers
- **Moderation**: Built-in tools, manageable at scale
- **Performance**: Minimal impact on page load, lazy loading
- **Data Ownership**: Comments stored in platform we control
- **GDPR Compliance**: Transparent data practices, user rights respected

## Considered Options

### Option 1: Disqus

- Description: Popular third-party commenting platform with wide adoption
- Pros:
  - Mature platform with extensive features
  - Easy integration
  - Built-in moderation tools
  - Social sharing features
  - No backend infrastructure needed
- Cons:
  - ❌ Privacy concerns: tracking cookies, advertising, data mining
  - ❌ Ads on free tier
  - ❌ Not GDPR-friendly without paid tier
  - ❌ Requires separate Disqus account
  - ❌ Heavy JavaScript bundle impacts performance
  - ❌ Comments data owned by Disqus, not us

### Option 2: Commento

- Description: Privacy-focused, self-hosted commenting platform
- Pros:
  - Privacy-respecting, no tracking
  - Clean, lightweight interface
  - Open source
  - No ads
  - Full data ownership
- Cons:
  - ❌ Requires self-hosting infrastructure (cost, maintenance)
  - ❌ Separate authentication system needed
  - ❌ Ongoing maintenance burden
  - ❌ Database management required
  - ❌ Additional deployment complexity

### Option 3: Utterances

- Description: GitHub Issues-based commenting system
- Pros:
  - GitHub OAuth authentication
  - Free, no infrastructure costs
  - Privacy-friendly
  - GitHub-native workflow
  - Comments stored in our repository
- Cons:
  - ❌ Uses Issues instead of Discussions (less semantic fit)
  - ❌ Issues clutter the issue tracker
  - ❌ Less suitable for community discussions
  - ❌ Limited organization compared to Discussions

### Option 4: Giscus (Chosen)

- Description: GitHub Discussions-based commenting system using the GitHub Discussions API
- Pros:
  - ✅ GitHub OAuth authentication (secure, familiar to audience)
  - ✅ Free, zero infrastructure costs
  - ✅ Privacy-friendly: no cookies, no tracking, user consent via OAuth
  - ✅ Uses GitHub Discussions (semantic fit for blog comments)
  - ✅ Reactions, threading, nested replies
  - ✅ Comments stored in repository we control
  - ✅ Markdown support with syntax highlighting
  - ✅ Themeable (Gruvbox Dark theme matches site aesthetic)
  - ✅ Lazy loading support
  - ✅ Active development and community
  - ✅ Built-in moderation via GitHub permissions
- Cons:
  - Requires GitHub account (acceptable for technical audience)
  - Limited to GitHub ecosystem
  - Dependent on GitHub's infrastructure

## Decision Outcome

Chosen option: "Giscus (GitHub Discussions-based comments)"

Justification:

**Security & Authentication:**
- Leverages GitHub's robust OAuth 2.0 implementation
- No credential storage on our infrastructure
- Multi-factor authentication supported via GitHub
- GitHub handles all authentication security concerns
- Spam prevention via GitHub's abuse detection
- Moderation via GitHub repository permissions

**Privacy Approach:**
- No tracking cookies or analytics
- Explicit user consent required (GitHub OAuth login)
- Comments are public by design (transparent)
- Users retain full control over their GitHub data
- GDPR compliant through GitHub's data practices
- Users can edit or delete their own comments
- No third-party data sharing beyond GitHub

**Technical Excellence:**
- Zero infrastructure costs
- No database or backend to maintain
- Lazy loading prevents performance impact
- Component-based implementation in Astro
- Client-side script injection with event listeners
- Handles Astro view transitions correctly
- Themeable to match site design

**Community Benefits:**
- GitHub-native workflow appeals to developer audience
- Discussions are searchable on GitHub
- Notifications via GitHub's notification system
- Integrates with existing repository activity
- Builds community around the repository

The integration is implemented as a reusable Astro component (`src/components/Giscus.astro`) that:
1. Creates a container div for the Giscus widget
2. Dynamically loads the Giscus script client-side
3. Configures the widget with repository settings
4. Handles page load and view transition events
5. Lazy loads when scrolled into view

## Consequences

### Positive

- **Zero Cost**: No infrastructure or service fees
- **High Security**: GitHub's OAuth security model is industry-leading
- **Privacy-First**: No cookies, no tracking, explicit consent required
- **Low Maintenance**: GitHub handles all infrastructure and security
- **Developer-Friendly**: Appeals directly to our technical audience
- **Data Ownership**: Comments stored in our GitHub repository
- **Moderation Tools**: GitHub's built-in moderation and permissions
- **Performance**: Lazy loading, minimal JavaScript footprint
- **Flexibility**: Can migrate comments if needed (stored as GitHub Discussions)

### Negative

- **GitHub Dependency**: Requires GitHub account to comment
  - Mitigation: Acceptable for technical audience (most have GitHub accounts)
- **Ecosystem Lock-in**: Comments tied to GitHub platform
  - Mitigation: Can export data via GitHub API if migration needed
- **Rate Limits**: Subject to GitHub API rate limits
  - Mitigation: Lazy loading and caching reduce API calls

### Neutral

- Comments are public by design (no private discussions)
- Requires GitHub repository with Discussions enabled
- Users see GitHub UI for commenting (consistent with GitHub ecosystem)

## Implementation Details

**Repository Configuration:**
- Repository: `SecuringTheRealm/securing.quest`
- Discussions enabled with "General" category
- Mapping: pathname (each blog post URL maps to unique discussion)

**Security Configuration:**
- OAuth scope: public_repo (read/write to discussions)
- No elevated permissions required
- Users can only comment if logged into GitHub
- Repository maintainers have full moderation control

**Privacy Configuration:**
- No cookies set by Giscus
- No personal data collected beyond GitHub profile (user's choice to share)
- Reactions enabled (anonymous thumbs up/down)
- Metadata emission disabled (no tracking data sent)

**Technical Configuration:**
- Theme: `gruvbox_dark` (matches site aesthetic)
- Input position: top (easy access for commenting)
- Lazy loading: enabled (performance optimization)
- Cross-origin: anonymous (no credentials sent to Giscus CDN)

## References

- [Giscus Documentation](https://giscus.app/)
- [GitHub Discussions API](https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions)
- [GitHub OAuth Security](https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps)
- [Astro Client-Side Scripts](https://docs.astro.build/en/guides/client-side-scripts/)
