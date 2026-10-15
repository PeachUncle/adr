# ADR 001: Use Bun as Runtime

**Status:** Accepted

**Date:** 2025-10-18

**Context:**

WCAG Explorer is a full-stack TypeScript application consisting of a React frontend and a Cloudflare Workers backend. We needed to choose a JavaScript runtime and package manager that would:

- Provide fast installation times for dependencies
- Support TypeScript natively without complex configuration
- Offer good performance for development and build processes
- Work seamlessly with our existing tools (Vite, TypeScript, React)
- Support modern JavaScript/TypeScript features
- Have a reliable ecosystem and community

Traditional options like Node.js with npm/yarn/pnpm have been stable but are known for slower installation times and heavier disk usage. Bun emerged as a modern alternative promising significant performance improvements while maintaining compatibility with the Node.js ecosystem.

**Decision:**

We will use **Bun** as our primary JavaScript runtime and package manager for the WCAG Explorer project.

This applies to:
- Installing and managing dependencies
- Running development scripts
- Building the project
- Running local development servers

**Consequences:**

### Positive

1. **Performance Gains:**
   - Significantly faster package installation (3-10x faster than npm)
   - Quick startup times for development servers
   - Faster execution of TypeScript without transpilation

2. **Native TypeScript Support:**
   - Bun runs TypeScript files directly without requiring separate compilation
   - No need for ts-node or other TypeScript execution tools
   - Simplified toolchain and fewer dependencies

3. **Built-in Tooling:**
   - Integrated test runner (when needed in future)
   - Built-in bundler (though we're using Vite)
   - Native support for JSX/TSX

4. **Simplified Developer Experience:**
   - Single tool for multiple purposes
   - Familiar npm-compatible commands (`bun install`, `bun run`)
   - Compatible with existing `package.json` scripts

5. **Reduced Disk Space:**
   - More efficient `node_modules` structure
   - Global cache reduces duplication across projects

### Negative

1. **Maturity Concerns:**
   - Bun is relatively new (v1.0 released September 2023)
   - May encounter edge cases or bugs not present in Node.js
   - Smaller community and ecosystem compared to Node.js

2. **Team Learning Curve:**
   - Team members need to install and learn Bun
   - Different debugging techniques than Node.js
   - Potential differences in behavior vs Node.js

3. **CI/CD Integration:**
   - Need to set up Bun in CI/CD pipelines
   - Some CI services may not have built-in Bun support
   - Additional setup steps compared to Node.js

4. **Compatibility Risks:**
   - Although designed to be compatible, some npm packages may have issues
   - Native modules may not work as expected
   - Platform-specific builds (mainly targeting macOS/Linux, Windows support improving)

5. **Switching Costs:**
   - If we need to switch back to Node.js, requires team coordination
   - Lock files are Bun-specific (though npm-compatible)
   - Some documentation may reference npm/yarn commands

### Mitigation Strategies

1. **Fallback Option:** Keep the project compatible with Node.js by maintaining standard package.json structure
2. **Documentation:** Document Bun installation and usage in CONTRIBUTING.md
3. **CI Setup:** Use established Bun GitHub Actions for continuous integration
4. **Monitoring:** Track any compatibility issues and report them to Bun team

**Alternatives Considered:**

### Node.js + npm
- **Pros:** Most mature, widest compatibility, default choice
- **Cons:** Slower install times, larger disk footprint, requires additional tools for TypeScript
- **Reason for rejection:** Performance and developer experience improvements with Bun outweigh maturity benefits

### Node.js + pnpm
- **Pros:** Faster than npm, efficient disk usage, growing adoption
- **Cons:** Still slower than Bun, additional tool to learn, doesn't run TypeScript natively
- **Reason for rejection:** Bun offers better performance and native TypeScript support

### Node.js + Yarn
- **Pros:** Reliable, good performance, workspaces support
- **Cons:** Slower than Bun, version fragmentation (v1 vs v2+), doesn't run TypeScript natively
- **Reason for rejection:** Similar to pnpm, Bun provides better overall experience

### Deno
- **Pros:** Native TypeScript, secure by default, modern standard library
- **Cons:** Different module system, less npm compatibility, would require significant architecture changes
- **Reason for rejection:** Not compatible with existing Vite/React ecosystem without compatibility layer

**Notes:**

- This decision primarily affects local development and does not impact the production deployment of the Cloudflare Worker backend
- The React frontend is built and served as static files, so runtime choice doesn't affect production frontend performance
- We maintain compatibility with Node.js to allow flexibility if the ecosystem changes
