# ADR-0004: Deployment Strategy Migration to Vercel

> **Scope**: Deployment Infrastructure

- **Status:** Accepted
- **Date:** 2025-12-04
- **Feature:** 001-platform-foundation-setup
- **Supersedes:** ADR-0001 (Static Site Deployment on GitHub Pages)
- **Context:** 
  The project repository is currently **Private**. GitHub Pages only offers free hosting for **Public** repositories. The user wishes to keep the repository code private while still deploying the documentation site publicly (or privately). GitHub Pages for private repositories requires a paid GitHub Pro/Enterprise plan. Vercel offers free hosting for hobby projects connected to private GitHub repositories.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? Yes.
     2) Alternatives: Multiple viable options considered with tradeoffs? Yes.
     3) Scope: Cross-cutting concern (not an isolated detail)? Yes.
-->

## Decision

We will migrate the deployment strategy from **GitHub Pages** to **Vercel**.

- **Hosting**: Vercel
- **CI/CD**: Vercel Git Integration (Automatic deploys on push)
- **Configuration**: Project root set to `frontend/` in Vercel settings.

## Consequences

### Positive

- **Cost**: Free hosting for private repositories (Hobby tier).
- **Ease of Use**: Zero-config CI/CD. No GitHub Actions workflow file needed in the repo.
- **Features**: Automatic Preview Deployments for every Pull Request (Deploy Previews), which significantly improves the review process.
- **Performance**: Vercel's Edge Network is highly optimized for frontend frameworks like Docusaurus.

### Negative

- **Vendor Lock-in**: Moves hosting outside of the GitHub ecosystem, adding a second service to manage.
- **URL Change**: The default URL structure changes from `username.github.io/repo` to `project-name.vercel.app`.

## Alternatives Considered

### Make Repo Public (GitHub Pages)
- **Pros**: Keeps everything in GitHub, free Pages.
- **Cons**: Exposes source code, which the user explicitly declined.
- **Rationale**: Rejected based on user constraint to keep code private.

### GitHub Pro (Paid)
- **Pros**: Private repo + GitHub Pages.
- **Cons**: Monthly cost ($4/mo).
- **Rationale**: Rejected as unnecessary cost when free alternatives exist.

## References

- Feature Spec: specs/001-platform-foundation-setup/spec.md
- Superseded ADR: history/adr/0001-static-site-deployment-on-github-pages.md
