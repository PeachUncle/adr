# ADR-0008: Authentication and Session Management Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-06
- **Feature:** 003-rag-chatbot
- **Context:** Chatbot must support both guest (anonymous) and authenticated users to balance low-friction onboarding with premium features (unlimited history, cross-device sync). Anonymous users need session persistence without signup barrier. Must incentivize authentication after demonstrating value. 90-day retention for anonymous vs unlimited for authenticated creates compliance requirement. Better Auth chosen for OAuth support without reinventing auth infrastructure.

## Decision

We will use a dual-mode authentication strategy with progressive engagement:

- **Auth Service**: Better Auth (self-hosted or cloud) with REST API integration
  - Providers: Email/password + OAuth (Google, GitHub)
  - Session Format: JWT in `better-auth.session_token` cookie
  - Validation: Middleware calls `GET /api/auth/session` with cookie headers
- **Guest Mode**: Immediate access without signup
  - Session ID: Browser-generated UUID stored in localStorage
  - Storage: Client-side localStorage (JSON array of messages)
  - Rate Limit: 20 messages/day tracked by session_token (prevent abuse)
  - Upgrade Prompt: After 5 messages with benefits messaging
- **Migration Flow**: localStorage → Postgres on authentication
  - Endpoint: `POST /api/chat/migrate` accepts localStorage JSON payload
  - Deduplication: Check existing messages by content hash (prevent double-send)
  - Continuity: Preserve conversation order with original timestamps
- **Retention Policy**: 90-day cleanup for anonymous, unlimited for authenticated
  - Background job: `DELETE FROM chat_sessions WHERE user_id IS NULL AND created_at < NOW() - INTERVAL '90 days'`
  - Cascade: Automatically deletes messages and feedback via foreign keys

## Consequences

### Positive

- Low-friction onboarding: Users try chatbot immediately (no signup barrier)
- Progressive engagement: Upgrade prompt after demonstrating value (5 messages)
- Better Auth handles OAuth complexity (Google/GitHub login) without custom implementation
- localStorage provides offline-first UX (works without network for guests)
- 90-day retention balances storage costs vs user experience
- Authentication unlocks premium features (clear value proposition for conversion)
- Session migration preserves conversation continuity (good UX on signup)

### Negative

- Dual storage strategy increases complexity (localStorage sync + database persistence)
- Better Auth adds external dependency (service downtime blocks authenticated access)
- Migration edge cases: partial failures, duplicate detection, race conditions
- localStorage quota limits (typically 5-10MB, ~500 messages max per browser)
- No Python SDK for Better Auth (must use REST API directly = more boilerplate)
- 90-day cleanup requires cron job (operational overhead, monitoring required)
- Anonymous rate limiting by session_token is gameable (new incognito window = new session)

## Alternatives Considered

**Alternative A: NextAuth.js (Unified Auth Service)**
- Pros: Mature ecosystem, excellent TypeScript support, many OAuth providers
- Cons: Requires Next.js backend (frontend-backend coupling), no Python integration
- Rejected: Backend is FastAPI (Python), NextAuth requires Node.js

**Alternative B: Auth0 (Managed Auth Service)**
- Pros: Enterprise-grade, extensive features, excellent documentation
- Cons: Expensive ($25/month for custom domain, 7000 users), overkill for hackathon
- Rejected: Cost prohibitive for free-tier hackathon project

**Alternative C: Supabase Auth (Postgres-Backed Auth)**
- Pros: Integrated with Postgres, generous free tier, PostgreSQL Row-Level Security (RLS)
- Cons: Vendor lock-in to Supabase, RLS complexity for multi-tenant, less flexible OAuth config
- Rejected: Want flexibility to use Neon for Postgres without Supabase coupling

**Alternative D: Custom JWT Auth (Build In-House)**
- Pros: Full control, no external dependencies, zero cost
- Cons: Reinventing auth is high-risk (security vulnerabilities), OAuth integration complex, no time for hackathon
- Rejected: Security risk + implementation time not justified

**Why Better Auth + Guest Mode Won**: Best balance of low-friction UX, OAuth support, and hackathon timeline. Guest mode maximizes trial conversions while Better Auth handles authentication complexity.

## References

- Feature Spec: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md) (FR-009 to FR-012, FR-022, Clarifications)
- Implementation Plan: [specs/003-rag-chatbot/plan.md](../../specs/003-rag-chatbot/plan.md) (Authentication Strategy section)
- Related ADRs: ADR-0007 (Data Storage - impacts session persistence)
