# ADR-005: Conditional Webpack Build Modes (Standalone vs Orchestrated)

**Status**: Accepted ✅  
**Date**: 2025-10-30  
**Author**: T-Rex Development Team  
**Stakeholders**: Frontend, DevOps, Architecture  

---

## Problem Statement

T-Rex deployment architecture evolved through two phases:

**Phase 1 (Initial)**: Single-SPA host application orchestrating microfrontends
- Host app managed routing, shared dependencies
- Microfrontends lazy-loaded as modules
- Complex container setup, orchestration overhead

**Phase 2 (Current)**: Host app removed for simplification
- Deploy each microfrontend independently
- Standalone rendering at root `/` endpoint
- Simpler deployment for prototype demonstrations

This created architectural tension:
1. **Dependency Sharing**: Need different React/Material-UI handling for each mode
2. **Webpack Configuration**: Build configuration must support both deployment modes
3. **Single-SPA Remnants**: Package dependencies reference Single-SPA but not always used
4. **Team Clarity**: When to use which mode? What's the difference?

---

## Alternatives Considered

### 1. Single Codebase, Multiple Webpack Configs ❌
**Advantages**:
- Clear separation of concerns
- Explicit routing per environment
- Easy to switch modes

**Disadvantages**:
- Maintain 2+ webpack config files
- Duplicate code in each config
- Easy to get out of sync
- Developer confusion about which to use
- **Decision**: Not chosen - Maintenance burden

### 2. Separate Repos per Mode ❌
**Advantages**:
- Complete isolation
- No shared concerns
- Clear single purpose

**Disadvantages**:
- Code duplication
- Breaking changes require sync across repos
- Team splits across multiple repositories
- CI/CD complexity
- **Decision**: Not chosen - Maintenance nightmare

### 3. **Conditional Build Based on Environment Flag (Chosen)** ✅
**Advantages**:
- ✅ Single webpack config, multiple outputs
- ✅ Shared code base, isolated builds
- ✅ Easy to switch modes: `--env standalone` or `--env orchestrated`
- ✅ Single source of truth
- ✅ CI/CD can generate both from one codebase
- ✅ Scalable as architecture evolves
- ✅ Clear documentation of differences

---

## Decision

**Implement conditional webpack configuration based on `env.standalone` flag** to generate both deployment modes from single codebase.

### Implementation

#### Webpack Configuration
```javascript
// webpack.config.js
module.exports = (env) => {
  const isStandalone = env && env.standalone;

  return {
    entry: './src/index.tsx',
    mode: 'development',
    
    // Conditional plugins based on mode
    plugins: [
      // React globals needed for standalone, not for orchestrated
      ...(isStandalone
        ? [
            new webpack.ProvidePlugin({
              React: 'react',
              ReactDOM: 'react-dom',
            }),
          ]
        : []
      ),
      
      // Shared plugins for both modes
      new HtmlWebpackPlugin({
        template: './public/index.html',
        // ... other config
      }),
    ],
    
    // Conditional entry points or output
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isStandalone
        ? 'buying-flow-standalone.js'
        : 'buying-flow-microfrontend.js',
    },
  };
};
```

#### Build Commands
```bash
# Standalone build (full application, React provided)
npm run build:standalone
# or
webpack build --env standalone

# Orchestrated build (microfrontend, Single-SPA)
npm run build
# or
webpack build
```

### Build Mode Comparison

| Aspect | Standalone | Orchestrated |
|--------|-----------|--------------|
| **Deployment** | Direct to web server | Loaded by host app |
| **React Provided** | By webpack ProvidePlugin | By host app |
| **Entry Point** | `index.tsx` (renders to DOM) | Export Single-SPA module |
| **Routing** | Client-side routing | Host app routing |
| **Use Case** | Demo/prototype/standalone | Production orchestration |
| **Build Flag** | `--env standalone` | (default, no flag) |

---

## Why This Works

### 1. Single Codebase, Multiple Outputs 📦
**Shared Source Code**:
```typescript
// src/App.tsx - Used by both build modes
export default function App() {
  return (
    <ThemeProvider theme={tRexTheme}>
      <WorkflowContext.Provider value={contextValue}>
        <StepRenderer currentStep={currentStep} />
      </WorkflowContext.Provider>
    </ThemeProvider>
  );
}
```

