---
# === Metadata ===
template_type: "adr"
version: "1.0.0"
created: "2025-10-30"
last_updated: "2025-10-30"
status: "Accepted"
target_audience: ["AI Assistants", "Code Architects", "Development Team"]
description: "Initial tech stack selection for So Quotable MVP"

# === ADR Metadata ===
adr_number: "001"
title: "Initial Tech Stack Selection"
date: "2025-10-30"
deciders: ["Taylor (Project Owner)"]
tags: ["architecture", "tech-stack", "database", "infrastructure", "MVP"]
---

# ADR-001: Initial Tech Stack Selection

**Date**: 2025-10-30

**Status**: Accepted

**Deciders**: Taylor (Project Owner)

**Tags**: architecture, tech-stack, database, infrastructure, MVP

---

## Context

So Quotable is a web application for generating verified quote images. Users select a person and verified quote, then generate a shareable image with the quote overlaid on a photo of that person. The project is a passion project focused on learning modern web development patterns while solving a real problem: the difficulty of creating credible, verified quote images for online discussions.

### Key Requirements

- **Data Model**: Relational structure (people → quotes → images)
- **Core Features**: Search quotes/people, verify sources, multiple images per person, text overlay generation, shareable URLs
- **Scale**: Hobby project, <10k users initially
- **Developer**: Solo JavaScript developer, prefers minimal operational overhead
- **Hosting**: Frontend on Vercel (decided)
- **Goals**: Fast iteration, learning opportunity, production-quality UX

### Technical Considerations

1. **Backend Architecture**: Need database, authentication, file storage, and serverless functions
2. **Image Processing**: Text overlay on images (core feature)
3. **Image Storage**: Both curated person photos and user-generated quote images
4. **Search**: Full-text search across quotes and people names
5. **Developer Experience**: TypeScript preferred, minimal ops overhead

---

## Decision

We will use the following tech stack for the MVP:

### Frontend

- **Framework**: Next.js (App Router) with TypeScript
- **Hosting**: Vercel
- **Image Components**: `next-cloudinary` for optimized image delivery

### Backend

- **Database & Functions**: Convex
  - Reactive TypeScript-first database
  - Serverless functions (queries, mutations, actions)
  - Built-in file storage
  - Real-time capabilities

- **Authentication**: Convex Auth
  - Email/password + OAuth providers
  - Built on Auth.js
  - Free tier (no MAU limits initially)

### Image Storage & Processing

- **Platform**: Cloudinary (Free Tier: 25GB storage, 25GB bandwidth/month)

- **Base Images** (Person Photos):
  - Store curated person photos in Cloudinary
  - Multiple images per person (primary + alternates)
  - Source: Wikimedia Commons, public domain images
  - Manual curation (100-500 images for MVP)

- **Generated Images** (Quote Overlays):
  - Cloudinary URL transformations for text overlay
  - Stored in Cloudinary with unique shareable URLs
  - Auto-deletion after 30 days (imgflip-style ephemeral storage)
  - Metadata tracked in Convex database

### Quote Generation Approach

- **Client-Side Preview**: Canvas API for real-time editing
- **Server-Side Generation**: Cloudinary transformations for final output
- **Hybrid Workflow**: User edits in browser → generates final image via Cloudinary URL

### Data Model (MVP)

- **People**: Manually curated database
- **Quotes**: Pre-verified quotes with sources
- **Images**: Multiple images per person (stored in Cloudinary)
- **Generated Images**: User-created quote overlays (temporary storage)

---

## Consequences

### Positive Consequences

1. **Fast Development Velocity**
   - One `git push` deploys frontend + backend automatically
   - TypeScript end-to-end type safety (schema → functions → UI)
   - No Docker required for local development
   - Automatic preview environments (Vercel + Convex)

2. **Minimal Operational Overhead**
   - No database migrations to write (Convex handles schema evolution)
   - No infrastructure management (fully managed services)
   - Built-in authentication (no third-party auth service)
   - Automatic CDN delivery (Cloudinary + Vercel)

