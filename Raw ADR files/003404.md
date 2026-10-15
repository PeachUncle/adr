# ADR 002: Hybrid Screenplay + Page Object Model

**Status:** Accepted  
**Date:** 2025-12-30  
**Decision Makers:** SDET Lead, Automation Engineers

## Context

UI test organization required a clear pattern. Common patterns include:
- Page Object Model (POM)
- Screenplay Pattern
- Keyword-Driven
- Linear Scripts

## Decision

We implemented a **Hybrid Approach**: Screenplay for high-level flows + POM for atomic operations.

## Architecture

```
UiStepBindings (Thin Glue Layer)
    ↓
Screenplay Tasks (Business-Level Actions)
    ↓
Page Objects (Technical Implementation)
    ↓
Locators (Element Selectors)
```

## Rationale

### Why Hybrid?

1. **Best of Both Worlds**
   - Screenplay: Readable, business-focused tests
   - POM: Reusable, maintainable technical layer

2. **Clear Separation**
   - Tasks = "What to do" (business intent)
   - Pages = "How to do it" (technical implementation)

3. **Flexibility**
   - Simple scenarios can use POM directly
   - Complex workflows use Screenplay
   - No forced over-engineering

### Screenplay Advantages
- Actor-centric (represents user behavior)
- Highly readable test code
- Easy to compose complex flows
- Decouples test intent from implementation

### POM Advantages
- Industry standard (low learning curve)
- Encapsulates page structure
- Easy to maintain when UI changes
- Simple for atomic operations

### Why Not Pure Screenplay?
- Overkill for simple page interactions
- Steeper learning curve for beginners
- More boilerplate for trivial operations

### Why Not Pure POM?
- Business logic leaks into steps
- Hard to read complex flows
- Less expressive for user journeys

## Implementation Examples

### Using POM Directly (Simple Assertion)
```csharp
[Then(@"debe ver la página de inventario")]
public async Task ThenDebeVerLaPaginaDeInventario()
{
    var page = new SauceDemoLoginPage(Context.Page!);
    var visible = await page.IsInventoryVisibleAsync();
    Assert.That(visible, Is.True);
}
```

### Using Screenplay (Complex Flow)
```csharp
[When(@"ingresa credenciales válidas")]
public async Task WhenIngresaCredencialesValidas()
{
    await _actor!.AttemptsTo(new LoginToSauceDemo(username, password));
}

// Task encapsulates the flow
public class LoginToSauceDemo : ITask
{
    public async Task ExecuteAsync(Actor actor)
    {
        var page = new SauceDemoLoginPage(actor.Page);
        await page.NavigateAsync();
        await page.LoginAsync(_username, _password);
    }
}
```

## Consequences

### Positive
- Flexible: Choose pattern based on complexity
- Maintainable: Clear separation of concerns
- Readable: Business intent is explicit
- Scalable: Easy to add new pages/tasks

### Negative
- Two patterns to learn (vs one)
- Requires judgment on when to use each
- Slightly more initial setup

### Mitigation
- Document guidelines in CONTRIBUTING.md
- Provide examples of each pattern
- Code reviews enforce consistency

## Guidelines

### Use Screenplay When:
- Multi-step user flows
- Business process automation
- Complex interactions across multiple pages
- Reusable user journeys

### Use POM Directly When:
- Single page interactions
- Simple assertions
- Element visibility checks
- Atomic operations

## Alternatives Considered

| Pattern | Pros | Cons | Decision |
|---------|------|------|----------|
| Pure POM | Simple, standard | Limited expressiveness | ❌ Too rigid |
| Pure Screenplay | Highly readable | Overkill for simple tests | ❌ Over-engineered |
| Keyword-Driven | Non-technical friendly | Maintenance nightmare | ❌ Not suitable |
| **Hybrid** | Flexible, best practices | Two patterns | ✅ **Selected** |

## References
- [Screenplay Pattern Explained](https://serenity-bdd.info/docs/screenplay/screenplay_fundamentals)
- [Page Object Model Best Practices](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/)
