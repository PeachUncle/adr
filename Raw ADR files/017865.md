# 0002. Use Deno as Primary Runtime

Date: 2025-11-03

## Status

Accepted

## Context

The state-docs project needs to choose a primary runtime environment for development and execution. We need a runtime that:

1. Supports modern TypeScript without complex build configurations
2. Has good performance characteristics
3. Provides a secure sandbox by default
4. Has an active ecosystem and good tooling
5. Allows for flexibility to support multiple runtimes if needed

Traditional Node.js requires build tools like TypeScript compiler, bundlers, and complex configuration files. While Node.js has a massive ecosystem, it can be heavyweight for tool development.

## Decision

We will use **Deno 2.x** as the primary runtime for state-docs, while maintaining compatibility with Node.js through the `dnt` (Deno to Node Transform) build tool.

Key aspects of this decision:
- Deno is the development and testing environment
- TypeScript runs directly without compilation
- Standard library provides file system and path utilities
- Node.js compatibility is achieved through a build step using `dnt`
- Runtime adapters in `runtime.ts` abstract platform differences

## Consequences

### Positive

- **Simplified development**: No need for tsconfig.json, complex build setups, or bundlers
- **Native TypeScript**: TypeScript runs directly without compilation step during development
- **Modern features**: Top-level await, ES modules by default, modern APIs
- **Security**: Explicit permissions model (`-A` flag or granular permissions)
- **Standard library**: Well-designed standard library for common tasks
- **Dual runtime support**: Can publish to both JSR (Deno) and npm (Node.js)
- **Better DX**: Faster feedback loops during development

### Negative

- **Smaller ecosystem**: Fewer packages compared to npm (though npm packages can be used)
- **Learning curve**: Team members familiar with Node.js need to learn Deno specifics
- **Build step needed**: Node.js users need the dnt build process
- **Adoption barrier**: Some users may prefer pure Node.js solutions
- **Dual testing**: Must test in both Deno and Node.js runtimes
- **Adapter maintenance**: Runtime adapters add a layer of complexity

### Risks

- **Deno ecosystem maturity**: Deno is newer than Node.js, ecosystem still growing
  - *Mitigation*: Can use npm packages via `npm:` specifier; have Node.js compatibility layer
- **Breaking changes**: Deno is still evolving, may have breaking changes
  - *Mitigation*: Pin to specific Deno version; monitor changelogs
- **Community support**: Smaller community compared to Node.js
  - *Mitigation*: Active Deno Discord and community; good documentation

## Alternatives Considered

- **Node.js only**: Use Node.js as the only runtime
  - *Why not chosen*: Requires complex build configuration, slower development experience, no native TypeScript support
  
- **Bun**: Use Bun as the primary runtime
  - *Why not chosen*: Even newer than Deno, smaller ecosystem, less mature tooling
  
- **Pure Node.js with ESBuild**: Use Node.js with modern build tools
  - *Why not chosen*: Still requires build configuration, doesn't solve the DX issues
  
- **Go or Rust**: Use compiled languages
  - *Why not chosen*: Loses the flexibility and rapid development of JavaScript/TypeScript

## References

- [Deno Manual](https://docs.deno.com/)
- [dnt - Deno to Node Transform](https://github.com/denoland/dnt)
- [runtime.ts - Runtime adapters](../../runtime.ts)
- [deno.json - Deno configuration](../../deno.json)
