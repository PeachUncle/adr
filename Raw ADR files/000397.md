# ADR 001: xUnit Fluent BDD vs Reqnroll for Acceptance Testing

**Status**: Accepted

# Context

AcceptanceTesting.Core provides two distinct approaches for implementing BDD-style acceptance tests:

1. **Reqnroll with Gherkin Syntax** - Traditional BDD using `.feature` files and step definitions
2. **xUnit with Fluent BDD API** - Code-first BDD using a fluent Given/When/Then interface

A critical decision factor is test execution performance, particularly at scale.

## Performance Analysis

### Test Execution Times

| Framework | First Test | Subsequent Tests | Performance Ratio |
|-----------|-----------|------------------|-------------------|
| **Reqnroll** | 2.7 seconds | 300ms | Baseline |
| **xUnit Fluent BDD** | 450ms | 100ms | **6x faster (first), 3x faster (subsequent)** |

### Performance Impact at Scale

The performance difference becomes increasingly significant as test suites grow:

| Test Suite Size | Reqnroll (estimated) | xUnit BDD (estimated) | Time Saved |
|----------------|---------------------|---------------------|------------|
| 10 tests | 5.4s | 1.35s | **4.05s (75%)** |
| 50 tests | 17.4s | 4.85s | **12.55s (72%)** |
| 100 tests | 32.7s | 9.35s | **23.35s (71%)** |
| 500 tests | 152.7s | 50.35s | **102.35s (67%)** |
| 1000 tests | 302.7s (5 min) | 100.35s (1.7 min) | **202.35s (67%)** |

**Key Insight**: At enterprise scale (1000+ tests), xUnit provides approximately **3 minutes faster feedback** compared to Reqnroll, which is critical for CI/CD pipelines and developer productivity.

## Execution Performance Analysis

**xUnit**: Minimal overhead, native test runner integration

**Reqnroll**: Additional overhead from Gherkin parsing and step binding resolution

**Impact**: CI/CD feedback cycles, developer wait times, build server costs

## Developer Experience Comparison

#### Reqnroll Approach
```csharp
// Feature file: Login.feature
Feature: User Authentication
  Scenario: Successful login
    Given I am on the login page
    When I log in with valid credentials
    Then I should see the dashboard

// Step definitions: LoginSteps.cs
[Given("I am on the login page")]
public async Task GivenIAmOnTheLoginPage()
{
    await _navigationActor.GoToLoginPage();
}
```

**Pros:**
- Business-readable Gherkin syntax
- Non-technical stakeholders can read/write scenarios
- Standardized BDD format
- Better for regulatory/documentation requirements

**Cons:**
- Context switching between `.feature` files and step definitions
- Step binding resolution can be unclear
- Generated `.feature.cs` files add complexity
- Slower test execution
- Requires Gherkin knowledge

#### xUnit Fluent BDD Approach
```csharp
[Fact]
public async Task UserCanLoginSuccessfully()
{
    await Scenario.Create("User login flow", _output)
        .Given("a user is on the login page", async ctx =>
            await _navigationActor.GoToLoginPage())
        .When("the user logs in with valid credentials", async ctx =>
            await _authenticationOrchestrator.LoginUser("test", "pass123"))
        .Then("the user should see the dashboard", async ctx =>
            await _dashboardValidator.ShouldBeDisplayed())
        .RunAsync();
}
```

**Pros:**
- All code in one place - no file switching
- Native C# debugging and IntelliSense
- Significantly faster test execution
- No generated files to manage
- Type-safe step definitions
- Familiar xUnit patterns

**Cons:**
- Requires programming knowledge to read/write scenarios
- Less accessible to non-technical stakeholders
- Not a standardized format

## Output and Reporting

Both approaches provide detailed step-by-step output:

**xUnit BDD Output:**
```
Scenario: User login flow
--------------------------------------------------
Given a user is on the login page
  Completed in 125ms

 When the user logs in with valid credentials
  Completed in 245ms

 Then the user should see the dashboard
  Completed in 89ms
--------------------------------------------------
Scenario completed successfully with 3 step(s)
```

