# Decision 003: Branch-Based Subfolder Deployment Strategy

**Date:** 2025-11-08
**Status:** Accepted
**Deciders:** Christopher Junker, Claude Code
**Related Issues:** TBD
**Related PR:** #19

## Context

Currently, the portfolio site deploys automatically from the `master` branch to cjunker.dev using GitHub Actions. Every push to master triggers a deployment, which can be problematic for:

1. **Production stability** - Untested changes can accidentally deploy to production
2. **Testing workflow** - No staging environment to test before production
3. **Rollback capability** - No easy way to revert to a previous working version
4. **Feature previews** - No way to preview feature branches before merging

**Current workflow:**
```
Push to master → Tests run → Deploy to cjunker.dev
```

**Desired workflow:**
```
Push to master → Tests run → Deploy to cjunker.dev (production root)
Push to staging/feature → Tests run → Deploy to staging.cjunker.dev (subfolder)
```

## Decision

**Implement branch-based deployments with subfolder staging using a single gh-pages branch.**

### Architecture

**Production Environment:**
- Domain: `cjunker.dev`
- Trigger: Push to `master` branch
- Deployment: Root of `gh-pages` branch
- Source: Master branch

**Staging Environment:**
- Domain: `staging.cjunker.dev`
- Trigger: Push to `staging`, `feature/*` branches
- Deployment: `/staging` subfolder of `gh-pages` branch
- Source: Any non-master branch

### Workflow

1. **Development:**
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   # → Automatically deploys to staging.cjunker.dev
   ```

2. **Test on Staging:**
   ```bash
   # Visit https://staging.cjunker.dev to preview changes
   # Staging auto-updates on every push to feature branch
   ```

3. **Merge to Master:**
   ```bash
   # After testing on staging, create PR
   # After review and merge to master
   git checkout master
   git pull origin master
   # → Automatically deploys to cjunker.dev (production)
   ```

4. **Rollback (if needed):**
   ```bash
   git revert <bad-commit>
   git push origin master
   # → Deploys reverted version to production
   ```

## Rationale

### Why Branch-Based Subfolder Deployments?

1. **Automatic Preview Environments**
   - Every feature branch automatically deploys to staging
   - No manual tagging required
   - Instant feedback loop for development

2. **Single GitHub Pages Branch**
   - Works within GitHub Pages limitations (one site per repo)
   - Production at root: `gh-pages/`
   - Staging at subfolder: `gh-pages/staging/`
   - Both served from same branch, different paths

3. **True CI/CD**
   - Continuous deployment on every push
   - No manual release steps
   - Recruiters recognize this as production-grade workflow

4. **Simple Rollback**
   - Git revert on master immediately rolls back production
   - No tag management complexity
   - Standard git workflow

5. **DNS Routing**
   - Production (cjunker.dev) → gh-pages root
   - Staging (staging.cjunker.dev) → gh-pages /staging subfolder
   - Single CNAME setup, automatic subfolder routing

### Why This Beats Tag-Based Deployment

1. **Fewer Steps**
   - Branch-based: Push → auto-deploy
   - Tag-based: Push → tag → push tag → deploy
   - Eliminates manual tagging friction

2. **GitHub Pages Native**
   - Subfolder approach works natively with GitHub Pages
   - No workarounds or multiple branches needed
   - Uses peaceiris/actions-gh-pages action (battle-tested)

3. **Better Developer Experience**
   - Feature branches auto-preview
   - No remembering tag formats
   - Staging always shows latest non-master work

4. **Cleaner Git History**
   - No proliferation of staging tags
   - Production history = master branch commits
   - Easier to understand deployment timeline

## Alternatives Considered

### Option 1: Tag-Based Deployment (Rejected)
**Deploy from Git tags (v1.0.0, staging-v1.0.0) to separate branches**

**Pros:**
- Explicit version control
- Semantic versioning for releases
- Clear deployment intent

**Cons:**
- Manual tagging friction (extra steps)
- GitHub Pages limitation: can't serve multiple sites from one repo
- Requires separate gh-pages branches (gh-pages-production, gh-pages-staging)
- Not true CI/CD (requires manual tag creation)
- More complex workflow

**Decision:** Rejected - too complex, doesn't work cleanly with GitHub Pages

### Option 2: Two Separate Repositories (Rejected)
**resume-improvements (prod) + resume-improvements-staging (staging)**

**Pros:**
- Complete isolation
- Separate commit histories
- Easier GitHub Pages setup

**Cons:**
- Code duplication
- Must sync changes between repos
- More complex maintenance
- Doubles git operations

**Decision:** Rejected - unnecessary complexity

### Option 3: External Hosting for Staging (Considered)
**GitHub Pages for prod + Netlify/Vercel for staging**

**Pros:**
- Separate services
- Netlify/Vercel offer great preview features

**Cons:**
- Additional service dependency
- Different deployment processes
- Potential cost (free tiers have limits)
- Inconsistent environments
- Overkill for static HTML site

**Decision:** Rejected - unnecessary external dependency

### Option 4: Branch-Based Subfolder Deployment (Selected)
**gh-pages branch with root for production, /staging subfolder for staging**

**Pros:**
- Single repository, single deployment branch
- Automatic CI/CD on every push
- Works natively with GitHub Pages
- No manual tagging required
- Feature branch auto-previews
- Simple DNS setup (subdomain → subfolder)
- Uses battle-tested peaceiris/actions-gh-pages action
- Clean git history

**Cons:**
- No explicit version tags (can add later if needed)
- Staging URL includes /staging path (minor aesthetic issue)

**Decision:** **Selected** - cleanest, most CI/CD-like, works with GitHub Pages

## Consequences

### Positive
- ✅ True CI/CD with automatic deployments
- ✅ Staging environment for testing (auto-preview)
- ✅ Simple workflow (push = deploy)
- ✅ Easy rollback (git revert)
- ✅ Works natively with GitHub Pages
- ✅ Feature branch previews
- ✅ Single gh-pages branch (cleaner)
- ✅ No manual tagging friction

### Negative
- ⚠️ No explicit versioning (can add git tags separately if needed)
- ⚠️ Staging URL has /staging path (minor UX issue)

### Neutral
- 📝 DNS configuration required for staging subdomain (one-time setup)
- 📝 Production deploys on every master push (can add branch protection)

## Implementation Plan

### Phase 1: GitHub Actions Workflow (1 hour)
- [x] Create `.github/workflows/deploy.yml`
- [x] Configure triggers for master, staging, and feature branches
- [x] Add deployment jobs:
  - deploy-production: master → gh-pages root
  - deploy-staging: non-master → gh-pages /staging
- [x] Use peaceiris/actions-gh-pages@v3 action

**Workflow Logic:**
```yaml
on:
  push:
    branches: [ master, staging, 'feature/**' ]
  pull_request: [ master ]

