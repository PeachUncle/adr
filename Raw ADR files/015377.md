# ADR 001: Fastify Framework Selection

**Status**: Accepted

**Date**: 2025-10-05

**Context**:
We needed to select a web framework for building the basic health check server. The framework must meet the following requirements:
- Node.js 20.0.0+ LTS compatibility (constitutional requirement)
- TypeScript 5.5.0+ support with comprehensive type definitions
- High performance for handling health check requests without rate limiting
- Native ESM support (modern standard)
- Active maintenance and robust ecosystem
- Clean Architecture compatibility (framework-agnostic business logic)

The framework will power a simple `/status` endpoint initially, but must scale to support future service additions while maintaining performance and developer experience.

**Decision**:
We chose **Fastify v5.6.1** as the web framework.

**Rationale**:
- **Performance**: Fastify delivers 30,000+ requests/second, significantly outperforming alternatives. This ensures health checks remain responsive even under heavy load.
- **Modern Architecture**: Native ESM support and async/await patterns align with modern JavaScript standards and our TypeScript configuration.
- **TypeScript Excellence**: Comprehensive type definitions and first-class TypeScript support provide type safety and superior IDE integration.
- **Active Maintenance**: Current major version (v5.x) with active development as of October 2025, ensuring long-term viability.
- **Plugin Ecosystem**: Robust plugin system allows clean separation of concerns and supports Clean Architecture principles.
- **Framework Independence**: Schema-based validation and plugin architecture allow business logic isolation in domain/application layers.

**Alternatives Considered**:
1. **Express.js**:
   - Pros: Most mature ecosystem, widespread adoption
   - Cons: Slower performance, callback-based patterns, lacks native TypeScript support, aging architecture
   - Rejected: Performance limitations and lack of modern patterns

2. **Koa**:
   - Pros: Excellent middleware design, modern async/await patterns
   - Cons: Smaller ecosystem, fewer plugins, less TypeScript support
   - Rejected: Limited ecosystem for future growth

3. **NestJS**:
   - Pros: Enterprise-grade framework, built-in Clean Architecture support
   - Cons: Heavyweight for simple health check, steep learning curve, unnecessary complexity
   - Rejected: Over-engineered for current requirements

**Consequences**:

**Positive**:
- High-performance health checks capable of handling unlimited concurrent requests (FR-010 requirement)
- Excellent TypeScript developer experience with full type safety
- Native JSON Schema validation reduces external dependencies
- Plugin architecture supports Clean Architecture layer separation
- Async/await patterns improve code readability and error handling
- Modern ESM modules enable better tree-shaking and optimization

**Negative**:
- Smaller community compared to Express (mitigated by active development and comprehensive documentation)
- Less Stack Overflow content for troubleshooting (mitigated by excellent official documentation)
- Plugin patterns may require learning curve for Express developers

**Neutral**:
- Requires Node.js 20.0.0+ (aligns with constitutional requirements, not a limitation)
- Schema-based validation requires different approach than class-validator patterns
- Framework-specific plugins isolated to infrastructure layer per Clean Architecture

**Implementation Notes**:
- Fastify server configuration resides in `infrastructure/web/server.ts`
- Route definitions in `infrastructure/web/routes/` directory
- Controllers in `infrastructure/web/controllers/` handle HTTP-specific logic
- JSON schemas in `infrastructure/web/schemas/` for request/response validation
- Business logic remains framework-independent in domain/application layers

**References**:
- [Fastify Documentation](https://fastify.dev/)
- [Fastify TypeScript Guide](https://fastify.dev/docs/latest/Reference/TypeScript/)
- Research findings: `/Users/abhishek/Documents/Personal/readme-kit/specs/001-create-basic-server/research.md`
- Feature specification: `/Users/abhishek/Documents/Personal/readme-kit/specs/001-create-basic-server/spec.md`
