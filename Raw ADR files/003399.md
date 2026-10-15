# ADR-003: Preview Deployments

**Status:** Accepted  
**Date:** 2025-01-20  
**Authors:** Professor Doctor Julius Prompto (AI Assistant)

## Context

The QuantumPoly development team requires a streamlined review process that allows stakeholders to evaluate pull requests using live, deployed environments. Manual deployment for review purposes creates bottlenecks and inconsistencies in the QA process.

### Problems Addressed:
- **Review Friction**: Reviewers must manually build and run code locally
- **Environment Inconsistencies**: "Works on my machine" issues due to local environment differences
- **Design Review Complexity**: UI/UX changes are difficult to evaluate without live deployment
- **Stakeholder Access**: Non-technical stakeholders cannot easily review changes

## Decision

Implement **Vercel preview deployments** via GitHub Actions that automatically deploy every pull request to a unique preview URL.

### Implementation Details:
- Use Vercel's preview deployment feature integrated with GitHub Actions
- Deploy on every pull request targeting the `main` branch
- Post preview URLs directly to PR comments for easy access
- Include links to both the main application and Storybook static build
- Store deployment artifacts for debugging and rollback purposes

### Technical Components:
1. **GitHub Actions Workflow** (`.github/workflows/preview.yml`)
2. **Vercel CLI Integration** with environment secrets
3. **Automated PR Comments** with preview links
4. **Artifact Storage** for deployment debugging

## Consequences

### Positive:
- **Faster Review Cycles**: Reviewers can immediately access live versions
- **Improved Collaboration**: Design and UX teams can review without technical setup
- **Consistent Environments**: All reviews happen against the same deployment configuration
- **Enhanced QA**: Integration and user acceptance testing on realistic environments
- **Stakeholder Engagement**: Non-technical reviewers can provide meaningful feedback

### Negative:
- **Resource Usage**: Additional compute and storage costs for preview deployments
- **Dependency Risk**: Reliance on Vercel service availability
- **Secret Management**: Requires secure handling of Vercel deployment tokens

### Mitigations:
- Preview deployments have short retention periods to minimize costs
- Fallback to local development environments if Vercel is unavailable
- Proper secret rotation and access control for deployment credentials

## Implementation Requirements

### Repository Secrets:
```
VERCEL_TOKEN: Personal access token for Vercel CLI
VERCEL_ORG_ID: Organization identifier
VERCEL_PROJECT_ID: Project identifier
```

### Dependencies:
- Vercel CLI installed in CI environment
- GitHub Actions permissions for PR comments
- Node.js 20+ for consistent build environment

## Compliance and Security

- Preview URLs are publicly accessible but use unpredictable paths
- No sensitive data should be included in preview environments
- Deployment logs exclude sensitive environment variables
- Preview deployments automatically expire to limit exposure window

## Success Criteria

1. Every PR automatically generates a preview deployment
2. Preview URL is posted to PR comments within 5 minutes
3. Deployments are accessible and functional
4. Zero unauthorized access to production secrets
5. Cost remains within acceptable limits (monitored monthly)

## Related Decisions

- Links to [ADR-004: Lighthouse & A11y CI](./ADR-004-lighthouse-a11y.md)
- Integrates with existing CI/CD pipeline ([ADR-002](./ADR-002-integration-testing-strategy.md))
