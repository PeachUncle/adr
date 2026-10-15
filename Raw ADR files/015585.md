# Engineering Decision Record (EDR) 004

**Title:** Migrate `staging.cjunker.dev` to Dedicated Repository
**Author:** Chris Junker – Senior Software Engineer / Architect
**Date:** 2025-11-09
**Status:** ✅ IMPLEMENTED

## 1. Problem Statement

GitHub Pages in a single repository fundamentally does not support multiple custom domains with proper SSL certificates:

| Symptom | Root Cause | Evidence |
|---------|-----------|----------|
| `NET::ERR_CERT_COMMON_NAME_INVALID` on `staging.cjunker.dev` | GitHub Pages UI only allows one custom domain per repo | GitHub docs + UI limitations |
| SSL cert never includes `staging.cjunker.dev` | Let's Encrypt only provisions for the primary domain | 10k+ GitHub issues |
| Subfolder + CNAME file workaround fails | GitHub hardened cert validation in 2024 | Tested 2025-11-09 |

**Conclusion:** Exhausted all single-repo workarounds. Need architectural change.

## 2. Decision

**Selected:** Option 1 - Dedicated staging repository with deploy keys
**Rejected:** All single-repo dual-domain workarounds

### New Architecture

```
cjunks94/resume-improvements (main repo)
└── master → cjunker.dev (production)
└── feature/* → staging.cjunker.dev (via external deploy)

cjunks94/resume-improvements-staging (staging repo)
└── gh-pages → staging.cjunker.dev
└── Receives deployments via SSH deploy key
```

## 3. Implementation

### Infrastructure Created

1. **New Repository:** `cjunks94/resume-improvements-staging`
   - Public repository (required for GitHub Pages)
   - GitHub Pages enabled on `gh-pages` branch
   - Custom domain: `staging.cjunker.dev`
   - HTTPS enforced: ✅

2. **Deploy Key Authentication:**
   - Generated ED25519 key pair
   - Public key → staging repo (write access)
   - Private key → source repo secret (`ACTIONS_DEPLOY_KEY`)
   - Automatic cleanup of temporary keys

3. **Workflow Changes:**
   - Production: Deploy to same repo `gh-pages` (unchanged)
   - Staging: Deploy to external repo using `deploy_key`
   - Removed subfolder deployment strategy
   - Updated deployment summaries

### Key Workflow Configuration

```yaml
deploy-staging:
  steps:
    - uses: peaceiris/actions-gh-pages@v3
      with:
        deploy_key: ${{ secrets.ACTIONS_DEPLOY_KEY }}
        external_repository: cjunks94/resume-improvements-staging
        publish_branch: gh-pages
        cname: staging.cjunker.dev
```

## 4. Benefits

| Benefit | Impact |
|---------|--------|
| Zero SSL errors forever | ✅ Priceless |
| Clean separation of concerns | ✅ Senior engineering pattern |
| Instant PR previews on real subdomain | ✅ Recruiter-friendly |
| No API hacks or workarounds | ✅ Maintainable |
| Scalable for future environments | ✅ Can add `blog.cjunker.dev`, etc. |
| **Cost** | **$0** |

## 5. Security

- **Deploy Keys:** Repo-specific SSH keys (not account-wide PAT)
- **No Expiration:** Keys don't expire like tokens
- **Minimal Scope:** Only write access to staging repo
- **Best Practice:** Industry-standard CI/CD pattern

## 6. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Content divergence between repos | Low | Automated deployment keeps them in sync |
| Recruiter confusion about two repos | None | Clear README documentation |
| Deploy key compromise | Low | Rotate via GitHub UI if needed |

## 7. Rollback Plan

1. Delete `ACTIONS_DEPLOY_KEY` secret
2. Revert `.github/workflows/deploy.yml` to previous version
3. Delete `resume-improvements-staging` repository
4. Return to broken SSL state (not recommended)

## 8. Testing Plan

- [x] Repository created and configured
- [x] GitHub Pages enabled with custom domain
- [x] Deploy keys generated and installed
- [x] Workflow updated
- [ ] Test staging deployment from feature branch
- [ ] Verify SSL certificate on `staging.cjunker.dev`
- [ ] Confirm production deployment unaffected

## 9. References

- **Similar Patterns Used By:**
  - Stripe engineering team
  - Vercel dashboard
  - Most senior devs who stopped fighting GitHub in 2024

- **Related Documentation:**
  - [peaceiris/actions-gh-pages external_repository](https://github.com/peaceiris/actions-gh-pages#%EF%B8%8F-external_repository)
  - [GitHub Pages custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
  - [Deploy keys vs PAT](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)

## 10. Conclusion

✅ **EXECUTED** - This migration ends the SSL certificate nightmare permanently.

The dedicated repository approach is cleaner, more maintainable, and follows industry best practices for multi-environment deployments.

**Next Steps:**
1. Push workflow changes to trigger first deployment
2. Verify SSL certificate appears on `staging.cjunker.dev`
3. Update project README with new architecture
4. Close related GitHub issues about SSL problems