**Reqnroll Output:**
```
Feature: User Authentication
Scenario: Successful login
  Given I am on the login page
  When I log in with valid credentials  
  Then I should see the dashboard
```

Both provide comparable readability and debugging information.

## Maintainability Comparison

| Aspect | Reqnroll | xUnit Fluent BDD |
|--------|----------|------------------|
| Code Colocation | ❌ Separate files | ✅ Single file |
| Refactoring Support | ⚠️ Manual updates needed | ✅ IDE refactoring works |
| Generated Files | ❌ `.feature.cs` to manage | ✅ None |
| Step Reusability | ✅ Across features | ✅ Standard C# methods |
| Debugging | ⚠️ Context switching | ✅ Seamless |

## Decision

**Recommendation**: Use xUnit Fluent BDD as the default approach, with Reqnroll available for teams with specific business stakeholder requirements.

## Rationale

1. **Performance at Scale**: The 3-6x performance advantage becomes critical as test suites grow. Faster feedback improves developer productivity and reduces CI/CD costs.

2. **Developer Productivity**: Single-file approach with full IDE support (IntelliSense, refactoring, debugging) streamlines development workflows.

3. **Maintainability**: No generated files, native C# tooling, and code colocation reduce maintenance burden.

4. **Modern Development Practices**: Aligns with code-first approaches common in modern .NET development.

# Consequences

## Benefits

- ✅ Faster test execution improves CI/CD feedback loops
- ✅ Reduced context switching improves developer flow
- ✅ No generated files simplify repository management
- ✅ Better IDE integration for debugging and refactoring
- ✅ Lower learning curve for C# developers

## Trade-offs

- ❌ Tests are less accessible to non-technical stakeholders
- ❌ Not using standardized Gherkin format
- ❌ May require additional documentation for business context

## Risks

1. **Stakeholder Engagement**: Non-technical stakeholders may have difficulty reading or contributing to code-first tests
2. **Documentation Drift**: Without living documentation from Gherkin, business requirements may become disconnected from test implementation
3. **Industry Standards**: Deviating from Gherkin standard may make onboarding BDD practitioners more difficult

## Mitigation Strategies

For teams requiring stakeholder visibility:
1. Generate human-readable test reports from xUnit output
2. Maintain feature documentation separately
3. Use descriptive scenario and step names
4. Consider hybrid approach: xUnit for technical tests, Reqnroll for stakeholder-facing scenarios

# Alternatives Considered

## Reqnroll with Gherkin Syntax

**Approach:**
- Traditional BDD using `.feature` files and step definitions
- Business-readable Gherkin syntax

**When to Choose:**
- Non-technical stakeholders actively write/review tests
- Regulatory requirements mandate human-readable specs
- Living documentation is a primary goal
- Team has strong BDD/Gherkin experience

**Example:**
```csharp
// Feature file: Login.feature
Feature: User Authentication
  Scenario: Successful login
    Given I am on the login page
    When I log in with valid credentials
    Then I should see the dashboard

// Step definitions: LoginSteps.cs
[Given("I am on the login page")]
public async Task GivenIAmOnTheLoginPage()
{
    await _navigationActor.GoToLoginPage();
}
```

**Advantages:**
- Business-readable Gherkin syntax
- Non-technical stakeholders can read/write scenarios
- Standardized BDD format
- Better for regulatory/documentation requirements

**Disadvantages:**
- Context switching between `.feature` files and step definitions
- Step binding resolution can be unclear
- Generated `.feature.cs` files add complexity
- Slower test execution (2.7s first test, 300ms subsequent)
- Requires Gherkin knowledge

# References

- [Martin Fowler - Fluent Interface](https://martinfowler.com/bliki/FluentInterface.html)
- [Project README - xUnit BDD Scenarios](../README.md#xunit-bdd-scenarios)
- [Project README - Reqnroll Integration](../README.md#bdd-integration-with-reqnroll)
- Performance benchmarks: Internal testing on .NET 8.0
