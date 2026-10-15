# ADR-0001: Use .NET 9 for Backend Framework

## Status

Accepted

## Context

Grafana-banana requires a robust, performant backend framework for building a modern web API. The backend needs to:

- Provide high performance and low latency
- Support modern development practices (async/await, dependency injection)
- Have excellent tooling and IDE support
- Offer strong typing and compile-time safety
- Support containerization and cloud deployment
- Have a large, active community and ecosystem
- Provide built-in support for observability (metrics, tracing, logging)
- Support OpenAPI/Swagger documentation
- Offer long-term support and security updates

## Decision

We will use .NET 9 with ASP.NET Core as the backend framework, implementing the Minimal API pattern for endpoint definitions.

### Key Technologies
- **.NET 9**: Latest Long-Term Support (LTS) version of .NET
- **ASP.NET Core**: Web framework for building APIs
- **Minimal APIs**: Lightweight approach for defining HTTP endpoints
- **OpenTelemetry**: For distributed tracing and metrics
- **Serilog**: For structured logging
- **Health Checks**: Built-in health check endpoints

## Consequences

### Positive

1. **Performance**: .NET 9 provides excellent performance, competitive with native languages
2. **Type Safety**: Strong typing reduces runtime errors
3. **Tooling**: Excellent IDE support (Visual Studio, VS Code, Rider)
4. **Ecosystem**: Large package ecosystem via NuGet
5. **Cross-Platform**: Runs on Windows, Linux, macOS
6. **Modern Features**: Support for latest C# features (records, pattern matching, etc.)
7. **Built-in Features**: 
   - Dependency injection
   - Configuration management
   - Health checks
   - OpenAPI generation
8. **Observability**: Native OpenTelemetry integration
9. **Security**: Regular security updates and patches
10. **Documentation**: Comprehensive Microsoft documentation
11. **Container Support**: Optimized Docker images available
12. **Long-Term Support**: LTS version ensures stability and support

### Negative

1. **Learning Curve**: Team members unfamiliar with .NET need to learn
2. **Ecosystem Lock-in**: Primary ecosystem is .NET-centric
3. **Size**: .NET runtime is larger than some alternatives (Node.js, Go)
4. **Windows Heritage**: Though cross-platform, some Windows-specific conventions remain
5. **Breaking Changes**: Major version upgrades can introduce breaking changes

### Neutral

1. **Open Source**: .NET is open source but primarily driven by Microsoft
2. **Community**: Large community, but different culture than JavaScript/Python
3. **Deployment**: Requires .NET runtime on target systems (or self-contained deployment)

## Implementation

### Timeline
- Initial implementation: Completed
- Migration to .NET 9: Completed
- Ongoing: Keep updated with .NET LTS releases

### Owner
@markcoleman

### Dependencies
- .NET 9 SDK installed on development machines
- .NET 9 runtime available in deployment environments
- Container base images support .NET 9

### Migration Path

For future major version upgrades:
1. Review breaking changes in migration guide
2. Update project files and dependencies
3. Test thoroughly in development environment
4. Update CI/CD pipelines
5. Update Docker base images
6. Deploy to staging for validation
7. Deploy to production with rollback plan

## Alternatives Considered

### Alternative 1: Node.js + Express/NestJS

**Pros:**
- JavaScript/TypeScript across full stack (same language as frontend)
- Large ecosystem (npm)
- Fast development for simple APIs
- Lower learning curve if team knows JavaScript
- Smaller container images

**Cons:**
- Less type safety (even with TypeScript)
- Performance limitations for CPU-intensive tasks
- Callback hell / Promise complexity for complex flows
- Runtime errors more common
- Less mature observability integration
- Single-threaded model has limitations

**Why Rejected:**
While JavaScript consistency across the stack is attractive, .NET provides better performance, type safety, and tooling for building robust backend services. The observability requirements favor .NET's native OpenTelemetry integration.

### Alternative 2: Go

**Pros:**
- Excellent performance
- Small binary size
- Fast compilation
- Built for concurrent operations
- Native binary compilation (no runtime needed)
- Growing observability ecosystem

**Cons:**
- Simpler type system
- Less mature web framework ecosystem
- More verbose error handling
- Smaller community than .NET
- Less comprehensive standard library for web APIs
- Steeper learning curve for object-oriented developers

**Why Rejected:**
Go's performance is excellent, but .NET provides a better balance of performance, developer productivity, and ecosystem maturity. The richer framework and tooling in .NET accelerate development.

### Alternative 3: Java/Spring Boot

**Pros:**
- Mature ecosystem
- Enterprise-proven
- Strong typing
- Excellent tooling
- Large community
- Comprehensive frameworks

**Cons:**
- More verbose than .NET
- Slower startup times
- Larger memory footprint
- Spring Boot can be heavyweight
- Configuration complexity
- Older language features

**Why Rejected:**
While Java/Spring Boot is enterprise-proven, .NET 9 offers similar capabilities with better performance, lower resource usage, and more modern language features. C# is more concise than Java while maintaining type safety.

### Alternative 4: Python + FastAPI/Django

**Pros:**
- Rapid development
- Extensive libraries for data science/ML
- Simple syntax
- Large community
- Good for scripting and automation

**Cons:**
- Performance limitations (GIL)
- Dynamic typing leads to runtime errors
- Less suitable for large-scale applications
- Deployment complexity
- Type hints are optional and not enforced
- Observability integration less mature

**Why Rejected:**
Python's dynamic typing and performance characteristics make it less suitable for a production web API where type safety and performance are priorities. .NET provides better performance and compile-time safety.

## References

- [.NET 9 Documentation](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-9)
- [ASP.NET Core Documentation](https://learn.microsoft.com/en-us/aspnet/core/)
- [Minimal APIs Overview](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis)
- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [Project Repository](https://github.com/markcoleman/Grafana-banana)

## Related ADRs

- [ADR-0002: Use Angular for Frontend Framework](./ADR-0002-angular-frontend-framework.md)
- [ADR-0003: Use Grafana Stack for Observability](./ADR-0003-grafana-observability-stack.md)

## Metadata

| Field | Value |
|-------|-------|
| **Created** | 2025-10-25 |
| **Updated** | 2025-10-25 |
| **Author** | @markcoleman |
| **Reviewers** | Architecture Review Board |
| **Status** | Accepted |
| **Implementation Status** | Complete |
