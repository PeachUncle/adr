# Architecture Decision Record: Media Manager Technology Stack

## Status

Proposed

## Date

2025-06-10

## Context

We need to build a media collection management system that allows users to:
- Track movie collections with metadata from TMDB
- Manage storage locations (bins) for physical media
- Search and filter their collection
- Secure access to their personal collection

Key constraints:
- System will be deployed in a homelab environment
- Integration with TMDB API is required
- Need for easy deployment and maintenance
- Learning opportunity for specific technologies

## Decision

We will implement the system using the following technology stack:

1. Frontend:
   - Svelte as the core framework
   - Skeleton UI toolkit for components and styling
   - Single-page application (SPA) architecture

2. Backend:
   - FastAPI (Python) for the REST API
   - Session-based authentication
   - OpenAPI/Swagger for API documentation
   - TMDB API integration for movie metadata

3. Database:
   - MongoDB for data storage
   - Collections for movies, bins, users, and sessions

4. Infrastructure:
   - Docker containers for all components
   - docker-compose for orchestration
   - Multi-container architecture (frontend, backend, database)

## Consequences

### Positive

- FastAPI provides excellent performance and automatic API documentation
- Svelte offers great performance and simple reactivity
- Skeleton UI accelerates frontend development with pre-built components
- MongoDB's flexible schema suits media metadata storage
- Docker ensures consistent deployment across environments
- Session-based auth provides simple, secure authentication

### Negative

- Learning curve for team members new to Svelte or FastAPI
- MongoDB might be overengineered for the initial simple data structure
- Session-based auth may limit future scaling (if needed)

### Neutral

- TMDB API integration adds external dependency
- Docker adds deployment complexity but improves reproducibility

## Alternatives Considered

### Frontend Alternatives

1. React + Tailwind CSS
   - Pros: Larger ecosystem, more resources
   - Cons: More complex, larger bundle size
   - Why not: Learning opportunity with Svelte preferred

2. Vue.js
   - Pros: Similar to Svelte, good documentation
   - Cons: Larger bundle size than Svelte
   - Why not: Svelte offers better performance and simpler syntax

### Backend Alternatives

1. Node.js + Express
   - Pros: Large ecosystem, JavaScript throughout
   - Cons: Less structured than FastAPI
   - Why not: Python preference and FastAPI's built-in features

2. Django
   - Pros: Batteries included, robust
   - Cons: Heavier than needed
   - Why not: FastAPI better suits API-first approach

### Authentication Alternatives

1. JWT-based auth
   - Pros: Stateless, scalable
   - Cons: More complex implementation
   - Why not: Session-based simpler for current needs

2. OAuth2
   - Pros: Standardized, third-party integration
   - Cons: Overkill for current requirements
   - Why not: Can be added later if needed

## Compliance

- Will follow OWASP security best practices
- API documentation will follow OpenAPI specification
- Docker best practices for container security

## Related Decisions

- Future ADR needed for backup strategy
- Future ADR needed if implementing OAuth2

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Svelte Documentation](https://svelte.dev/)
- [Skeleton Documentation](https://www.skeleton.dev/)
- [TMDB API Documentation](https://developers.themoviedb.org/3)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
