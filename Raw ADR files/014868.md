# ADR-0008: Adopt OpenSSF Best Practices Badge Program

**Status**: Proposed
**Date**: 2025-10-19
**Decision Makers**: pytest-jux maintainers
**Consulted**: OpenSSF Best Practices Badge criteria, security community standards
**Informed**: pytest-jux contributors and users

## Context

### Current State

pytest-jux has established a strong security foundation:
- ✅ XMLDSig signature generation and verification
- ✅ Cryptographic key management (RSA, ECDSA)
- ✅ SLSA Build Level 2 compliance (ADR-0006)
- ✅ Automated test suite (Sprint 1-3)
- ✅ Static analysis tools (ruff, mypy)
- ✅ Security documentation (SECURITY.md, THREAT_MODEL.md)
- ✅ Test coverage visibility standards (ADR-0007)

**However**, we lack **formal certification** of these security practices:
- ❌ No industry-recognized security badge
- ❌ No third-party validation of practices
- ❌ No systematic gap analysis
- ❌ No public trust signal for security-conscious users

### Problem Statement

**Security credibility requires verifiable evidence:**

1. **Trust Gap**: Users cannot easily verify security claims
2. **Competitive Position**: Few pytest plugins demonstrate security maturity
3. **Best Practice Gaps**: No systematic identification of security weaknesses
4. **Compliance Pressure**: EU CRA (2027) requires security due diligence
5. **Community Standards**: Industry expects formal security certifications

**For a security-focused plugin** (XMLDSig signatures, crypto keys, supply chain security), **lack of formal certification undermines credibility**.

### What is OpenSSF Best Practices Badge?

The **Open Source Security Foundation (OpenSSF) Best Practices Badge** is a **free, voluntary certification program** for open source projects to demonstrate adherence to security and quality best practices.

**Program Overview:**
- **Free**: No cost to participate (open source projects)
- **Self-Certification**: Projects answer criteria questions
- **Automated Verification**: System validates many answers
- **Public Badge**: Displayable badge demonstrates compliance
- **Three Levels**: Passing → Silver → Gold (progressive maturity)

**Badge Authority:**
- Managed by Linux Foundation and OpenSSF
- Industry-recognized standard (used by CNCF, Apache, etc.)
- Referenced in government procurement (NIST, CISA)
- Correlates with OpenSSF Scorecard metrics

### Badge Levels and Requirements

#### **Passing Badge** (~60 criteria)

**Categories:**
- **Basics**: Project description, license, contribution process
- **Change Control**: Version control, release notes, unique versions
- **Reporting**: Bug tracker, vulnerability disclosure process
- **Quality**: Automated tests, CI/CD, reproducible builds
- **Security**: No hardcoded credentials, crypto best practices, HTTPS
- **Analysis**: Static analysis, memory safety, warning flags

**Key MUST Criteria:**
- Open source license (OSI-approved)
- Public version control repository
- Vulnerability reporting process (private channel, ≤60 day response)
- Automated test suite
- No leaked credentials
- Static code analysis
- Cryptographic RNG (secure random number generation)
- HTTPS for downloads (counter MITM)

**Key SHOULD Criteria:**
- 80%+ statement coverage
- Release notes for each version
- Reproducible builds
- Two-factor authentication for developers

#### **Silver Badge** (Passing + ~40 criteria)

**Enhanced Requirements:**
- 80%+ test coverage (enforced)
- Two-factor authentication (2FA) for all committers
- Signed releases (GPG/PGP or equivalent)
- Bus factor >1 (multiple independent contributors)
- Documented coding standards
- Automated dependency tracking

#### **Gold Badge** (Silver + ~20 criteria)

**Advanced Requirements:**
- 90%+ branch coverage
- External security review
- Hardening mechanisms enabled
- Multiple static analysis tools
- Dynamic analysis (fuzzing)
- Reproducible builds verified

### pytest-jux Security Positioning

**Why badge matters for pytest-jux:**

