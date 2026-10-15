# ADR 0002: SBOM Format and Digital Signature Choice

**Status**: Accepted  
**Date**: 2026-01-05  
**Context**: Feature 003 - Automated Binary Release Pipeline  
**Related**: [spec.md](../../specs/003-automated-release-pipeline/spec.md), [research.md](../../specs/003-automated-release-pipeline/research.md)

## Context

To ensure software supply chain security and transparency, we need to:

1. Generate Software Bill of Materials (SBOM) for all releases
2. Provide digital signatures for critical artifacts (SBOM and checksums)
3. Enable users to verify the integrity and authenticity of downloaded binaries

This decision records our choices for SBOM format and signature mechanism.

## Decision

### SBOM Format: CycloneDX 1.4 (JSON)

We will use **CycloneDX 1.4** in **JSON format** for all SBOM generation.

**Tool**: `anchore/sbom-action` GitHub Action

**Rationale**:

1. **Industry Standard**: CycloneDX is widely adopted and supported by security tools (Dependency-Track, OWASP, etc.)
2. **Comprehensive**: Captures dependencies, licenses, vulnerabilities, and component relationships
3. **Machine-Readable**: JSON format is easy to parse and integrate with automated tools
4. **GitHub Actions Integration**: `anchore/sbom-action` provides seamless integration with minimal configuration
5. **Multi-Language Support**: Supports .NET, Go, Python, Java, JavaScript, and more
6. **Security**: Using pinned commit SHA (`61119d458adab75f756bc0b9e4bde25725f86a7a`) prevents supply chain attacks
7. **Maintainability**: Reduces custom script complexity (50+ lines reduced to 4 lines of YAML)

**Alternative Considered**: SPDX 2.3

- **Pros**: SPDX is also widely adopted, supported by Linux Foundation
- **Cons**: Less comprehensive for vulnerability tracking compared to CycloneDX; JSON tooling less mature

### Digital Signature: GPG (GNU Privacy Guard)

We will use **GPG** with RSA 4096-bit keys to sign SBOM and SHA256SUMS files.

**Implementation**: `.github/scripts/sign-artifacts.sh`

**Signed Artifacts**:

1. `wt-v<version>-sbom.json.asc` (SBOM signature)
2. `SHA256SUMS.asc` (Checksum file signature)

**Rationale**:

1. **Ubiquitous**: GPG is available on all platforms (Windows, Linux, macOS) and widely understood
2. **Trust Model**: Supports web-of-trust and key verification through public key servers
3. **GitHub Integration**: GitHub Actions supports GPG signing via secrets
4. **Standard**: Used by major open-source projects (Debian, Fedora, Apache Foundation)
5. **Free**: No external service fees (unlike commercial certificate authorities)
6. **Scriptable**: Easy to automate in CI/CD pipelines

**Alternative Considered**: Sigstore/Cosign

- **Pros**: Modern, keyless signing, integrated with OIDC, supports container images
- **Cons**: Requires external Sigstore infrastructure; less familiar to developers; primarily container-focused

**Alternative Considered**: GitHub Actions Attestations

- **Pros**: Native GitHub integration, no key management needed
- **Cons**: Verification requires GitHub CLI or API; not widely adopted outside GitHub ecosystem

## Consequences

### Positive

- **Transparency**: Users can verify all dependencies in the binary
- **Security**: Digital signatures prevent tampering and ensure authenticity
- **Automation**: SBOM generation is fully automated via GitHub Actions
- **Compliance**: Meets NTIA minimum elements for SBOM requirements
- **Trust**: GPG signatures provide cryptographic proof of artifact origin

### Negative

- **Key Management**: GPG private key must be securely stored in GitHub Secrets
- **Key Rotation**: Requires manual process to rotate GPG keys and re-sign old releases
- **User Friction**: Users must import GPG public key before verification (one-time setup)
- **File Size**: SBOM and signature files add ~100-500 KB per release

### Maintenance

- **GPG Key Expiration**: Keys should be renewed every 2 years
- **Public Key Distribution**: Public key is published in `/docs/GPG_PUBLIC_KEY.asc`
- **SBOM Updates**: If SBOM format changes, update workflow and documentation

## Implementation Notes

### SBOM Generation Workflow

```yaml
- name: Generate SBOM
  uses: anchore/sbom-action@61119d458adab75f756bc0b9e4bde25725f86a7a # v0.17.2
  with:
    path: ./wt.cli
    format: cyclonedx-json
    output-file: release-assets/wt-${{ needs.calculate-version.outputs.version }}-sbom.json
```

### GPG Signing Workflow

```bash
# Import GPG key from secrets
echo "$GPG_PRIVATE_KEY" | gpg --batch --import

# Sign SBOM
gpg --batch --yes --passphrase "$GPG_PASSPHRASE" \
  --pinentry-mode loopback \
  --armor --detach-sign wt-v1.0.0-sbom.json

# Sign checksums
gpg --batch --yes --passphrase "$GPG_PASSPHRASE" \
  --pinentry-mode loopback \
  --armor --detach-sign SHA256SUMS
```

### User Verification (Documented in quickstart.md)

```bash
# Import public key (one-time)
curl -fsSL https://raw.githubusercontent.com/kuju63/wt/main/docs/GPG_PUBLIC_KEY.asc | gpg --import

# Verify SBOM signature
gpg --verify wt-v1.0.0-sbom.json.asc wt-v1.0.0-sbom.json

# Verify checksum signature
gpg --verify SHA256SUMS.asc SHA256SUMS
```

## References

- [CycloneDX Specification](https://cyclonedx.org/specification/overview/)
- [NTIA SBOM Minimum Elements](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom)
- [GNU Privacy Guard](https://gnupg.org/)
- [Anchore SBOM Action](https://github.com/anchore/sbom-action)
- [GitHub Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## Review Schedule

This ADR should be reviewed:

- Before major version 1.0.0 release
- If SBOM format standards change (CycloneDX 2.0 release)
- If GPG key rotation is required
- If Sigstore/Cosign adoption becomes widespread
