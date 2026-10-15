# 5. Adopt Python Ecosystem Security Framework

Date: 2025-10-15

## Status

Accepted

## Context

pytest-jux handles cryptographic operations (XML digital signatures) and integrates with infrastructure test automation workflows. This creates significant security requirements:

1. **Cryptographic Code**: XMLDSig signature generation and verification requires security assurance
2. **Supply Chain Risk**: Plugin runs in CI/CD pipelines, supply chain attacks could compromise test infrastructure
3. **Trust Chain**: Plugin establishes chain-of-trust for test reports, integrity is critical
4. **Infrastructure Context**: System administrators and integrators rely on plugin security

The Python ecosystem has mature security tooling and supply chain initiatives through:
- Python Package Index (PyPI) security features
- Open Source Security Foundation (OpenSSF)
- Python Packaging Authority (PyPA) official tools
- Python Software Foundation (PSF) Security Developer-in-Residence

## Decision

We will adopt a comprehensive Python ecosystem security framework with three tiers of implementation:

### Tier 1: Essential Security (Sprint 1)

**Automated Vulnerability Scanning**:
- **pip-audit** (PyPA official): Scan dependencies for known vulnerabilities
- **ruff**: Static security analysis for Python code (flake8-bandit rules)
- **safety**: Dependency vulnerability database scanner
- **OpenSSF Scorecard**: Automated security best practices scoring

**CI/CD Integration**:
- GitHub Actions workflow for security scanning
- Pre-commit hooks for local security checks
- Security test suite for cryptographic operations

**Documentation**:
- SECURITY.md with vulnerability reporting process
- Security coding standards and threat model
- Cryptographic standards and approved algorithms

### Tier 2: Supply Chain Hardening (Pre-1.0)

**Package Integrity**:
- **Trusted Publishers**: OIDC-based publishing to PyPI (no long-lived tokens)
- **SBOM Generation**: CycloneDX format for transparency
- **Sigstore Signing**: Keyless signing for release artifacts
- **Hash-Pinned Dependencies**: pip-tools with --require-hashes

**Dependency Management**:
- Dependabot for automated security updates
- Lock files with cryptographic hashes
- Automated dependency review in pull requests

### Tier 3: Cryptographic Assurance (Ongoing)

**Code Review Requirements**:
- 100% test coverage for cryptographic code paths
- Mandatory 2-person review for crypto changes
- Security champion approval for sensitive operations
- Review log in docs/security/CRYPTO_REVIEWS.md

**Advanced Testing**:
- Property-based testing with Hypothesis for edge cases
- Fuzzing with malformed XML inputs
- Attack simulation (XXE, billion laughs, signature wrapping)
- Constant-time operation validation

## Rationale

### Why This Framework?

**Python Ecosystem Alignment**:
- Uses official PyPA tools (pip-audit) and PSF-endorsed practices
- Leverages OpenSSF investments in Python security
- Follows PyPI Trusted Publishers model for supply chain security

**Cryptographic Software Requirements**:
- XML signatures are security-critical, require higher assurance
- Supply chain attacks targeting CI/CD are increasing
- System administrators need confidence in plugin integrity

**Industry Standards**:
- SLSA framework compliance for supply chain
- OWASP guidelines for secure Python development
- NIST guidance for cryptographic software

### Alternatives Considered

**Alternative 1: Minimal Security (Basic Testing Only)**
- **Pros**: Lower overhead, faster development
- **Cons**: Inadequate for cryptographic software, supply chain risks unaddressed
- **Decision**: Rejected - cryptographic code demands comprehensive security

**Alternative 2: External Security Audit Only**
- **Pros**: Professional review, comprehensive assessment
- **Cons**: Expensive, one-time snapshot, not continuous
- **Decision**: Deferred to post-1.0, but continuous automation needed now

**Alternative 3: Custom Security Tooling**
- **Pros**: Tailored to specific needs
- **Cons**: Maintenance burden, reinventing wheel, less community trust
- **Decision**: Rejected - leverage mature Python ecosystem tools

## Consequences

**Positive:**

- **Vulnerability Detection**: Automated scanning catches CVEs in dependencies early
- **Supply Chain Trust**: Trusted Publishers and Sigstore provide verifiable provenance
- **Cryptographic Assurance**: Comprehensive testing and review for security-critical code
- **Community Confidence**: OpenSSF Scorecard demonstrates commitment to security
- **Ecosystem Alignment**: Uses standard Python security practices
- **CI/CD Protection**: Security gates prevent vulnerable code from reaching production
- **Transparency**: SBOM and security documentation build user trust

