# ADR-027: Development Container Architecture

## Status

Accepted

## Context

The platform requires a consistent, optimized development environment that:

- Provides all necessary CLI tools for event-sourced microservices development
- Integrates with the Doppler-based secret management strategy (ADR-004)
- Minimizes container startup time for developer productivity
- Supports both local development and cloud-based development environments
- Maintains compatibility with VS Code Dev Containers and GitHub Codespaces

### Performance Requirements

Initial dev container builds were taking 2-3 minutes due to:
- CLI tool downloads (Doppler, Confluent, Wrangler, Neon)
- npm package installations (TypeScript, ESLint, Prettier, etc.)
- System package updates
- User-specific configuration

This impacted developer productivity, especially for frequent container rebuilds.

### Tool Requirements

The platform requires specific CLI tools for the technology stack:
- **Doppler CLI**: Secret management integration
- **Wrangler CLI**: Cloudflare Workers deployment
- **Neon CLI**: PostgreSQL database management
- **Confluent CLI**: Apache Kafka/event streaming
- **AWS CLI**: Cloud infrastructure management
- **Terraform**: Infrastructure as Code
- **Node.js ecosystem**: npm, pnpm, TypeScript, ESLint, Prettier

## Decision

We will implement a **Layered Docker Build Strategy** with runtime optimization for dev containers.

### Architecture

**Base Image**: Microsoft Universal Dev Container (`mcr.microsoft.com/devcontainers/universal:4-linux`)
- Ubuntu 24.04 LTS (Noble Numbat) with glibc 2.39 for modern tooling compatibility
- Provides Node.js, Python, Git, GitHub CLI pre-installed
- Includes common development tools and VS Code integration
- Enhanced support for Cloudflare Wrangler CLI debugging (requires glibc 2.35+)

**Custom Dockerfile Layer Structure**:
1. **System Dependencies Layer** (cached): Essential packages via apt-get
2. **CLI Tools Layer** (cached): Platform-specific CLI installations
3. **npm Global Packages Layer** (cached): Development tooling
4. **Verification Layer** (cached): Tool availability checks
5. **Runtime Configuration** (script): User-specific and token-based setup

### Implementation Strategy

#### Docker Layer Optimization (90% of setup cached)

**Dockerfile handles**:
- System package installation and updates
- CLI tool downloads and installation (Doppler, Confluent, Wrangler, Neon)
- npm global package installation (TypeScript, ESLint, Prettier, etc.)
- Tool verification and path configuration
- Permission setup for npm global directory

**Benefits of caching**:
- CLI downloads: ~60 seconds → cached
- npm installations: ~45 seconds → cached  
- System updates: ~30 seconds → cached
- Total cached: ~135 seconds (~90% of original setup time)

#### Runtime Script Optimization (10% of setup)

**setup-optimized.sh handles**:
- Git user configuration (user-specific, cannot be cached)
- Doppler token authentication and secret injection
- Environment variable setup for current session
- Verification of cached tool availability

**Runtime operations**:
- Git config: ~1 second
- Doppler authentication: ~2 seconds
- Secret injection: ~2 seconds
- Total runtime: ~5 seconds

### Feature Integration Strategy

**Managed via Features** (compatibility with base image):
- Java JDK 24 (Microsoft distribution)
- AWS CLI (official feature)
- Terraform (official feature)  
- Docker-outside-of-Docker (container access)

**Managed via Dockerfile** (optimization and custom requirements):
- Node.js tooling (uses existing from Universal image)
- Python tooling (uses existing from Universal image)
- Platform-specific CLI tools (Doppler, Confluent, Wrangler, Neon)
- npm development packages

### Security Integration

**Environment Variable Architecture** (per ADR-004):
- **Host-injected variables**: DEV_EMAIL, DEV_USER_NAME, DOPPLER_TOKEN
- **Doppler-managed secrets**: All API keys and sensitive tokens
- **Container environment**: Automatic secret injection via setup script

**Secret Management Flow**:
1. Host provides only DOPPLER_TOKEN (service token)
2. Container authenticates with Doppler using token
3. Doppler injects all platform secrets as environment variables
4. Secrets available for all CLI tools and development workflows

## Performance Impact

### Before Optimization
- **First Build**: ~3-4 minutes (image pull + full setup)
- **Rebuild**: ~2-3 minutes (full setup.sh execution)
- **Container Start**: ~2-3 minutes every time

### After Optimization  
- **First Build**: ~4-5 minutes (Docker build with layer caching)
- **Rebuild**: ~10-15 seconds (only runtime configuration)
- **Container Start**: ~5 seconds after first build

### Performance Metrics
- **85% reduction** in rebuild time
- **90% of operations** now cached in Docker layers
- **10% runtime operations** remain for user-specific configuration

## Implementation Details

### Dockerfile Strategy

