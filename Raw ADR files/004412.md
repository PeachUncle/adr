---
ADR #: 0002
Title: Continuous Quality and Security Mandate
Date: 2025-11-11
Status: Accepted
Authors: UCF Core Team
---

# 1. Context

## The Problem: Production Requires More Than Just Working Code

As the UCF transitions from prototype to production deployment, **"it works on my machine"** is insufficient. Production-grade systems require:

1. **Supply Chain Security**: Dependencies (npm, PyPI, Maven) contain known vulnerabilities (CVEs)
2. **Code Quality Assurance**: Technical debt, code smells, and complexity accumulate silently
3. **Security Vulnerability Detection**: OWASP Top 10 vulnerabilities (XSS, injection, auth bypass) lurk in custom code
4. **Maintainability Standards**: Copy-paste errors, dead code, and poor error handling degrade systems over time
5. **Continuous Verification**: Security and quality must be checked on every commit, not post-deployment

Without automated, mandatory scanning, the UCF risks:
- **Security breaches**: Exploitable vulnerabilities in production
- **Technical bankruptcy**: Unmaintainable codebases that resist evolution
- **Reputation damage**: Public security incidents erode trust in regenerative systems
- **Regulatory non-compliance**: Failure to meet industry standards for due diligence

## Forces at Play

### Two Complementary Security Layers

Modern software systems face threats at two distinct layers:

| Layer | Risk Type | Tool Class | Example Tools |
| :--- | :--- | :--- | :--- |
| **External Dependencies** | Supply chain vulnerabilities (CVEs in third-party code) | Dependency Scanning | Snyk, Dependabot, Trivy |
| **Internal Code** | Security vulnerabilities + quality issues in custom code | SAST (Static Application Security Testing) | SonarCloud, Semgrep, CodeQL |

**Key Insight**: These are **complementary, not overlapping**. A project needs both:
- **Snyk** detects a vulnerable version of `express` in `package.json`
- **SonarCloud** detects SQL injection in your own authentication code

Neither tool can replace the other.

### UCF Strategic Alignment

This mandate directly supports multiple UCF objectives:

| UCF Goal | How This ADR Supports It |
| :--- | :--- |
| **EHDC Enhancement 3 (Secret Management)** | Snyk detects hardcoded credentials in dependencies; SonarCloud flags secrets in custom code |
| **Engineer's Tier Measurability** | SonarCloud Quality Gates provide objective metrics (A/B/C/D/E ratings, coverage %, complexity) |
| **Verifiable Wisdom** | Security findings are traceable to CVE databases (Snyk) and OWASP standards (SonarCloud) |
| **Conscious Evolution** | Technical debt visibility enables intentional refactoring decisions |
| **Cross-Pillar Interoperability** | Standardized security practices enable safe integration between labs |

### Industry Standards

This is not a UCF innovation—it is **baseline due diligence**:

- **OWASP SAMM**: Secure Development Lifecycle requires SAST + SCA (Software Composition Analysis)
- **NIST SSDF**: Supply Chain Security framework mandates dependency scanning
- **SOC 2 / ISO 27001**: Compliance audits require documented security controls
- **CII Best Practices Badge**: Open-source projects must demonstrate vulnerability management

**Competitive necessity**: Any project seeking grants, partnerships, or enterprise adoption will be asked:
- "Do you scan for CVEs?"
- "What's your SonarCloud rating?"
- "How do you prevent injection attacks?"

Answering "we don't" disqualifies the UCF from professional consideration.

## Constraints

### Technical Constraints
- Must integrate with **GitHub Actions** (primary CI/CD platform)
- Must support **multi-language** codebases (JavaScript/TypeScript, Python, Solidity)
- Must provide **clear actionable feedback** (not just noise)
- Must be **free for open-source** projects (SonarCloud/Snyk have OSS tiers)

### Operational Constraints
- Cannot block every PR on minor issues (requires configurable thresholds)
- Must educate developers on findings (not just fail builds cryptically)
- Must respect developer velocity (fast feedback loops)

