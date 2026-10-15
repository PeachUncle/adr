# ADR-001: Stack Selection

## Status

Accepted

## Date

16-12-2025

## Context

Alembic requires a full-stack architecture capable of:
- Server-side rendering for SEO (landing pages)
- Interactive client-side UI (card animations, chat)
- Async API for LLM integration
- User authentication and data persistence
- Payment processing

The developer is learning while building, so the stack should:
- Have excellent tooling and documentation
- Be job-market relevant
- Support AI-assisted development (Cursor, v0.dev)
- Allow for rapid iteration

## Decision

We will use the following stack:

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Next.js 15 | Best AI tooling support, SSR/SSG, job relevance |
| **UI Components** | shadcn/ui | Accessible, customizable, AI-friendly |
| **Styling** | Tailwind CSS | Utility-first, fast iteration |
| **Backend** | FastAPI | Python async, auto-docs, type safety |
| **Database** | Supabase (PostgreSQL) | All-in-one: DB, Auth, Storage, RLS |
| **Hosting (FE)** | Vercel | Zero-config Next.js deployment |
| **Hosting (BE)** | Railway | Simple Docker deployment |

## Alternatives Considered

### Frontend

**SvelteKit**
- Pros: Simpler mental model, faster to learn, excellent performance
- Cons: Smaller ecosystem, less job relevance, fewer AI tools
- Decision: Rejected due to ecosystem and career considerations

**Astro**
- Pros: Content-focused, great SSG, fast
- Cons: Less suited for interactive apps, smaller ecosystem
- Decision: Rejected for interactivity requirements

### Backend

**Next.js API Routes**
- Pros: Single deployment, simpler architecture
- Cons: Vercel-only, limited Python ML ecosystem, less flexible
- Decision: Rejected for Python ecosystem access and flexibility

**Django**
- Pros: Battle-tested, comprehensive, great ORM
- Cons: Heavier, synchronous by default, slower for LLM calls
- Decision: Rejected for async requirements

### Database

**PlanetScale**
- Pros: Infinite scaling, branching, MySQL compatible
- Cons: No built-in auth, no storage, foreign key limitations
- Decision: Rejected for missing auth/storage

**Neon**
- Pros: Serverless PostgreSQL, branching, scale-to-zero
- Cons: No built-in auth or storage
- Decision: Rejected for missing auth/storage

## Consequences

### Positive

1. **AI Tooling**: v0.dev generates shadcn/ui components directly
2. **Career Growth**: Next.js and FastAPI are highly marketable skills
3. **Rapid Development**: Supabase provides auth/storage without custom code
4. **Type Safety**: TypeScript + Pydantic catch errors early
5. **Documentation**: Both frameworks have excellent docs
6. **Community**: Large communities for troubleshooting

### Negative

1. **Two Languages**: TypeScript (frontend) + Python (backend) increases complexity
2. **Separate Deployments**: Frontend and backend deploy independently
3. **CORS**: Cross-origin requests require configuration
4. **Learning Curve**: Next.js App Router has a steeper learning curve
5. **Cost**: Two hosting platforms (though both have free tiers)

### Neutral

1. **Vendor Lock-in**: Moderate lock-in to Vercel (Next.js) and Supabase
2. **Migration Path**: Moving away from Supabase Auth would require effort

