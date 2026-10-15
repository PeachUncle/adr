# ADR-0006: Adopt SLSA Build Level 2 Compliance

Date: 2025-10-19

## Status

Proposed

## Context

pytest-jux is a security-focused testing tool that signs JUnit XML test reports with XMLDSig signatures. As a tool that provides cryptographic attestations for test results, it is critical that pytest-jux itself has verifiable supply chain security.

### Current State

**Security Measures in Place:**
- Automated security scanning (pip-audit, ruff security rules, trivy)
- OpenSSF Scorecard monitoring
- GitHub Actions for CI/CD (hosted build platform)
- Cryptographic signing capability for test reports
- Comprehensive security documentation

**Security Gaps:**
- No build provenance generation for pytest-jux releases
- No cryptographic attestation that releases were built from audited source
- No mechanism for consumers to verify package authenticity
- Potential for supply chain attacks between source code and PyPI package

### The Problem

Without build provenance, consumers of pytest-jux cannot verify:
1. **Source authenticity**: Was the package built from the public GitHub repository?
2. **Build integrity**: Was the build process tampered with?
3. **Distribution integrity**: Is the PyPI package identical to what was built?

This is particularly critical for pytest-jux because:
- It handles cryptographic keys (signing keys for test reports)
- It integrates into CI/CD pipelines (trusted environment)
- It processes test results (potentially sensitive information)
- It claims to provide security guarantees (signed test reports)

### SLSA Framework

Supply-chain Levels for Software Artifacts (SLSA, pronounced "salsa") is a security framework developed by Google and the OpenSSF to prevent supply chain attacks.

**SLSA Build Level 2 Requirements:**
1. **Build L1 (prerequisite)**:
   - Provenance generation (unambiguous artifact identification)
   - Hosted build platform (not individual workstations)
   - Provenance distribution to consumers

2. **Build L2 (additional)**:
   - Provenance signed by build platform (not tenant/developer)
   - Provenance authenticity verification enabled
   - Security controls prevent tenant tampering

**Benefits of SLSA L2:**
- Cryptographic proof packages were built from specific source commits
- Protection against compromised developer workstations
- Protection against malicious build script injection
- Independent verification by any consumer
- Industry-standard supply chain security

### Alternatives Considered

**Alternative 1: Manual Signing Only**
- Developer signs releases with personal GPG key
- **Rejected**: Single point of failure, doesn't prove build platform integrity, key compromise risk

**Alternative 2: Sigstore/Cosign Only**
- Use Sigstore for keyless signing
- **Rejected**: Doesn't provide full build provenance, only signature attestation

**Alternative 3: SLSA Build Level 3**
- Add hermetic builds and non-falsifiable provenance
- **Deferred**: L3 requires significant infrastructure (hermetic build environment), L2 provides substantial security improvement with lower implementation cost

**Alternative 4: Status Quo**
- Continue with current security practices only
- **Rejected**: Insufficient for a security-focused tool, doesn't protect against supply chain attacks

## Decision

We will adopt **SLSA Build Level 2 compliance** for all pytest-jux releases using the official SLSA GitHub Generator.

### Implementation Approach

**1. Build Infrastructure**
- Use GitHub Actions as the hosted build platform (already in use)
- Create dedicated build workflow (`.github/workflows/build.yml`)
- Generate reproducible builds with `python -m build`
- Compute SHA-256 hashes of all artifacts

**2. Provenance Generation**
- Use `slsa-framework/slsa-github-generator` (official implementation)
- Generate SLSA Provenance v1.0 format
- Sign provenance with GitHub Actions OIDC (no tenant secrets)
- Include build metadata (source commit, build parameters, timestamps)

**3. Provenance Distribution**
- Upload provenance to GitHub Releases (alongside artifacts)
- Publish provenance to PyPI (using attestations feature)
- Make provenance publicly accessible for verification

**4. Consumer Verification**
- Document verification process using `slsa-verifier`
- Provide examples in security documentation
- Add SLSA badge to README

**5. Automation**
- Provenance generation on every tagged release (`v*`)
- Automated PyPI publishing with Trusted Publishing (OIDC)
- No manual intervention required for releases

### Technical Components

**SLSA Provenance Structure:**
```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {
      "name": "pytest_jux-0.1.4-py3-none-any.whl",
      "digest": {"sha256": "abc123..."}
    }
  ],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {
      "buildType": "https://slsa-framework.github.io/github-actions-buildtypes/workflow/v1",
      "externalParameters": {
        "workflow": {"ref": "refs/tags/v0.1.4", "repository": "jrjsmrtn/pytest-jux"}
      },
      "resolvedDependencies": [...]
    },
    "runDetails": {
      "builder": {"id": "https://github.com/slsa-framework/slsa-github-generator/..."},
      "metadata": {"invocationId": "...", "startedOn": "2025-10-19T..."}
    }
  }
}
```

**Verification Command:**
```bash
slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.1.4.intoto.jsonl \
  --source-uri github.com/jrjsmrtn/pytest-jux \
  pytest_jux-0.1.4-py3-none-any.whl
```