### Philosophical Constraints (UCF Alignment)
- **Transparency over security through obscurity**: Findings should be documented openly
- **Education over enforcement**: Teach developers why patterns are insecure
- **Evolution over perfection**: Allow technical debt if consciously managed
- **Regeneration over extraction**: Refactoring debt is a "double-and-scale" return mechanism

---

# 2. Decision

## Mandate Dual-Layer Continuous Security & Quality Scanning

The UCF hereby mandates:

### **Layer 1: Dependency Security (Supply Chain Risk)**

**Tool**: [Snyk](https://snyk.io/) or equivalent (Dependabot, Trivy, etc.)

**Scope**: All repositories with `package.json`, `requirements.txt`, `pom.xml`, `go.mod`, etc.

**Integration**:
- GitHub Actions workflow runs on every PR
- Scans all direct and transitive dependencies
- Fails build if **High or Critical CVEs** detected (configurable)
- Provides automated fix PRs where possible

**Example Implementation**:
```yaml
# .github/workflows/security.yml
name: Security Scan
on: [pull_request, push]
jobs:
  snyk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: snyk/actions/node@master  # or python, etc.
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
```

### **Layer 2: Code Quality & Security (SAST)**

**Tool**: [SonarCloud](https://sonarcloud.io/) or equivalent (Semgrep, CodeQL)

**Scope**: All repositories with custom code (not just config/docs repos)

**Integration**:
- GitHub Actions workflow runs on every PR
- Analyzes all source files for:
  - **Security vulnerabilities** (OWASP Top 10: injection, XSS, auth bypass, etc.)
  - **Bugs** (null pointer exceptions, resource leaks, logic errors)
  - **Code smells** (complexity, duplication, dead code)
  - **Test coverage** (% of code exercised by tests)
- Fails build if **Quality Gate** conditions not met (configurable)
- Provides inline PR comments on new issues

**Example Implementation**:
```yaml
# .github/workflows/quality.yml
name: Quality Scan
on: [pull_request, push]
jobs:
  sonarcloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for blame data
      - uses: sonarsource/sonarcloud-github-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### **Configuration Standards**

**SonarCloud Quality Gate** (Minimum Thresholds):

| Metric | New Code Threshold | Overall Code Threshold |
| :--- | :--- | :--- |
| **Security Rating** | A (no vulnerabilities) | B (minor issues only) |
| **Maintainability Rating** | A | B |
| **Coverage on New Code** | ≥80% | ≥70% |
| **Duplicated Lines** | ≤3% | ≤5% |
| **Code Smells (Severity: Major+)** | 0 new issues | Monitored (not blocking) |

**Snyk Policy**:
- **High/Critical CVEs**: Block PR merge
- **Medium CVEs**: Warn (allow merge with justification)
- **Low CVEs**: Informational only
- **License violations**: Block GPL/AGPL in non-GPL projects

### **Exemption Process**

Not all findings warrant blocking merges. Exemptions allowed when:

1. **False Positive**: Tool misidentifies code (document in PR)
2. **Accepted Risk**: Security issue mitigated by other controls (document in ADR)
3. **Technical Debt Roadmap**: Issue acknowledged, fix scheduled (create GitHub issue)
4. **Prototype Phase**: Pre-alpha code not yet production-bound (label branch accordingly)

**Exemption Documentation**:
```markdown
## Security Scan Exemption
**Finding**: SonarCloud reports SQL injection in `getUserData()`
**Justification**: Input is parameterized via ORM, false positive
**Evidence**: [Link to ORM documentation]
**Approved By**: @maintainer-handle
**Review Date**: 2025-11-11
```

---

# 3. Consequences

## Positive Consequences

### Security Improvements
✅ **Proactive vulnerability detection**: CVEs caught before deployment, not after breach
✅ **Reduced attack surface**: OWASP vulnerabilities eliminated systematically
✅ **Supply chain transparency**: Dependency tree risks visible and managed
✅ **Compliance readiness**: Audit trail for security due diligence (SOC 2, ISO 27001)

### Quality Improvements
✅ **Technical debt visibility**: Complexity and code smells quantified objectively
✅ **Maintainability metrics**: SonarCloud ratings provide "Engineer's Tier" proof
✅ **Regression prevention**: New issues blocked at PR stage, not discovered in production
✅ **Knowledge transfer**: New contributors learn secure coding patterns via feedback

### Operational Benefits
✅ **Automated enforcement**: No manual security reviews for common issues
✅ **Fast feedback loops**: Findings appear in PR within minutes
✅ **Reduced incident response costs**: Prevention cheaper than breach remediation
✅ **Developer education**: Tools teach best practices through actionable suggestions

### UCF-Specific Benefits
✅ **Professionalizes UCF**: Demonstrates production readiness to partners/funders
✅ **Protects reputation**: Security incidents erode trust in regenerative systems
✅ **Enables Federation**: Safe cross-lab integrations require guaranteed security standards
✅ **Supports EHDC Enhancement 3**: Secret management validated continuously

## Negative Consequences

### Developer Friction
⚠️ **Build time increase**: Scans add 1-3 minutes per PR
⚠️ **False positive noise**: Not all findings are genuine issues
⚠️ **Cognitive load**: Developers must learn to interpret findings
⚠️ **Merge delays**: Blocking issues must be resolved before merging

**Mitigation**:
- Cache dependencies to speed up scans
- Tune tool sensitivity to reduce false positives (Quality Gate thresholds)
- Provide training materials (OWASP Top 10, SonarCloud rules documentation)
- Allow exemptions with documented justification

### Operational Overhead
⚠️ **Token management**: Snyk/SonarCloud tokens must be securely stored in GitHub Secrets
⚠️ **Configuration maintenance**: Quality Gates and policies need periodic review
⚠️ **Tool outages**: Third-party service downtime blocks CI/CD
⚠️ **Learning curve**: Maintainers must understand tool configuration

**Mitigation**:
- Use GitHub Secrets + Dependabot for token rotation
- Quarterly review of Quality Gate thresholds (adjust as codebase matures)
- Retry logic + fallback to local scanning tools
- Maintainer training sessions + runbooks

### Cost Considerations
⚠️ **Free tier limits**: SonarCloud/Snyk OSS tiers have LOC/project limits
⚠️ **Paid tiers for private repos**: Some labs may require paid subscriptions
⚠️ **Tool lock-in risk**: Switching SAST/SCA vendors requires reconfiguration

**Mitigation**:
- All UCF repos are open-source (free tiers sufficient)
- Evaluate alternatives (Semgrep, CodeQL, Trivy) if limits reached
- Use standard GitHub Actions integration (portable across tools)

### Prototype Velocity Impact
⚠️ **Early-stage projects slowed**: Alpha/pre-alpha code may not meet Quality Gates
⚠️ **Experimentation friction**: Rapid prototyping hampered by strict rules
⚠️ **Innovation tax**: Security scans may feel premature for proofs-of-concept

**Mitigation**:
- **Branch-based exemptions**: `prototype/*` branches bypass strict checks
- **Graduated enforcement**:
  - Pre-alpha: Snyk only (block Critical CVEs)
  - Alpha: Snyk + SonarCloud (warn on issues)
  - Beta: Snyk + SonarCloud (block new issues)
  - Production: Snyk + SonarCloud (block all issues)
- **Conscious debt**: Document technical debt roadmap, address before production

## Neutral Consequences

### Tooling Ecosystem
🔄 **GitHub Actions as CI/CD standard**: Reinforces GitHub-centric workflow
🔄 **SonarCloud/Snyk as reference implementations**: Other tools (Semgrep, Trivy) equally valid
🔄 **Badge culture**: Repos display SonarCloud/Snyk badges (social proof of quality)

### Process Changes
🔄 **PR review checklists expand**: Reviewers must verify scan results addressed
🔄 **Definition of Done updates**: "All scans pass" becomes merge criteria
🔄 **Onboarding materials grow**: New contributors must learn security basics

### Metrics Culture
🔄 **SonarCloud ratings as KPIs**: "Maintain A rating" becomes team goal
🔄 **CVE count tracking**: Zero High/Critical CVEs as success metric
🔄 **Technical debt dashboards**: Quantified debt visible in SonarCloud UI

---

# 4. Alternatives Considered

## Alternative A: Manual Security Reviews Only

**Description**: Rely on human code reviewers to spot security issues during PR review.

**Why Rejected**:
- **Human error**: Reviewers miss vulnerabilities (especially in dependencies)
- **Inconsistent standards**: Different reviewers apply different rigor
- **Scalability**: Manual review doesn't scale to large codebases
- **Knowledge asymmetry**: Junior developers may not recognize OWASP issues
- **Time-consuming**: Thorough security review adds days to PR cycle
- **No historical tracking**: No audit trail of what was checked

**Example Failure Mode**: Reviewer approves PR unaware that `lodash@4.17.15` has a prototype pollution CVE.

## Alternative B: Annual Third-Party Penetration Testing

**Description**: Hire external security firms to audit code once per year.

**Why Rejected**:
- **Delayed feedback**: Issues discovered months after introduction (expensive to fix)
- **Snapshot in time**: Audit becomes stale as code evolves
- **High cost**: Professional pentests cost $10k-$50k+ per audit
- **Reactive**: Finds issues after deployment, not before
- **Limited scope**: Audits typically focus on deployed apps, not all repos

**Partial Adoption**: Pentesting remains valuable for production systems, but complements (not replaces) continuous scanning.

## Alternative C: Single-Tool Solution (e.g., Only Snyk)

**Description**: Use Snyk (which now includes SAST) for both dependency + code scanning.

**Why Rejected** (for SonarCloud):
- **Specialized tools excel**: SonarCloud's SAST and quality metrics more mature than Snyk Code
- **Quality metrics**: SonarCloud provides maintainability ratings, complexity, duplication (Snyk doesn't)
- **Community standards**: SonarCloud widely recognized for code quality certification
- **Price**: SonarCloud OSS tier more generous for large projects
- **UCF precedent**: Many projects already use SonarCloud, less disruption

**Considered but not mandated**: Snyk Code is a valid alternative; labs may choose it if preferred.

## Alternative D: GitHub Advanced Security (CodeQL + Dependabot)

**Description**: Use GitHub's built-in tools (CodeQL for SAST, Dependabot for dependencies).

**Why Not Mandated** (but allowed):
- **Pros**:
  - Native GitHub integration (no third-party tokens)
  - CodeQL highly accurate (low false positives)
  - Dependabot automatic PRs for dependency updates
  - Free for public repos
- **Cons**:
  - CodeQL doesn't provide maintainability metrics (no code smells, complexity ratings)
  - Dependabot less comprehensive than Snyk (fewer vulnerability databases)
  - No unified dashboard across repos (SonarCloud provides org-wide view)

**Decision**: Labs may substitute GitHub Advanced Security for Snyk/SonarCloud **if** they demonstrate equivalent coverage. This ADR mandates the **capability**, not the specific vendor.

## Alternative E: Self-Hosted Tools (SonarQube, Trivy)

**Description**: Run open-source versions of scanning tools on UCF infrastructure.

**Why Not Mandated** (but allowed):
- **Pros**:
  - No third-party data sharing (privacy)
  - No free tier limits
  - Full control over configuration
- **Cons**:
  - Infrastructure cost (servers, maintenance)
  - Operational burden (updates, uptime)
  - No built-in GitHub PR comments (requires custom integration)
  - Smaller community (SonarCloud has better rule updates)

**Decision**: Self-hosted options allowed for labs with specific compliance requirements, but cloud versions (SonarCloud/Snyk) are the default recommendation.

---

# 5. Federation of Labs Promotion Pipeline

## Originating Lab
**Cross-Lab Infrastructure Mandate** (not lab-originated)

This ADR originates from **industry best practices** and **UCF production readiness requirements**, not a specific Implementation Lab. It is introduced as **constitutional infrastructure** that all labs must adopt.

## Rationale for Direct UCF Integration

**Why mandate before lab validation?**

1. **Industry standard**: SAST/SCA are non-negotiable for production systems (OWASP, NIST, SOC 2)
2. **Risk mitigation**: Security breaches affect entire Federation, not just one lab
3. **Professional credibility**: Partners/funders expect documented security practices
4. **EHDC Enhancement 3**: Secret management validation requires continuous scanning
5. **Time-sensitive**: Labs approaching production need this now (EHDC beta, open-science-dlt pilot)

**Validation pathway**:
- ✅ **Industry consensus**: OWASP SAMM, NIST SSDF, CII Best Practices all require this
- ✅ **Tool maturity**: SonarCloud/Snyk battle-tested by millions of projects
- ✅ **UCF precedent**: Some labs already use these tools informally
- 🔄 **Empirical**: Labs will validate integration process and provide feedback for ADR updates

## Lab Adoption Roadmap

### Phase 1: Pilot Integration (Q4 2025)

**Target Labs**:
- **EHDC** (Pillar IV): TypeScript/Solidity codebase
- **open-science-dlt** (Pillar I): TypeScript/Python codebase

**Tasks**:
1. ✅ Create SonarCloud + Snyk organizations (one per lab)
2. ✅ Configure GitHub Actions workflows (copy from templates)
3. ✅ Establish baseline Quality Gates (initially permissive)
4. ✅ Run first scans, triage findings
5. ✅ Resolve Critical/High issues blocking production
6. ✅ Document lessons learned (update this ADR if needed)

**Success Criteria**:
- Zero High/Critical CVEs in `main` branches
- SonarCloud rating ≥B for all production services
- GitHub Actions passing on all new PRs

### Phase 2: Federation-Wide Rollout (Q1 2026)

**Target Labs**:
- **Symbiotic Grid** (Blueprint)
- **Culture Lab** (Pillar II - future)
- **Education Lab** (Pillar III - future)
- **Any new Implementation Labs**

**Tasks**:
1. Replicate Phase 1 setup (automated via cookiecutter templates)
2. Provide training materials (OWASP Top 10, SonarCloud rules)
3. Establish cross-lab security working group (share findings/mitigations)
4. Quarterly security reviews (aggregate metrics across labs)

**Success Criteria**:
- 100% of production labs have scanning enabled
- Cross-lab security incidents ≤1 per year
- Community contributions to security runbooks

### Phase 3: Maturation & Optimization (Q2-Q4 2026)

**Tasks**:
1. **Tighten Quality Gates**: Incrementally raise thresholds as technical debt paid down
2. **Advanced features**: Enable SonarCloud security hotspot review, Snyk container scanning
3. **Metrics dashboard**: Aggregate security/quality metrics across Federation
4. **Publish playbook**: Open-source "UCF Security Handbook" for external projects

**Success Criteria**:
- SonarCloud rating ≥A for all production services
- <10 open High/Critical CVEs across all labs
- ≥3 external projects adopt UCF security playbook

## Promotion Justification

**Cross-Pillar Necessity**: Every lab (Science, Culture, Education, Ecosystem) writes code requiring security
**Risk management**: Single breach affects entire Federation reputation
**Professional standard**: Non-negotiable for grants, partnerships, compliance audits
**Enabler for other ADRs**: Many patterns (secret management, token economics) depend on secure foundations
**Low implementation cost**: Free for open-source, GitHub Actions integration straightforward

**This ADR establishes the precedent for mandatory infrastructure when:**
1. Industry standards are unambiguous (OWASP, NIST)
2. Risk is systemic (affects entire Federation)
3. Cost of inaction is catastrophic (security breach, data loss)
4. Implementation is standard practice (not experimental)

---

# 6. Implementation Checklist

## UCF-Level Infrastructure

- ✅ Create this ADR (0002-continuous-quality-security-mandate.md)
- 🔄 Create GitHub Actions workflow templates:
  - `.github/workflows/snyk-scan.yml`
  - `.github/workflows/sonarcloud-scan.yml`
- 🔄 Document configuration guide:
  - `docs/security/snyk-setup.md`
  - `docs/security/sonarcloud-setup.md`
- 🔄 Create exemption request template:
  - `.github/ISSUE_TEMPLATE/security-exemption.md`
- 🔄 Add badge requirements to lab README templates:
  - `[![Security Rating](https://sonarcloud.io/...)]`
  - `[![Known Vulnerabilities](https://snyk.io/...)]`

## Lab-Specific Implementation

### EHDC (Pillar IV)
- 🔄 Enable Snyk for `package.json` (TypeScript services)
- 🔄 Enable SonarCloud for TypeScript + Solidity
- 🔄 Configure Quality Gates (initial: B rating minimum)
- 🔄 Triage existing findings (prioritize High/Critical)
- 🔄 Document in EHDC ADR series (cross-reference this ADR)

### open-science-dlt (Pillar I)
- 🔄 Enable Snyk for `package.json` + `requirements.txt`
- 🔄 Enable SonarCloud for TypeScript + Python
- 🔄 Configure Quality Gates (initial: B rating minimum)
- 🔄 Triage existing findings (prioritize High/Critical)
- 🔄 Document in open-science-dlt ADR series

### Symbiotic Grid (Blueprint)
- 📅 Enable scans when code transitions from Blueprint → Implementation
- 📅 Validate hardware controller code (Python, C++)
- 📅 Document IoT-specific security considerations

## Training & Documentation

- 🔄 Create OWASP Top 10 training module (for developers)
- 🔄 Create SonarCloud rule interpretation guide
- 🔄 Create Snyk CVE triage flowchart
- 🔄 Record walkthrough video: "Setting up security scans"
- 🔄 Establish security champions program (1 per lab)

## Ongoing Governance

- 🔄 Quarterly security working group meetings
- 🔄 Annual review of Quality Gate thresholds
- 🔄 Track metrics:
  - CVE count (trend down over time)
  - SonarCloud ratings (trend toward A)
  - Time-to-remediation (measure efficiency)
  - False positive rate (adjust tool sensitivity)

---

# 7. Success Metrics

## Technical Metrics (Tracked per Lab)

### Security Metrics
- **CVE count**: 0 High/Critical CVEs in `main` branch (measured by Snyk)
- **Security rating**: SonarCloud Security Rating ≥A for new code, ≥B overall
- **Time-to-remediation**: <7 days from CVE disclosure to patch deployment
- **False positive rate**: <10% of Snyk/SonarCloud findings marked as false positives

### Quality Metrics
- **Maintainability rating**: SonarCloud Rating ≥A for new code, ≥B overall
- **Test coverage**: ≥80% for new code, ≥70% overall
- **Code duplication**: ≤3% duplicated lines in new code
- **Complexity**: No functions with cyclomatic complexity >15 in new code

## Operational Metrics (Tracked Federation-Wide)

- **Adoption rate**: 100% of production labs have scanning enabled by Q2 2026
- **Build pass rate**: ≥95% of PRs pass security scans on first attempt (after initial cleanup)
- **Developer satisfaction**: ≥80% of developers rate tools as "helpful" in surveys
- **Incident count**: ≤1 security incident per year attributable to missed vulnerability

## Business Metrics (UCF-Wide Impact)

- **Grant success rate**: Security practices cited in successful grant proposals
- **Partnership velocity**: Faster due diligence with auditable security controls
- **Compliance readiness**: SOC 2 Type II achievable within 12 months if pursued
- **Community adoption**: ≥3 external projects adopt UCF security playbook by EOY 2026

## Continuous Improvement Metrics

- **Quality Gate evolution**: Thresholds tightened by 10% year-over-year
- **Technical debt reduction**: Total SonarCloud debt hours decrease ≥20% annually
- **Education impact**: ≥90% of new contributors complete OWASP training before first PR
- **Tool efficiency**: Scan time <3 minutes per PR (optimized via caching)

---

# 8. References

## Industry Standards

1. **OWASP SAMM** (Software Assurance Maturity Model): [https://owaspsamm.org/](https://owaspsamm.org/)
   - Security Practice: "Security Testing" (Level 1 requires SAST)
2. **NIST SSDF** (Secure Software Development Framework): [https://csrc.nist.gov/Projects/ssdf](https://csrc.nist.gov/Projects/ssdf)
   - Practice PW.8: "Review and/or analyze the software's code to identify vulnerabilities"
3. **CII Best Practices Badge**: [https://bestpractices.coreinfrastructure.org/](https://bestpractices.coreinfrastructure.org/)
   - Criterion: "The project MUST have a documented process for responding to vulnerability reports"
4. **OWASP Top 10** (2021): [https://owasp.org/Top10/](https://owasp.org/Top10/)
   - Reference for common vulnerability types (injection, XSS, etc.)

## Tool Documentation

5. **SonarCloud**: [https://sonarcloud.io/](https://sonarcloud.io/)
   - Quality Gate Configuration: [https://docs.sonarcloud.io/improving/quality-gates/](https://docs.sonarcloud.io/improving/quality-gates/)
   - GitHub Actions Integration: [https://github.com/SonarSource/sonarcloud-github-action](https://github.com/SonarSource/sonarcloud-github-action)
6. **Snyk**: [https://snyk.io/](https://snyk.io/)
   - GitHub Actions Integration: [https://github.com/snyk/actions](https://github.com/snyk/actions)
   - Severity Thresholds: [https://docs.snyk.io/snyk-cli/test-for-vulnerabilities/set-severity-thresholds](https://docs.snyk.io/snyk-cli/test-for-vulnerabilities/set-severity-thresholds)

## Alternatives

7. **GitHub Advanced Security**: [https://docs.github.com/en/code-security](https://docs.github.com/en/code-security)
   - CodeQL for SAST
   - Dependabot for dependency updates
8. **Semgrep**: [https://semgrep.dev/](https://semgrep.dev/)
   - Open-source SAST tool (alternative to SonarCloud)
9. **Trivy**: [https://trivy.dev/](https://trivy.dev/)
   - Open-source vulnerability scanner (alternative to Snyk)

## UCF Context

10. **ADR-0001**: SE(3) Double-and-Scale Regenerative Principle
    - Establishes precedent for mathematically-grounded patterns
11. **EHDC Enhancement 3**: Secret Management
    - Requires continuous validation of credential handling
12. **Repository Relationships**: Federation of Labs governance model
    - Context for cross-lab standards
13. **Conscious Evolution Framework**: Philosophical foundations
    - "Verifiable wisdom" requires measurable quality metrics

---

# 9. Appendix: Glossary

**SAST**: Static Application Security Testing - analyzing source code for vulnerabilities without executing it
**SCA**: Software Composition Analysis - scanning dependencies for known vulnerabilities (CVEs)
**CVE**: Common Vulnerabilities and Exposures - standardized identifier for security vulnerabilities
**OWASP**: Open Web Application Security Project - nonprofit focused on software security
**Quality Gate**: SonarCloud's pass/fail criteria for code quality (e.g., "no new Critical issues")
**Technical Debt**: Accumulated code quality issues that increase maintenance cost over time
**Code Smell**: Maintainability issue that doesn't cause bugs but makes code harder to understand
**Cyclomatic Complexity**: Metric for number of independent paths through code (higher = harder to test)
**False Positive**: Tool flags issue that isn't actually a vulnerability (requires human review)
**Severity Threshold**: Minimum CVE severity that blocks build (e.g., High/Critical only)
**Transitive Dependency**: Dependency-of-a-dependency (e.g., your app uses `express`, which uses `body-parser`)
**Shift Left**: Detecting issues early in development cycle (PR stage) vs. late (production)
**Blast Radius**: Scope of damage if vulnerability exploited (e.g., single service vs. entire database)

---

**Status**: ✅ **ACCEPTED** (2025-11-11)

**Next Review**: Q2 2026 (after Phase 2 lab rollout complete)

**Supersedes**: None

**Related ADRs**:
- ADR-0001 (establishes precedent for foundational patterns)
- Future EHDC ADRs (will reference this for secret management validation)
- Future open-science-dlt ADRs (will reference this for data integrity)
