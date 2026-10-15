# 3. Dependency Injection and Service Initialization

## Status

Accepted

Date: 2025-06-25

## Context

Our Go domain services require a consistent approach to dependency management and service initialization that:

- Enforces clean component boundaries via interface-based dependencies
- Ensures consistent initialization and wiring of components
- Creates a predictable flow for application startup
- Supports the principles outlined in our Interface Design Principles
- Provides clear ownership and lifecycle management of dependencies

Without a standardized approach to dependency injection, we encounter challenges such as:

- Difficult-to-track component dependencies and initialization order
- Inconsistent initialization patterns across services
- Complex dependency management in large services
- Implicit dependencies through package-level variables

## Decision

We will adopt a constructor-based dependency injection pattern with the following principles:

### 1. Constructor Injection

- Components receive all dependencies through constructor functions
- Dependencies are explicitly declared as parameters
- Constructors return the interface types defined in accordance with our
  [Interface Design Principles](./0002-interface-design-principles.md)

```go
// NewService creates a new JWT service instance
func NewService(logger *zap.Logger, secret []byte) Service {
	return &service{
		logger: logger,
		secret: secret,
	}
}
```

### 2. Layered Initialization

- Initialize dependencies in dependency order:
  1. Infrastructure (logger, database, external clients)
  2. Repositories (data access layers)
  3. Services (business logic)
  4. Handlers (HTTP/API endpoints)
- Use feature-based initialization functions to organize wiring
- Centralize all wiring in the main application entry point

```go
func main() {
	// Initialize infrastructure
	logger := initLogger()
	db := initDatabase(ctx, logger)

	// Initialize features
	jwtService := initJWTFeature(logger)
	refreshService := initRefreshFeature(logger, db)
	initCustomersFeature(logger, db, router, refreshService, jwtService)
}
```

### 3. Standard Parameter Order

- Logger (*zap.Logger) as the first constructor parameter
- Domain-specific dependencies follow in order of importance
- Use configuration objects for complex initialization settings
- Required parameters before optional parameters

### 4. No Global State

- Avoid package-level variables for dependencies
- No init() functions with side effects
- All dependencies must be explicitly passed
- Dependency lifecycles managed by the application entry point

## Consequences

### Positive

- Clear, explicit dependency relationships
- Unified initialization approach across services
- Easy to swap implementations in tests or production
- Dependencies are managed at the appropriate level
- Changes to a component only affect direct consumers

### Negative

- More verbose initialization code in application entry points
- More parameters in constructor functions
- Requires discipline to maintain the pattern

### Neutral

- Some initial setup overhead for initialization organization
- Need to carefully consider dependency ordering

## Implementation Notes

### Feature Initialization Example

```go
func initCustomersFeature(logger *zap.Logger, db *mongo.Database, router *gin.Engine, 
                         refreshService refresh.Service, jwtService jwt.Service) {
	// Initialize the repository
	repo := customers.NewRepository(logger, db, clock.RealClock{})

	// Initialize the service
	service := customers.NewService(logger, repo, refreshService, jwtService)

	// Initialize the handler and register routes
	handler := customers.NewHandler(logger, service)
	handler.RegisterRoutes(router)
}
```

## Related Documents

- [Interface Design Principles](./0002-interface-design-principles.md)

## Contributors

- Àlex Grau Roca
