# ADR-001: DevContainer Architecture and Tooling Strategy

**Status**: Accepted
**Date**: 2025-09-28
**Deciders**: Human + Claude

## Context

Setting up a TypeScript development environment for agentic coding requires careful orchestration of multiple runtimes, tools, and databases. The project needs:

1. **Dual Runtime Support**: Deno for tooling/scripts + Node.js for application code
2. **Database Integration**: Kuzu (graph) + DuckDB (analytics) for semantic analysis
3. **Consistent Environment**: Reproducible development setup across different machines
4. **Tool Integration**: Multiple TypeScript tools, linters, analyzers, and transformers

The challenge was creating a DevContainer that properly configures all these components while maintaining clean separation of concerns.

## Decision

We decided to implement a **multi-runtime DevContainer** with the following architecture:

### Container Structure
- **Base Image**: `mcr.microsoft.com/devcontainers/typescript-node:1-22-bookworm`
- **Runtime Separation**:
  - Deno for scripts in `scripts/` and `bench/` directories
  - Node.js for application code in `src/` and `tests/`
- **Build Context**: DevContainer directory with parent directory access
- **File Organization**: Project files mounted via DevContainer, not copied during build

### Key Architectural Decisions

1. **No File Copying in Docker Build**
   - DevContainer automatically mounts project at `/workspace/`
   - Eliminated redundant COPY commands that were causing build failures
   - Configuration files accessed via mount, not copied during build

2. **JSR Package Management for Deno**
   - Migrated from `deno.land/std` URLs to JSR packages (`jsr:@std/...`)
   - Proper import maps in `deno.json` for consistent module resolution
   - Version-locked to `^0.224.0` to match container Deno version

3. **Graceful Degradation for Optional Tools**
   - Kuzu installation made optional (commented out due to archive structure changes)
   - Init script checks for tool availability before attempting operations
   - Clear warning messages when optional tools are unavailable

4. **Proper Permission Management**
   - Cache directories created with correct ownership (`node` user)
   - Git configuration set during container initialization
   - Workspace permissions managed during Docker build

## Consequences

### Positive
- **Fast Container Builds**: No file copying means faster rebuilds
- **Consistent Environment**: All developers get identical tool versions
- **Runtime Separation**: Clear boundaries between Deno (tooling) and Node (app)
- **Graceful Failures**: Missing tools don't break the entire setup
- **Modern Package Management**: JSR provides better dependency resolution

### Negative
- **Complex Configuration**: Multiple configuration files need coordination
- **Version Dependencies**: JSR packages must match Deno version in container
- **Tool Installation Complexity**: Some tools (Kuzu) have brittle installation scripts
- **Initial Setup Time**: First build installs many tools and dependencies

### Risks
- **Version Drift**: Container Deno version could drift from JSR package versions
- **Tool Availability**: Upstream changes in tool distribution (like Kuzu) can break builds
- **Configuration Complexity**: Multiple runtime environments increase cognitive load

## Implementation Details

### File Structure Created
```
.devcontainer/
├── Dockerfile              # Multi-runtime environment setup
├── devcontainer.json       # VS Code integration and commands
└── .env                    # Environment variables

config/
├── deno.json              # Deno runtime configuration
├── tsconfig.node.json     # Node.js TypeScript configuration
├── .eslintrc.js          # ESLint rules
└── .prettierrc           # Code formatting

hooks/                     # Git hooks (placeholder)
scripts/                   # Deno-powered tooling
```

### Key Configuration Files

**devcontainer.json**:
- Build context set to parent directory
- PostCreateCommand handles git config, cache setup, dependency installation
- Proper port forwarding for development servers

**deno.json**:
- JSR imports for standard library (`jsr:@std/fmt@^0.224.0`)
- Runtime separation via `deno.enablePaths` and `deno.disablePaths`
- Task definitions for common operations

**Dockerfile**:
- System tools: Rust, Deno, Bun, DuckDB, various CLI tools
- No file copying (relies on DevContainer mount)
- Proper directory structure and permissions

### Critical Fixes Applied

1. **Import Path Resolution**
   - Fixed `@std/fmt/colors.ts` → `@std/fmt/colors`
   - Updated all scripts to use clean JSR imports
   - Proper version constraints in import map

2. **Permission Issues**
   - Added `chown -R node:node /workspace` in Dockerfile
   - Cache directory creation with proper permissions
   - Git configuration in postCreateCommand

3. **Build Context Problems**
   - Changed from copying files to mounting them
   - Proper build context configuration
   - Eliminated path doubling issues

## Alternatives Considered

1. **Single Runtime (Node-only)**
   - Rejected: Would lose Deno's superior tooling capabilities
   - Deno provides better script execution, import maps, and built-in utilities

2. **Separate Containers**
   - Rejected: Would complicate development workflow
   - Single container provides better integration and simpler mental model

3. **File Copying Strategy**
   - Rejected: Caused build failures and redundancy
   - DevContainer mounting is more efficient and maintains file sync

## Follow-up Actions

1. **Fix Kuzu Installation**: Research current Kuzu CLI distribution format
2. **Optimize Container Size**: Review installed tools for necessity
3. **Add Development Scripts**: Create common development task automation
4. **Documentation**: Create developer onboarding guide for container usage

## Related Decisions

- ADR-002: Runtime Separation Strategy (planned)
- ADR-003: Database Integration Patterns (planned)
- ADR-004: Tool Chain Selection (planned)