1. **Security-Critical Function**: Signing test reports with cryptographic signatures
2. **Trust Requirement**: Users entrust private keys to the plugin
3. **Supply Chain Security**: Part of CI/CD pipelines (critical infrastructure)
4. **Claims Require Proof**: We claim security rigor, must demonstrate it
5. **Competitive Advantage**: Few pytest plugins have security badges
6. **EU CRA Preparation**: Badge demonstrates security due diligence

**Security Claims We Make:**
- XMLDSig signature generation (cryptographically secure)
- SLSA L2 compliance (verifiable builds)
- No credential leakage (secure key management)
- Reproducible builds (supply chain integrity)

**Badge validates these claims** through third-party criteria.

### Gap Analysis (Current vs. Passing Badge)

**Already Meeting (~80% of Passing criteria):**

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **basics_oss** | ✅ Met | MIT license (OSI-approved) |
| **repo_public** | ✅ Met | GitHub: jrjsmrtn/pytest-jux |
| **repo_track** | ✅ Met | Git version control |
| **version_unique** | ✅ Met | Semantic versioning (0.1.x) |
| **changelog** | ✅ Met | CHANGELOG.md (Keep a Changelog) |
| **test** | ✅ Met | pytest test suite |
| **test_invocation** | ✅ Met | `pytest` command |
| **test_continuous_integration** | ✅ Met | GitHub Actions |
| **static_analysis** | ✅ Met | ruff, mypy (strict mode) |
| **crypto_random** | ✅ Met | secrets module, cryptography lib |
| **delivery_mitm** | ✅ Met | HTTPS (PyPI) |
| **no_leaked_credentials** | ✅ Met | No hardcoded secrets |
| **build_reproducible** | ✅ Met | SLSA L2 reproducible builds |
| **provenance_available** | ✅ Met | SLSA provenance (GitHub Releases) |

**Gaps to Address (~20%):**

| Criterion | Status | Gap | Sprint 6 Task |
|-----------|--------|-----|---------------|
| **vulnerability_report_process** | ⚠️ Gap | No documented process | US-6.2: Update SECURITY.md |
| **vulnerability_report_private** | ⚠️ Gap | No private channel | US-6.2: Enable GitHub Security Advisories |
| **vulnerability_report_response** | ⚠️ Gap | No response SLA | US-6.2: Document ≤60 day commitment |
| **test_statement_coverage80** | ⚠️ Gap | Coverage not measured | US-6.1: Codecov integration (ADR-0007) |
| **release_notes** | ⚠️ Gap | CHANGELOG not linked | US-6.4: Link from GitHub Releases |
| **release_notes_vulns** | ⚠️ Gap | Security fixes not highlighted | US-6.2: Update CHANGELOG format |

**All gaps addressable in Sprint 6** (2-3 weeks).

### Alternatives Considered

#### Alternative 1: No Formal Certification
**Pros**: Zero effort, no external dependencies
**Cons**: No trust signal, no gap analysis, competitive disadvantage
**Decision**: Rejected - badge provides high value for low effort

#### Alternative 2: ISO 27001 Certification
**Pros**: Industry-standard security certification, enterprise recognition
**Cons**: Expensive ($10k-50k), heavyweight process, designed for organizations not OSS projects
**Decision**: Rejected - cost prohibitive, overkill for OSS project

#### Alternative 3: CII Best Practices (Predecessor)
**Pros**: Same program (CII merged into OpenSSF)
**Cons**: Deprecated, replaced by OpenSSF
**Decision**: Rejected - use current program (OpenSSF)

#### Alternative 4: SOC 2 Compliance
**Pros**: Enterprise trust, audit-based
**Cons**: Very expensive ($20k-100k), requires organization, annual audits
**Decision**: Rejected - designed for SaaS companies, not applicable

#### Alternative 5: OWASP Verification Standard
**Pros**: Security-focused, comprehensive
**Cons**: Designed for web apps, not libraries
**Decision**: Rejected - not applicable to CLI/library project

