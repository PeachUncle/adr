# ADR-015: Website Hosting Service

## Status

Accepted

## Context

The project requires a simple, cost-effective, and reliable hosting solution for
static web assets.

## Decision

We decided to use **GitHub Pages** as the hosting solution.

## Reasons

1. **Cost Efficiency**:
   - GitHub Pages is free for public repositories, eliminating hosting costs.

2. **Streamlined Workflow**:
   - Developers can push changes directly to a configured branch to trigger
     deployments, simplifying the release process.

3. **Security**:
   - Built-in HTTPS support without the need for additional configuration.

4. **Developer Familiarity**:
   - Team members are already familiar with GitHub, minimizing the learning
     curve.

5. **Scalability**:
   - While limited to static sites, GitHub Pages can handle a significant amount
     of traffic with its CDN-backed infrastructure.

## Consequences

1. **No Server-Side Capabilities**:
   - GitHub Pages only supports static content; any server-side logic must be
     handled via APIs hosted elsewhere.

2. **Repository Visibility**:
   - Free hosting is limited to public repositories unless using GitHub Pro or
     an organizational plan.

3. **Limited Storage and Bandwidth**:
   - There are soft limits on storage and bandwidth, but these are generally
     sufficient for most static sites.

4. **Custom Build Requirements**:
   - Non-Jekyll projects (e.g., React, Vue) require a pre-build step and custom
     CI/CD configuration using GitHub Actions.

## Alternatives Considered

### Azure Static Web Apps

- **Pros**: Built-in CI/CD and serverless API support.
- **Cons**: Requires additional configuration and is not entirely free beyond
  a certain usage limit.

### Netlify

- **Pros**: Powerful CI/CD and serverless functions.
- **Cons**: Pricing can escalate quickly with higher traffic.

### AWS S3 + CloudFront

- **Pros**: Highly scalable and customizable.
- **Cons**: Requires manual setup for CI/CD, SSL, and other configurations.
