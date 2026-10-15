# ADR-0001: Static Site Deployment on GitHub Pages

> **Scope**: Deployment Strategy and Infrastructure

- **Status:** Superseded (by ADR-0004)
- **Date:** 2025-12-04
- **Feature:** 001-platform-foundation-setup
- **Context:** We are initializing the "Physical AI & Humanoid Robotics Textbook" platform. We need a hosting solution that is cost-effective (ideally free), reliable, supports static site generation, and integrates tightly with our source control on GitHub. The site needs to be publicly accessible.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? Yes.
     2) Alternatives: Multiple viable options considered with tradeoffs? Yes.
     3) Scope: Cross-cutting concern (not an isolated detail)? Yes.
-->

## Decision

We will use **GitHub Pages** served via **GitHub Actions** as the deployment platform.

- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions (`.github/workflows/deploy.yml`)
- **Asset Source**: Static build artifacts from Docusaurus

## Consequences

### Positive

- **Zero Cost**: Free hosting for public repositories.
- **Integrated Security**: Tightly integrated with the repository's permission model. No external API keys or secrets to manage for basic deployment (uses `GITHUB_TOKEN`).
- **Simplicity**: Keeps the "ops" stack self-contained within the GitHub ecosystem.
- **Automatic HTTPS**: GitHub Pages provides SSL by default.

### Negative

- **Static Only**: No server-side rendering or backend logic (Serverless functions would require additional setup or services).
- **Build Minutes**: Consumes GitHub Actions runner minutes (though the free tier is generous).
- **Latency**: Global CDN performance is good but may be less tunable than a custom CloudFront setup.

## Alternatives Considered

### External Hosting (Vercel / Netlify)
- **Pros**: Excellent developer experience, Preview Deployments for PRs, edge functions.
- **Cons**: Adds an external dependency/service to manage.
- **Rationale**: Rejected to minimize external dependencies for the foundational setup. Can be reconsidered if dynamic features are needed.

### Cloud Infrastructure (AWS S3 + CloudFront)
- **Pros**: Industry standard, infinite scale, granular control.
- **Cons**: High complexity to set up (Terraform/CDK), potential costs, overkill for a textbook site.
- **Rationale**: Rejected due to complexity and maintenance overhead.

## References

- Feature Spec: specs/001-platform-foundation-setup/spec.md
- Implementation Plan: specs/001-platform-foundation-setup/plan.md