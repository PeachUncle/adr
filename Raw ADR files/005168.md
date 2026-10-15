# ADR-0022: Clean Architecture CLI Implementation

## Status
**Accepted**

## Context
The Value Train requires a robust command-line interface to implement deterministic business logic that cannot rely on LLM interpretation alone. The CLI must handle complex workflows, rule validation, context detection, and artifact management while maintaining high code quality, testability, and extensibility.

Current challenges include:
- **Non-Deterministic Behavior**: Critical business logic implemented in prompts leads to inconsistent results
- **Monolithic Structure**: Existing Python implementation lacks clear separation of concerns
- **Limited Testability**: Prompt-based logic is difficult to unit test and validate
- **Scalability Issues**: Adding new commands and features requires significant refactoring
- **Maintenance Overhead**: Business logic scattered across multiple files and formats

## Decision
We will implement a clean architecture CLI using .NET 8, following Domain-Driven Design principles with clear separation of concerns, CQRS patterns via MediatR, and feature-based organization.

### Architecture Principles
1. **Clean Architecture**: Clear dependency inversion with domain at the center
2. **Feature-Based Organization**: Group related functionality by business capability
3. **CQRS Pattern**: Separate command (write) and query (read) operations
4. **Dependency Injection**: Loose coupling through interface-based design
5. **Structured Logging**: Comprehensive observability and debugging capabilities

## Architecture

### Project Structure
```
/src/
├── ValueTrain.Domain/
│   ├── Entities/              # Core business entities
│   ├── Interfaces/            # Infrastructure contracts
│   ├── ValueObjects/          # Immutable domain objects
│   ├── Enums/                 # Domain enumerations
│   └── ValueTrain.Domain.csproj
├── ValueTrain.Application/
│   ├── Features/              # Feature-based organization (see below)
│   ├── Common/                # Shared application services
│   │   ├── Interfaces/
│   │   ├── Behaviors/         # MediatR pipeline behaviors
│   │   └── Exceptions/
│   └── ValueTrain.Application.csproj
├── ValueTrain.Infrastructure/
│   ├── FileSystem/            # File operations, template management
│   ├── GitHub/                # GitHub API integration
│   ├── Git/                   # Git operations
│   ├── Logging/               # Structured logging implementation
│   ├── Configuration/         # Settings and configuration
│   └── ValueTrain.Infrastructure.csproj
└── ValueTrain.Presentation/
    ├── Cli/
    │   ├── Commands/           # Spectre.Console command classes
    │   ├── Extensions/         # DI and configuration extensions
    │   ├── Infrastructure/     # CLI-specific services
    │   ├── Program.cs          # Entry point and DI configuration
    │   └── ValueTrain.Presentation.Cli.csproj
    ├── Api/                    # Future: Web API for agent communication
    │   └── ValueTrain.Presentation.Api.csproj
    └── Ui/                     # Future: Web UI for business users
        └── ValueTrain.Presentation.Ui.csproj
```

### Feature-Based Application Layer
Following the established [Application Layer Naming Standards](../../developer-guides/application-layer-naming-standards.md):

```
/src/ValueTrain.Application/Features/
├── SessionManagement/
│   ├── StartSession/
│   │   ├── StartSessionCommand.cs
│   │   ├── StartSessionCommandHandler.cs
│   │   ├── StartSessionCommandValidator.cs
│   │   └── StartSessionResponse.cs
│   ├── UpdateSessionContext/
│   └── GetSessionStatus/
├── IntakeMode/
│   ├── ExecuteIntake/
│   │   ├── ExecuteIntakeCommand.cs
│   │   ├── ExecuteIntakeCommandHandler.cs
│   │   ├── ExecuteIntakeCommandValidator.cs
│   │   └── ExecuteIntakeResponse.cs
│   ├── ValidateIntakeCompletion/
│   └── CreateOpportunityBrief/
├── ContextDetection/
│   └── DetectWorkContext/
│       ├── DetectWorkContextQuery.cs
│       ├── DetectWorkContextQueryHandler.cs
│       └── DetectWorkContextResponse.cs
├── RuleValidation/
│   ├── ValidateRules/
│   └── EnforceQualityGates/
├── ArtifactManagement/
│   ├── CreateArtifact/
│   ├── ValidateArtifact/
│   ├── CheckArtifacts/           # Replaces check_artifacts.py
│   └── GenerateFromTemplate/
├── ChecklistValidation/
│   └── CheckTodos/               # Replaces check_todo.py
├── SessionManagement/
│   ├── StartSession/
│   ├── UpdateSessionContext/
│   ├── AdvancePhase/             # Replaces conductor_update.py
│   └── MigrateSession/           # Replaces migrate_session.py
├── TestRunner/
│   └── RunTests/                 # Replaces test_runner.py
└── GitHubIntegration/
    ├── UpdateIssueStatus/
    ├── CreatePullRequest/
    └── GetProjectItems/
```

