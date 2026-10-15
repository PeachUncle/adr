# ADR-001: TypeScript NPM Package Setup for Mastra Compatibility

## Purpose
This document records the architecture decision for setting up PackFS as a TypeScript NPM package with dual module support (ESM/CommonJS) to ensure compatibility with Mastra and other TypeScript LLM frameworks.

## Classification
- **Domain:** Technology
- **Stability:** Semi-stable
- **Abstraction:** Structural
- **Confidence:** Established
- **Lifecycle Stage:** Planning

## Content

### Status
Accepted

### Context
PackFS is being developed as an NPM package that will be consumed by LLM agent frameworks, with the first consumer being a Mastra-based project. Modern TypeScript frameworks have varying requirements for module formats, and compatibility issues can arise from:

1. **Module Format Conflicts**: Some frameworks expect ESM modules, others CommonJS
2. **TypeScript Configuration**: Different frameworks may have different TypeScript compilation targets
3. **Export Structure**: Framework integration requires specific export patterns
4. **Dependency Management**: Peer dependencies and optional dependencies need careful handling
5. **Build Tooling**: The build process must generate compatible outputs for all target frameworks

Research into Mastra and modern TypeScript LLM frameworks revealed that:
- Mastra uses modern ESM modules with TypeScript
- Most frameworks support both ESM and CommonJS but prefer ESM
- Framework-specific adapters are expected to be provided as separate entry points
- Type definitions must be comprehensive and accurately reflect runtime behavior
- Build outputs should include both formats for maximum compatibility

### Decision
We will configure PackFS as a dual-module TypeScript NPM package with the following architecture:

1. **Dual Module Output**: Generate both ESM and CommonJS builds using TypeScript compiler with separate configurations
2. **Multiple Entry Points**: Provide framework-specific entry points via package.json exports field
3. **Comprehensive Type Definitions**: Export all public types and ensure full TypeScript compatibility
4. **Modern TypeScript Configuration**: Target ES2020 with NodeNext module resolution
5. **Framework Adapters**: Create dedicated adapter modules for each supported framework (Mastra, LangChain, etc.)

### Consequences

#### Benefits
- **Maximum Compatibility**: Both ESM and CommonJS consumers can use the package
- **Framework-Specific Optimization**: Dedicated adapters provide optimal integration patterns
- **Type Safety**: Full TypeScript support with comprehensive type definitions
- **Future-Proof**: Modern configuration supports evolving JavaScript ecosystem
- **Developer Experience**: Clear entry points and examples for each framework
- **Maintainability**: Separate configurations allow independent optimization

#### Drawbacks
- **Build Complexity**: Requires multiple TypeScript configurations and build steps
- **Bundle Size**: Dual outputs increase package size
- **Maintenance Overhead**: Multiple entry points require more testing and documentation
- **Configuration Complexity**: More complex package.json and tsconfig setup

#### Trade-offs
- **Simplicity vs Compatibility**: Chose compatibility over simple single-format output
- **Bundle Size vs Accessibility**: Larger package size for broader framework support
- **Maintenance vs Features**: More maintenance burden for better framework integration

### Alternatives Considered

#### Alternative 1: ESM-Only Package
- **Description**: Publish only ESM modules with "type": "module"
- **Pros**: Simpler build process, smaller bundle, modern standard
- **Cons**: Excludes CommonJS consumers, potential compatibility issues
- **Why Rejected**: Would limit adoption by frameworks still using CommonJS

#### Alternative 2: CommonJS-Only Package
- **Description**: Publish only CommonJS modules
- **Pros**: Maximum compatibility with legacy systems, simpler build
- **Cons**: Not future-proof, suboptimal for modern frameworks like Mastra
- **Why Rejected**: Mastra and modern frameworks prefer ESM

#### Alternative 3: Single Entry Point with Runtime Detection
- **Description**: Use single entry point with runtime module format detection
- **Pros**: Simpler package structure, automatic format selection
- **Cons**: Runtime overhead, complex implementation, potential edge cases
- **Why Rejected**: Adds unnecessary complexity and potential failure points

#### Alternative 4: Separate Packages for Each Format
- **Description**: Publish @packfs/esm and @packfs/cjs as separate packages
- **Pros**: Clear separation, optimized for each format
- **Cons**: Package management complexity, version synchronization issues
- **Why Rejected**: Creates maintenance burden and user confusion

### Implementation Notes

#### Package Structure
```
src/
├── core/                     # Core layer components
├── integration/              # Integration layer with framework adapters
├── backends/                 # Backend layer implementations
├── types/                    # TypeScript type definitions
└── index.ts                  # Main entry point
```

#### TypeScript Configurations
- **tsconfig.json**: Base configuration with NodeNext module resolution
- **tsconfig.esm.json**: ESM-specific build targeting dist/esm/
- **tsconfig.cjs.json**: CommonJS-specific build targeting dist/cjs/

#### Package.json Key Fields
```json
{
  "type": "module",
  "main": "./dist/cjs/index.js",
  "module": "./dist/esm/index.js",
  "types": "./dist/esm/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/esm/index.js",
      "require": "./dist/cjs/index.js",
      "types": "./dist/esm/index.d.ts"
    },
    "./mastra": {
      "import": "./dist/esm/integration/frameworks/mastra.js",
      "require": "./dist/cjs/integration/frameworks/mastra.js",
      "types": "./dist/esm/integration/frameworks/mastra.d.ts"
    }
  }
}
```

#### Build Process
1. Clean previous builds
2. Build ESM version with tsconfig.esm.json
3. Build CommonJS version with tsconfig.cjs.json
4. Add package.json marker to CJS output directory
5. Run tests against both outputs

#### Framework Integration Pattern
Each framework adapter will:
- Import core PackFS functionality
- Provide framework-specific tool definitions
- Handle framework-specific error patterns
- Include usage examples and documentation

### Compliance Verification

#### Build Verification
- Both ESM and CommonJS outputs are generated successfully
- Type definitions are complete and accurate
- All entry points resolve correctly
- No circular dependencies exist

#### Compatibility Testing
- Test imports work in both ESM and CommonJS environments
- Verify Mastra integration works with generated adapters
- Test with other major frameworks (LangChain, AutoGPT, etc.)
- Validate TypeScript compilation in consuming projects

#### Quality Checks
- All public APIs have comprehensive type definitions
- Framework adapters follow consistent patterns
- Documentation includes examples for each supported framework
- Performance benchmarks meet established criteria

## Relationships
- **Parent Nodes:** [decisions/decision_index.md]
- **Child Nodes:** None
- **Related Nodes:** 
  - [foundation/project_definition.md] - implements - Supports project objective of framework integration
  - [foundation/principles.md] - follows - Implements framework-agnostic and TypeScript-first principles
  - [cross_cutting/api_design_guide.md] - guides - API design follows established patterns
  - [processes/creation.md] - informs - Creation process includes build configuration setup

## Navigation Guidance
- **Access Context:** Use this document when setting up the build process or understanding module format decisions
- **Common Next Steps:** After reviewing this decision, explore the API design guide and creation processes
- **Related Tasks:** Package setup, build configuration, framework integration, TypeScript configuration
- **Update Patterns:** This document should be updated if module format requirements change or new frameworks are supported

## Metadata
- **Created:** 2025-06-18
- **Last Updated:** 2025-06-18
- **Updated By:** AI Agent (Cline)
- **Deciders:** Project maintainer, based on research into Mastra and TypeScript framework requirements

## Change History
- 2025-06-18: Initial creation based on research into TypeScript NPM package best practices for Mastra compatibility