deploy-production:
  if: github.ref == 'refs/heads/master'
  # → Deploys to gh-pages root

deploy-staging:
  if: github.ref != 'refs/heads/master'
  # → Deploys to gh-pages /staging subfolder
```

### Phase 2: GitHub Environments (30 min)
- [ ] Create `production` environment in GitHub repo settings
- [ ] Create `staging` environment
- [ ] Configure environment protection rules (optional: require approval for prod)

### Phase 3: DNS Configuration (30 min)
- [ ] Add CNAME record for staging.cjunker.dev
- [ ] Test DNS propagation
- [ ] GitHub Pages will auto-route subdomain to subfolder

**DNS Records:**

Production (cjunker.dev) - Already configured:
```
Type: A
Name: @
Value: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
```

Staging (staging.cjunker.dev) - New:
```
Type: CNAME
Name: staging
Value: cjunks94.github.io
TTL: 3600
```

### Phase 4: Documentation (1 hour)
- [ ] Update DEPLOYMENT.md with branch-based workflow
- [ ] Add workflow examples
- [ ] Document staging environment usage
- [ ] Update README.md deployment section

### Phase 5: Testing (1 hour)
- [ ] Push to feature branch, verify staging deployment
- [ ] Merge to master, verify production deployment
- [ ] Test rollback with git revert

## Branch Strategy

### Production Branch
- **Branch:** `master`
- **Deployment:** Automatic on push
- **Target:** gh-pages root → cjunker.dev

### Staging Branches
- **Branches:** `staging`, `feature/*`
- **Deployment:** Automatic on push
- **Target:** gh-pages /staging → staging.cjunker.dev

### Pull Requests
- **Trigger:** Tests only (no deployment)
- **Purpose:** CI checks before merge

## Rollback Strategy

To rollback production:

```bash
# Option 1: Revert specific commit
git checkout master
git revert <bad-commit-sha>
git push origin master
# → Automatically deploys reverted version

# Option 2: Revert to specific commit (hard reset)
git checkout master
git reset --hard <good-commit-sha>
git push origin master --force
# ⚠️ Use with caution - rewrites history
```

## Success Criteria

- [x] Production deploys automatically from `master` branch
- [x] Staging deploys automatically from non-master branches
- [ ] cjunker.dev serves production site (root of gh-pages)
- [ ] staging.cjunker.dev serves staging site (/staging subfolder)
- [x] Tests run before deployment
- [x] GitHub Actions workflow passes
- [ ] Documentation updated
- [ ] DNS configured for staging subdomain

## Estimated Effort

**Total: 3-4 hours**

Breakdown:
- GitHub Actions workflow: 1 hour ✅
- GitHub environments setup: 30 min
- DNS configuration: 30 min
- Documentation: 1 hour
- Testing and validation: 1 hour

## References

- GitHub Pages Docs: https://docs.github.com/en/pages
- GitHub Actions Deployment: https://docs.github.com/en/actions/deployment/about-deployments
- peaceiris/actions-gh-pages: https://github.com/peaceiris/actions-gh-pages
- GitHub Pages Subfolder Deployment: https://github.com/peaceiris/actions-gh-pages#%EF%B8%8F-deploy-to-external-repository-external_repository

## Timeline

- **Proposed:** 2025-11-08
- **Accepted:** 2025-11-09
- **Implementation Start:** 2025-11-09
- **Target Completion:** 2025-11-09

## Notes

### GitHub Pages Configuration

After workflow is set up:
1. Go to **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **gh-pages** / **(root)**
4. Custom domain: `cjunker.dev`
5. Enforce HTTPS: ✅

### DNS Configuration for Staging

Add CNAME record at your DNS provider:
- **Type:** CNAME
- **Name:** staging
- **Value:** cjunks94.github.io
- **TTL:** 3600

GitHub Pages will automatically route `staging.cjunker.dev` to the `/staging` subfolder.

### Future Enhancements

- Deployment status badges in README
- Slack/email notifications on deployments
- Optional: Add git tags for releases (alongside auto-deployment)
- Branch protection rules for master

---

**Status Update:**
- 2025-11-08: Decision proposed
- 2025-11-09: Decision accepted, workflow implemented