**Negative:**

- **CI/CD Complexity**: Additional workflow steps increase build time
- **Development Overhead**: Security reviews slow feature velocity
- **Maintenance Burden**: Security tooling requires updates and monitoring
- **False Positives**: Automated scanners may flag non-issues requiring triage
- **Learning Curve**: Contributors need familiarity with security tools

**Neutral:**

- **Dependency Updates**: Automated updates may introduce breaking changes (mitigated by tests)
- **Documentation**: Security docs require ongoing maintenance (standard for any docs)

## Implementation Plan

### Phase 1: Essential Security (Sprint 1 - Week 1-2)

**Week 1: Core Security Infrastructure**
1. Create `docs/security/` directory structure
2. Implement SECURITY.md with vulnerability reporting
3. Document threat model (STRIDE analysis)
4. Create cryptographic standards document
5. Configure ruff security rules in pyproject.toml

**Week 2: Automation and Testing**
6. Implement GitHub Actions security workflow
7. Add security pre-commit hooks
8. Create security test suite skeleton
9. Configure pip-audit and safety
10. Enable Dependabot

### Phase 2: Supply Chain (Pre-1.0 - Weeks 3-6)

**Week 3-4: Package Integrity**
1. Generate SBOM with CycloneDX
2. Implement hash-pinned dependencies
3. Document Trusted Publishers setup
4. Prepare Sigstore signing workflow

**Week 5-6: Hardening**
5. SLSA provenance generation
6. Security release process documentation
7. Vulnerability disclosure policy
8. OpenSSF Scorecard optimization

### Phase 3: Continuous Improvement (Post-1.0)

**Ongoing Activities**:
1. Regular security audits (quarterly)
2. Crypto code review log maintenance
3. Security documentation updates
4. Community security engagement
5. CVE assignment process for vulnerabilities

## Validation Criteria

Security framework will be validated through:

1. **Automated Scanning**: CI passes with no high-severity vulnerabilities
2. **Test Coverage**: 100% coverage for cryptographic code
3. **Scorecard Rating**: OpenSSF Scorecard score >7.0/10
4. **Documentation**: All required security docs present and current
5. **Supply Chain**: SBOM and signatures for all releases
6. **Community**: Security contact responsive within 48 hours

## Security Contact

**Vulnerability Reporting**:
- Email: jrjsmrtn+security@gmail.com
- Process: Coordinated disclosure, 90-day embargo
- Response Time: 48 hours acknowledgment

## References

### Python Ecosystem Security

- PyPI Trusted Publishers: https://docs.pypi.org/trusted-publishers/
- pip-audit (PyPA): https://github.com/pypa/pip-audit
- PSF Security: https://www.python.org/dev/security/
- PSF Security Developer-in-Residence: https://sethmlarson.dev/

### OpenSSF Resources

- Alpha-Omega: https://openssf.org/community/alpha-omega/
- Scorecard: https://github.com/ossf/scorecard
- SLSA: https://slsa.dev/
- Sigstore: https://www.sigstore.dev/

### Security Standards

- OWASP Python Security: https://owasp.org/www-project-python-security/
- PyPA Security Guidelines: https://packaging.python.org/guides/security/
- NIST Cryptographic Standards: https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines

### Tools

- Ruff: https://github.com/astral-sh/ruff
- Safety: https://github.com/pyupio/safety
- Trivy: https://github.com/aquasecurity/trivy
- CycloneDX: https://cyclonedx.org/
- Dependabot: https://docs.github.com/en/code-security/dependabot

## Related Decisions

- ADR-0001: Record architecture decisions (establishes documentation framework)
- ADR-0002: Adopt development best practices (establishes quality standards)
- ADR-0003: Use Python 3 with pytest, lxml, signxml, and SQLAlchemy stack (establishes dependencies)
- ADR-0004: Adopt Apache License 2.0 (establishes legal framework)

## Notes

This security framework is inspired by the EFF Ægis initiative principles but adapted for the Python ecosystem's mature security tooling and practices. It balances security rigor with development velocity through automation and clear processes.

The framework will evolve as the Python ecosystem security landscape changes, particularly as PyPI completes TUF implementation (PEP 458) and SLSA adoption increases.