### Security Properties

**What SLSA L2 Prevents:**
- ✅ Malicious code injection after repository compromise
- ✅ Build script tampering
- ✅ Compromised developer workstation attacks
- ✅ Man-in-the-middle attacks during distribution
- ✅ Package substitution attacks

**What SLSA L2 Does NOT Prevent:**
- ❌ Malicious code in source repository (requires code review)
- ❌ Compromised dependencies (requires SLSA L3+ dependency verification)
- ❌ GitHub Actions platform compromise (requires hermetic builds)

## Consequences

### Positive

**Security:**
- Cryptographic proof that releases match audited source code
- Protection against supply chain attacks at build time
- Consumer verification capability for all releases
- Industry-standard security posture for security-focused tool

**Trust:**
- Increased confidence from security-conscious users
- Alignment with OpenSSF best practices
- Demonstrates commitment to supply chain security
- Credibility as a security tool

**Operational:**
- Automated provenance generation (no manual steps)
- Zero additional secrets to manage (GitHub OIDC)
- PyPI Trusted Publishing integration
- Auditable build process

**Ecosystem:**
- Prepares for future ecosystem requirements (many ecosystems moving to SLSA)
- Foundation for SLSA L3 adoption (hermetic builds)
- Compatible with emerging security standards

### Negative

**Complexity:**
- Additional GitHub Actions workflow configuration
- Learning curve for maintainers unfamiliar with SLSA
- Documentation overhead for verification process

**Dependencies:**
- Dependency on SLSA GitHub Generator (maintained by SLSA team)
- Dependency on GitHub Actions OIDC (requires GitHub infrastructure)
- Dependency on PyPI attestation support

**Limitations:**
- SLSA L2 doesn't verify dependency provenance (future work)
- Doesn't prevent compromised source code (requires code review)
- Verification requires additional tools (`slsa-verifier`)

### Migration Path

**Phase 1: Foundation (Sprint 4 Week 1-2)**
- Create build workflow
- Add SLSA provenance generation
- Test with pre-release (v0.1.5-alpha1)

**Phase 2: Distribution (Sprint 4 Week 3)**
- Configure PyPI Trusted Publishing
- Upload provenance to GitHub Releases
- Verify end-to-end flow

**Phase 3: Documentation (Sprint 4 Week 4)**
- Write SLSA verification guide
- Add README badge
- Create consumer examples

**Phase 4: Validation (Sprint 4 Week 5)**
- External verification testing
- Security review
- Announce SLSA L2 compliance

### Future Enhancements (Post-Sprint 4)

**SLSA Build Level 3:**
- Hermetic builds (isolated build environment)
- Dependency provenance verification
- Non-falsifiable provenance

**Additional Security:**
- Dependency pinning with lock files
- Reproducible build verification
- Supply chain monitoring for dependencies

## Implementation

### Sprint 4 Deliverables

1. **GitHub Actions Workflow** (`.github/workflows/build.yml`)
   - Build automation with artifact hashing
   - SLSA provenance generation
   - PyPI publishing with attestations

2. **Security Documentation** (`docs/security/SLSA_VERIFICATION.md`)
   - Verification guide for consumers
   - Example verification commands
   - Provenance structure explanation

3. **README Updates**
   - SLSA L2 badge
   - Security section enhancement
   - Verification process overview

4. **ADR Documentation** (this document)
   - Decision rationale
   - Implementation details
   - Migration strategy

5. **Sprint Plan** (`docs/sprints/sprint-4-slsa-compliance.md`)
   - Detailed task breakdown
   - Timeline and milestones
   - Success metrics

### Success Metrics

**Technical:**
- [ ] SLSA provenance generated for all releases
- [ ] Provenance verifiable with `slsa-verifier`
- [ ] PyPI attestations published
- [ ] GitHub Releases include provenance

**Documentation:**
- [ ] Verification guide complete with examples
- [ ] README includes SLSA badge
- [ ] Consumer verification tested by external party

**Security:**
- [ ] OpenSSF Scorecard score improvement
- [ ] SLSA L2 badge displayed
- [ ] No manual secrets in build process

### Rollback Plan

If SLSA implementation causes issues:
1. Disable automated provenance generation (remove workflow job)
2. Continue manual releases with existing process
3. Document issues and reassess approach
4. Keep build workflow for future retry

Manual release process remains available as fallback.

## Related Decisions

- **ADR-0002**: Adopt development best practices (security framework foundation)
- **ADR-0003**: Use Python 3 with pytest/lxml/signxml stack (build toolchain)
- **ADR-0005**: Adopt Python ecosystem security framework (security posture)

## References

- [SLSA Specification v1.0](https://slsa.dev/spec/v1.0/)
- [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator)
- [SLSA Verifier](https://github.com/slsa-framework/slsa-verifier)
- [PyPI Attestations](https://docs.pypi.org/attestations/)
- [OpenSSF SLSA Guidance](https://openssf.org/blog/2023/12/14/slsa-build-level-1-requirements/)
- [GitHub OIDC for SLSA](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