#### Alternative 6: OpenSSF Scorecard Only
**Pros**: Automated, free, GitHub integration
**Cons**: No badge, no self-certification, less comprehensive
**Decision**: Complement (not replace) - Scorecard + Badge together

**Comparison Matrix:**

| Option | Cost | Effort | Recognition | Applicability | Decision |
|--------|------|--------|-------------|---------------|----------|
| **OpenSSF Badge** | Free | Low (2-3 weeks) | High (OSS) | Perfect | ✅ **Selected** |
| ISO 27001 | $10k-50k | High (6+ months) | High (Enterprise) | Poor | ❌ Rejected |
| SOC 2 | $20k-100k | High (6+ months) | High (Enterprise) | Poor | ❌ Rejected |
| OWASP | Free | Medium | Medium | Poor (web apps) | ❌ Rejected |
| Scorecard | Free | Zero (automated) | Medium | Good | ✅ Complement |
| None | Free | Zero | None | N/A | ❌ Rejected |

### Benefits of Badge for pytest-jux

#### Trust and Credibility
- ✅ **Public Trust Signal**: Badge visible on README demonstrates security maturity
- ✅ **Third-Party Validation**: Not self-assessed, criteria enforced by OpenSSF
- ✅ **Industry Recognition**: Used by major projects (Kubernetes, TensorFlow, etc.)
- ✅ **User Confidence**: Security-conscious users see verified practices

#### Security Improvements
- ✅ **Gap Analysis**: Systematic identification of security weaknesses
- ✅ **Best Practice Guidance**: Criteria provide roadmap for improvements
- ✅ **Continuous Improvement**: Quarterly re-verification encourages maintenance
- ✅ **Vulnerability Process**: Forces documentation of security response

#### Competitive Advantage
- ✅ **Market Differentiation**: Few pytest plugins have security badges
- ✅ **Professional Image**: Demonstrates project maturity
- ✅ **Enterprise Adoption**: Enterprises prefer certified OSS
- ✅ **Community Leadership**: Position as security-focused plugin

#### Compliance and Standards
- ✅ **EU CRA Preparation**: Demonstrates security due diligence for 2027 requirements
- ✅ **NIST SSDF Alignment**: Criteria align with NIST secure development framework
- ✅ **OpenSSF Scorecard**: Badge correlates with improved Scorecard scores
- ✅ **Supply Chain Security**: Reinforces SLSA L2 compliance

## Decision

**We will pursue the OpenSSF Best Practices Badge at the Passing level.**

### Scope

**Target Level**: Passing Badge (foundation)
- Silver Badge: Future consideration (Sprint 7+)
- Gold Badge: Long-term goal (after project maturity)

**Timeline**: Sprint 6 (2-3 weeks)
- Week 1: Coverage visibility + SBOM generation
- Week 2: Security process + badge application
- Week 3: Badge completion + documentation

**Effort Estimate**: ~16-24 hours total
- Coverage visibility: 8 hours (US-6.1)
- Security process: 4 hours (US-6.2)
- SBOM generation: 4 hours (US-6.3)
- Badge application: 4-8 hours (US-6.4)

### Implementation Approach

#### Phase 1: Address Gaps (Week 1-2)

**US-6.1: Test Coverage Visibility** (ADR-0007)
- Configure pytest-cov (≥85% overall, ≥90% crypto)
- Integrate Codecov
- Display coverage badge
- Enable PR diff coverage

**US-6.2: Vulnerability Disclosure Process**
- Update SECURITY.md with reporting process
- Enable GitHub Security Advisories
- Document severity levels (Critical, High, Medium, Low)
- Commit to ≤60 day response time
- Provide security contact method

**US-6.3: SBOM Generation**
- Add cyclonedx-bom to build workflow
- Generate SBOM for every release
- Upload SBOM to GitHub Releases
- Document SBOM usage for consumers

#### Phase 2: Badge Application (Week 2-3)