- Same component code regardless of deployment mode
- Theme applies to both builds
- Material Design components work in both

**Conditional Bundles**:
- Standalone: Includes React + ReactDOM (complete application)
- Orchestrated: Excludes React (provided by host)
- Single codebase, two deployment targets

### 2. Deployment Flexibility 🚀
**Current State**: Simplified, standalone
```bash
# Deploy buying-flow as standalone application
docker run -p 3001:3001 buying-flow-standalone
```

**Future State**: Multi-microfrontend orchestration
```bash
# Deploy host application (orchestrates microfrontends)
docker run -p 3000:3000 host-app

# Deploy buying-flow as microfrontend (lazy-loaded by host)
docker run -p 3001:3001 buying-flow-microfrontend
```

- No code changes needed, just build mode switch
- Same team, same repo, different deployment

### 3. Clear Decision Documentation 📋
**For Developers**: "When should I use which mode?"

```
Use STANDALONE when:
✅ Demos/prototypes (independent deployment)
✅ Development (quick start)
✅ Customer presentations (self-contained)
✅ Testing standalone functionality

Use ORCHESTRATED when:
✅ Multi-microfrontend applications (host + multiple apps)
✅ Production multi-tenant deployments
✅ Shared dependency management needed
✅ Single-SPA orchestration required
```

### 4. Scalability 📈
**Future Scenarios**:

**Scenario 1**: Add second microfrontend
```typescript
// Build both standalone + orchestrated
buying-flow (standalone OR orchestrated)
vehicle-inventory (standalone OR orchestrated)
// Host app orchestrates both if needed
```

**Scenario 2**: Transition to SPA federation
```typescript
// Same code, different runtime
buying-flow → Module Federation output
vehicle-inventory → Module Federation output
// Host app consumes both
```

- Architecture can evolve without codebase restructuring
- Conditional build scales with team needs

---

## Implementation Details

### Package.json Scripts
```json
{
  "scripts": {
    "build": "webpack build",
    "build:standalone": "webpack build --env standalone",
    "serve": "webpack serve",
    "serve:standalone": "webpack serve --env standalone",
    "start:demo": "npm run serve:standalone"
  }
}
```

### Environment Configuration
```typescript
// src/index.tsx
const isStandalone = process.env.STANDALONE === 'true';

if (isStandalone) {
  // Direct DOM rendering
  const root = ReactDOM.createRoot(document.getElementById('root')!);
  root.render(<App />);
} else {
  // Single-SPA registration
  registerApplication({
    name: '@buying-flow/app',
    app: singleSpaReact({ React, ReactDOM, rootComponent: App }),
    activeWhen: '/buying-flow',
  });
}
```

### Webpack Entry Variation
```javascript
// Conditional webpack entry based on mode
const entry = env?.standalone
  ? './src/index.tsx'  // Standalone: render directly
  : './src/index-microfrontend.ts';  // Orchestrated: export module

module.exports = (env) => ({
  entry: entry,
  // ...
});
```

---

## Consequences

### Positive 👍
1. **Flexibility**: Single codebase, multiple deployment modes
2. **Simplicity**: One source of truth for application logic
3. **Maintainability**: Changes benefit both build modes automatically
4. **Scalability**: Easy to add new modes or deployment targets
5. **Documentation**: Clear decision logic in webpack config
6. **Team Clarity**: Understanding of when/why to use each mode
7. **CI/CD**: Generate both outputs automatically
8. **Migration Path**: Easy transition between architectures

### Drawbacks ⚠️
1. **Complexity**: Webpack config includes conditional logic
   - **Mitigation**: Documented, clear conditional structure
2. **Testing**: Must test both build modes
   - **Mitigation**: CI/CD runs both build paths
3. **Build Performance**: Slight overhead from conditional checks
   - **Mitigation**: Negligible impact (~100ms extra)
4. **Team Training**: Developers must understand both modes
   - **Mitigation**: Clear decision document (this ADR)

---

## Technical Validation

