# ADR 002: Adopt Azure Functions for API Endpoints to Mitigate Cold Starts

## Status
Proposed

## Context
The application is currently deployed as an Azure Web App, which experiences significant cold start delays (60+ seconds for the first request after inactivity). This occurs because Azure unloads the app from memory to conserve resources on lower tiers, requiring full initialization on the next request including .NET runtime loading, JIT compilation, and database seeding.

While enabling "Always On" and scaling up the App Service Plan can mitigate this, these solutions increase costs and may not be suitable for all scenarios. Serverless architectures like Azure Functions offer an alternative approach where functions are event-driven and can scale to zero, potentially providing faster cold starts for API endpoints.

The current architecture uses ASP.NET Core with FastEndpoints, Entity Framework Core with SQLite, and MediatR for CQRS. The API serves patient and contributor data with family relationships.

## Decision
We will evaluate adopting Azure Functions (using .NET Isolated model for .NET 9 compatibility) for API endpoints to address cold start issues. This involves:

- Migrating FastEndpoints to Azure Functions HTTP triggers.
- Maintaining the existing domain logic (UseCases, Core, Infrastructure).
- Using dependency injection and MediatR within functions.
- Configuring function warm-up and scaling settings.

If the evaluation shows significant cold start improvements (target: <5 seconds for first request) without compromising functionality or increasing complexity unduly, we will proceed with the migration.

## Consequences

### Positive

- **Faster Cold Starts**: Azure Functions typically have quicker cold starts than full Web Apps, especially for lightweight APIs.
- **Automatic Scaling**: Functions scale automatically based on demand, potentially reducing costs for variable traffic.
- **Pay-Per-Use**: Only pay for actual executions, which could be cost-effective for low-traffic scenarios.
- **Isolation**: Each function can be deployed independently, improving deployment flexibility.

### Negative

- **Stateless Nature**: Functions are stateless by default, requiring careful handling of database connections and any shared state.
- **Configuration Complexity**: Additional configuration needed for dependency injection, logging, and database context management in serverless environment.
- **Development Overhead**: Requires restructuring the application to work with function triggers instead of a monolithic web app.
- **Monitoring Challenges**: Different monitoring and logging approaches compared to Web Apps.
- **Database Considerations**: SQLite file-based database may not be ideal for serverless; potential need to migrate to Azure SQL or similar.
- **Cold Starts Still Possible**: While generally faster, functions can still experience cold starts, especially after scaling to zero.

### Risks

- Potential performance issues with EF Core in serverless environment.
- Increased complexity in testing and local development.
- Possible vendor lock-in to Azure Functions.

## References

- [Azure Functions Cold Start Performance](https://docs.microsoft.com/en-us/azure/azure-functions/functions-best-practices#reduce-cold-start-delays)
- [Azure Functions .NET Isolated Model](https://docs.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide)
- [Serverless Architecture Patterns](https://docs.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree)
- [ADR 001: Replace Autofac with .NET Core Dependency Injection](adr-001-dotnet-di-adoption.md) - Related architectural decision.