**US-6.4: Badge Registration and Certification**
1. Register project at https://www.bestpractices.dev/
2. Complete questionnaire (all categories)
3. Provide evidence for each criterion
4. Submit for automated verification
5. Address any identified gaps
6. Obtain Passing badge
7. Display badge on README
8. Document maintenance process

#### Phase 3: Maintenance (Ongoing)

**Quarterly Re-verification:**
- Review badge criteria (criteria may change)
- Update evidence if project changes
- Re-certify to maintain badge
- Track new criteria for Silver/Gold

**Continuous Improvement:**
- Monitor OpenSSF Scorecard alignment
- Track badge criteria changes
- Plan for Silver badge (future sprint)

### Badge Criteria Mapping

**Complete Criteria Coverage:**

| Category | Criteria | Status | Evidence/Action |
|----------|----------|--------|-----------------|
| **Basics** | Open source license | ✅ Met | MIT (pyproject.toml) |
| | Project description | ✅ Met | README.md |
| | Public repo | ✅ Met | GitHub: jrjsmrtn/pytest-jux |
| | Contribution docs | ✅ Met | CONTRIBUTING.md |
| **Change Control** | Version control | ✅ Met | Git + GitHub |
| | Unique versions | ✅ Met | Semantic versioning |
| | Release notes | 🔧 Fix | Link CHANGELOG from releases |
| **Reporting** | Bug tracker | ✅ Met | GitHub Issues |
| | Vuln process | 🔧 Fix | Update SECURITY.md (Week 2) |
| | Private reporting | 🔧 Fix | Enable Security Advisories (Week 2) |
| | Response time | 🔧 Fix | Document ≤60 days (Week 2) |
| **Quality** | Automated tests | ✅ Met | pytest suite |
| | CI/CD | ✅ Met | GitHub Actions |
| | Test coverage | 🔧 Fix | Codecov integration (Week 1) |
| **Security** | No credentials | ✅ Met | Code review verified |
| | Crypto RNG | ✅ Met | secrets module |
| | HTTPS | ✅ Met | PyPI (HTTPS only) |
| **Analysis** | Static analysis | ✅ Met | ruff, mypy |
| | Memory safety | ✅ Met | Python (memory-safe) |
| | Warnings | ✅ Met | mypy strict mode |

**Legend**: ✅ Met | 🔧 Fix | ⚠️ N/A

### Success Criteria

**Technical Success:**
- [ ] All MUST criteria met (100%)
- [ ] All SHOULD criteria met or justified
- [ ] All SUGGESTED criteria evaluated
- [ ] Badge earned (Passing level)
- [ ] Badge displayed on README
- [ ] Automated verification passed

**Process Success:**
- [ ] Vulnerability process documented
- [ ] Test coverage ≥85% (Codecov)
- [ ] SBOM generated for releases
- [ ] Security contact method provided
- [ ] Response time commitment stated

**Community Success:**
- [ ] Badge publicly visible
- [ ] Trust signal for users
- [ ] Competitive positioning improved
- [ ] Security credibility demonstrated

### Maintenance Commitment

**Quarterly Review** (4 times/year):
- Review badge status on bestpractices.dev
- Check for new criteria or requirements
- Update evidence if project changed
- Re-certify to maintain badge

**Annual Assessment**:
- Evaluate progress toward Silver badge
- Review security practices
- Update security documentation
- Plan improvements for next level

**Effort**: ~2 hours/quarter, ~8 hours/year

## Consequences

### Positive Consequences

#### Security Improvements
- ✅ **Systematic Gap Analysis**: Badge criteria identify security weaknesses
- ✅ **Vulnerability Process**: Forces documentation of security response
- ✅ **Best Practice Adoption**: Criteria guide security improvements
- ✅ **Continuous Improvement**: Quarterly review encourages maintenance

#### Trust and Credibility
- ✅ **Public Verification**: Badge demonstrates verified security practices
- ✅ **Third-Party Validation**: Not self-assessed, OpenSSF-enforced
- ✅ **Industry Recognition**: Used by major OSS projects
- ✅ **User Confidence**: Security-conscious users see badge

