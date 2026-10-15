---
title: "ADR-002: Adoption of Aspire for Distributed Application Development"
date: 2025-11-13
status: Accepted
tags: [aspire, distributed-applications, orchestration, development-tools]
---

# ADR-002: Adoption of Aspire for Distributed Application Development

## Status

Accepted

## Date

2025-11-13

## Context

Modern application development increasingly involves distributed architectures with multiple services, databases, message queues, and other dependencies. Developing, debugging, and deploying these distributed applications presents several challenges:

1. **Complex Local Development**: Running multiple services locally requires managing startup order, service discovery, connection strings, and inter-service communication
2. **Configuration Management**: Different configurations for development, staging, and production environments lead to errors and inconsistencies
3. **Debugging Difficulties**: Debugging across multiple services and understanding distributed transactions is complex
4. **Deployment Complexity**: Moving from local development to cloud deployment often requires rewriting infrastructure definitions
5. **Dependency Management**: Ensuring all required services (databases, caches, message brokers) are available and properly configured
6. **Environment Parity**: Maintaining consistency between development and production topologies

Traditional approaches involve managing multiple configuration files, Docker Compose setups, complex scripts, and separate infrastructure-as-code definitions for deployment. This creates friction between development and production environments.

**Aspire** (https://aspire.dev) is a unified platform for building, running, debugging, and deploying distributed applications. It provides a code-first approach to defining application architecture and orchestration, bridging the gap between local development and cloud deployment.

## Decision

We have decided to adopt **Aspire as the standard platform for developing and deploying distributed, web-enabled applications** at Wigo4it.

### Scope

This ADR applies to:
- **Web-enabled applications**: ASP.NET Core web applications, Web APIs, Blazor applications
- **Distributed systems**: Microservices architectures, service-oriented applications
- **Polyglot applications**: While Aspire originates from the .NET ecosystem, it is designed as a polyglot platform and can orchestrate services written in any language
- **Cloud-native applications**: Applications intended for deployment to Kubernetes or cloud platforms

### Exclusions

This ADR does **NOT** apply to:
- **Console applications** without web/network interfaces
- **Desktop applications** (WPF, WinForms, MAUI desktop)
- **Mobile-only applications** (iOS, Android) without backend services
- **Single-service applications** with no distributed components
- **Legacy applications** not being actively modernized

## Rationale

### Why Aspire is the Go-To Tool

#### 1. Unified Development Experience
Aspire provides a **single command to launch and debug your entire distributed application**. Instead of:
- Starting multiple terminal windows
- Running multiple `dotnet run` commands
- Managing Docker Compose files
- Configuring service discovery manually

You simply run the AppHost project, and Aspire:
- Starts all services in the correct order
- Handles dependencies automatically
- Configures service-to-service connections
- Provides a unified dashboard for monitoring

#### 2. Code-First Configuration
**Define your application architecture in code, not complex config files.** Benefits include:

- **Type Safety**: Configuration errors caught at compile time, not runtime
- **IntelliSense Support**: Full IDE support with code completion and documentation
- **Version Control**: Infrastructure definition lives alongside application code
- **Refactoring**: Use familiar development tools to restructure your architecture
- **No YAML Hell**: Avoid brittle configuration files that break with minor syntax errors

Example:
```csharp
var builder = DistributedApplication.CreateBuilder(args);

var cache = builder.AddRedis("cache");
var db = builder.AddPostgres("postgres")
    .AddDatabase("catalogdb");

builder.AddProject<Projects.CatalogApi>("catalogapi")
    .WithReference(db)
    .WithReference(cache);
```

#### 3. Local Orchestration
Aspire **automatically handles service startup, dependencies, and connections** during development:

- **Dependency Management**: Services start in the correct order based on dependencies
- **Service Discovery**: Automatic configuration of service endpoints
- **Connection String Management**: Automatic generation and injection of connection strings
- **Resource Provisioning**: Containers for databases, caches, and message queues started automatically
- **Health Checks**: Monitoring of service health and readiness

#### 4. Deployment Flexibility
Deploy to **Kubernetes, cloud providers, or your own servers** using the same architecture definition:

- **Consistent Topology**: Local development matches production architecture
- **Multiple Targets**: Deploy to Azure Container Apps, Kubernetes, Docker, or custom hosts
- **No Rewrite**: Same architecture code works for both development and production
- **Infrastructure-as-Code**: Generate deployment manifests from your AppHost definition
- **Cloud-Agnostic**: Not locked into a specific cloud provider

#### 5. Polyglot Platform Support
While Aspire originates from the .NET ecosystem, it is **designed to be polyglot**:

- **Container Support**: Orchestrate services written in any language via containers
- **Dockerfile Integration**: Use existing Dockerfiles for non-.NET services
- **Language Agnostic**: Python, Node.js, Java, Go services can be integrated
- **Mixed Architectures**: Combine .NET services with services in other languages
- **Future-Proof**: Aspire's architecture supports expanding to more languages

#### 6. Rich Ecosystem and Extensibility
Aspire provides **extensibility through integrations**:

- **Pre-built Integrations**: Redis, PostgreSQL, MongoDB, RabbitMQ, Kafka, and more
- **Custom Resources**: Define your own resource types
- **Tool Integration**: Works with existing developer tools and workflows
- **Community Components**: Growing ecosystem of community-contributed integrations

#### 7. Enhanced Developer Experience
Aspire improves day-to-day development:

- **Unified Dashboard**: Real-time view of all services, logs, traces, and metrics
- **Structured Logging**: Centralized log aggregation across all services
- **Distributed Tracing**: Built-in OpenTelemetry support for tracing requests
- **Metrics Collection**: Automatic collection and visualization of metrics
- **Fast Iteration**: Changes reflected quickly without restarting everything

### Development vs Production Consistency

Aspire bridges the gap between development and production:

- **Development**: Run services locally with automatic dependency management
- **Production**: Deploy the same architecture to cloud platforms
- **Consistency**: Local environment matches production topology
- **No Surprises**: Catch configuration issues early in development

**Aspire doesn't replace your existing deployment workflows**—it enhances them by providing a consistent way to define and manage your application architecture across environments.

## Consequences

### Positive Consequences

1. **Faster Development Cycles**: Developers spend less time on setup and configuration
2. **Reduced Configuration Errors**: Type-safe configuration reduces runtime errors
3. **Easier Onboarding**: New team members can run entire system with single command
4. **Better Debugging**: Unified dashboard and tracing simplify troubleshooting
5. **Consistent Environments**: Development matches production, reducing "works on my machine" issues
6. **Improved Productivity**: Less time managing infrastructure, more time writing features
7. **Cloud-Ready**: Applications designed for cloud deployment from day one
8. **Standardization**: Consistent approach across all distributed applications
9. **Future-Proof**: Polyglot support allows gradual adoption of new technologies
10. **Better Observability**: Built-in monitoring, logging, and tracing

### Negative Consequences

1. **Learning Curve**: Team members need to learn Aspire concepts and APIs
2. **Additional Tooling**: Requires Aspire CLI and .NET SDK installation
3. **.NET Dependency**: AppHost project requires .NET SDK even for polyglot apps
4. **Early Stage**: Aspire is relatively new; some edge cases may not be covered
5. **Migration Effort**: Existing distributed apps require refactoring to adopt Aspire
6. **Opinionated Structure**: Aspire enforces specific architectural patterns
7. **Debugging Complexity**: Initial setup of distributed debugging may be complex

### Migration Considerations

For existing distributed applications:

1. **Greenfield Projects**: Use Aspire from day one
2. **Active Development**: Plan migration during feature work or refactoring
3. **Legacy Projects**: Evaluate migration only if significant modernization is planned
4. **Gradual Adoption**: Can introduce Aspire incrementally service-by-service

## Implementation

### Immediate Actions (Month 1)

1. **Install Aspire CLI** on all developer machines:
   ```bash
   dotnet workload install aspire
   ```

2. **Update Project Templates**: Create Aspire-based templates for new distributed apps

3. **Training**: Provide team training on Aspire concepts:
   - AppHost project structure
   - Resource definitions
   - Service references
   - Local orchestration
   - Deployment options

4. **Documentation**: Create internal guides for:
   - Setting up new Aspire projects
   - Adding resources and services
   - Debugging distributed applications
   - Deploying to various targets

### Short Term (Months 2-3)

1. **Pilot Projects**: Select 2-3 new distributed applications to build with Aspire
2. **Feedback Loop**: Gather team feedback and refine practices
3. **Integration Catalog**: Document available Aspire integrations for common services
4. **CI/CD Integration**: Update build pipelines to support Aspire projects
5. **Deployment Templates**: Create templates for deploying to target environments

### Medium Term (Months 4-6)

1. **Migration Planning**: Identify existing distributed apps for Aspire migration
2. **Best Practices**: Document patterns and anti-patterns learned from pilot projects
3. **Custom Integrations**: Develop Aspire integrations for company-specific services
4. **Observability**: Establish standards for logging, tracing, and metrics
5. **Performance Baselines**: Measure and document performance characteristics

### Long Term (6+ Months)

1. **Polyglot Expansion**: Explore integrating non-.NET services
2. **Advanced Scenarios**: Implement complex distributed patterns
3. **Tooling Enhancement**: Develop internal tools to enhance Aspire workflows
4. **Knowledge Sharing**: Regular tech talks and demos of Aspire capabilities
5. **Continuous Improvement**: Regularly review and update Aspire practices

## Guidelines

### When to Use Aspire

✅ **Use Aspire when**:
- Building new distributed applications
- Application has multiple services that need to communicate
- Application uses databases, caches, or message queues
- Planning to deploy to cloud or Kubernetes
- Team needs unified development experience
- Consistency between dev and prod environments is important

❌ **Do NOT use Aspire when**:
- Building single-service applications
- Creating console utilities or tools
- Developing desktop or mobile-only apps
- Working on legacy apps not being modernized
- Application has no network/distributed components

### Required Project Structure

Aspire projects should follow this structure:
```
MySolution/
├── src/
│   ├── MyApp.AppHost/          # Aspire orchestration project
│   ├── MyApp.ServiceDefaults/  # Shared configuration
│   ├── MyApp.ApiService/       # API service
│   ├── MyApp.WebApp/           # Web frontend
│   └── MyApp.Worker/           # Background worker
└── docs/
```

### Development Workflow

1. **Start Development**: Run the AppHost project (`dotnet run --project MyApp.AppHost`)
2. **Monitor Dashboard**: Use Aspire dashboard to view logs, traces, and metrics
3. **Debug Services**: Attach debugger to individual services as needed
4. **Test Changes**: Aspire automatically restarts changed services
5. **Deploy**: Use `azd deploy` or similar commands for deployment

### Deployment Targets

Approved deployment targets for Aspire applications:
- **Azure Container Apps** (Primary recommendation)
- **Kubernetes** (AKS or any K8s cluster)
- **Docker Compose** (Development/staging only)
- **Azure Container Instances**
- **Self-hosted containers** (with appropriate orchestration)

## Monitoring and Review

- **Quarterly Reviews**: Assess Aspire adoption and address any issues
- **Feedback Collection**: Gather ongoing developer feedback
- **Training Updates**: Update training materials as Aspire evolves
- **Tooling Review**: Evaluate new Aspire features and integrations
- **Annual Assessment**: Review this ADR for continued relevance

## Exceptions

Exceptions to this ADR may be granted for:

1. **Platform Constraints**: Third-party platforms that don't support Aspire deployment
2. **Customer Requirements**: Customer-mandated deployment methods
3. **Regulatory Requirements**: Compliance requirements incompatible with Aspire
4. **Legacy Integration**: Systems that must integrate tightly with non-Aspire legacy apps

All exceptions must be:
- Documented with technical justification
- Approved by architecture team
- Reviewed annually for continued validity

## References

- [Aspire Documentation](https://aspire.dev/)
- [What is Aspire?](https://aspire.dev/get-started/what-is-aspire/)
- [Aspire AppHost](https://aspire.dev/get-started/app-host/)
- [Aspire Integrations Gallery](https://aspire.dev/integrations/gallery/)
- [Aspire Samples](https://aka.ms/aspiresamples)
- [Microsoft Learn: .NET Aspire](https://learn.microsoft.com/dotnet/aspire)
- [Aspire GitHub Repository](https://github.com/dotnet/aspire)

## Related Documents

- ADR-001: Migration to .NET 10
- Architecture Guidelines: Microservices Design
- DevOps Guidelines: Container Orchestration
- Cloud Standards: Azure Deployment Practices
