# ADR-005: Chainguard Zero-CVE Container Strategy

**Status**: Accepted
**Date**: 2024-12-11
**Deciders**: Platform Architecture Team, Security Team

## Context

Traditional container base images (Ubuntu, Alpine, Debian) frequently contain dozens to hundreds of CVEs, creating POA&M burden and compliance risk. Aegis must demonstrate a proactive security posture to achieve FedRAMP ATO.

**Problem Statement**:

- `ubuntu:22.04` typically has 50-100 CVEs
- `node:18` has 100-200 CVEs (includes OS + Node.js vulnerabilities)
- `nginx:latest` has 30-60 CVEs
- Manual patching of base images is time-consuming and error-prone

**FedRAMP Requirement**:

- NIST 800-53 SI-2: Flaw Remediation (30-day SLA for critical CVEs)
- Continuous monitoring of container images
- Evidence of vulnerability management process

## Decision

We will use **Chainguard Images** as the primary base images for all Aegis platform containers and recommend them for user workloads:

### 1. Chainguard Image Catalog

**What are Chainguard Images?**

- Minimal, hardened container images built on `wolfi` (Chainguard's Linux distribution)
- Zero CVEs at time of publication (patched within hours of disclosure)
- Cryptographically signed with cosign
- SBOM included with every image
- Rootless by default (non-root user `65532`)
- No shell, no package manager (attack surface minimization)

**Aegis Platform Images**:

```yaml
services:
  api:
    base_image: cgr.dev/chainguard/node:latest
    # Zero CVEs, includes Node.js 18+ runtime only

  workers:
    base_image: cgr.dev/chainguard/node:latest

  web:
    base_image: cgr.dev/chainguard/nginx:latest
    # Zero CVEs, nginx binary only, no shell

  postgres:
    base_image: cgr.dev/chainguard/postgres:latest
    # Zero CVEs, PostgreSQL 15+

  redis:
    base_image: cgr.dev/chainguard/redis:latest
```

### 2. Dockerfile Migration

**Before (Traditional Base Image)**:

```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 4000
CMD ["node", "dist/index.js"]

# Result: 150+ CVEs
```

**After (Chainguard Image)**:

```dockerfile
# Multi-stage build
FROM cgr.dev/chainguard/node:latest-dev AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production image
FROM cgr.dev/chainguard/node:latest
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./

# Chainguard images use non-root user 65532 by default
USER 65532
EXPOSE 4000
CMD ["node", "dist/index.js"]

# Result: 0 CVEs
```

**Key Differences**:

- `cgr.dev/chainguard/node:latest-dev` for build stage (includes npm, yarn)
- `cgr.dev/chainguard/node:latest` for runtime (Node.js binary only, no npm)
- No shell (`/bin/sh` not present)
- No package manager (apk, apt not available)
- Non-root user enforced

### 3. Chainguard Image Selection Guide

| Use Case          | Chainguard Image                     | Traditional Equivalent     |
| ----------------- | ------------------------------------ | -------------------------- |
| Node.js API       | `cgr.dev/chainguard/node:latest`     | `node:18-alpine`           |
| Python API        | `cgr.dev/chainguard/python:latest`   | `python:3.11-slim`         |
| Static web server | `cgr.dev/chainguard/nginx:latest`    | `nginx:alpine`             |
| PostgreSQL        | `cgr.dev/chainguard/postgres:latest` | `postgres:15`              |
| Redis             | `cgr.dev/chainguard/redis:latest`    | `redis:7-alpine`           |
| Go binary         | `cgr.dev/chainguard/static:latest`   | `gcr.io/distroless/static` |

### 4. Image Verification (cosign)

All Chainguard images are signed with cosign. Verify before use:

```bash
# Verify signature
cosign verify \
  --certificate-identity=https://github.com/chainguard-images/images/.github/workflows/release.yaml@refs/heads/main \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  cgr.dev/chainguard/node:latest

# Verify attestation (SBOM)
cosign verify-attestation \
  --type spdx \
  --certificate-identity=https://github.com/chainguard-images/images/.github/workflows/release.yaml@refs/heads/main \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  cgr.dev/chainguard/node:latest | jq '.payload | @base64d | fromjson'
```

### 5. Gatekeeper Policy Enforcement

Enforce Chainguard images (or other approved registries) via Gatekeeper:

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sAllowedRepos
metadata:
  name: require-chainguard-or-harbor
spec:
  match:
    kinds:
      - apiGroups: ['']
        kinds: ['Pod']
    namespaces: ['aegis-tenant-*']
  parameters:
    repos:
      - 'cgr.dev/chainguard' # Chainguard registry
      - 'harbor.aegis.dso.mil' # Internal Harbor registry
      - 'registry1.dso.mil/ironbank' # Platform One Iron Bank
```

### 6. CI/CD Integration

Update GitHub Actions workflow to use Chainguard images:

```yaml
name: Build with Chainguard Base

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build with Chainguard base
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: false
          tags: aegis/api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Scan for vulnerabilities (should be zero)
        run: |
          grype aegis/api:${{ github.sha }} --fail-on critical

      - name: Verify zero CVEs
        run: |
          CVE_COUNT=$(grype aegis/api:${{ github.sha }} -o json | jq '.matches | length')
          if [ "$CVE_COUNT" -gt 0 ]; then
            echo "❌ Found $CVE_COUNT CVEs (expected 0 with Chainguard base)"
            exit 1
          fi
          echo "✅ Zero CVEs confirmed"
```

### 7. Update Strategy

Chainguard images are updated continuously (multiple times per week):

```yaml
# Renovate Bot configuration (.github/renovate.json)
{
  'extends': ['config:base'],
  'packageRules':
    [
      {
        'matchDatasources': ['docker'],
        'matchPackagePatterns': ['^cgr.dev/chainguard/'],
        'schedule': ['every weekend'],
        'automerge': true,
        'automergeType': 'pr',
        'platformAutomerge': true,
      },
    ],
}
```

**Benefits**:

- Automated PRs for Chainguard image updates
- Auto-merge if CI passes (safe because Chainguard maintains zero CVEs)
- Weekly update cadence balances freshness with stability

### 8. Cost Considerations

**Chainguard Pricing** (as of 2024):

- **Free tier**: Public images (cgr.dev/chainguard/\*)
- **Enterprise tier**: $1000/month for private image builds and support

**Recommendation**:

- Use free tier for Aegis platform (sufficient for most use cases)
- Upgrade to Enterprise if custom base images needed

**ROI Calculation**:

```
Manual CVE remediation cost:
- 50 CVEs per image × 3 images = 150 CVEs
- 30 minutes per CVE triage = 75 hours
- $150/hour security engineer rate = $11,250
- Quarterly patching cycle = $45,000/year

Chainguard Enterprise cost: $12,000/year

Savings: $33,000/year + reduced compliance risk
```

## Consequences

### Positive

✅ **Zero CVEs**: Eliminates 90%+ of POA&M items from base image vulnerabilities
✅ **Faster ATO**: Reduced attack surface accelerates FedRAMP authorization
✅ **Compliance**: Meets NIST 800-53 SI-2 (Flaw Remediation) proactively
✅ **Minimal attack surface**: No shell, no package manager reduces exploit potential
✅ **Cryptographic verification**: cosign signatures provide supply chain security
✅ **Included SBOM**: SPDX SBOM embedded in every image

### Negative

❌ **Learning curve**: Teams must adapt to shell-less, minimal images
❌ **Debugging difficulty**: No shell means no `docker exec` for troubleshooting
❌ **Dependency constraints**: Cannot install packages at runtime (must use multi-stage builds)
❌ **Enterprise cost**: $1000/month if custom images needed

### Neutral

⚖️ **Slightly larger build images**: Multi-stage builds increase build time by ~30 seconds
⚖️ **Registry dependency**: Requires access to cgr.dev (mitigated by Harbor caching)

## Alternatives Considered

### Alternative 1: Google Distroless

**Rejected**: Good minimal images, but still contains 5-10 CVEs. Not as frequently updated as Chainguard.

### Alternative 2: Alpine Linux

**Rejected**: Typically 10-30 CVEs. `apk` package manager increases attack surface.

### Alternative 3: Ubuntu LTS (manual patching)

**Rejected**: 50-100 CVEs, requires dedicated team for patching, does not meet FedRAMP 30-day SLA.

### Alternative 4: Platform One Iron Bank

**Accepted for alternative**: Can be used alongside Chainguard. Iron Bank images are hardened and DISA STIG-compliant, but may contain 5-20 CVEs. Use for images not available in Chainguard catalog.

## Implementation Notes

- Sprint 0: Use Chainguard images for all Aegis platform services
- M5: Document Chainguard usage in Big Bang integration guide
- M7: Automated remediation engine generates Chainguard-based Dockerfiles

## References

- [Chainguard Images Catalog](https://images.chainguard.dev/)
- [Chainguard Documentation](https://edu.chainguard.dev/)
- [Platform One Iron Bank](https://p1.dso.mil/products/iron-bank)
- [NIST 800-53 SI-2: Flaw Remediation](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#!/control?version=5.1&number=SI-2)
