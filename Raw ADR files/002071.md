# ADR 0002: Authentication Architecture for Docusaurus-Based Physical AI Book

## Status
Accepted

## Date
2025-12-18

## Context
The Physical AI Book platform requires user authentication with profile collection for personalization. The system consists of a Docusaurus frontend with static hosting requirements and a FastAPI backend. We need to select an authentication approach that works with static hosting, integrates with existing architecture, and provides secure user management.

Key constraints include:
- Static hosting compatibility (GitHub Pages)
- Integration with existing Docusaurus architecture
- Need for profile data collection (software/hardware experience)
- Security requirements for user data

## Decision
We will use better-auth with server-side session management and cookie-based authentication. The architecture will be:

- Frontend: Docusaurus React components using better-auth's React hooks
- Backend: FastAPI integration with better-auth's API endpoints
- Session management: Server-side sessions with HTTP-only cookies
- Database: Neon Postgres with better-auth's database adapter
- Profile data: Separate user_profiles table linked to users

## Alternatives Considered
- JWT tokens with localStorage: Rejected due to XSS vulnerabilities and security concerns with static hosting
- Custom authentication implementation: Rejected due to complexity and maintenance overhead
- Third-party authentication providers only: Rejected as we need custom profile data collection
- Client-side only authentication: Rejected due to security limitations with static hosting

## Consequences
### Positive
- Secure session management with HTTP-only cookies
- Good integration with React/Docusaurus components
- Proper server-side validation and security
- Support for custom profile data collection
- Works with static hosting requirements

### Negative
- Requires backend API endpoints for authentication
- More complex than client-side solutions
- Additional dependency on better-auth
- Requires proper CORS configuration

## References
- specs/4-auth-profiling-integration/plan.md
- specs/4-auth-profiling-integration/research.md
- specs/4-auth-profiling-integration/data-model.md