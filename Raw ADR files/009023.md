# ADR-004: Ollama for Local LLM Execution

**Status:** ✅ Accepted  
**Date:** October 2025  
**Context:** Development Environment Setup

## Context

Development and testing required LLM capabilities without:

- Incurring Azure OpenAI API costs ($0.01-0.03 per 1K tokens)
- Requiring internet connectivity
- Exposing API keys in development environments
- Dependency on external service availability

Options:

- Always use Azure OpenAI (expensive for dev/test)
- Mock LLM responses (not realistic for testing)
- Run local LLM server (Ollama, LocalAI, LM Studio)
- Use smaller cloud models (still requires connectivity)

## Decision

Selected **Ollama** with **llama3.2:3b** model for local LLM execution during development and integration testing.

## Rationale

1. **Cost-Free Development**: Unlimited local inference at no cost
2. **Offline Capability**: Works without internet connection
3. **Fast Startup**: Docker container starts in seconds via Aspire
4. **Adequate Quality**: llama3.2:3b sufficient for development/testing
5. **Production Parity**: Same Semantic Kernel abstraction as Azure OpenAI
6. **CI/CD Integration**: Can run integration tests with actual LLM locally
7. **Simple API**: OpenAI-compatible REST API
8. **Model Variety**: Easy to switch models (llama, phi, mixtral, etc.)

## Consequences

### Positive

- Zero API costs for developers
- Faster development iteration (no network latency)
- Integration tests run with real LLM responses
- Same code path as production (via ILLMService abstraction)
- Dev container includes Ollama pre-configured

### Negative

- Requires 4GB+ RAM for llama3.2:3b model
- Slower inference than Azure OpenAI (20-25s vs 2-3s)
- Quality gap: llama3.2:3b vs GPT-4o (acceptable for dev)
- CI/CD pipelines need Ollama service container
- Model quality inconsistencies vs production GPT-4o

### Risks Mitigated

- Aspire AppHost orchestrates Ollama container automatically
- CI workflow pulls Ollama Docker image before tests
- ILLMService abstraction allows seamless Azure/Ollama switching
- Integration tests use longer timeouts for Ollama (30s vs 10s)

## Implementation Details

**Aspire Configuration** (src/EduMind.AppHost/Program.cs):

```csharp
var ollama = builder.AddContainer("ollama", "ollama/ollama")
    .WithBindMount("ollama-data", "/root/.ollama")
    .WithHttpEndpoint(port: 11434, targetPort: 11434)
    .WithCommand("serve");

// Pull llama3.2:3b model on startup
ollama.WithCommand("run", "llama3.2:3b");
```

**Provider Selection Logic**:

```csharp
// Development: Use Ollama
if (builder.Environment.IsDevelopment())
{
    builder.Services.AddSingleton<ILLMService>(sp => 
        new OllamaLLMService("http://localhost:11434", "llama3.2:3b"));
}
// Production: Use Azure OpenAI
else
{
    builder.Services.AddSingleton<ILLMService>(sp => 
        new AzureOpenAILLMService(config["AzureOpenAI:Endpoint"]));
}
```

**Performance Characteristics**:

- **Ollama (llama3.2:3b)**: 20-25s per evaluation, ~500 tokens/s
- **Azure OpenAI (GPT-4o)**: 2-3s per evaluation, ~5000 tokens/s
- **Quality**: 85% accuracy (Ollama) vs 95% accuracy (Azure) for question generation

## Alternative Considered: Stub/Mock Responses

**Rejected because:**

- Not realistic for integration testing
- Misses LLM-specific edge cases (timeouts, token limits, formatting errors)
- Developers can't validate prompt engineering changes
- CI tests don't catch LLM integration issues

## Related Decisions

- ADR-003: Semantic Kernel for AI Integration
- ADR-007: .NET Aspire for Local Orchestration
- ADR-090: Question Generation Strategy

## References

- `src/EduMind.AppHost/Program.cs` - Ollama container configuration
- `.github/workflows/ci-integration-tests.yml` - Ollama in CI
- Commit: `ec6269e` - "feat: enable Ollama integration tests on PRs using Aspire"
- tests/test-ollama-integration.sh
