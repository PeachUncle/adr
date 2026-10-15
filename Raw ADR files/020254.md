# 3. Hosting Provider and Deployment Architecture

Date: 2025-06-15

## Status

Accepted

## Context

We need to select both a deployment architecture and hosting provider for our React / TypeScript application. The solution should align with our project priorities of minimizing development effort while providing learning opportunities. For data protection and other political reasons, I prefer European ownership of the hosting provider, and it needs to be cost-effective for a hobby project.

Two primary deployment architectures are available:
1. **Serverless platforms** (optimized for React frameworks)
2. **Docker containers** (providing dev/prod environment parity)

## Decision

We will use:
- **Docker containers** as our architecture
- **Koyeb** as our hosting provider

Koyeb's company HQ is in Paris (France) but we will use their Frankfurt (Germany) region.

### Deployment Architecture Decision

**Docker containers** were chosen over serverless functions for:
- Perfect development/production environment parity for easier debugging
- Provider portability and reduced vendor lock-in
- Educational value in learning containerization skills
- Compatibility with European hosting providers

### Hosting Provider Alternatives Considered for Docker Containers

- **Render** - Rejected due to Canadian ownership, though offers superior developer experience
- **Railway** - Rejected due to US ownership, more complex setup, and higher baseline costs
- **Scaleway** - Rejected despite French ownership due to complex GitHub Actions + Container Registry setup requirements
- **Fly.io** - Rejected due to Canadian ownership and additional complexity requiring flyctl and manual GitHub Actions configuration

### Hosting Providers Considered for Serverless Platforms

- **Vercel**
- **Netlify**

Both offer excellent React framework support but don't align with our Docker container decision or geographic preferences.

### Key Factors

- Serverless container scaling with pay-per-use pricing
- Developer experience and setup complexity
- Geographic preference for European providers
- Learning opportunities for best practices

## Consequences

**What becomes easier:**
- Perfect development/production environment consistency
- Learning transferable Docker skills
- Provider portability
- European data sovereignty and provider ownership

**What becomes more difficult:**
- Container layers complicate local debugging and development workflow
- Less React-specific optimization of static assets compared to Vercel or Netlify

**Risks:**
- Dependency on Koyeb's platform stability and pricing

### Notes

Koyeb is hosted on bare metal from several different providers and designed so that the bare metal providers have no access to data. This gives them redundancy and independence from any one provider.
