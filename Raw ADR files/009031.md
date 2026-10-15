# ADR-050: xUnit Test Framework

**Status:** ✅ Accepted  
**Date:** October 2025  
**Context:** Testing Framework Selection

## Context

The project needed a testing framework for:

- Unit tests (business logic, agents, orchestration)
- Integration tests (API endpoints, database operations)
- Performance tests (load testing, benchmarks)

Options:

- xUnit (modern, extensible, community favorite)
- NUnit (mature, feature-rich, traditional)
- MSTest (Microsoft, built into Visual Studio)

## Decision

Selected **xUnit** as the testing framework for all test projects.

## Rationale

1. **Modern Design**: Created by original NUnit authors, improved API
2. **Parallelization**: Tests run in parallel by default (faster CI/CD)
3. **Theory/InlineData**: Parameterized tests with clean syntax
4. **No Test State**: No test fixtures, each test isolated
5. **Community Standard**: Most popular in .NET community
6. **.NET Native**: First-class support in dotnet test CLI
7. **Extensions**: Rich ecosystem (Moq, FluentAssertions, etc.)

## Consequences

### Positive

- **Fast tests**: Parallel execution reduces test time by 60-70%
- **Clean syntax**: `[Fact]`, `[Theory]`, `[InlineData]` are intuitive
- **Isolated tests**: No shared state between tests (no teardown needed)
- **Easy mocking**: Works seamlessly with Moq, NSubstitute
- **IDE support**: Excellent VS Code + C# DevKit integration

### Negative

- **No test fixtures**: Must create setup/teardown via constructors/IDisposable
- **Learning curve**: Developers familiar with NUnit need to adapt
- **Breaking changes**: xUnit 3.0 will have breaking changes (manageable)

### Risks Mitigated

- Used `[Collection]` attribute for tests needing shared context
- Configured test output logging for debugging
- Added test runsettings for code coverage
- Integration tests use `IClassFixture<WebApplicationFactory>` for API testing

## Implementation

**Test Project Structure**:

```
tests/
├── AcademicAssessment.Tests.Unit/          # xUnit unit tests
│   ├── Agents/
│   │   ├── MathematicsAgentTests.cs
│   │   └── PhysicsAgentTests.cs
│   ├── Orchestration/
│   │   └── StudentProgressOrchestratorTests.cs
│   └── Analytics/
│       └── PerformanceAnalyticsTests.cs
├── AcademicAssessment.Tests.Integration/   # xUnit integration tests
│   ├── Controllers/
│   │   ├── AssessmentControllerTests.cs
│   │   └── StudentAnalyticsControllerTests.cs
│   └── Database/
│       └── RepositoryTests.cs
└── AcademicAssessment.Tests.Performance/   # xUnit + BenchmarkDotNet
    └── LLMPerformanceTests.cs
```

**Example Unit Test**:

```csharp
public class MathematicsAgentTests
{
    private readonly Mock<ILLMService> _llmServiceMock;
    private readonly MathematicsAssessmentAgent _agent;

    public MathematicsAgentTests()
    {
        _llmServiceMock = new Mock<ILLMService>();
        _agent = new MathematicsAssessmentAgent(_llmServiceMock.Object);
    }

    [Fact]
    public async Task ProcessTaskAsync_GenerateAssessment_ReturnsValidQuestions()
    {
        // Arrange
        var task = new AgentTask
        {
            Type = "generate_assessment",
            Data = new { StudentId = Guid.NewGuid(), QuestionCount = 5 }
        };
        
        _llmServiceMock.Setup(x => x.GenerateAsync(It.IsAny<string>()))
            .ReturnsAsync("1. What is 2+2? A) 3 B) 4 C) 5\n2. ...");

        // Act
        var result = await _agent.ProcessTaskAsync(task);

        // Assert
        Assert.Equal(TaskStatus.Completed, result.Status);
        Assert.NotNull(result.Result);
        var questions = result.Result as List<Question>;
        Assert.Equal(5, questions.Count);
    }

    [Theory]
    [InlineData(DifficultyLevel.Easy, "elementary algebra")]
    [InlineData(DifficultyLevel.Medium, "quadratic equations")]
    [InlineData(DifficultyLevel.Hard, "calculus derivatives")]
    public void GetPromptForDifficulty_ReturnsCorrectTopic(
        DifficultyLevel difficulty, 
        string expectedTopic)
    {
        // Act
        var prompt = _agent.GetPromptForDifficulty(difficulty);

        // Assert
        Assert.Contains(expectedTopic, prompt, StringComparison.OrdinalIgnoreCase);
    }
}
```