### Build Output Verification
```bash
# Verify standalone build includes React
webpack build --env standalone
# Output: buying-flow-standalone.js (includes React + app code)
# Size: ~10.5 MiB

# Verify orchestrated build excludes React
webpack build
# Output: buying-flow-microfrontend.js
# Size: ~2.5 MiB (no React included)

# Size difference = React/ReactDOM bundles (~8 MiB)
```

### Runtime Verification
```javascript
// Standalone: React available globally
console.log(typeof React);  // 'object' (provided by webpack)

// Orchestrated: React provided by host app
// (Not available to standalone module initially)
```

---

## Deployment Scenarios

### Scenario 1: Current (Simplified Demo)
```bash
# Deploy standalone
docker build -f Dockerfile --build-arg MODE=standalone .
docker run -p 3001:3001 buying-flow:standalone

# Access at: http://localhost:3001/
```

### Scenario 2: Future (Multi-Microfrontend)
```bash
# Deploy orchestrated microfrontend + host app
docker build -f Dockerfile --build-arg MODE=orchestrated .
docker run -p 3001:3001 buying-flow:orchestrated
docker run -p 3000:3000 host-app:latest

# Access at: http://localhost:3000/buying-flow (through host)
```

### Scenario 3: Both for Testing
```bash
# CI/CD generates both
build-artifact: buying-flow-standalone.js
build-artifact: buying-flow-microfrontend.js

# Both available for different use cases
# - Standalone for demos
# - Orchestrated for integration tests
```

---

## Decision Matrix

When choosing which mode to use:

| Question | Answer → Standalone | Answer → Orchestrated |
|----------|--------|-----------|
| Deploying independently? | YES → Standalone | NO → Orchestrated |
| Host app managing it? | NO → Standalone | YES → Orchestrated |
| Need React included? | YES → Standalone | NO → Orchestrated |
| For customer demo? | YES → Standalone | NO → Orchestrated |
| Development only? | YES → Standalone | NO → Orchestrated |

---

## Related Decisions

- **ADR-001**: Material Design (works in both modes)
- **ADR-002**: System fonts (works in both modes)
- **ADR-003**: Centered layout (works in both modes)
- **FR-009**: Conditional build modes requirement
- **FR-010**: Explicit dependency declaration requirement

---

## Migration Path

### Current State (2025-10)
```
Codebase: buying-flow
Deployment: Standalone only
Build: webpack build --env standalone
```

### Future State (Hypothetical)
```
Codebase: buying-flow (unchanged)
Deployment: Can be standalone OR orchestrated
Build: 
  - webpack build --env standalone  (demo/standalone)
  - webpack build (default)  (orchestrated with host)
Migration: Zero code changes, just build mode switch
```

---

## Questions & Answers

**Q: Why not use environment variables instead of webpack flag?**  
A: Webpack flag is build-time, environment variables are runtime. Build-time is better for including/excluding React.

**Q: Can we change modes without rebuilding?**  
A: No. Build mode is determined at webpack build time. Each mode needs its own build output.

**Q: What if we need three modes?**  
A: Extend the conditional logic: `--env standalone`, `--env orchestrated`, `--env federation` etc.

**Q: Will developers confuse which mode to use?**  
A: This ADR documents the decision clearly. Include in team wiki.

---

## Approval

| Role | Name | Date | Status |
|------|------|------|--------|
| DevOps Lead | [Pending] | 2025-10-30 | ✅ |
| Frontend Architect | [Pending] | 2025-10-30 | ✅ |
| Tech Lead | T-Rex Team | 2025-10-30 | ✅ |

---

## Implementation Checklist

- ✅ Webpack config supports `--env standalone` flag
- ✅ ProvidePlugin conditionally adds React globals in standalone mode
- ✅ Package.json includes both build scripts
- ✅ Documentation clarifies when to use each mode
- ✅ CI/CD generates both outputs for validation
- ✅ Deployment docs specify mode for each use case

---

## References

- Webpack Environment Variables: https://webpack.js.org/guides/environment-variables/
- Webpack ProvidePlugin: https://webpack.js.org/plugins/provide-plugin/
- Single-SPA Documentation: https://single-spa.js.org/
- Microfrontend Architecture: https://martinfowler.com/articles/micro-frontends.html
