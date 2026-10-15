# Tech Stack Selection

**Status**: Decided
**Date**: 2024-11-23
**Decision**: Astro + Airtable Stack

## Context

We need to choose a tech stack for The Vibe Coders community website that balances:
- Speed of development
- Performance requirements (< 2s load time)
- Simplicity (KISS principle)
- Maintainability by small team

## Decision Drivers

1. **Easy to maintain** - Less code heavy, simple architecture
2. **Developer velocity** - Ship fast, iterate quickly
3. **Performance** - Fast load times, good SEO
4. **Minimal complexity** - Fewer dependencies, less to learn
5. **YAGNI compliance** - Not over-engineered
6. **Hosting simplicity** - One-click deploys

## Considered Options

### Option 1: Astro + Airtable (Selected ✅)
**Pros:**
- **Perfect for content sites** - Built for this use case
- **Minimal JavaScript by default** - Ships zero JS unless you add it
- **Less code heavy** - Simple mental model, easy to maintain
- **Great performance** - Static by default, fast load times
- **Island architecture** - Add interactivity only where needed
- **Airtable as backend** - No custom database code needed
- **Visual CMS** - Non-developers can manage content

**Cons:**
- Smaller ecosystem than React
- Less suited for highly interactive apps (not a problem for us)

### Option 2: Next.js + Vercel
**Pros:**
- Excellent DX with hot reload
- Built-in image optimization
- Huge ecosystem, lots of examples
- Great shadcn/ui support

**Cons:**
- **Too code heavy** - More complex than needed
- React overhead for mostly static site
- application Router adds complexity
- Requires more maintenance

### Option 3: Vanilla HTML/CSS/JS
**Pros:**
- Ultimate simplicity
- No build process

**Cons:**
- Slow development
- No component reuse
- Manual everything

## Decision

**Selected: Astro with Airtable Backend**

### Rationale
1. **Simplicity** - Less code heavy, easier to maintain long-term
2. **Perfect fit** - Astro is built for content sites like ours
3. **Minimal JS** - Ships zero JavaScript by default, add only where needed
4. **Airtable** - Visual database, no backend code, non-devs can manage
5. **Fast by default** - Static generation gives excellent performance
6. **YAGNI aligned** - Prevents over-engineering by design

### Implementation Plan

```bash
# Initial setup
npm create astro@latest the-vibe-coders -- --template minimal --typescript --tailwind
cd the-vibe-coders

# Add React for islands where needed
npx astro add react

# Install Airtable SDK
npm install airtable
```

### Stack Details

**Frontend:**
- Astro (Static site generator with islands)
- TypeScript (optional, lighter usage)
- Tailwind CSS (utility-first styling)
- React components (only for interactive islands)

**Backend/CMS:**
- Airtable (all content, forms, and data)
  - Posts table (organizer updates)
  - Applications table (organizer applications)
  - Organizers table (authentication mapping)

**Services:**
- Vercel or Netlify (hosting - both work great with Astro)
- Auth0 (Google + GitHub login for organizers)
- Luma Calendar (embedded widgets, no API needed)
- Cloudinary or Airtable attachments (images)

**Key Architecture Decisions:**
- Static build with ISR for Airtable data
- Protected routes using Auth0 for organizer uploads
- Embed Luma widgets directly (no API complexity)
- Use Airtable forms API for submissions

## Consequences

### Positive
- **Dramatically less code** - Simpler components, less boilerplate
- **Easier maintenance** - Less to understand, less to break
- **Faster by default** - Ships minimal JavaScript
- **Lower learning curve** - Astro is simpler than Next.js
- **Airtable simplicity** - No custom backend code at all
- **Cost effective** - Free tiers cover our needs

### Negative
- Smaller ecosystem than React/Next.js
- Less documentation/examples available
- Airtable has API rate limits (not an issue at our scale)

### Mitigations
- Use React islands where we need rich interactivity
- Airtable's limits are generous for our use case
- Astro's documentation are excellent and community is growing

## Notes

This decision aligns perfectly with our principles:
- **KISS**: Astro + Airtable is simpler than custom backend
- **YAGNI**: Can't over-engineer when the framework prevents it
- **"Less code heavy"**: Significantly less code than Next.js
- **"Easy to maintain"**: Fewer dependencies, clearer architecture

The stack actively prevents the temptation to over-build.