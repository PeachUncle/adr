# 4. ES Modules and Modern JavaScript/TypeScript Stack

Date: 2025-08-28

## Status

Accepted

## Context

The project needed to choose a module system and JavaScript/TypeScript configuration. The main options were:

- **CommonJS (CJS)**: Traditional Node.js module system using `require()` and `module.exports`
- **ES Modules (ESM)**: Modern JavaScript standard using `import` and `export`
- **Mixed/Hybrid**: Supporting both systems with transpilation

Key considerations:

- Future-proofing and alignment with modern JavaScript standards
- Performance characteristics and tree-shaking capabilities
- Ecosystem compatibility and tool support
- Developer experience and debugging
- TypeScript integration and type safety
- Node.js version requirements and compatibility

## Decision

We chose **ES Modules (ESM)** with modern TypeScript configuration:

1. **Module System**: Pure ES Modules with `"type": "module"` in package.json
2. **TypeScript Target**: ES2022 with NodeNext module resolution
3. **Node.js Requirement**: Minimum Node.js 22.0.0 for full ESM support
4. **Strict Configuration**: Maximum TypeScript strictness enabled

### Implementation Details

- **package.json**: `"type": "module"` enables ESM-first approach
- **TypeScript Config**:
  - Target: ES2022 (modern features, excellent Node.js support)
  - Module: NodeNext (best TypeScript ESM support)
  - Strict: All strict flags enabled for maximum type safety
- **Import Extensions**: `.js` extensions required in imports (ESM standard)
- **File Extensions**: `.ts` source files compile to `.js` with proper ESM exports

## Consequences

### Positive

- **Modern Standards**: Aligned with current JavaScript ecosystem direction
- **Performance**: Better tree-shaking and optimization opportunities
- **Type Safety**: Excellent TypeScript integration with strict configuration
- **Future-Proof**: No migration needed as ecosystem moves to ESM
- **Developer Experience**: Modern IDE support and better tooling
- **Debugging**: Cleaner stack traces and better source map support
- **Ecosystem**: Growing ecosystem of ESM-first packages

### Negative

- **Learning Curve**: Developers familiar with CommonJS need to adapt
- **Import Extensions**: Requires `.js` extensions in imports (TypeScript quirk)
- **Ecosystem Compatibility**: Some older packages may require special handling
- **Node.js Requirement**: Restricts to Node.js 22+ (modern requirement)
- **Bundling Complexity**: Some bundlers need special ESM configuration

### Mitigation

- **Documentation**: Comprehensive guide in CLAUDE.md for ESM patterns
- **Tooling**: ESLint rules help catch common ESM mistakes
- **Examples**: Clear examples of import/export patterns throughout codebase
- **CI/CD**: Automated validation ensures proper ESM usage
- **Dependencies**: Careful selection of ESM-compatible packages

## References

- [Node.js ES Modules Documentation](https://nodejs.org/api/esm.html)
- [TypeScript ESM Support](https://www.typescriptlang.org/docs/handbook/esm-node.html)
- [ES Modules: A cartoon deep-dive](https://hacks.mozilla.org/2018/03/es-modules-a-cartoon-deep-dive/)
