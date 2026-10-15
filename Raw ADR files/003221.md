# ADR-033: Choice of Netlify Environment Deployment Strategy

## Status

Accepted

## Context

The PlumbingPOC project requires separate environments for development, testing, and production to ensure safe deployment and testing of changes. The existing production site is already set up on Netlify connected to the main branch. We need to decide how to handle deployments for dev and test branches, weighing the options of adding branch deploys to the existing site versus creating separate sites for each environment.

## Decision

We will create separate Netlify sites for each environment:
- Production: Connected to main branch (existing site)
- Test: Connected to test branch (new site)
- Dev: Connected to dev branch (new site)

This approach provides better isolation between environments, allows for separate domains/subdomains, and enables environment-specific configurations (e.g., different environment variables).

## Consequences

- **Positive:**
  - Clear separation of concerns: Dev, test, and prod environments are completely isolated
  - Easier testing and debugging: Changes in dev/test don't risk affecting production
  - Flexible configuration: Each site can have its own build settings, environment variables, and domains
  - Better CI/CD integration: GitHub Actions can deploy to specific sites based on branch

- **Negative:**
  - Additional setup complexity: Requires creating and managing multiple Netlify sites
  - Potential cost: Multiple sites may exceed free tier limits (though Netlify's free plan allows 1 site per account, additional sites require paid plans)
  - More secrets to manage: Each site needs its own Site ID and potentially separate auth tokens

- **Risks:**
  - None significant, as the existing production site remains untouched during setup
  - If free tier limitations are hit, we can consolidate or upgrade as needed

## Alternatives Considered

- **Branch deploys on single site:** Add dev and test branches to the existing production site. This is simpler but risks mixing environments and could temporarily affect the live site with untested changes.

## References

- Task 0055: GitHub Branches and Pipeline Setup
- Netlify Documentation: Branch Deploys vs. Multiple Sites