```dockerfile
FROM mcr.microsoft.com/devcontainers/universal:2-linux

# Configure npm global directory (avoids permission issues)
ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global
ENV PATH=/usr/local/share/npm-global/bin:$PATH

# Layer 1: System dependencies (cached)
RUN apt-get update && apt-get install -y essential-packages

# Layer 2: CLI tools (cached)  
RUN curl ... | sh  # Doppler
RUN curl ... | sh  # Confluent
# ... other CLI installations

# Layer 3: npm packages (cached)
RUN npm install -g pnpm wrangler neonctl typescript eslint prettier

# Layer 4: Verification (cached)
RUN verify-all-tools-installed

USER codespace
```

### Container Configuration

```json
{
  "build": { "dockerfile": "Dockerfile" },
  "features": {
    "ghcr.io/devcontainers/features/java:1": { "version": "24" },
    "ghcr.io/devcontainers/features/aws-cli:1": {},
    "ghcr.io/devcontainers/features/terraform:1": {},
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {}
  },
  "postCreateCommand": "bash .devcontainer/setup-optimized.sh",
  "containerEnv": {
    "DOPPLER_TOKEN": "${localEnv:DOPPLER_TOKEN}",
    "DEV_EMAIL": "${localEnv:DEV_EMAIL}",
    "DEV_USER_NAME": "${localEnv:DEV_USER_NAME}"
  }
}
```

### Directory Structure

**onCreateCommand**: Creates workspace directory structure once
```bash
mkdir -p /workspaces/{packages,services,apps,contracts,tests,infra}
```

**postCreateCommand**: Runs optimized setup script for user configuration

## Consequences

### Positive

- **Developer Productivity**: 85% reduction in container startup time
- **Consistent Environment**: All developers get identical tool versions
- **Reliable Builds**: Docker layer caching eliminates download failures
- **Security Integration**: Seamless Doppler secret management
- **Scalable**: Easy to add new tools to cached layers
- **Cloud Compatible**: Works with both local Docker and cloud environments

### Negative

- **Initial Complexity**: More sophisticated build process than simple image
- **Dockerfile Maintenance**: Need to maintain custom Dockerfile
- **Debugging**: More layers to debug if build issues occur
- **Storage**: Larger image size due to pre-installed tools

### Risks and Mitigations

**Risk**: Dockerfile build failures block all development  
**Mitigation**: Comprehensive tool verification in build process

**Risk**: Tool version drift between cached image and runtime  
**Mitigation**: Version pinning and regular image rebuilds

**Risk**: Secret injection failures  
**Mitigation**: Graceful degradation in setup script with clear error messages

## Alternatives Considered

### Simple Image + Features Only
- **Pros**: Simple configuration, no custom Dockerfile
- **Cons**: No optimization, conflicts between features and existing tools
- **Decision**: Rejected due to performance impact and tool conflicts

### Fully Custom Base Image
- **Pros**: Maximum optimization, complete control
- **Cons**: No Universal image benefits, complex maintenance
- **Decision**: Rejected due to maintenance overhead

### Multiple Specialized Images
- **Pros**: Optimized for specific use cases
- **Cons**: Complexity, consistency issues
- **Decision**: Rejected for single dev container requirement

## Success Metrics

- **Build Time**: First build < 5 minutes, rebuilds < 30 seconds
- **Reliability**: 99% successful container builds
- **Tool Availability**: 100% of required CLI tools available post-build
- **Developer Satisfaction**: Positive feedback on container startup speed
- **Secret Integration**: Seamless Doppler secret injection in 100% of cases

## Future Evolution

### Potential Enhancements
- **Multi-architecture**: ARM64 support for Apple Silicon
- **Custom Features**: Convert CLI installations to reusable features
- **Version Management**: Automated tool version updates
- **Health Monitoring**: Container health checks and metrics

### Technology Considerations
- **Container Registry**: Consider private registry for optimized base images
- **Build Automation**: GitHub Actions for automated image updates
- **Testing**: Automated testing of container builds

## Related ADRs

- **ADR-004**: Security and Compliance Strategy (secret management integration)
- **ADR-015**: Deployment Strategy (CI/CD pipeline integration)
- **ADR-016**: Application Architecture Standards (development tooling requirements)

---

## Revision History

### 2025-10-11: Upgraded to Universal 4.x
- **Change**: Upgraded base image from `universal:2-linux` to `universal:4-linux`
- **Rationale**: Better Cloudflare Wrangler CLI debugging support requiring glibc 2.35+
- **Benefits**:
  - Ubuntu 24.04 LTS (Noble Numbat) with glibc 2.39
  - Improved compatibility with modern CLI tooling
  - Enhanced debugging capabilities for Cloudflare Workers
  - All existing functionality preserved (codespace user, nvm group)
- **Status**: Implemented

---
*Timestamp: 2025-10-01 (Updated: 2025-10-11)*
*Status: Implemented and optimized for ~85% performance improvement*