**Example Integration Test**:

```csharp
public class AssessmentControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    private readonly WebApplicationFactory<Program> _factory;

    public AssessmentControllerTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetAssessment_ValidId_ReturnsAssessment()
    {
        // Arrange
        var assessmentId = Guid.Parse("00000000-0000-0000-0000-000000000001");

        // Act
        var response = await _client.GetAsync($"/api/v1/assessments/{assessmentId}");

        // Assert
        response.EnsureSuccessStatusCode();
        var assessment = await response.Content.ReadFromJsonAsync<Assessment>();
        Assert.NotNull(assessment);
        Assert.Equal(assessmentId, assessment.Id);
    }
}
```

**Test Configuration** (tests/coverlet.runsettings):

```xml
<?xml version="1.0" encoding="utf-8" ?>
<RunSettings>
  <DataCollectionRunSettings>
    <DataCollectors>
      <DataCollector friendlyName="XPlat Code Coverage">
        <Configuration>
          <Format>opencover,cobertura</Format>
          <Exclude>[*.Tests]*,[*]*.Program</Exclude>
          <IncludeDirectory>../src/**/*.cs</IncludeDirectory>
        </Configuration>
      </DataCollector>
    </DataCollectors>
  </DataCollectionRunSettings>
</RunSettings>
```

## Test Execution

**Local Development**:

```bash
# Run all tests
dotnet test

# Run specific test project
dotnet test tests/AcademicAssessment.Tests.Unit

# Run with code coverage
dotnet test --collect:"XPlat Code Coverage" --settings tests/coverlet.runsettings

# Run specific test
dotnet test --filter FullyQualifiedName~MathematicsAgentTests.ProcessTaskAsync
```

**CI/CD Pipeline**:

```yaml
- name: Run unit tests
  run: dotnet test --configuration Release --no-build --logger "trx;LogFileName=test-results.trx"

- name: Upload test results
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-results
    path: '**/test-results.trx'
```

## Test Coverage Requirements

**Minimum coverage targets**:

- **Unit tests**: 80% code coverage
- **Integration tests**: All API endpoints covered
- **Critical paths**: 100% coverage (authentication, assessment submission, scoring)

**Current coverage** (as of latest run):

- Overall: 78% (target: 80%)
- Core: 85%
- Agents: 72%
- Orchestration: 81%
- Web API: 68%

## Testing Patterns

**AAA Pattern** (Arrange-Act-Assert):

```csharp
[Fact]
public async Task MethodName_Scenario_ExpectedBehavior()
{
    // Arrange - Set up test data and mocks
    var student = CreateTestStudent();
    
    // Act - Execute the method under test
    var result = await _service.ProcessAsync(student);
    
    // Assert - Verify the outcome
    Assert.NotNull(result);
}
```

**Theory Tests** (parameterized):

```csharp
[Theory]
[InlineData(85, Grade.A)]
[InlineData(75, Grade.B)]
[InlineData(65, Grade.C)]
public void CalculateGrade_ScoreProvided_ReturnsCorrectGrade(
    int score, Grade expectedGrade)
{
    var result = GradingService.CalculateGrade(score);
    Assert.Equal(expectedGrade, result);
}
```

**Mocking with Moq**:

```csharp
var repositoryMock = new Mock<IStudentRepository>();
repositoryMock.Setup(x => x.GetByIdAsync(It.IsAny<Guid>()))
    .ReturnsAsync(testStudent);
```

## Alternative Considered: NUnit

**Rejected because:**

- More verbose syntax (`[Test]` vs `[Fact]`)
- Test fixtures require explicit setup/teardown
- Slower parallel execution
- Less modern API design

## Related Decisions

- ADR-051: Integration Test Approach
- ADR-052: E2E Testing with Playwright
- ADR-040: Reusable GitHub Actions Workflows (test execution)

## References

- `tests/AcademicAssessment.Tests.Unit/` - Unit test project
- `tests/AcademicAssessment.Tests.Integration/` - Integration test project
- `tests/coverlet.runsettings` - Coverage configuration
- Commit: `ecdfd20` - "feat: Complete Task 1.11 - Comprehensive unit tests"
- Commit: `03e8284` - "ci: Enable integration tests on all PRs"
