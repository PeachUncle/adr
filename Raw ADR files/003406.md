# ADR 004: Dependency Injection with Autofac

**Status:** Accepted  
**Date:** 2025-12-30  
**Decision Makers:** SDET Lead, Framework Architects

## Context

SpecFlow step bindings required dependencies (services, settings, contexts). Options included:
- Constructor injection (requires DI container)
- Static singletons
- Manual instantiation in steps
- Service locator pattern

## Decision

Implement **Dependency Injection** using **Autofac** as the IoC container.

## Rationale

### Why DI?

1. **Testability**
   - Easy to mock services for unit testing
   - Isolated component testing
   - Clear dependencies

2. **Maintainability**
   - Single Responsibility Principle
   - Decoupled components
   - Easy to refactor

3. **Flexibility**
   - Swap implementations (e.g., mock API clients)
   - Configure lifetimes (singleton, per-scenario)
   - Environment-specific registrations

### Why Autofac?

| Feature | Autofac | MS DI | Decision |
|---------|---------|-------|----------|
| SpecFlow Integration | ✅ Native | ⚠️ Custom | ✅ **Selected** |
| Lifetime Scopes | ✅ Advanced | ⚠️ Basic | ✅ **Selected** |
| Modules | ✅ Built-in | ❌ No | ✅ **Selected** |
| Registration Flexibility | ✅ High | ⚠️ Medium | ✅ **Selected** |
| Learning Curve | ⚠️ Moderate | ✅ Easy | Acceptable |

**Key Factor**: SpecFlow has official `SpecFlow.Autofac` package.

## Implementation

### Container Configuration

```csharp
// Core/DependencyInjection/DependencyInjectionConfig.cs
[ScenarioDependencies]
public static ContainerBuilder CreateContainerBuilder()
{
    var builder = new ContainerBuilder();

    // Configuration (singleton)
    builder.RegisterInstance(ConfigManager.Settings).SingleInstance();

    // Playwright (per-scenario)
    builder.Register(c => Microsoft.Playwright.Playwright.CreateAsync().GetAwaiter().GetResult())
        .As<IPlaywright>()
        .InstancePerLifetimeScope();

    // Services (per-scenario)
    builder.RegisterType<BookingService>().As<IBookingService>().InstancePerLifetimeScope();
    builder.RegisterType<GitHubService>().As<IGitHubService>().InstancePerLifetimeScope();

    return builder;
}
```

### Step Binding Injection

```csharp
[Binding]
public class ApiStepBindings
{
    private readonly IBookingService _bookingService;
    private readonly AppSettings _settings;

    // Constructor injection (Autofac resolves automatically)
    public ApiStepBindings(
        ScenarioContext scenarioContext,
        IBookingService bookingService,
        AppSettings settings)
    {
        _scenarioContext = scenarioContext;
        _bookingService = bookingService;
        _settings = settings;
    }

    [When(@"se envía POST /booking")]
    public async Task WhenSeEnviaPostBooking()
    {
        // Use injected service (no manual instantiation)
        var response = await _bookingService.CreateBookingAsync(booking);
    }
}
```

### Lifetime Scopes

| Scope | Lifetime | Use Case |
|-------|----------|----------|
| `SingleInstance` | Application | Configuration, static data |
| `InstancePerLifetimeScope` | Per scenario | Services, Playwright, contexts |
| `InstancePerDependency` | Per resolution | Transient objects |

## Consequences

### Positive
- **Testability**: Easy to unit test step bindings with mocked services
- **Decoupling**: Step bindings don't know about service implementations
- **Maintainability**: Single place to manage dependencies
- **Scalability**: Easy to add new services

### Negative
- **Learning curve**: Team needs to understand DI concepts
- **Magic**: Dependencies "appear" (not obvious to beginners)
- **Debugging**: Container resolution errors can be cryptic

### Mitigation
- Document DI patterns in CONTRIBUTING.md
- Provide examples of service registration
- Use clear error messages
- Code reviews enforce proper usage

## Anti-Pattern Avoided

### ❌ Manual Instantiation (Before DI)

```csharp
[When(@"se envía POST /booking")]
public async Task WhenSeEnviaPostBooking()
{
    // ❌ Tight coupling, hard to test
    var playwright = await Playwright.CreateAsync();
    var context = await ApiRequestContextFactory.CreateAsync(playwright, url);
    var client = new RestfulBookerClient(context);
    var response = await client.CreateBookingAsync(booking);
    
    // What about cleanup? Who owns playwright?
}
```

### ✅ With DI (After)

```csharp
[When(@"se envía POST /booking")]
public async Task WhenSeEnviaPostBooking()
{
    // ✅ Clean, testable, lifecycle managed
    var response = await _bookingService.CreateBookingAsync(booking);
}
```

## Testing Benefits

### Unit Testing Step Bindings

```csharp
[Test]
public async Task StepBinding_Should_CallService_WhenExecuted()
{
    // Arrange
    var mockService = Substitute.For<IBookingService>();
    var scenarioContext = new ScenarioContext(/* ... */);
    var stepBindings = new ApiStepBindings(scenarioContext, mockService, settings);

    // Act
    await stepBindings.WhenSeEnviaPostBooking();

    // Assert
    await mockService.Received(1).CreateBookingAsync(Arg.Any<BookingRequest>());
}
```

## Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Autofac DI** | SpecFlow native, flexible | Learning curve | ✅ **Selected** |
| MS DI | Simpler, .NET native | No SpecFlow support | ❌ Rejected |
| Static Singletons | Simple | Not testable | ❌ Rejected |
| Manual Instantiation | No magic | Tight coupling | ❌ Rejected |
| Service Locator | Flexible | Anti-pattern | ❌ Rejected |

## Migration Path

### Phase 1: Infrastructure (Completed)
- ✅ Install `SpecFlow.Autofac`
- ✅ Create `DependencyInjectionConfig`
- ✅ Register core services

### Phase 2: Refactor Step Bindings (Completed)
- ✅ Convert to constructor injection
- ✅ Remove manual instantiation
- ✅ Use injected services

### Phase 3: Testing (Future)
- ⏳ Add unit tests for step bindings
- ⏳ Add integration tests for services

## References
- [Autofac Documentation](https://autofac.readthedocs.io/)
- [SpecFlow.Autofac](https://www.nuget.org/packages/SpecFlow.Autofac/)
- [Dependency Injection Principles](https://martinfowler.com/articles/injection.html)