#### Competitive Advantage
- ✅ **Market Differentiation**: Few pytest plugins have security badges
- ✅ **Professional Image**: Demonstrates project maturity
- ✅ **Enterprise Adoption**: Enterprises prefer certified OSS
- ✅ **Community Leadership**: Security-focused positioning

#### Compliance
- ✅ **EU CRA Preparation**: Demonstrates security due diligence
- ✅ **NIST SSDF Alignment**: Criteria align with NIST framework
- ✅ **OpenSSF Scorecard**: Improves Scorecard metrics
- ✅ **Supply Chain Security**: Reinforces SLSA L2

#### Project Quality
- ✅ **Documentation Quality**: Forces comprehensive security docs
- ✅ **Process Maturity**: Establishes formal security processes
- ✅ **Transparency**: Public badge = public accountability
- ✅ **Contributor Clarity**: Clear security expectations

### Negative Consequences

#### Effort and Time
- ⚠️ **Initial Setup**: 16-24 hours over 2-3 weeks
- ⚠️ **Quarterly Maintenance**: 2 hours per quarter
- ⚠️ **Criteria Updates**: Occasional re-work if criteria change
- ⚠️ **Documentation Burden**: Must maintain evidence

**Mitigation**: Automate verification where possible, schedule quarterly reviews.

#### Potential Misuse
- ⚠️ **Badge as Goal**: Focus on badge vs. security (cargo cult)
- ⚠️ **Checkbox Mentality**: Meet criteria without spirit
- ⚠️ **False Confidence**: Badge ≠ bug-free code

**Mitigation**:
- Emphasize security culture over badge
- Use criteria as roadmap, not just checklist
- Educate users: badge shows practices, not perfection

#### Maintenance Overhead
- ⚠️ **Criteria Drift**: Requirements may change over time
- ⚠️ **Re-certification**: Must re-verify quarterly
- ⚠️ **Badge Loss Risk**: Could lose badge if criteria not met

**Mitigation**:
- Calendar quarterly reviews
- Track criteria changes (OpenSSF announcements)
- Maintain high standards consistently

#### Dependency Risk
- ⚠️ **External Service**: Depends on bestpractices.dev availability
- ⚠️ **Program Changes**: OpenSSF could change program
- ⚠️ **Badge Validity**: Trust depends on OpenSSF reputation

**Mitigation**:
- OpenSSF (Linux Foundation) is stable organization
- Badge is supplemental, not primary security measure
- SLSA L2 + Scorecard provide redundancy

### Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|---------|------------|
| **Criteria too difficult** | Low | Medium | Start with Passing (achievable), defer Silver |
| **Lose badge later** | Low | Medium | Quarterly reviews, maintain practices |
| **Time exceeds estimate** | Medium | Low | 80% criteria already met, gaps are small |
| **Badge not recognized** | Low | Medium | OpenSSF is Linux Foundation (well-known) |
| **Criteria change** | Medium | Low | Subscribe to OpenSSF announcements |
| **False sense of security** | Medium | High | Educate: badge shows practices, not perfection |

### Alternatives Re-evaluation

**Why not just OpenSSF Scorecard?**
- Scorecard is automated, badge is self-certified
- Badge provides public trust signal (visible badge)
- Badge criteria are more comprehensive
- **Decision**: Use both (complementary)

**Why not wait for Silver/Gold?**
- Passing badge is achievable now (80% met)
- Silver requires 2FA enforcement (infrastructure change)
- Gold requires external security review ($$$)
- **Decision**: Passing now, Silver later (Sprint 7+)

**Why not other security certifications?**
- ISO 27001, SOC 2: Expensive ($10k-100k), designed for enterprises
- OWASP: Designed for web applications (not libraries)
- Custom: No industry recognition
- **Decision**: OpenSSF is free, OSS-focused, recognized

### Rollback Plan

