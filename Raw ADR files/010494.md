# ADR-001: OSS Project Structure for Community Engagement

**Status:** Accepted 2026-01-03
**Date:** 2026-01-03
**Decision Makers:** @amiable-dev/maintainers
**Reviewed By:** LLM Council (GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

---

## Context

The litellm-langfuse-railway repository provides Railway deployment templates for LiteLLM + Langfuse infrastructure. To maximize open source community engagement and collaboration, we need to establish a consistent project structure that:

1. Lowers the barrier to contribution
2. Provides clear governance and communication channels
3. Ensures code quality through automated workflows
4. Protects both contributors and maintainers with proper policies

The existing [llm-council](https://github.com/amiable-dev/llm-council) repository serves as the organizational template for OSS projects.

### Current State

The repository currently contains:
- Template-specific code (starter/, production/, shared/)
- README documentation
- Operational docs (RUNBOOK.md, UPGRADE.md, COMPARISON.md)
- CLAUDE.md for AI assistant guidance

### Missing OSS Infrastructure

- No community standards (Code of Conduct, Contributing guidelines)
- No GitHub configuration (issue templates, PR templates, CODEOWNERS)
- No CI/CD workflows
- No security policy
- No explicit license file
- No governance documentation
- No `.gitignore` (critical for preventing secret leaks)

## Non-Goals

This ADR explicitly does NOT cover:
- Runtime monitoring of deployed templates
- User authentication/authorization within LiteLLM/Langfuse
- Multi-cloud deployment (Railway-only)
- Template marketplace submission (future ADR)
- Support for LiteLLM/Langfuse runtime errors (only deployment configuration)

## Decision

Adopt the llm-council OSS structure with the following adaptations for this infrastructure-focused (non-Python-package) repository:

### 1. Community Standards Files (Root Level)

| File | Purpose | Adaptation |
|------|---------|------------|
| `LICENSE` | MIT License | Standard MIT |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 | No changes |
| `CONTRIBUTING.md` | Contribution guidelines | Adapt for Railway templates; include cost warnings and testing strategy |
| `GOVERNANCE.md` | Decision-making process | Define maintainer roles, decision process, and succession plan |
| `SECURITY.md` | Vulnerability reporting | Focus on template security; clarify upstream vs template issues |
| `SUPPORT.md` | Help channels | GitHub Discussions + issue templates |
| `CHANGELOG.md` | Version history | **Mandatory** - tracks env var changes, service topology updates |
| `.gitignore` | Prevent accidental commits | **Critical** - block `.env`, `railway.env`, secrets |

### 2. GitHub Configuration (.github/)

```
.github/
├── CODEOWNERS              # Maintainer review requirements
├── FUNDING.yml             # Sponsorship links
├── dependabot.yml          # Dependency updates (GitHub Actions only)
├── ISSUE_TEMPLATE/
│   ├── config.yml          # Template chooser + discussion links
│   ├── bug_report.md       # Deployment issues
│   └── feature_request.md  # Template improvements
├── PULL_REQUEST_TEMPLATE.md
└── workflows/
    ├── validate-templates.yml  # TOML/YAML/Dockerfile linting
    └── security.yml            # Secret scanning (gitleaks)
```

### 3. Documentation Structure

```
docs/
├── adr/                    # Architecture Decision Records
│   └── ADR-001-oss-project-structure.md
└── (existing production docs remain in production/docs/)
```

### 4. CI/CD Workflows

**validate-templates.yml** - Runs on PRs:
- TOML syntax validation (`taplo check`)
- YAML syntax validation (`yamllint`)
- GitHub Actions validation (`actionlint`)
- Dockerfile linting (`hadolint`) - if Dockerfiles present
- Docker Compose validation (`docker compose config`)
- Markdown link checking (`lychee`)

**security.yml** - Runs on push/PR:
- Gitleaks secret scanning
- Dependency review for Actions
- No CodeQL (not a software project)

**Supply Chain Hardening (Council Recommendation):**
- Pin all GitHub Actions to specific SHAs (not mutable tags like `@v4`)
- Use `permissions: contents: read` (least privilege)
- Consider `step-security/harden-runner`

### 5. Adaptations from llm-council

| llm-council Feature | Adaptation | Rationale |
|---------------------|------------|-----------|
| Python CI (pytest, ruff, mypy) | Remove | No Python package |
| PyPI publishing | Remove | Not a package |
| Coverage reporting | Remove | No code to test |
| DCO sign-off | Keep | IP protection |
| Pre-commit hooks | Simplify (gitleaks + yamllint) | Minimal code changes |
| CHANGELOG.md | **Mandatory** | Template changes affect deployments |
| CITATION.cff | Remove | Not academic software |
| MkDocs documentation | Remove | READMEs sufficient |
| Dependabot (pip) | Remove → Consider RenovateBot | No Python deps; Renovate better for Docker image tags in TOML |
| Dependabot (actions) | Keep | Maintain CI security |

**Council Note:** Dependabot struggles with Docker image tags in custom config files. Consider RenovateBot for better regex support to update image tags in `railway.toml`.

### 6. CODEOWNERS Configuration

```
# Default owners
* @amiable-dev/maintainers

# Template definitions (critical)
*/railway.toml @amiable-dev/maintainers

# CI/CD workflows
.github/ @amiable-dev/maintainers

# Shared configuration
shared/litellm/config.yaml @amiable-dev/maintainers

# Dockerfiles (if present)
**/Dockerfile @amiable-dev/maintainers
```

### 7. Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Deployment or template issues |
| `enhancement` | Template improvements |
| `documentation` | README/docs updates |
| `good first issue` | Beginner-friendly |
| `help wanted` | Needs community help |
| `starter-template` | Affects starter/ |
| `production-template` | Affects production/ |
| `security` | Security-related |
| `upstream` | Issue belongs to LiteLLM/Langfuse upstream |

### 8. Versioning Strategy (Council Recommendation)

Establish semantic versioning for templates:
- Use Git tags (e.g., `v1.0.0`, `v1.1.0`)
- Breaking changes (env var renames, service topology changes) = MAJOR
- New features (new service, new config option) = MINOR
- Bug fixes (typo, docs) = PATCH

Document in README which versions of LiteLLM, Langfuse, and Postgres are supported.

### 9. Contributing Guidelines Additions (Council Recommendations)

CONTRIBUTING.md must include:

1. **Cost Awareness Warning:**
   > Testing these templates creates real resources on Railway which may incur costs. Contributors are responsible for their own Railway credits and LLM API usage.

2. **Template Testing Strategy:**
   - Static validation: TOML/YAML linting passes
   - Deploy validation (optional): `railway up --detach` to test project
   - Health check verification: `curl` to `/health` endpoints
   - PR submission with test evidence (screenshots acceptable)

3. **Secrets Handling:**
   - Never commit `.env` files
   - Use fake/placeholder values in examples
   - Forked repositories do not inherit secrets

### 10. Security Policy Additions (Council Recommendations)

SECURITY.md must clarify:

1. **Scope:**
   - Template security (insecure defaults, exposed ports, missing auth) → Report HERE
   - LiteLLM runtime vulnerabilities → Report to [LiteLLM security](https://github.com/BerriAI/litellm/security)
   - Langfuse runtime vulnerabilities → Report to [Langfuse security](https://github.com/langfuse/langfuse/security)

2. **Response SLAs:**
   - Initial response: 48 hours
   - Triage: 7 days
   - Critical fixes: Best effort

3. **If Secrets Are Exposed:**
   - Rotate immediately in Railway dashboard
   - Check Railway audit logs
   - No need to report to maintainers unless template-related

## Consequences

### Positive

1. **Lower contribution barrier**: Clear guidelines reduce friction for new contributors
2. **Consistent governance**: Aligned with other amiable-dev projects
3. **Automated quality**: CI catches issues before merge
4. **Security posture**: Secret scanning prevents accidental exposure; supply chain hardening protects CI
5. **Discoverability**: Standard files improve GitHub's community profile score
6. **Version clarity**: Semantic versioning enables stable deployments

### Negative

1. **Maintenance overhead**: More files to keep updated
2. **Initial setup effort**: One-time cost to create all files
3. **Lighter CI**: Less automated validation than code-heavy projects

### Neutral

1. No breaking changes to existing functionality
2. Repository structure remains unchanged

## Compliance / Validation

- [ ] All community standards files created and linked from README
- [ ] GitHub "Community Standards" checklist shows 100% completion
- [ ] CI workflows pass on main branch
- [ ] Issue templates function correctly
- [ ] CODEOWNERS properly routes review requests
- [ ] Branch protection rules enabled (require PR reviews, status checks)

## Implementation Checklist

### Phase 1: Foundation & Security (P0) - Day 1
- [ ] LICENSE (MIT)
- [ ] .gitignore (critical - prevent secret leaks)
- [ ] CODE_OF_CONDUCT.md
- [ ] SECURITY.md (with upstream reporting links)
- [ ] .github/workflows/security.yml (Gitleaks)
- [ ] .editorconfig (consistent formatting)

### Phase 2: Contribution Experience (P0) - Week 1
- [ ] CONTRIBUTING.md (include cost warnings, testing strategy)
- [ ] .github/CODEOWNERS
- [ ] .github/ISSUE_TEMPLATE/bug_report.md
- [ ] .github/ISSUE_TEMPLATE/feature_request.md
- [ ] .github/ISSUE_TEMPLATE/config.yml
- [ ] .github/PULL_REQUEST_TEMPLATE.md
- [ ] CHANGELOG.md (initialize)

### Phase 3: Automation & Governance (P1) - Week 2
- [ ] .github/workflows/validate-templates.yml (taplo, yamllint, actionlint)
- [ ] .github/dependabot.yml (or renovate.json for Docker image tags)
- [ ] GOVERNANCE.md (roles, decisions, succession)
- [ ] .gitleaks.toml (reduce false positives)
- [ ] Update README with badges, support matrix

### Phase 4: Community Growth (P2) - Month 1
- [ ] SUPPORT.md
- [ ] .github/FUNDING.yml
- [ ] .pre-commit-config.yaml
- [ ] Enable GitHub Discussions (Q&A, Ideas, Show & Tell)
- [ ] docs/architecture.md (Mermaid diagram)

---

## LLM Council Review Summary

**Reviewed:** 2026-01-03
**Tier:** High (4 models: GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, Grok 4.1)

### Key Findings Incorporated

1. **Security Automation → P0**: Gitleaks must be active before inviting contributions to prevent accidental secret commits.

2. **CHANGELOG.md Mandatory**: Infrastructure changes (env var renames) are breaking changes; users need version history.

3. **`.gitignore` Critical**: #1 source of secret leaks in template repos; must block `.env`, `railway.env`.

4. **Supply Chain Hardening**: Pin GitHub Actions to SHAs, use least-privilege permissions.

5. **GOVERNANCE.md → P1**: Define decision-making power early to avoid bike-shedding.

6. **Upstream Label**: Add `upstream` label to redirect issues to LiteLLM/Langfuse repositories.

7. **Cost Awareness**: Contributors must understand testing creates real Railway resources.

8. **Template Versioning**: Use semantic versioning tags for stable deployment references.

9. **RenovateBot Consideration**: Dependabot struggles with Docker tags in custom files; Renovate offers better regex support.

### Dissenting Views

- **Grok 4.1** suggested MkDocs might be worth reconsidering at P2 as the project grows.
- **Claude Opus 4.5** noted that DCO sign-off adds friction; consider inbound=outbound licensing as alternative.

---

## References

- [llm-council repository](https://github.com/amiable-dev/llm-council) - Organizational template
- [GitHub Community Standards](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions)
- [Contributor Covenant](https://www.contributor-covenant.org/)
- [Railway Template Documentation](https://docs.railway.app/guides/templates)
- [OpenSSF Scorecard](https://scorecard.dev/) - Security health metrics
- [Step Security Harden Runner](https://github.com/step-security/harden-runner)
