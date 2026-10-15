# ADR-003: Web Framework Choice - NestJS vs Express.js

## Status

Accepted

## Context

SwiftTrack requires a robust web framework for building RESTful APIs and WebSocket services. The framework must support dependency injection, decorators, validation, documentation generation, and be suitable for a microservices architecture.

## Decision

We will use **NestJS** as our primary web framework for all microservices.

## Rationale

### NestJS Advantages

1. **Architectural Structure**: Built-in support for modular, scalable architecture
2. **Dependency Injection**: Powerful IoC container with decorators
3. **Decorators**: Clean, declarative approach to validation, guards, interceptors
4. **TypeScript First**: Excellent TypeScript support out of the box
5. **Documentation**: Automatic OpenAPI/Swagger generation
6. **WebSocket Support**: Built-in Socket.IO integration
7. **Microservices**: Native support for microservice patterns
8. **Ecosystem**: Rich ecosystem of modules and integrations
9. **Testing**: Comprehensive testing utilities and mocking support

### Express.js Comparison

While Express.js offers:

- **Simplicity**: Minimal, unopinionated framework
- **Performance**: Slightly better raw performance
- **Flexibility**: Complete freedom in architecture choices
- **Ecosystem**: Massive ecosystem of middleware

It lacks:

- **Structure**: No built-in architectural patterns
- **Type Safety**: Requires significant setup for TypeScript
- **Validation**: Manual setup for request validation
- **Documentation**: No automatic API documentation
- **Consistency**: High risk of inconsistent patterns across services

## Implementation Approach

### Service Architecture

```typescript
// Standard NestJS Service Structure
@Module({
  imports: [TypeOrmModule.forFeature([Entity])],
  controllers: [Controller],
  providers: [Service, Repository],
  exports: [Service],
})
export class FeatureModule {}
```

### Key Patterns

1. **Controllers**: Handle HTTP requests and responses
2. **Services**: Business logic layer
3. **Repositories**: Data access layer
4. **DTOs**: Data transfer objects with validation
5. **Guards**: Authentication and authorization
6. **Interceptors**: Cross-cutting concerns (logging, caching)
7. **Pipes**: Data transformation and validation

### Microservice Communication

```typescript
// Message-based communication
@MessagePattern('order.created')
async handleOrderCreated(data: OrderCreatedEvent) {
  // Handle event
}

// HTTP-based communication
@Get('/health')
async getHealth(): Promise<HealthCheckResult> {
  return this.healthService.check();
}
```

## Configuration Strategy

### Environment Configuration

- Use NestJS ConfigModule for environment variables
- Type-safe configuration with validation
- Hierarchical configuration (default → environment → local)

### Database Integration

- TypeORM integration for PostgreSQL
- Repository pattern for data access
- Migration support with CLI

### Validation Strategy

- class-validator for DTO validation
- Transform pipes for data transformation
- Global validation pipe configuration

## Consequences

### Positive

- **Faster Development**: Built-in patterns reduce boilerplate
- **Consistency**: Standardized structure across all services
- **Type Safety**: Excellent TypeScript integration
- **Documentation**: Automatic API documentation generation
- **Testing**: Comprehensive testing support
- **Scalability**: Well-suited for microservice architecture
- **Maintainability**: Clear separation of concerns

### Negative

- **Learning Curve**: Steeper learning curve than Express
- **Overhead**: Slightly more overhead than raw Express
- **Abstraction**: Higher level of abstraction may hide some details
- **Bundle Size**: Larger bundle size than minimal Express app

### Development Guidelines

1. **Module Design**: One module per business domain
2. **Dependency Injection**: Use DI for all service dependencies
3. **Error Handling**: Global exception filters for consistent error responses
4. **Validation**: DTO validation at controller level
5. **Authentication**: JWT guards with role-based authorization
6. **Logging**: Structured logging with correlation IDs

## Migration Considerations

### From Express

If migrating from Express:

1. **Controllers**: Convert route handlers to NestJS controllers
2. **Middleware**: Convert to guards, interceptors, or pipes
3. **Validation**: Replace custom validation with class-validator
4. **DI**: Refactor to use NestJS dependency injection

### Performance Optimizations

1. **Fastify**: Can switch to Fastify adapter for better performance
2. **Compression**: Enable gzip compression
3. **Caching**: Use built-in caching module
4. **Rate Limiting**: Built-in throttler module

## Monitoring and Observability

### Built-in Features

- Health check endpoints (Terminus module)
- Metrics collection integration
- Request/response logging
- Error tracking and reporting

### Custom Implementations

- Correlation ID tracking
- Performance monitoring
- Custom business metrics
- Distributed tracing integration

## Alternative Frameworks Considered

### Fastify

- Pros: Better performance, JSON schema validation
- Cons: Smaller ecosystem, less mature TypeScript support

### Koa.js

- Pros: Modern async/await support, lightweight
- Cons: Minimal feature set, requires more manual setup

### Express.js + TypeScript

- Pros: Full control, large ecosystem
- Cons: Significant boilerplate, no built-in patterns

## Review Date

This decision will be reviewed in 12 months or if performance requirements cannot be met with current architecture.