If badge pursuit fails or is too costly:

**Immediate** (Week 2 if blocked):
1. Stop badge application
2. Keep security improvements (SECURITY.md, coverage, SBOM)
3. Use OpenSSF Scorecard only

**Short-term** (Month 1):
1. Document why badge was not obtained
2. Create internal security checklist (badge criteria)
3. Implement improvements without formal badge

**Long-term** (Year 1):
1. Re-evaluate badge criteria changes
2. Consider Silver badge if Passing becomes easier
3. Monitor industry trends for alternatives

### Implementation Timeline

**Week 1** (Coverage + SBOM):
- Day 1-2: Configure pytest-cov, create codecov.yml, document ADR-0007 ✅
- Day 3: Integrate Codecov, add token, verify upload
- Day 4: Analyze coverage, fill gaps, add badge
- Day 5: SBOM generation, document usage

**Week 2** (Security + Application):
- Day 1: Update SECURITY.md with vulnerability process
- Day 2: Enable GitHub Security Advisories, document severity
- Day 3: Register on bestpractices.dev
- Day 4: Complete badge questionnaire (Basics, Change Control)
- Day 5: Complete badge questionnaire (Reporting, Quality, Security, Analysis)

**Week 3** (Completion):
- Day 1: Review automated verification results
- Day 2: Address any gaps identified
- Day 3: Submit for final review, obtain badge
- Day 4: Add badge to README, update docs
- Day 5: Sprint retrospective, document maintenance

## Related Decisions

- **ADR-0002**: Adopt Development Best Practices (TDD, quality standards)
- **ADR-0005**: Adopt Python Ecosystem Security Framework (security foundation)
- **ADR-0006**: Adopt SLSA Build Level 2 Compliance (supply chain security)
- **ADR-0007**: Adopt Test Coverage Visibility Standards (quality metrics)
- **Sprint 0**: Project Initialization (security framework established)
- **Sprint 5**: SLSA Build Level 2 (provenance generation)
- **Sprint 6**: OpenSSF Best Practices Badge (this decision)

## References

### OpenSSF Best Practices

- [OpenSSF Best Practices Badge Program](https://www.bestpractices.dev/)
- [Badge Criteria (Passing Level)](https://www.bestpractices.dev/en/criteria/0)
- [Badge Criteria (Silver Level)](https://www.bestpractices.dev/en/criteria/1)
- [Badge Criteria (Gold Level)](https://www.bestpractices.dev/en/criteria/2)
- [OpenSSF Best Practices FAQ](https://github.com/coreinfrastructure/best-practices-badge/blob/main/doc/faq.md)

### Standards and Frameworks

- [NIST Secure Software Development Framework (SSDF)](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [CISA Secure by Design Principles](https://www.cisa.gov/securebydesign)
- [OpenSSF Scorecard](https://securityscorecards.dev/)
- [EU Cyber Resilience Act](https://digital-strategy.ec.europa.eu/en/library/cyber-resilience-act)

### Related Documentation

- [Sprint 6: OpenSSF Best Practices Badge Plan](../sprints/sprint-06-openssf-best-practices-badge.md)
- [Security Policy](../security/SECURITY.md) (to be updated)
- [SLSA Verification Guide](../security/SLSA_VERIFICATION.md)
- [Threat Model](../security/THREAT_MODEL.md)

### Industry Examples

Projects with OpenSSF badges:
- [Kubernetes](https://www.bestpractices.dev/en/projects/569) (Gold)
- [TensorFlow](https://www.bestpractices.dev/en/projects/1486) (Passing)
- [Django](https://www.bestpractices.dev/en/projects/6739) (Passing)
- [pytest](https://www.bestpractices.dev/en/projects/1090) (Passing)

---

**Decision Date**: 2025-10-19
**Status**: Proposed (to be accepted after Sprint 6 completion)
**Next Review**: 2026-01-19 (quarterly badge re-verification)
**Target Completion**: Sprint 6 Week 3 (Passing badge earned)
