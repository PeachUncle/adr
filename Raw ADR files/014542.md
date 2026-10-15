# 001. Headless CMS Selection

**Date**: 2025-12-17  
**Status**: Proposed  
**Deciders**: Development Team, Business Owner  
**Technical Story**: Related to [tech-stack.md - Dynamic Content](../tech-stack.md#1-dynamic-content-rendering-system)

---

## Context and Problem Statement

Currently, the website content (About, Services, Testimonials) is hardcoded directly in the HTML. While JSON files exist for this content, they are not being utilized. This creates several problems:

1. **Developer dependency**: Content changes require modifying HTML files and redeploying the site
2. **Slow update cycle**: Simple content updates (e.g., adding a testimonial) take 30+ minutes
3. **Error-prone**: Non-technical users can't safely edit content without risking breaking the site
4. **Scalability**: As content grows (more services, testimonials, blog posts), managing it in HTML becomes unwieldy

We need to decide whether to implement a headless CMS or stick with a simpler JSON-based approach for content management.

---

## Decision Drivers

- **Budget**: Monthly cost must be justified by time savings and business value
- **Ease of use**: Business owner (non-technical) must be able to edit content independently
- **Developer experience**: Integration should be straightforward with our vanilla JS stack
- **Content complexity**: Current needs are simple (text, images), but may grow to include rich formatting, media libraries
- **Time to implement**: Should provide value within 2-3 weeks of implementation
- **Performance**: Should not significantly slow down site load times
- **Vendor lock-in risk**: Ability to migrate content if needed

---

## Considered Options

1. **Keep JSON files, build vanilla JS renderer**
2. **Sanity.io (Headless CMS)**
3. **Contentful (Headless CMS)**
4. **Markdown + Git-based CMS (e.g., NetlifyCMS, TinaCMS)**

---

## Decision Outcome

**Chosen option**: **"Sanity.io (Headless CMS)"** (Proposed - pending final approval)

**Rationale**: While the JSON approach is simpler initially, Sanity provides the best balance of ease-of-use for non-technical editors, developer experience, and long-term scalability. The free tier is generous enough for our needs, and the investment in setup time (2-3 weeks) will pay off quickly as content updates become frequent and complex.

### Consequences

#### Positive (Good) ✅

- **Non-technical editing**: Business owner can add testimonials, update services without developer help
- **Media management**: Built-in image CDN with automatic optimization (WebP, responsive sizes)
- **Content versioning**: Drafts, publishing workflow, rollback capability
- **Structured content**: Validation ensures content quality (e.g., testimonials must have author + text)
- **Future-proof**: Can easily add blog, student resources, FAQs as structured content
- **Great DX**: GROQ query language is powerful yet intuitive; real-time preview in studio
- **No backend needed**: Sanity hosts the content, we just query it via API

#### Negative (Bad) ⚠️

- **Learning curve**: Team must learn Sanity schema design and GROQ queries (~1 week)
- **Vendor dependency**: Tied to Sanity's platform (though content export is possible via API)
- **Build complexity**: Adds a build step (fetch from Sanity API during build or at runtime)
- **Potential cost**: Free tier covers current needs, but scaling may require paid plan ($99-199/mo)
- **Overkill for now**: Current content is simple; might not need full CMS power immediately

#### Neutral (Trade-offs) ⚖️

- **Implementation time**: 2-3 weeks vs. 1 week for vanilla JS renderer
- **Performance**: API calls add latency, but can be mitigated with caching and static generation
- **Hosted studio**: Studio is hosted by Sanity (convenient) but requires internet for editing

---

## Detailed Analysis of Options

### Option 1: Keep JSON Files, Build Vanilla JS Renderer

**Description**: Implement JavaScript functions that read existing JSON files (`about.json`, `services.json`, `testimonials.json`) and dynamically render them into the DOM at page load.

**Pros**:
- ✅ **Simplest implementation**: No external dependencies, ~1 week of work
- ✅ **Zero cost**: No monthly fees
- ✅ **Full control**: No vendor lock-in
- ✅ **Performance**: No API calls, content is bundled with site
- ✅ **Works with current stack**: Vanilla JS, no new tooling

**Cons**:
- ❌ **Still requires git/deploy**: Editing JSON files means git commits and Netlify rebuilds
- ❌ **No user-friendly editor**: Business owner must edit raw JSON (error-prone)
- ❌ **No media management**: Images still managed manually
- ❌ **No validation**: Easy to break JSON syntax or structure
- ❌ **No versioning**: No drafts or rollback without git knowledge
- ❌ **Limited scalability**: Adding blog or complex content requires building more infrastructure

**Estimated Effort**: 1 week  
**Technical Complexity**: Low  
**Ongoing Maintenance**: Low (but frequent developer involvement for content changes)

---

### Option 2: Sanity.io (Headless CMS)

**Description**: Integrate Sanity as a headless CMS for all content. Content editors use Sanity Studio (a React-based admin interface) to manage content, which is then fetched via API at build time or runtime.

**Pros**:
- ✅ **User-friendly editor**: Beautiful, intuitive UI for non-technical users
- ✅ **Structured content**: Define schemas (e.g., testimonial has author, text, rating)
- ✅ **Real-time collaboration**: Multiple editors can work simultaneously
- ✅ **Built-in image CDN**: Automatic image optimization, responsive images
- ✅ **Powerful queries**: GROQ language is flexible for filtering, sorting, joining content
- ✅ **Excellent documentation**: Large community, great DX
- ✅ **Free tier**: 100K API requests/mo, 10GB bandwidth, 3 users (sufficient for years)
- ✅ **TypeScript support**: Generate types from schemas

**Cons**:
- ❌ **Learning curve**: GROQ, schema design, studio customization (~1 week to learn)
- ❌ **Vendor lock-in**: Tied to Sanity ecosystem (though export is possible)
- ❌ **Build complexity**: Need to fetch content at build time or implement caching for runtime
- ❌ **Free tier limits**: May eventually need paid plan if traffic grows significantly
- ❌ **Requires backend logic**: SSG (Static Site Generation) or SSR (Server-Side Rendering) for best performance

**Estimated Effort**: 2-3 weeks (schema design, migration, integration, training)  
**Technical Complexity**: Medium  
**Ongoing Maintenance**: Low (Sanity handles infrastructure)

**Pricing**:
- Free: 100K requests/mo, 10GB bandwidth, 3 users
- Growth: $99/mo for 1M requests, 100GB, 10 users
- Enterprise: Custom pricing

---

### Option 3: Contentful (Headless CMS)

**Description**: Similar to Sanity, Contentful is a headless CMS with a visual editor for non-technical users. Content is fetched via API.

**Pros**:
- ✅ **User-friendly**: Clean UI, easy for non-technical editors
- ✅ **Structured content**: Define content models with validation
- ✅ **Media library**: Built-in asset management
- ✅ **GraphQL API**: Alternative to REST for more efficient queries
- ✅ **Established platform**: Used by Fortune 500 companies, highly reliable

**Cons**:
- ❌ **More expensive**: Free tier is more restrictive (25K records, 10 users, but limited API calls)
- ❌ **Less developer-friendly**: UI is more enterprise-focused, less modern than Sanity
- ❌ **Slower innovation**: Updates/features roll out slower than Sanity
- ❌ **Query language**: Less flexible than GROQ (relies on REST or GraphQL)

**Estimated Effort**: 2-3 weeks (similar to Sanity)  
**Technical Complexity**: Medium  
**Ongoing Maintenance**: Low

**Pricing**:
- Free: 25K records, 50 roles, 10 users (but limited API calls)
- Team: $489/mo (significant jump from free)

---

### Option 4: Markdown + Git-Based CMS (NetlifyCMS, TinaCMS)

**Description**: Content stored as Markdown files in the git repo, edited via a web-based UI that commits changes back to GitHub.

**Pros**:
- ✅ **No vendor lock-in**: Content lives in your repo
- ✅ **Free**: No monthly costs
- ✅ **Version control**: Native git history
- ✅ **Simple**: Markdown is human-readable and portable

**Cons**:
- ❌ **Limited structure**: Markdown is less structured than CMS schemas
- ❌ **No media CDN**: Images stored in repo (increases repo size)
- ❌ **Slower editing experience**: Not as polished as Sanity/Contentful
- ❌ **Git knowledge helpful**: Editors benefit from understanding commits, branches
- ❌ **Build required**: Still triggers Netlify rebuild on every change

**Estimated Effort**: 1-2 weeks  
**Technical Complexity**: Medium  
**Ongoing Maintenance**: Medium (self-hosted UI, potential git conflicts)

---

## More Information

### Related Decisions
- Related to [tech-stack.md](../tech-stack.md#1-dynamic-content-rendering-system)
- May influence [ADR-003: Student Portal Architecture](003-student-portal-architecture.md) (shared content for student resources)

### Research & References
- [Sanity.io Documentation](https://www.sanity.io/docs)
- [Sanity Pricing](https://www.sanity.io/pricing)
- [GROQ Query Language](https://www.sanity.io/docs/groq)
- [Comparison: Sanity vs Contentful](https://www.sanity.io/contentful-vs-sanity)
- [Case Study: Migration from hardcoded to Sanity](https://www.sanity.io/blog/example)

### Validation Plan
If we choose Sanity:
- **Week 1-2**: Build proof-of-concept with one content type (testimonials)
- **Success criteria**: Business owner can add/edit testimonials without help
- **Week 3**: Migrate all content (about, services)
- **Month 2**: Track content update frequency (goal: >5 updates/month)
- **Month 3**: Measure editor satisfaction (goal: 4/5 rating)
- **Review date**: Q2 2026 - Reassess if free tier is sufficient or if we need to upgrade

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-12-17 | Initial proposal | Development Team |
| TBD | Decision pending team discussion | - |