3. **Excellent Developer Experience**
   - TypeScript-first architecture
   - Instant hot reload in local development
   - Real-time reactive queries (Convex)
   - Simple mental model (functions are the API)

4. **Image Processing Capabilities**
   - Server-side text overlay without writing Canvas code
   - Automatic image optimization (WebP, compression)
   - Responsive images out of the box
   - Custom font support (upload fonts to Cloudinary)

5. **Cost-Effective for MVP**
   - Convex free tier: 1GB storage, unlimited functions
   - Cloudinary free tier: 25GB storage, 25GB bandwidth/month
   - Total cost: $0/month until significant growth
   - Predictable pricing ($25/month Convex + $0 Cloudinary if staying under free tier)

6. **Scalability Path**
   - Convex auto-scales horizontally
   - Cloudinary handles CDN scaling automatically
   - No performance tuning needed initially
   - Clear upgrade path when needed

### Negative Consequences

1. **Vendor Lock-in (Moderate-High)**
   - **Convex**: Proprietary query language and reactive system
     - Migration effort: 1-2 weeks (rewrite backend functions)
     - Data export available (JSON/SQL)
   - **Cloudinary**: Proprietary transformation URLs
     - Migration effort: Update URLs, rebuild overlay logic
     - Images are standard JPG/PNG (portable)
   - **Mitigation**: Keep business logic separate from platform-specific code

2. **Less Transferable Skills**
   - Convex knowledge is niche (not SQL/PostgreSQL)
   - TypeScript skills are highly transferable (positive)
   - No database administration experience gained
   - Limited to Convex's query capabilities (no raw SQL)

3. **Platform Limitations**
   - Convex is newer, less battle-tested at massive scale
   - No self-hosting option (must use Convex Cloud)
   - Cloudinary free tier limits (25GB bandwidth/month = ~50k image views)
   - Must trust platform reliability

4. **Image Storage Trade-offs**
   - Two separate services (Convex + Cloudinary)
   - More complex than single-platform solution
   - Cloudinary lock-in for image transformations
   - Cleanup job needed for expired generated images

### Neutral Consequences

1. **Learning Curve**
   - New platform to learn (Convex), but well-documented
   - Cloudinary transformations require understanding syntax
   - Modern React patterns (Server Components, App Router)

2. **Future Considerations**
   - User-submitted quotes (Phase 2) will need approval workflow
   - Paid user tiers could offer permanent image storage
   - May need to migrate to PostgreSQL if complex queries needed
   - Cloudinary paid tier ($89/month) if exceeding free tier

---

## Alternatives Considered

### Alternative 1: Supabase (PostgreSQL)

**Description**: Open-source Firebase alternative with PostgreSQL database, built-in auth, and storage.

**Pros**:

- Perfect fit for relational data model
- PostgreSQL skills are highly transferable
- Zero vendor lock-in (standard SQL database)
- Full-text search built-in
- SQL migrations (version-controlled)
- Can self-host if needed

**Cons**:

- Requires Docker for local development
- More operational overhead (migrations, indexes, RLS policies)
- Learning curve for PostgreSQL concepts
- No built-in image transformations (would need Cloudinary anyway)
- Manual joins and query optimization

**Why not chosen**:
Higher operational overhead for solo developer. While PostgreSQL is more portable and offers valuable learning, the need for manual migrations, Docker setup, and database tuning adds complexity that slows MVP development. Convex's TypeScript-first approach and zero-config local development better align with "fast iteration" and "minimal ops" goals. If complex relational queries become necessary later, migration path exists.

### Alternative 2: Firebase (Firestore + Cloud Functions)

**Description**: Google's mature BaaS platform with NoSQL database and comprehensive ecosystem.

**Pros**:

- Mature platform with extensive documentation
- Scales automatically on Google infrastructure
- Real-time updates built-in
- Strong mobile app support
- Large community and ecosystem

**Cons**:

- **Poor fit for relational data** - requires denormalization
- No built-in full-text search (would need Algolia - extra cost/complexity)
- Expensive read/write pricing model (costs grow with usage)
- High vendor lock-in (proprietary Firestore format)
- Cloud Functions cold start issues (500ms-2s delays)
- Manual migration scripts (no versioning)
- Security rules in custom language (learning curve)

**Why not chosen**:
Fundamentally wrong architecture for relational data. The people → quotes → images relationship would require data denormalization, leading to update anomalies and increased complexity. Lack of full-text search would force integration of Algolia (another service to manage). The pay-per-read pricing model could become expensive with search-heavy usage. Cold start issues with Cloud Functions would degrade user experience.

### Alternative 3: Convex Storage Only (No Cloudinary)

**Description**: Use Convex's built-in file storage for both base and generated images.

**Pros**:

- Everything in one platform (simpler mental model)
- Lower vendor lock-in (only Convex)
- No API keys to manage for second service
- Cheaper at scale ($25/month vs $89/month for Cloudinary paid)

**Cons**:

- No image transformations (text overlay requires Canvas API)
- No automatic optimization (manual WebP conversion needed)
- No responsive images out of the box
- Must build text overlay generation from scratch
- Pre-optimize all images before upload
- Shareable URLs not optimized for social media

**Why not chosen**:
Missing critical feature: server-side text overlay. Building Canvas API-based overlay generation is complex and time-consuming. Cloudinary's transformation URLs generate quote images via simple URL syntax, eliminating 2-3 weeks of Canvas development work. Automatic image optimization (WebP, compression) provides better user experience for free. Cloudinary's 25GB free tier is sufficient for MVP and hobby scale.

---

## Implementation Notes

### Initial Setup Checklist

1. **Convex Setup**

   ```bash
   npm install convex
   npx convex dev
   # Creates project, starts local backend
   ```

2. **Cloudinary Setup**
   - Sign up for free tier
   - Get Cloud Name, API Key, API Secret
   - Add environment variables to Vercel
   - Configure upload presets

3. **Next.js Integration**

   ```bash
   npm install next-cloudinary
   # Configure in next.config.js
   ```

4. **Schema Definition**

   ```typescript
   // convex/schema.ts
   (people, quotes, images(cloudinaryId), generatedImages);
   ```

5. **Authentication Setup**
   ```bash
   npm install @convex-dev/auth
   # Configure providers (email, Google, GitHub)
   ```

### Development Workflow

```bash
# Terminal 1: Convex backend
npx convex dev

# Terminal 2: Next.js frontend
npm run dev

# Deploy to production
git push origin main
# Vercel builds Next.js automatically
# Convex deploys backend automatically
```

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_CONVEX_URL=https://[project].convex.cloud
NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## Links

- [Convex Documentation](https://docs.convex.dev)
- [Cloudinary Documentation](https://cloudinary.com/documentation)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Convex Auth](https://labs.convex.dev/auth)
- [next-cloudinary](https://next.cloudinary.dev)

---

## Notes

### Future Enhancements (Post-MVP)

1. **User-Submitted Quotes**
   - Admin approval workflow
   - Community flagging system
   - Source verification helpers

2. **Paid User Tier**
   - Permanent image storage (no 30-day deletion)
   - Higher resolution exports
   - Custom font uploads
   - Priority support

3. **Advanced Features**
   - Image cropping/editing UI
   - Multiple font styles
   - Text positioning controls
   - Quote collections/favorites
   - Social sharing optimizations

### Migration Considerations

If the project outgrows this stack:

- **Convex → PostgreSQL**: Export data to SQL, rewrite queries
- **Cloudinary → Self-hosted**: Download images, implement CDN
- **Both → AWS**: S3 + Lambda + RDS (full control, more ops work)

Current stack is sufficient for 10k-100k users. Re-evaluate at scale.

---

## Revision History

| Date       | Author | Description                               |
| ---------- | ------ | ----------------------------------------- |
| 2025-10-30 | Taylor | Initial version - MVP tech stack decision |
