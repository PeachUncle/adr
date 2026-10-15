# ADR 003: Affected-Only CI/CD with Conditional Render Webhooks

**Status:** Accepted  
**Date:** 2025-01-18  
**Deciders:** Jeff Crosley (Architect)

## Context

The JeffApp monorepo contains multiple independently deployable applications (`api-gateway`, `nav-shell`, `component-showcase`) and shared libraries. To optimize CI/CD pipeline efficiency and reduce unnecessary deployments, we need:

- Fast feedback on PRs (test only what changed)
- Targeted production deployments (deploy only affected apps)
- Clear separation between build/test and deployment phases
- Cost optimization (minimize redundant builds and deploys on Render)

### Requirements

- Detect which projects are affected by changes
- Run lint/test/build only for affected projects
- Trigger Render deployments conditionally per app
- Skip deploys on PRs (only deploy from `main`)
- Handle monorepo dependencies correctly

## Decision

Use **Nx affected detection** with **conditional GitHub Actions jobs** triggering **Render deploy webhooks** only for changed applications.

### Pipeline Architecture

```yaml
# .github/workflows/main.yml

1. affected-detection
   ↓
   - Run: npx nx show projects --affected
   - Output: JSON list of affected projects

2. build-and-test (runs on every push)
   ↓
   - Run: npx nx affected --target=lint,test,build
   - Uses: Nx caching for unchanged projects

3. deploy_* (conditional, only on main)
   ↓
   - If: contains(affected-projects, 'api-gateway')
   - Run: curl Render webhook for api-gateway

   - If: contains(affected-projects, 'nav-shell')
   - Run: curl Render webhook for nav-shell

   - If: contains(affected-projects, 'component-showcase')
   - Run: curl Render webhook for component-showcase
```

### Implementation Details

**Affected Detection:**

```yaml
- name: Get affected projects
  id: affected
  run: |
   AFFECTED=$(npx nx show projects --affected --base=origin/main)
   echo "projects=$AFFECTED" >> $GITHUB_OUTPUT
```

**Conditional Deploy:**

```yaml
deploy_nav_shell:
 needs: [affected-detection, build-and-test]
 if: |
  github.ref == 'refs/heads/main' &&
  contains(needs.affected-detection.outputs.projects, 'nav-shell')
 steps:
  - name: Trigger Render Deploy
    run: curl -X POST ${{ secrets.RENDER_SHELL_DEPLOY_HOOK }}
```

**Render Service Configuration (Dashboard):**

- Auto-Deploy: **OFF** (we control via webhooks)
- Branch: `main`
- Build/Start Commands: Service-specific (see ADR 001, 002)

## Consequences

### Positive

- **Faster CI:** Test suite runs in ~2-5 min instead of ~10-15 min (when only one app changes)
- **Targeted deploys:** Showcase update doesn't redeploy gateway; gateway update doesn't redeploy shell
- **Cost reduction:** Fewer Render build minutes consumed (pay only for affected services)
- **Clear separation:** GitHub Actions orchestrates; Render focuses on hosting
- **PR safety:** No production deploys from feature branches

### Negative

- **Complexity:** More sophisticated workflow logic than "always build everything"
- **Dependency tracking:** Must ensure Nx dependency graph is accurate or risk missed deploys
- **Debugging:** Conditional logic can be harder to troubleshoot than linear pipelines
- **Webhook management:** Three separate secrets to maintain (one per service)

### Mitigation

- Regularly verify Nx graph accuracy: `npx nx graph`
- Add workflow logging for affected detection results
- Document Render webhook setup in `docs/guides/render-deployment-guide.md`
- Monitor for false negatives (changed code not triggering deploy)

## Alternatives Considered

### Always-Deploy Strategy

```yaml
# Rejected: deploy all services on every push
deploy:
 steps:
  - name: Deploy all
    run: |
     curl ${{ secrets.RENDER_API_DEPLOY_HOOK }}
     curl ${{ secrets.RENDER_SHELL_DEPLOY_HOOK }}
     curl ${{ secrets.RENDER_SHOWCASE_DEPLOY_HOOK }}
```

**Rejected because:**

- Wasteful (deploys unchanged services)
- Slower (unnecessary Render build queue time)
- Higher cost (Render charges per build minute)
- No benefit over affected-only approach

### Render Auto-Deploy on Push

```yaml
# Rejected: let Render watch repo directly
# (Render dashboard: Auto-Deploy = ON)
```

**Rejected because:**

- No affected detection (always deploys on every push)
- Cannot run tests before deploy (Render builds immediately)
- No control over when deploys happen
- Cannot skip deploys on PRs
- Bypasses GitHub Actions orchestration

### Nx Cloud Distributed Tasks

```yaml
# Considered but deferred: Nx Cloud DTE
- run: npx nx affected --target=build --parallel=3
```

**Not rejected, but deferred:**

- Current setup is sufficient for small monorepo (3 apps)
- Nx Cloud DTE adds cost and complexity
- Revisit when build times exceed 10 minutes or team size grows
- Easy to add later without changing architecture

### GitHub Actions Matrix Strategy

```yaml
# Considered: dynamic job matrix
strategy:
 matrix:
  project: ${{ fromJson(needs.affected.outputs.projects) }}
steps:
 - run: npx nx build ${{ matrix.project }}
```

**Not rejected, but current approach preferred:**

- Matrix is cleaner for homogeneous jobs (all same type)
- Current approach gives explicit control per service
- Service-specific deploy steps differ (Node vs Static Site)
- Easier to read/debug explicit jobs
- May revisit when we have 5+ similar services

## References

- Nx Affected: https://nx.dev/concepts/affected
- Related: ADR 001 (Runtime Configuration), ADR 002 (Showcase Deployment)
- Implementation: `.github/workflows/main.yml`
- Deployment Guide: `docs/guides/render-deployment-guide.md`
- Render Webhooks: https://render.com/docs/deploy-hooks