### CLI Command Structure
Using Spectre.Console for rich terminal UI and command organization:

```csharp
// ValueTrain.Presentation.Cli/Commands/IntakeCommand.cs
[Description("Execute intake mode for requirements gathering")]
public class IntakeCommand : AsyncCommand<IntakeCommand.Settings>
{
    private readonly IMediator _mediator;
    private readonly IAnsiConsole _console;

    public class Settings : CommandSettings
    {
        [Description("GitHub issue ID")]
        [CommandOption("--issue-id")]
        public int? IssueId { get; set; }

        [Description("Force context detection")]
        [CommandOption("--context")]
        public string? Context { get; set; }
    }

    public override async Task<int> ExecuteAsync(CommandContext context, Settings settings)
    {
        // ASCII Art Display
        _console.Write(new FigletText("INTAKE").Color(Color.Green));
        
        // Execute via MediatR
        var command = new ExecuteIntakeCommand 
        { 
            IssueId = settings.IssueId,
            ForcedContext = settings.Context 
        };
        
        var result = await _mediator.Send(command);
        
        // Display results
        DisplayResults(result);
        
        return result.IsSuccess ? 0 : 1;
    }
}
```

### Domain Layer Design
Core business entities and rules:

```csharp
// ValueTrain.Domain/Entities/Session.cs
public class Session : Entity
{
    public SessionId Id { get; private set; }
    public string Mode { get; private set; }
    public WorkContext Context { get; private set; }
    public SessionStatus Status { get; private set; }
    public List<Artifact> Artifacts { get; private set; }
    
    public Result TransitionTo(string newMode)
    {
        // Business rules for mode transitions
        if (!IsValidTransition(Mode, newMode))
            return Result.Failure($"Invalid transition from {Mode} to {newMode}");
            
        Mode = newMode;
        AddDomainEvent(new SessionModeChanged(Id, newMode));
        return Result.Success();
    }
}

// ValueTrain.Domain/ValueObjects/WorkContext.cs
public class WorkContext : ValueObject
{
    public ContextType Type { get; }
    public string Description { get; }
    
    public static WorkContext Business => new(ContextType.Business, "Business strategy and opportunity analysis");
    public static WorkContext MLEngineering => new(ContextType.MLEngineering, "Machine learning model development");
    public static WorkContext SoftwareEngineering => new(ContextType.SoftwareEngineering, "Software development and integration");
}
```

### Infrastructure Layer Implementation
External service integrations:

```csharp
// ValueTrain.Infrastructure/GitHub/GitHubService.cs
public class GitHubService : IGitHubService
{
    private readonly GitHubClient _client;
    private readonly ILogger<GitHubService> _logger;

    public async Task<Result<Issue>> GetIssueAsync(int issueNumber)
    {
        try
        {
            _logger.LogInformation("Retrieving GitHub issue {IssueNumber}", issueNumber);
            
            var issue = await _client.Issue.Get("owner", "repo", issueNumber);
            return Result.Success(issue);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to retrieve GitHub issue {IssueNumber}", issueNumber);
            return Result.Failure<Issue>($"Failed to retrieve issue: {ex.Message}");
        }
    }
}
```

### MediatR Pipeline Behaviors
Cross-cutting concerns implementation:

```csharp
// ValueTrain.Application/Common/Behaviors/LoggingBehavior.cs
public class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly ILogger<LoggingBehavior<TRequest, TResponse>> _logger;

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken cancellationToken)
    {
        var requestName = typeof(TRequest).Name;
        
        _logger.LogInformation("Executing {RequestName} with {@Request}", requestName, request);
        
        var stopwatch = Stopwatch.StartNew();
        var response = await next();
        stopwatch.Stop();
        
        _logger.LogInformation("Completed {RequestName} in {ElapsedMs}ms", requestName, stopwatch.ElapsedMilliseconds);
        
        return response;
    }
}
```

## Technology Stack

### Core Framework
- **.NET 8**: Latest LTS version with enhanced performance
- **Spectre.Console**: Rich terminal UI and command framework
- **MediatR**: CQRS implementation and request/response patterns
- **FluentValidation**: Input validation and business rule enforcement

### Infrastructure
- **Microsoft.Extensions.Hosting**: Dependency injection and configuration
- **Serilog**: Structured logging with multiple sinks
- **Octokit**: GitHub API integration
- **LibGit2Sharp**: Git operations and repository management

### Quality and Testing
- **xUnit**: Unit testing framework
- **FluentAssertions**: Assertion library for readable tests
- **Moq**: Mocking framework for unit tests
- **ArchUnitNET**: Architecture constraint testing

## Implementation Details

### ASCII Art Integration
Each command displays distinctive ASCII art for visual feedback:

```csharp
public static class AsciiArt
{
    public static void DisplayCommand(IAnsiConsole console, string commandName, Color color = null)
    {
        color ??= Color.Green;
        console.Write(new FigletText(commandName.ToUpper()).Color(color));
        console.WriteLine();
    }
}
```

