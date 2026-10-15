# ADR 002: Docker Multi-Stage Build with Alpine Base Image

**Status**: Accepted

**Date**: 2025-10-05

**Context**:
The feature specification requires a "Dockerizable setup independent of host system environment/packages" (FR-005). We needed to determine the optimal Docker configuration strategy that balances:
- Image size and deployment efficiency
- Build performance and caching
- Security (attack surface reduction)
- Development and production parity
- Node.js 20 LTS compatibility
- Separation of build-time vs runtime dependencies

The Docker setup must support TypeScript compilation, efficient dependency management, and production-ready deployment without relying on host system configuration.

**Decision**:
We adopted a **multi-stage Docker build** with **Alpine Linux base image** (node:20-alpine).

**Architecture**:
```dockerfile
Stage 1 (deps):     Install all dependencies (dev + prod)
Stage 2 (builder):  Compile TypeScript to JavaScript
Stage 3 (prod-deps): Install production dependencies only
Stage 4 (runner):   Final runtime image with compiled code
```

**Rationale**:
- **Image Size**: Alpine base reduces image size to 40-50MB vs 200MB+ for Debian-based images. Multi-stage builds eliminate dev dependencies from final image, reducing size by 50-70%.
- **Security**: Minimal Alpine image reduces attack surface. Non-root user (nodejs:1001) enhances container security. No shell or package managers in final image.
- **Build Efficiency**: Separate dependency stages enable Docker layer caching. Rebuilds only affected layers when code changes.
- **Dependency Separation**: Build dependencies (TypeScript, Vitest) excluded from production image. Only compiled JavaScript and runtime dependencies in final image.
- **Node.js LTS Support**: node:20-alpine officially supports Node.js 20 LTS, meeting constitutional requirements.

**Alternatives Considered**:
1. **Single-stage build**:
   - Pros: Simpler Dockerfile, easier to understand
   - Cons: Bloated images with dev dependencies, larger attack surface, slower deployments
   - Rejected: Image size and security concerns

2. **Debian-based images (node:20)**:
   - Pros: More packages available, familiar environment
   - Cons: 200MB+ base image, unnecessary packages, larger attack surface
   - Rejected: Excessive size for simple health check server

3. **Distroless images**:
   - Pros: Maximum security, minimal attack surface
   - Cons: Debugging complexity, overkill for current requirements, steeper learning curve
   - Rejected: Over-engineered for initial implementation

**Consequences**:

**Positive**:
- 50-70% reduction in final image size improves deployment speed and storage costs
- Build caching reduces rebuild time to seconds when only application code changes
- Non-root user (nodejs) enhances security posture
- Minimal Alpine base reduces CVE exposure and attack surface
- Clear separation between build and runtime environments
- Production images contain only necessary runtime dependencies

**Negative**:
- Alpine uses musl libc instead of glibc (potential compatibility issues with native modules)
- Debugging production containers more challenging without shell tools
- Multi-stage builds increase Dockerfile complexity for developers unfamiliar with pattern
- Build times increase for fresh builds (mitigated by layer caching)

**Neutral**:
- Requires Docker BuildKit for optimal caching (standard in modern Docker)
- Four-stage build process requires understanding of layer dependencies
- Alpine package manager (apk) differs from apt/yum if additional packages needed

**Implementation Details**:
```dockerfile
# Stage 1: Install all dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --include=dev

# Stage 2: Build TypeScript
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production dependencies only
FROM node:20-alpine AS prod-deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

# Stage 4: Runtime image
FROM node:20-alpine AS runner
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
USER nodejs
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

**Build and Deployment**:
- `docker build -t readme-kit:latest .` builds production image
- `docker-compose.yml` for local development and testing
- Image can be pushed to container registry for deployment

**Security Enhancements**:
- Non-root user (nodejs:1001) prevents privilege escalation
- Minimal base image reduces vulnerability exposure
- No shell in final image prevents container escape techniques
- Read-only filesystem possible for additional hardening (future consideration)

**References**:
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Alpine Linux Docker Images](https://hub.docker.com/_/alpine)
- Research findings: `/Users/abhishek/Documents/Personal/readme-kit/specs/001-create-basic-server/research.md`
- Feature specification: `/Users/abhishek/Documents/Personal/readme-kit/specs/001-create-basic-server/spec.md`