### Error Handling Strategy
Comprehensive error handling using Result patterns and structured logging:

```csharp
// ValueTrain.Domain/Common/Result.cs
public class Result<T>
{
    public bool IsSuccess { get; }
    public bool IsFailure => !IsSuccess;
    public T Value { get; }
    public string Error { get; }
    
    public static Result<T> Success(T value) => new(true, value, null);
    public static Result<T> Failure(string error) => new(false, default, error);
}
```

### Configuration Management
Hierarchical configuration with environment-specific overrides:

```json
// appsettings.json
{
  "GitHub": {
    "Owner": "charleslbryant",
    "Repository": "agenticops",
    "Token": "" // Set via environment variable
  },
  "ValueTrain": {
    "RulesPath": "docs/rules",
    "TemplatesPath": "docs/templates",
    "SessionContextPath": "docs/session-context"
  },
  "Serilog": {
    "MinimumLevel": "Information",
    "WriteTo": [
      { "Name": "Console" },
      { "Name": "File", "Args": { "path": "logs/valuetrain-.log", "rollingInterval": "Day" } }
    ]
  }
}
```

### Python Script Migration Commands

The CLI will include specific commands to replace existing Python scripts:

```bash
# Replace check_artifacts.py
agenticops artifacts check --phase intake --strict --create-missing

# Replace check_todo.py  
agenticops todos check --strict --mode intake

# Replace conductor_update.py
agenticops session advance --to discover --dry-run

# Replace migrate_session.py
agenticops session migrate --legacy-file old_session.json --backup

# Replace test_runner.py
agenticops test run --basic --verbose
```

Each command implements the same functionality as the Python scripts but with:
- Type safety and compile-time validation
- Comprehensive error handling and logging
- Rich terminal output with progress indicators
- Integration with the broader Value Train workflow

### Dependency Injection Setup
Clean separation of concerns through interface-based design:

```csharp
// ValueTrain.Presentation.Cli/Extensions/ServiceCollectionExtensions.cs
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddValueTrainServices(this IServiceCollection services, IConfiguration configuration)
    {
        // MediatR registration
        services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(StartSessionCommand).Assembly));
        
        // Pipeline behaviors
        services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
        services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
        
        // Infrastructure services
        services.AddScoped<IGitHubService, GitHubService>();
        services.AddScoped<IFileSystemService, FileSystemService>();
        services.AddScoped<IGitService, GitService>();
        
        return services;
    }
}
```

## Consequences

### Positive
- **Maintainability**: Clear separation of concerns and dependency inversion
- **Testability**: All business logic can be unit tested in isolation
- **Scalability**: Feature-based organization supports easy addition of new capabilities
- **Consistency**: Standardized naming and structure across all features
- **Observability**: Comprehensive logging and error handling throughout the system
- **User Experience**: Rich terminal UI with visual feedback and clear error messages

### Negative
- **Complexity**: More initial setup and boilerplate code compared to simple scripts
- **Learning Curve**: Team members need familiarity with clean architecture patterns
- **Over-Engineering Risk**: May be excessive for simple CLI operations

### Neutral
- **Migration Path**: Clear path from existing Python implementation to new architecture
- **Future Expansion**: Architecture supports web API and UI presentations without modification
- **Technology Alignment**: Aligns with Microsoft ecosystem and C# + Semantic Kernel decisions

## Migration Strategy

### Phase 1: Foundation Setup
1. Create project structure and basic DI configuration
2. Implement core domain entities and value objects
3. Set up MediatR pipeline with logging and validation behaviors
4. Create basic Spectre.Console command framework

### Phase 2: Core Commands Implementation
1. Implement session management features
2. Create intake mode command with full feature structure
3. Add context detection and rule validation capabilities
4. Implement artifact management with template integration

### Phase 3: Advanced Features
1. Add remaining Value Train mode commands
2. Implement GitHub integration for issue and project management
3. Add Git operations for branch and commit management
4. Create comprehensive test suite and architecture validation

### Phase 4: Production Readiness
1. Add configuration management and environment-specific settings
2. Implement comprehensive error handling and recovery
3. Add performance monitoring and health checks
4. Create deployment and distribution strategy

## Related Decisions
- [ADR-0007: Migrate from Python to C#](adr-0007-migrate-from-python-to-csharp.md)
- [ADR-0008: Adopt Semantic Kernel Agent Orchestration](adr-0008-adopt-semantic-kernel-agent-orchestration.md)
- [ADR-0016: Secure Command Line Tool](adr-0016-secure-command-line-tool.md)
- [ADR-0021: Rules System Framework](adr-0021-rules-system-framework.md)

## References
- [Application Layer Naming Standards](../../developer-guides/application-layer-naming-standards.md)
- [Clean Architecture Principles](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Spectre.Console Documentation](https://spectreconsole.net/)
- [MediatR Documentation](https://github.com/jbogard/MediatR)